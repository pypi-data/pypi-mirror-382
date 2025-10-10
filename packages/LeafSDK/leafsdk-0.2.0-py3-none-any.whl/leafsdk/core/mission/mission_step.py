# leafsdk/core/mission/mission_step.py
import numpy as np
import time
import json
import inspect
import traceback
import uuid
from typing import Dict, Any, List, Optional, Tuple, Union, TypeAlias, Sequence
from dataclasses import dataclass
from pymavlink import mavutil
from pymavlink.dialects.v20 import droneleaf_mav_msgs as leafMAV
from abc import ABC, abstractmethod

from leafsdk.utils.redis_helpers import setup_redis_subscriptions, unsetup_redis_subscriptions
from leafsdk.utils.mavlink_helpers import setup_mavlink_subscriptions, unsetup_mavlink_subscriptions
from leafsdk.core.mission.trajectory import WaypointTrajectory #, TrajectorySampler
from leafsdk.core.interfaces import IMavLinkProxy, IRedisProxy
from leafsdk.core.utils.transform import wrap_to_pi, deg2rad
from leafsdk import logger
from leafsdk.utils.logstyle import LogIcons



Tuple3D: TypeAlias = Tuple[float, float, float]   # exact length 3

@dataclass
class StepState:
    completed: bool = False
    paused: bool = False
    canceled: bool = False
    exec_count: int = 0

    def reset(self):
        self.completed = False
        self.paused = False
        self.canceled = False
        self.exec_count = 0

@dataclass
class StepMemory:
    yaw_offset: float = 0.0
    waypoint_offset: Tuple3D = (0.0, 0.0, 0.0)

    def reset(self):
        self.yaw_offset = 0.0
        self.waypoint_offset = (0.0, 0.0, 0.0)


