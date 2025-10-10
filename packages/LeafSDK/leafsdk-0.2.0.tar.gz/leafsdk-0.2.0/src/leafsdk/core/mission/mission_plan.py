# leafsdk/core/mission/mission_plan.py

import json
from typing import Optional, Literal, TypeAlias, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto
import traceback
import networkx as nx
import matplotlib.pyplot as plt
from leafsdk import logger
from leafsdk.utils.logstyle import LogIcons
from leafsdk.core.interfaces import IMavLinkProxy, IRedisProxy
from leafsdk.core.mission.mission_step import MissionStep, step_from_dict, StepMemory
from pymavlink.dialects.v20 import droneleaf_mav_msgs as leafMAV



class MissionState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    CANCELLED = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class MissionStatus:
    step_id: Optional[str] = None
    step_description: Optional[str] = None
    next_step_id: Optional[str] = None
    next_step_description: Optional[str] = None
    step_completed: bool = False
    state: MissionState = MissionState.IDLE

    def as_dict(self) -> dict:
        """Return a serializable dictionary for external systems."""
        return self.__dict__.copy()
    
    def reset(self):
        self.step_id = None
        self.step_description = None
        self.next_step_id = None
        self.next_step_description = None
        self.step_completed = False
        self.state = MissionState.IDLE

    def set_step(self, node: str, graph: nx.MultiDiGraph):
        self.step_id = str(node)
        self.step_description = graph.nodes[node]['step'].description()
    
    def set_next_step(self, node: str, graph: nx.MultiDiGraph):
        self.next_step_id = str(node)
        self.next_step_description = graph.nodes[node]['step'].description()

    def completed(self, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.COMPLETED
        self.step_completed = True
        self.set_step(node, graph)
        return _state != self.state
    
    def step_transition(self, prev_node: str, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.RUNNING
        self.step_completed = True
        self.set_step(prev_node, graph)
        self.set_next_step(node, graph)
        return _state != self.state

    def running(self, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.RUNNING
        self.set_step(node, graph)
        return _state != self.state

    def paused(self, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.PAUSED
        self.step_completed = True
        self.set_step(node, graph)
        return _state != self.state

    def canceled(self, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.CANCELLED
        self.step_completed = True
        self.set_step(node, graph)
        return _state != self.state

    def failed(self, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.FAILED
        self.set_step(node, graph)
        return _state != self.state


class MissionPlan:
    def __init__(self, name: str="UnnamedMission"):
        self.name = name
        self.mission_status = MissionStatus()
        self._current_step = None
        self._memory = StepMemory()
        self._validated = False
        self._graph = nx.MultiDiGraph()
        self._current_node = None
        self._head_node = None
        self._last_added_node = None
        self._mission_control_cmd = None

    def add(self, to_name: str, to_step: MissionStep, from_name: str=None, condition=None):
        first_node = not self._graph.nodes
        self.add_step(to_name, to_step)
        if first_node:
            self.set_start(to_name)
        if from_name:
            self.add_transition(from_name, to_name, condition)
        elif self._last_added_node:
            self.add_transition(self._last_added_node, to_name, condition)
        self._last_added_node = to_name

    def add_step(self, name: str, step: MissionStep):
        if name in self._graph:
            raise ValueError(f"Node name '{name}' already exists in mission plan '{self.name}'.")
        self._graph.add_node(name, step=step)

    def add_transition(self, from_step: str, to_step: str, condition=None):
        self._graph.add_edge(from_step, to_step, condition=condition, key=None)

    def set_start(self, name: str):
        if name not in self._graph:
            raise ValueError(f"Start node '{name}' not found in mission graph.")
        self._current_node = name
        self._head_node = name
        self._current_step = self._graph.nodes[name]['step']

    def run_step(self, mav_proxy: IMavLinkProxy=None, redis_proxy: IRedisProxy=None):
        """Execute the current mission step."""
        if self._mission_control_cmd == MissionState.CANCELLED:
                self._canceled()
                return self.mission_status.as_dict()    

        if self._current_step is None:
            logger.warning(f"{LogIcons.WARNING} Cannot run step: no current step available")
            self._mission_control_cmd = MissionState.IDLE
            self.mission_status.reset()
            return self.mission_status.as_dict()

        if self._current_step.first_exec():
            self._current_step.feed_memory(self._memory)
            logger.info(f"{LogIcons.RUN} Executing step: {self._current_node}")

        try:
            result, completed, self._memory = self._current_step.execute_step(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
        except Exception as e:
            self._failed(e)
            return self.mission_status.as_dict()

        if completed:
            if self._mission_control_cmd == MissionState.PAUSED:
                self._paused()
                return self.mission_status.as_dict()

            prev_node = self._current_node
            self._current_node = self._get_next_node(result)

            if self._current_node is None:
                self._completed(prev_node)
                return self.mission_status.as_dict()
            else:
                self._current_step = self._graph.nodes[self._current_node]['step']
                self.mission_status.step_transition(prev_node, self._current_node, self._graph)
                return self.mission_status.as_dict()
        
        self.mission_status.running(self._current_node, self._graph)
        return self.mission_status.as_dict()

    @property
    def current_step(self):
        """Get the current mission step being executed."""
        return self._current_step
    
    def _get_next_node(self, result) -> Optional[str]:
        """Determine the next node based on current node and conditions."""
        next_node = None
        for successor in self._graph.successors(self._current_node):
            condition = self._graph.edges[self._current_node, successor, 0].get("condition")
            if condition is None or condition == result:
                next_node = successor
                break
        return next_node
    
    def _completed(self, prev_node: str=None):
        """Handle mission completion procedures."""
        state_change_flag = self.mission_status.completed(prev_node, self._graph)
        self._mission_control_cmd = MissionState.COMPLETED
        self._current_step = None
        if state_change_flag:
            logger.info(f"{LogIcons.SUCCESS} Mission complete.")

    def _failed(self, e: Exception):
        """Handle mission failure procedures."""
        state_change_flag = self.mission_status.failed(self._current_node, self._graph)
        self._mission_control_cmd = MissionState.FAILED
        self._current_node = None
        self._current_step = None
        if state_change_flag:
            logger.error(f"{LogIcons.ERROR} Step {self._current_node} failed: {e}\n{traceback.format_exc()}")

    def pause(self, action: Optional[Literal["NONE"]] = "NONE", mav_proxy: IMavLinkProxy=None):
        """Pause the mission execution."""
        # Add action to pause the current step if supported, later on just like cancel
        action_map = {
            "NONE": 0
        }
        action_code = action_map.get(action, 0)  # Default to HOVER if invalid action

        if self.mission_status.state != MissionState.RUNNING:
            logger.warning(f"{LogIcons.WARNING} Mission cannot be paused, current state: {self.mission_status.state.name}.")
            return False
        
        if self._current_step is None:
            logger.warning(f"{LogIcons.WARNING} Cannot pause, no current step to pause.")
            return False
        
        if mav_proxy is None:
            logger.warning(f"{LogIcons.WARNING} Cannot pause, MAVLink proxy is required.")
            return False
        
        self._mission_control_cmd = MissionState.PAUSED

        msg = leafMAV.MAVLink_leaf_control_cmd_message(
                            target_system=mav_proxy.target_system,
                            cmd=0,
                            action=action_code
                        )
        mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
        logger.info(f"{LogIcons.RUN} Mission pause commanded.")
        
        return True

    def resume(self, mav_proxy: IMavLinkProxy=None):
        """Resume the mission execution."""
        if self.mission_status.state != MissionState.PAUSED:
            logger.warning(f"{LogIcons.WARNING} Mission cannot be resumed, current state: {self.mission_status.state.name}.")
            return False
        
        if self._current_step is None:
            logger.warning(f"{LogIcons.WARNING} Cannot resume, no current step to resume.")
            return False

        if mav_proxy is None:
            logger.warning(f"{LogIcons.WARNING} Cannot resume, MAVLink proxy is required.")
            return False
        
        self._current_step.resume()
        self._mission_control_cmd = MissionState.RUNNING

        msg = leafMAV.MAVLink_leaf_control_cmd_message(
                            target_system=mav_proxy.target_system,
                            cmd=1,
                            action=0
                        )
        mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
        logger.info(f"{LogIcons.RUN} Mission resume commanded.")
        
        return True

    def _paused(self):
        """Internal method to perform pause procedures."""
        state_change_flag = self.mission_status.paused(self._current_node, self._graph)
        if state_change_flag:
            self._current_step.pause()
            logger.info(f"{LogIcons.PAUSE} Mission paused at step: {self._current_node}")
    
    def is_paused(self):
        """Check if the mission is currently paused."""
        return self.mission_status.state == MissionState.PAUSED
    

    def cancel(self, action: Optional[Literal["NONE", "HOVER", "RETURN_TO_HOME", "LAND_IMMEDIATELY"]] = "HOVER", mav_proxy: IMavLinkProxy=None):
        # Map action strings to command codes
        action_map = {
            "NONE": 0,
            "HOVER": 1,
            "RETURN_TO_HOME": 2,
            "LAND_IMMEDIATELY": 3
        }
        action_code = action_map.get(action, 1)  # Default to HOVER if invalid action

        """Cancel the mission execution completely."""
        if self.mission_status.state != MissionState.RUNNING and self.mission_status.state != MissionState.PAUSED:
            logger.warning(f"{LogIcons.WARNING} Mission cannot be canceled, current state: {self.mission_status.state.name}.")
            return False
        
        if self._current_step is None:
            logger.warning(f"{LogIcons.WARNING} Cannot cancel, no current step to cancel.")
            return False
        
        if mav_proxy is None:
            logger.warning(f"{LogIcons.WARNING} Cannot cancel, MAVLink proxy is required.")
            return False

        self._mission_control_cmd = MissionState.CANCELLED
        
        # Send MAVLink cancel command
        msg = leafMAV.MAVLink_leaf_control_cmd_message(
                            target_system=mav_proxy.target_system,
                            cmd=2,
                            action=action_code
                        )
        mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
        logger.info(f"{LogIcons.RUN} Mission cancel commanded with action: {action}.")

        return True

    def _canceled(self):
        """Internal method to perform cancellation procedures."""
        state_change_flag = self.mission_status.canceled(self._current_node, self._graph)
        if state_change_flag:
            self._current_step.cancel()
            logger.info(f"{LogIcons.CANCEL} Mission cancelled at step: {self._current_node}")
            self._current_node = None
            self._current_step = None

    def is_cancelled(self):
        """Check if the mission has been cancelled."""
        return self.mission_status.state == MissionState.CANCELLED

    def add_subplan(self, subplan, prefix: str, connect_from: str=None, condition=None):
        if connect_from is None:
            connect_from = self._last_added_node
        renamed_nodes = {}
        for name, data in subplan._graph.nodes(data=True):
            new_name = f"{prefix}_{name}"
            self._graph.add_node(new_name, **data)
            renamed_nodes[name] = new_name

        for u, v, edata in subplan._graph.edges(data=True):
            self._graph.add_edge(renamed_nodes[u], renamed_nodes[v], **edata)

        self.add_transition(connect_from, renamed_nodes[subplan._head_node])
    
    def save_to_json_file(self, filepath: str):
        """Save the mission plan to a JSON file."""
        data = self._to_node_link_data()
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"{LogIcons.SUCCESS} MissionPlan file exported to: {filepath}")

    def as_dict(self) -> Dict[str, Any]:
        """Return the mission plan as a dictionary."""
        return self._to_node_link_data()
    
    def as_json(self) -> str:
        """Return the mission plan as a JSON string."""
        return json.dumps(self._to_node_link_data(), indent=2)

    def _to_node_link_data(self) -> Dict[str, Any]:
        self.validate()
        data = {
            "id": self.name,
            "nodes": [
                {
                    "name": name,
                    "type": step.__class__.__name__,
                    "params": step.to_dict()
                }
                for name, step in self._get_steps()
            ],
            "edges": [
                {"from": u, "to": v, "condition": self._graph.edges[u, v, k].get("condition")}
                for u, v, k in self._graph.edges
            ]
        }

        return data
        
    def reset(self):
        """Reset the mission plan to its initial state."""
        self._graph.clear()
        self.mission_status.reset()
        self._memory.reset()
        self._validated = False
        self._current_node = None
        self._current_step = None
        self._head_node = None
        self._last_added_node = None
        self._mission_control_cmd = None
        logger.info(f"{LogIcons.SUCCESS} MissionPlan has been reset.")

    def load(self, data: dict | str):
        """Load mission from a dictionary or JSON file path."""
        self.reset()

        if isinstance(data, str):
            with open(data, "r") as f:
                data = json.load(f)

        self.name = data.get("id", "UnnamedMission")

        for i, node in enumerate(data["nodes"]):
            step = step_from_dict(node["type"], node["params"])
            self.add_step(node["name"], step)
            if i == 0:
                self.set_start(node["name"])

        for edge in data["edges"]:
            self.add_transition(edge["from"], edge["to"], edge.get("condition"))

        logger.info(f"{LogIcons.SUCCESS} MissionPlan '{self.name}' loaded successfully.")


    def export_dot(self, filepath: str):
        try:
            from networkx.drawing.nx_pydot import write_dot
        except ImportError:
            logger.error(f"{LogIcons.ERROR} pydot or pygraphviz is required to export DOT files. Please install via pip.")

        # Add 'label' attributes to edges using the 'condition' attribute
        for u, v, data in self._graph.edges(data=True):
            if 'condition' in data:
                condition = data['condition']
                data['label'] = str(condition) if condition is not None else ''

        write_dot(self._graph, filepath)
        logger.info(f"{LogIcons.SUCCESS} DOT file exported to: {filepath}")

    def prepare(self, mav_proxy: IMavLinkProxy=None, redis_proxy: IRedisProxy=None):
        self.validate()
        for _, step in self._get_steps():
            step.setup(mav_proxy, redis_proxy)
        self._mission_control_cmd = MissionState.RUNNING
        logger.info(f"{LogIcons.SUCCESS} Mission plan has been prepared and ready for execution.")

    def _get_steps(self):
        for name, data in self._graph.nodes(data=True):
            yield name, data['step']

    def validate(self):
        errors = []
        for node in self._graph.nodes:
            successors = list(self._graph.successors(node))
            if len(successors) > 1:
                seen_conditions = set()
                for succ in successors:
                    edge_data = self._graph.get_edge_data(node, succ)
                    condition = edge_data[0].get("condition")
                    if condition is None:
                        errors.append(f"Missing condition for edge {node} → {succ}")
                    elif condition in seen_conditions:
                        errors.append(f"Duplicate condition '{condition}' for branching at {node}")
                    else:
                        seen_conditions.add(condition)

        if errors:
            for e in errors:
                logger.error(f"{LogIcons.ERROR} [prepare] {e}")
            raise ValueError("Mission plan validation failed. See errors above.")
        else:
            self._validated = True
            logger.info(f"{LogIcons.SUCCESS} Mission plan has been validated.")