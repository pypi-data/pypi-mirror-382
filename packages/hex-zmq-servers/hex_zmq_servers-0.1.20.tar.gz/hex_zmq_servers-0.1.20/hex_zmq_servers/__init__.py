#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2025 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2025-09-15
################################################################

from .hex_launch import HexLaunch, HEX_LOG_LEVEL, hex_log, hex_err

from .device_base import HexDeviceBase
from .zmq_base import HexRate, hex_zmq_ts_now, hex_zmq_ts_delta_ms
from .zmq_base import HexSafeValue, HexZMQClientBase, HexZMQServerBase, hex_server_helper
from .zmq_base import HexDummyZMQClient, HexDummyZMQServer

from .cam import HexCamBase, HexCamClientBase, HexCamServerBase
from .cam import HexDummyCam, HexDummyCamClient, HexDummyCamServer
from .cam import HexBerxelCam, HexBerxelCamClient, HexBerxelCamServer

from .mujoco import HexMujocoBase, HexMujocoClientBase, HexMujocoServerBase
from .mujoco import HexArcherD6yMujoco, HexArcherD6yMujocoClient, HexArcherD6yMujocoServer
from .mujoco import HexE3DesktopMujoco, HexE3DesktopMujocoClient, HexE3DesktopMujocoServer

from .robot import HexRobotBase, HexRobotClientBase, HexRobotServerBase
from .robot import HexDummyRobot, HexDummyRobotClient, HexDummyRobotServer
from .robot import HexGelloRobot, HexGelloRobotClient, HexGelloRobotServer
from .robot import HexHexArmRobot, HexHexArmRobotClient, HexHexArmRobotServer

import os

file_dir = os.path.dirname(os.path.abspath(__file__))
HEX_ZMQ_SERVERS_PATH_DICT = {
    "zmq_dummy": f"{file_dir}/zmq_base.py",
    "cam_dummy": f"{file_dir}/cam/dummy/dummy_cam_srv.py",
    "cam_berxel": f"{file_dir}/cam/berxel/berxel_cam_srv.py",
    "mujoco_archer_d6y":
    f"{file_dir}/mujoco/archer_d6y/archer_d6y_mujoco_srv.py",
    "mujoco_e3_desktop":
    f"{file_dir}/mujoco/e3_desktop/e3_desktop_mujoco_srv.py",
    "robot_dummy": f"{file_dir}/robot/dummy/dummy_robot_srv.py",
    "robot_gello": f"{file_dir}/robot/gello/gello_robot_srv.py",
    "robot_hex_arm": f"{file_dir}/robot/hex_arm/hex_arm_robot_srv.py",
}
HEX_ZMQ_CONFIGS_PATH_DICT = {
    "zmq_dummy": f"{file_dir}/config/zmq_dummy.json",
    "cam_dummy": f"{file_dir}/config/cam_dummy.json",
    "cam_berxel": f"{file_dir}/config/cam_berxel.json",
    "mujoco_archer_d6y": f"{file_dir}/config/mujoco_archer_d6y.json",
    "mujoco_e3_desktop": f"{file_dir}/config/mujoco_e3_desktop.json",
    "robot_dummy": f"{file_dir}/config/robot_dummy.json",
    "robot_gello": f"{file_dir}/config/robot_gello.json",
    "robot_hex_arm": f"{file_dir}/config/robot_hex_arm.json",
}

__all__ = [
    # version
    "__version__",

    # path
    "HEX_ZMQ_SERVERS_PATH_DICT",
    "HEX_ZMQ_CONFIGS_PATH_DICT",

    # launch
    "HexLaunch",
    "HEX_LOG_LEVEL",
    "hex_log",
    "hex_err",

    # base
    "HexDeviceBase",
    "HexRate",
    "hex_zmq_ts_now",
    "hex_zmq_ts_delta_ms",
    "HexSafeValue",
    "HexZMQClientBase",
    "HexZMQServerBase",
    "hex_server_helper",
    "HexDummyZMQClient",
    "HexDummyZMQServer",

    # camera
    "HexCamBase",
    "HexCamClientBase",
    "HexCamServerBase",
    "HexDummyCam",
    "HexDummyCamClient",
    "HexDummyCamServer",
    "HexBerxelCam",
    "HexBerxelCamClient",
    "HexBerxelCamServer",

    # mujoco
    "HexMujocoBase",
    "HexMujocoClientBase",
    "HexMujocoServerBase",
    "HexArcherD6yMujoco",
    "HexArcherD6yMujocoClient",
    "HexArcherD6yMujocoServer",
    "HexE3DesktopMujoco",
    "HexE3DesktopMujocoClient",
    "HexE3DesktopMujocoServer",

    # robot
    "HexRobotBase",
    "HexRobotClientBase",
    "HexRobotServerBase",
    "HexDummyRobot",
    "HexDummyRobotClient",
    "HexDummyRobotServer",
    "HexGelloRobot",
    "HexGelloRobotClient",
    "HexGelloRobotServer",
    "HexHexArmRobot",
    "HexHexArmRobotClient",
    "HexHexArmRobotServer",
]

# print("#### Thanks for using hex_zmq_servers :D ####")