class MissionStep(ABC):
    def __init__(self):
        self.state = StepState() # Holds the current state of the step
        self.output = True # Indicates the logical output of the step (mostly used for conditional steps)
        self.memory = StepMemory() # Holds any state information passed between steps through mission plan
        self._is_pausable = True # Indicates if the step can be paused
    
    @abstractmethod
    def execute_step_logic(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        """Execute the logic for the mission step - this is called repeatedly until the step is completed."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @abstractmethod
    def description(self) -> str:
        """
        Returns a string description of the step.
        This is used for logging and debugging purposes.
        """
        pass

    @classmethod
    def _init_from_dict(cls, params: Dict[str, Any]):
        sig = inspect.signature(cls.__init__)
        required_params = [
            name
            for name, p in sig.parameters.items()
            if name != "self" and p.default is inspect.Parameter.empty
        ]

        # validate required params
        missing = [p for p in required_params if p not in params]
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")

        return cls(**params)

    def setup(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        """Setup any resources needed for the step prior to mission plan execution."""
        self.reset()

    def start(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        """Execute one time operations at the start of the step."""
        pass

    def terminate(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        """Execute one time operations at the end of the step."""
        pass

    def execute_step(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None) -> Tuple[bool, bool, Optional[Dict[str, Any]]]:
        # Check cancellation before executing
        if self.state.canceled:
            self.terminate(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
            return self.output, self.state.completed, self.memory
        elif self.state.paused:
            return self.output, self.state.completed, self.memory

        if self.first_exec():
            self.start(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
            self._log_info()
            self.state.exec_count += 1
        elif not self.state.completed: 
            self.execute_step_logic(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
            self.state.exec_count += 1
            if self.state.completed:
                self.terminate(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
                logger.info(f"{LogIcons.SUCCESS} Done: {self.description()} completed!")
            
        return self.output, self.state.completed, self.memory
    
    def feed_memory(self, memory: Dict[str, Any]):
        """
        Feed initial state information to the step.
        This can be used to pass data from the mission plan to the step, between mission steps.
        """
        self.memory = memory
        logger.debug(f"{LogIcons.SUCCESS} Feeding state info to {self.__class__.__name__}: {memory}")

    def _log_info(self):
        logger.info(f"{LogIcons.RUN} Executing step: {self.description()}")

    def first_exec(self) -> bool:
        """Returns True if this is the first execution of the step logic."""
        return self.state.exec_count == 0
    
    def reset(self):
        """Reset the step state and memory to initial values."""
        self.state.reset()
        self.memory.reset()
        self.output = True

    def pause(self):
        """Pause the step if it is pausable."""
        if self._is_pausable and not self.state.canceled:
            self.state.paused = True
            logger.info(f"{LogIcons.PAUSE} Step paused: {self.description()}")
        else:
            logger.warning(f"{LogIcons.WARNING} Step cannot be paused: {self.description()}")

    def resume(self):
        """Resume the step if it was paused."""
        if self.state.paused and not self.state.canceled:
            self.state.paused = False
            logger.info(f"{LogIcons.RUN} Step resumed: {self.description()}")
        else:
            logger.warning(f"{LogIcons.WARNING} Step is not paused or has been canceled, cannot resume: {self.description()}")

    def cancel(self):
        """Cancel the step."""
        self.state.canceled = True
        logger.info(f"{LogIcons.CANCEL} Step canceled: {self.description()}")
        


class _GotoBase(MissionStep):
    def __init__(
            self,
            waypoints: Union[Tuple3D, Sequence[Tuple3D]],
            yaws_deg: Optional[Union[float, Sequence[float]]] = 0.0,      # 0.0 deg,
            speed: Optional[Union[float, Sequence[float]]] = 0.2,         # 0.2 m/s,
            yaw_speed: Optional[Union[float, Sequence[float]]] = 30.0,    # 30.0 deg/s,
            cartesian: Optional[bool] = False,
        ):
        super().__init__()

        # ---- Validate and normalize inputs ----
        waypoints = np.asarray(waypoints, dtype=float)

        if waypoints.ndim == 1:
            if waypoints.shape[0] != 3:
                raise ValueError(f"Single waypoint must have exactly 3 values, got {waypoints.shape[0]}")
            waypoints = waypoints[np.newaxis, :]  # shape -> (1, 3)
        elif waypoints.ndim == 2:
            if waypoints.shape[1] != 3:
                raise ValueError(f"Each waypoint must have exactly 3 values, got shape {waypoints.shape[1]}")
        else:
            raise ValueError(f"Waypoints must be a sequence with shape (3,) or (N,3), got shape {waypoints.shape}")

        self.waypoints = waypoints
        n = waypoints.shape[0]

        # ---- Normalize helper ----
        def normalize_param(param, name: str):
            arr = np.asarray(param, dtype=float)
            if arr.ndim == 0:  # scalar
                return np.full(n, float(arr))
            elif arr.ndim == 1:
                if arr.shape[0] != n:
                    raise ValueError(f"{name} must have length {n}, got {arr.shape[0]}")
                return arr
            else:
                raise ValueError(f"{name} must be scalar or 1D sequence, got shape {arr.shape}")

        self.yaws_deg  = normalize_param(yaws_deg, "yaws_deg")
        self.speed     = normalize_param(speed, "speed")
        self.yaw_speed = normalize_param(yaw_speed, "yaw_speed")
        self.cartesian = cartesian

        # ---- Internal state ----
        self.target_waypoint = self.waypoints[-1]  # Last waypoint is the target
        self.target_yaw = self.yaws_deg[-1]  # Last yaw is the target
        self.yaw_offset = 0.0  # Default yaw offset
        self.waypoint_offset = [0.0, 0.0, 0.0]  # Default position offset
        self.trajectory = None
        self.uuid_str = str(uuid.uuid4())
        self.queued_traj_ids: Dict[str, bool] = {}   # trajectories waiting for completion, value indicates if completed
        self.current_traj_segment: int = 0           # index of segment being processed

    def _handle_notify_trajectory_completed(self, channel: str, message: str) -> None:
        """
        Handle notification messages for trajectory completion.
        This function is triggered asynchronously by the Redis subscriber.

        It parses the message, extracts the trajectory_id, and stores it
        in an internal queue or list for later processing. This function
        must not block.

        Parameters
        ----------
        channel : str
            The Redis channel from which the message was received.
        message : str
            The message content, expected to be a JSON string with trajectory details.
        """
        logger.info(f"{LogIcons.SUCCESS} Received notification on {channel}: {message}")

        try:
            command_data = json.loads(message)
            traj_id = command_data.get("trajectory_id")

            if traj_id:
                self.queued_traj_ids[traj_id] = True
                logger.info(f"{LogIcons.SUCCESS} Trajectory completed: {traj_id}")
            else:
                logger.warning(f"{LogIcons.WARNING} Received notification without trajectory_id: {message}")
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Error parsing completion notification: {e}")

    def start(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        setup_redis_subscriptions(pattern="/petal-leafsdk/notify_trajectory_completed", callback=self._handle_notify_trajectory_completed, redis_proxy=redis_proxy)
        try:
            self.yaw_offset = self.memory.yaw_offset
            self.waypoint_offset = self.memory.waypoint_offset

            # update offsets for trajectory computation
            self.memory.waypoint_offset = self.waypoints[-1]
            self.memory.yaw_offset = deg2rad(self.yaws_deg[-1])
            logger.debug(f"{LogIcons.WARNING} Using waypoint offset: {self.waypoint_offset} and yaw offset: {self.yaw_offset}")

            # Compute trajectory once
            self.pos_traj_ids, self.pos_traj_json, self.yaw_traj_ids, self.yaw_traj_json = self._compute_trajectory(
                                                                                                self.waypoints,
                                                                                                self.yaws_deg,
                                                                                                self.speed,
                                                                                                self.yaw_speed,
                                                                                                home=self.waypoint_offset,
                                                                                                home_yaw=self.yaw_offset,
                                                                                                cartesian=self.cartesian,
                                                                                            )
            
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Error computing trajectory: {e}")
            logger.error(traceback.format_exc())
            raise e

    def execute_step_logic(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        """
        Execute mission step logic for sequential trajectory publishing.
        This function is designed to be called periodically (non-blocking).
        """
        total_segments = len(self.pos_traj_json)

        # If there are no uncompleted trajectories, publish next segment
        if all(list(self.queued_traj_ids.values())) and self.current_traj_segment < total_segments:
            self._publish_trajectory_segment(
                idx=self.current_traj_segment,
                pos_traj_seg=self.pos_traj_json[self.current_traj_segment],
                yaw_traj_seg=self.yaw_traj_json[self.current_traj_segment],
                pos_traj_id=self.pos_traj_ids[self.current_traj_segment],
                yaw_traj_id=self.yaw_traj_ids[self.current_traj_segment],
                redis_proxy=redis_proxy
            )
            self.current_traj_segment += 1
        elif all(list(self.queued_traj_ids.values())) and self.current_traj_segment >= total_segments:
            self.state.completed = True

    def terminate(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        unsetup_redis_subscriptions(pattern="/petal-leafsdk/notify_trajectory_completed", redis_proxy=redis_proxy)

    def _compute_trajectory(
        self,
        waypoints: Sequence[Tuple[float, float, float]],
        yaws_deg: Sequence[float],
        speed: Sequence[float],
        yaw_speed: Sequence[float],
        home: Tuple[float, float, float],
        home_yaw: float,
        cartesian: bool,
    ) ->  Tuple[List[str], List[Optional[str]], List[str], List[Optional[str]]]:
        """
        Compute the trajectory for the given waypoints and yaws.
        This function generates trajectory JSON files for each segment
        and returns their identifiers.
        
        Parameters
        ----------
        waypoints : Sequence[Tuple[float, float, float]]
            List of waypoints as (lat, lon, alt) or (x, y, z).
        yaws_deg : Sequence[float]
            List of yaw commands in degrees at each waypoint.
        speed : Sequence[float]
            List of speeds (m/s) for each segment.
        yaw_speed : Sequence[float]
            List of yaw speeds (deg/s) for each segment.
        home : Tuple[float, float, float]
            Home position reference (lat, lon, alt) or (x, y, z).
        home_yaw : float
            Home yaw reference in radians.
        cartesian : bool
            If True, waypoints are in Cartesian coordinates; if False, GPS coordinates.

        Returns
        -------
        pos_traj_ids : List[str]
            List of position trajectory segment identifiers.
        pos_traj_json : List[Optional[str]]
            List of position trajectory JSON strings (None if static).
        yaw_traj_ids : List[str]
            List of yaw trajectory segment identifiers.
        yaw_traj_json : List[Optional[str]]
            List of yaw trajectory JSON strings (None if static).
        """

        # Create trajectory json files for each segment based on the waypoints and yaws
        self.trajectory = WaypointTrajectory(
            waypoints=waypoints,
            yaws_deg=yaws_deg,
            speed=speed,
            yaw_speed=yaw_speed,
            home=home,
            home_yaw=home_yaw,
            cartesian=cartesian
        )
        
        pos_traj_ids, pos_traj_json = self.trajectory.build_pos_polynomial_trajectory_json(self.uuid_str)
        yaw_traj_ids, yaw_traj_json = self.trajectory.build_yaw_polynomial_trajectory_json(self.uuid_str)

        return pos_traj_ids, pos_traj_json, yaw_traj_ids, yaw_traj_json

    def _publish_trajectory_segment(
        self,
        idx: int,
        pos_traj_seg: str,
        yaw_traj_seg: str,
        pos_traj_id: str,
        yaw_traj_id: str,
        redis_proxy: Optional[IRedisProxy] = None
    ) -> None:
        """
        Publish a single trajectory segment (position and/or yaw) to Redis.

        This function does not block or wait for completion. Completion is
        handled asynchronously via `_handle_notify_trajectory_completed`.

        Parameters
        ----------
        idx : int
            Segment index (0-based).
        pos_traj_seg : str or None
            JSON string for the position trajectory segment, or None if static.
        yaw_traj_seg : str or None
            JSON string for the yaw trajectory segment, or None if static.
        pos_traj_id : str or None
            Identifier for the position trajectory segment.
        yaw_traj_id : str or None
            Identifier for the yaw trajectory segment.
        """
        try:
            if redis_proxy is None:
                logger.warning(f"{LogIcons.WARNING} Redis proxy not available, skipping trajectory publication")
                return

            # Skip publishing if both are None
            if pos_traj_seg is None and yaw_traj_seg is None:
                logger.warning(
                    f"{LogIcons.WARNING} Both position and yaw trajectory segments are static, "
                    f"skipping publication for segment {idx+1}"
                )
                return

            # Publish position trajectory
            if pos_traj_seg is not None:
                redis_proxy.publish(
                    channel="/traj_sys/queue_traj_primitive_pos",
                    message=pos_traj_seg,
                )
                self.queued_traj_ids[pos_traj_id] = False
                logger.info(f"{LogIcons.SUCCESS} Position trajectory segment {idx+1} published to Redis successfully")

            # Publish yaw trajectory
            if yaw_traj_seg is not None:
                redis_proxy.publish(
                    channel="/traj_sys/queue_traj_primitive_ori",
                    message=yaw_traj_seg,
                )
                self.queued_traj_ids[yaw_traj_id] = False
                logger.info(f"{LogIcons.SUCCESS} Yaw trajectory segment {idx+1} published to Redis successfully")

        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Error publishing trajectory segment {idx+1}: {e}")

    def to_dict(self):
        return {
            "waypoints": self.waypoints.tolist(),
            "yaws_deg": self.yaws_deg.tolist(),
            "speed": self.speed.tolist(),
            "yaw_speed": self.yaw_speed.tolist(),
        }

    def description(self) -> str:
        """
        Returns a string description of the step.
        This is used for logging and debugging purposes.
        """
        return f"Goto to waypoint {self.target_waypoint} with yaw {self.target_yaw}."

class GotoGPSWaypoint(_GotoBase):
    def __init__(
        self,
        waypoints: Union[Tuple3D, Sequence[Tuple3D]],
        yaws_deg: Optional[Union[float, Sequence[float]]] = 0.0,      # 0.0 deg,
        speed: Optional[Union[float, Sequence[float]]] = 2.0,         # 2.0 m/s,
        yaw_speed: Optional[Union[float, Sequence[float]]] = 30.0,    # 30.0 deg/s,
    ):
        super().__init__(waypoints=waypoints, yaws_deg=yaws_deg, speed=speed, yaw_speed=yaw_speed, cartesian=False)

    def description(self) -> str:
        return f"GotoGPSWaypoint to ({self.target_waypoint[0]}, {self.target_waypoint[1]}, {self.target_waypoint[2]}) with yaw {self.target_yaw}."

class GotoLocalPosition(_GotoBase):
    def __init__(
        self,
        waypoints: Union[Tuple3D, Sequence[Tuple3D]],
        yaws_deg: Optional[Union[float, Sequence[float]]] = 0.0,      # 0.0 deg,
        speed: Optional[Union[float, Sequence[float]]] = 2.0,         # 2.0 m/s,
        yaw_speed: Optional[Union[float, Sequence[float]]] = 30.0,    # 30.0 deg/s,
    ):
        super().__init__(waypoints=waypoints, yaws_deg=yaws_deg, speed=speed, yaw_speed=yaw_speed, cartesian=True)

    def description(self) -> str:
        return f"GotoLocalPosition to ({self.target_waypoint[0]}, {self.target_waypoint[1]}, {self.target_waypoint[2]}) with yaw {self.target_yaw}."


class Takeoff(MissionStep):
    def __init__(self, alt: Optional[float] = 1.0):
        super().__init__()
        self._is_pausable = False  # Takeoff step cannot be paused
        self.alt = alt
        self.waypoint_offset = [0.0, 0.0, 0.0]  # Default position offset
        self.yaw_offset = 0.0  # Default yaw offset
        self._offset_pos_recved = False
        self._offset_yaw_recved = False

        def handler_pos(msg: mavutil.mavlink.MAVLink_message) -> bool:
            self.waypoint_offset = [msg.x, msg.y, msg.z]
            self._offset_pos_recved = True
            logger.info(f"{LogIcons.SUCCESS} Received external trajectory offset position: {self.waypoint_offset}")
            return True

        def handler_ori(msg: mavutil.mavlink.MAVLink_message) -> bool:
            self.yaw_offset = wrap_to_pi(msg.z)
            self._offset_yaw_recved = True
            logger.info(f"{LogIcons.SUCCESS} Received external trajectory offset yaw: {self.yaw_offset}")
            return True
        
        self._handler_pos = handler_pos
        self._handler_ori = handler_ori

    def setup(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        super().setup(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
        setup_mavlink_subscriptions(
            key=str(leafMAV.MAVLINK_MSG_ID_LEAF_EXTERNAL_TRAJECTORY_OFFSET_ENU_POS),
            callback=self._handler_pos,
            duplicate_filter_interval=0.7,
            mav_proxy=mav_proxy
        )
        setup_mavlink_subscriptions(
            key=str(leafMAV.MAVLINK_MSG_ID_LEAF_EXTERNAL_TRAJECTORY_OFFSET_ENU_ORI),
            callback=self._handler_ori,
            duplicate_filter_interval=0.7,
            mav_proxy=mav_proxy
        )

    def start(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        if mav_proxy is not None:
            msg = leafMAV.MAVLink_leaf_do_takeoff_message(
                target_system=mav_proxy.target_system,
                altitude=self.alt
                )
            mav_proxy.send(key='mav', msg=msg,burst_count=4, burst_interval=0.1)
        else:
            logger.warning(f"{LogIcons.WARNING} MavLinkExternalProxy is not provided, cannot send takeoff message.")

    def execute_step_logic(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None) -> None:
        if self._offset_pos_recved and self._offset_yaw_recved:
            self.waypoint_offset[-1] += self.alt  # Adjust the altitude offset

            self.memory.waypoint_offset = self.waypoint_offset
            self.memory.yaw_offset = self.yaw_offset
            logger.debug(f"{LogIcons.WARNING} Takeoff with waypoint offset: {self.waypoint_offset} and yaw offset: {self.yaw_offset}")
            self.state.completed = True

    def terminate(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        unsetup_mavlink_subscriptions(
            key=str(leafMAV.MAVLINK_MSG_ID_LEAF_EXTERNAL_TRAJECTORY_OFFSET_ENU_POS),
            callback=self._handler_pos,
            mav_proxy=mav_proxy
        )
        unsetup_mavlink_subscriptions(
            key=str(leafMAV.MAVLINK_MSG_ID_LEAF_EXTERNAL_TRAJECTORY_OFFSET_ENU_ORI),
            callback=self._handler_ori,
            mav_proxy=mav_proxy
        )

    def to_dict(self):
        return {"alt": self.alt}
    
    def description(self) -> str:
        """
        Returns a string description of the step.
        This is used for logging and debugging purposes.
        """
        return f"Takeoff to altitude {self.alt}m."
    

class Wait(MissionStep):
    def __init__(self, duration: float):
        super().__init__()
        self.duration = duration
        self._is_pausable = False  # Wait step is not pausable
        self.tick = 0 # Used to track the start time of the wait

    def start(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        self.tick = time.time()

    def execute_step_logic(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        elapsed_time = time.time() - self.tick
        if elapsed_time >= self.duration:
            self.state.completed = True

    def to_dict(self):
        return {"duration": self.duration}

    def description(self) -> str:
        """
        Returns a string description of the step.
        This is used for logging and debugging purposes.
        """
        return f"Wait for {self.duration} seconds."
    

class Land(MissionStep):
    def __init__(self):
        super().__init__()
        self._is_pausable = False
        self._landed = False

    def _handle_notify_trajectory_completed(self, channel: str, message: str) -> None:
        """
        Handle notification messages for landing trajectory completion.

        Parameters
        ----------
        channel : str
            The Redis channel from which the message was received.
        message : str
            The message content, expected to be a JSON string with trajectory details.
        """
        logger.info(f"{LogIcons.SUCCESS} Received notification on {channel}: {message}")

        try:
            command_data = json.loads(message)
            traj_id = command_data.get("trajectory_id")

            if "land" in traj_id:
                # For Land step, we can directly mark completed on any trajectory completion
                self._landed = True
                logger.info(f"{LogIcons.SUCCESS} Trajectory completed: {traj_id}")
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Error parsing completion notification: {e}")

    def start(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        super().start(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
        setup_redis_subscriptions(pattern="/petal-leafsdk/notify_trajectory_completed", callback=self._handle_notify_trajectory_completed, redis_proxy=redis_proxy)
        if mav_proxy is not None:
            msg = leafMAV.MAVLink_leaf_do_land_message(
                target_system=mav_proxy.target_system,
            )
            mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
        else:
            logger.warning(f"{LogIcons.WARNING} MavLinkExternalProxy is not provided, cannot send land message.")

    def execute_step_logic(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None) -> None:
        if self._landed:
            self.state.completed = True

    def terminate(self, mav_proxy: Optional[IMavLinkProxy] = None, redis_proxy: Optional[IRedisProxy] = None):
        super().terminate(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
        unsetup_redis_subscriptions(pattern="/petal-leafsdk/notify_trajectory_completed", redis_proxy=redis_proxy)
        self._landed = False

    def to_dict(self):
        return {}
        
    def description(self) -> str:
        """
        Returns a string description of the step.
        This is used for logging and debugging purposes.
        """
        return "Land."
    

def step_from_dict(step_type: str, params: dict) -> MissionStep:
    step_classes = {
        "Takeoff": Takeoff,
        "GotoGPSWaypoint": GotoGPSWaypoint,
        "GotoLocalPosition": GotoLocalPosition,
        "Wait": Wait,
        "Land": Land,
        # Add more here
    }
    cls = step_classes.get(step_type)
    if cls is None:
        raise ValueError(f"Unknown mission_step type: {step_type}")
    
    return cls._init_from_dict(params)