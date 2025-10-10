# leafsdk/utils/mavlink_helpers.py
# MAVLink helper functions for LeafSDK

import sys, time
import os
from pymavlink.dialects.v20 import droneleaf_mav_msgs as leafMAV

from leafsdk import logger
from leafsdk.core.interfaces import IMavLinkProxy
from typing import Optional, Union
from leafsdk.utils.logstyle import LogIcons


def get_mav_msg_name_from_id(msg_id: int) -> Union[str, int]:
    """
    Get MAVLink message name from its ID.
    """
    try:
        msg_name = leafMAV.mavlink_map[msg_id].name
        return msg_name
    except KeyError:
        logger.warning(f"{LogIcons.WARNING} Unknown MAVLink message ID: {msg_id}")
        return msg_id

def parse_heartbeat(msg):
    """
    Parse heartbeat message and return system status info.
    """
    if msg.get_type() != "HEARTBEAT":
        logger.warning("Expected HEARTBEAT message, got something else.")
        return None

    status = {
        "type": msg.type,
        "autopilot": msg.autopilot,
        "base_mode": msg.base_mode,
        "custom_mode": msg.custom_mode,
        "system_status": msg.system_status,
        "mavlink_version": msg.mavlink_version,
    }
    logger.debug(f"Parsed heartbeat: {status}")
    return status

def setup_mavlink_subscriptions(key: str, callback: callable, mav_proxy: Optional[IMavLinkProxy] = None, duplicate_filter_interval: Optional[float] = 0):
    """Setup MAVLink subscriptions - call this after object creation if using MAVLink"""
    if mav_proxy is None:
        logger.warning(f"{LogIcons.WARNING} MAVLink proxy not provided, skipping MAVLink subscriptions")
        return
        
    try:
        # Subscribe to a general broadcast channel
        mav_proxy.register_handler(
            key=key,
            fn=callback,
            duplicate_filter_interval=duplicate_filter_interval
        )

        logger.info(f"{LogIcons.SUCCESS} MAVLink subscriptions set up successfully to {get_mav_msg_name_from_id(int(key))}.")
    except Exception as e:
        logger.error(f"{LogIcons.ERROR} Failed to set up MAVLink subscriptions: {e}")

def unsetup_mavlink_subscriptions(key: str, callback: callable, mav_proxy: Optional[IMavLinkProxy] = None):
    """Unsubscribe from MAVLink channels - call this when the step is no longer needed"""
    if mav_proxy is None:
        logger.warning(f"{LogIcons.WARNING} MAVLink proxy not provided, skipping MAVLink unsubscriptions")
        return
        
    try:
        mav_proxy.unregister_handler(key=key, fn=callback)
        logger.info(f"{LogIcons.SUCCESS} MAVLink subscriptions to {get_mav_msg_name_from_id(int(key))} have been removed.")
    except Exception as e:
        logger.error(f"{LogIcons.ERROR} Failed to remove MAVLink subscriptions: {e}")