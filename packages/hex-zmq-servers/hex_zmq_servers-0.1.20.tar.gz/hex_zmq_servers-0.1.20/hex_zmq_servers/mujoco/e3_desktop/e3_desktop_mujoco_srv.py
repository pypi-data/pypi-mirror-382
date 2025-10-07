#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2025 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2025-09-16
################################################################

import numpy as np
from hex_zmq_servers.zmq_base import HexSafeValue

try:
    from ..mujoco_base import HexMujocoServerBase
    from .e3_desktop_mujoco import HexE3DesktopMujoco
except (ImportError, ValueError):
    import sys
    from pathlib import Path
    this_file = Path(__file__).resolve()
    project_root = this_file.parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from hex_zmq_servers.mujoco.mujoco_base import HexMujocoServerBase
    from hex_zmq_servers.mujoco.e3_desktop.e3_desktop_mujoco import HexE3DesktopMujoco

NET_CONFIG = {
    "ip": "127.0.0.1",
    "port": 12345,
    "client_timeout_ms": 200,
    "server_timeout_ms": 1_000,
    "server_num_workers": 4,
}

MUJOCO_CONFIG = {
    "states_rate": 250,
    "img_rate": 30,
    "headless": False,
    "sens_ts": True,
}


class HexE3DesktopMujocoServer(HexMujocoServerBase):

    def __init__(
        self,
        net_config: dict = NET_CONFIG,
        params_config: dict = MUJOCO_CONFIG,
    ):
        HexMujocoServerBase.__init__(self, net_config)

        # mujoco
        self._device = HexE3DesktopMujoco(params_config)

        self._rgb_head_value = HexSafeValue()
        self._depth_head_value = HexSafeValue()
        self._rgb_left_value = HexSafeValue()
        self._depth_left_value = HexSafeValue()
        self._rgb_right_value = HexSafeValue()
        self._depth_right_value = HexSafeValue()

    def work_loop(self):
        try:
            self._device.work_loop([
                self._states_value,
                self._obj_pose_value,
                self._cmds_value,
                self._rgb_head_value,
                self._depth_head_value,
                self._rgb_left_value,
                self._depth_left_value,
                self._rgb_right_value,
                self._depth_right_value,
            ])
        finally:
            self._device.close()

    def _get_frame(self, recv_hdr: dict, depth_flag: bool):
        try:
            seq = recv_hdr["args"]
        except KeyError:
            print(f"\033[91m{recv_hdr['cmd']} requires `args`\033[0m")
            return {"cmd": f"{recv_hdr['cmd']}_failed"}, None

        # get camera name
        camera_name = recv_hdr["cmd"].split("_")[2]
        if camera_name == "head":
            value = self._rgb_head_value if not depth_flag else self._depth_head_value
        elif camera_name == "left":
            value = self._rgb_left_value if not depth_flag else self._depth_left_value
        elif camera_name == "right":
            value = self._rgb_right_value if not depth_flag else self._depth_right_value
        else:
            raise ValueError(f"unknown camera name: {camera_name}")

        try:
            ts, count, img = value.get()
        except Exception as e:
            print(f"\033[91m{recv_hdr['cmd']} failed: {e}\033[0m")
            return {"cmd": f"{recv_hdr['cmd']}_failed"}, None

        delta = (count - seq) % self._max_seq_num
        if delta >= 0 and delta < 5_000:
            return {
                "cmd": f"{recv_hdr['cmd']}_ok",
                "ts": ts,
                "args": count
            }, img
        else:
            return {"cmd": f"{recv_hdr['cmd']}_failed"}, None

    def _process_request(self, recv_hdr: dict, recv_buf: np.ndarray):
        if recv_hdr["cmd"] == "is_working":
            return self.no_ts_hdr(recv_hdr, self._device.is_working()), None
        elif recv_hdr["cmd"] == "reset":
            return self.no_ts_hdr(recv_hdr, self._device.reset()), None
        elif recv_hdr["cmd"] == "get_dofs":
            dofs = self._device.get_dofs()
            return self.no_ts_hdr(recv_hdr, dofs is not None), dofs
        elif recv_hdr["cmd"] == "get_limits":
            limits = self._device.get_limits()
            return self.no_ts_hdr(recv_hdr, limits is not None), limits
        elif recv_hdr["cmd"] == "get_states":
            return self._get_states(recv_hdr)
        elif recv_hdr["cmd"] == "get_obj_pose":
            return self._get_obj_pose(recv_hdr)
        elif recv_hdr["cmd"] == "set_cmds":
            return self._set_cmds(recv_hdr, recv_buf)
        elif recv_hdr["cmd"] == "get_intri":
            intri = self._device.get_intri()
            return self.no_ts_hdr(recv_hdr, intri is not None), intri
        elif recv_hdr["cmd"] == "get_rgb_head":
            return self._get_frame(recv_hdr, False)
        elif recv_hdr["cmd"] == "get_depth_head":
            return self._get_frame(recv_hdr, True)
        elif recv_hdr["cmd"] == "get_rgb_left":
            return self._get_frame(recv_hdr, False)
        elif recv_hdr["cmd"] == "get_depth_left":
            return self._get_frame(recv_hdr, True)
        elif recv_hdr["cmd"] == "get_rgb_right":
            return self._get_frame(recv_hdr, False)
        elif recv_hdr["cmd"] == "get_depth_right":
            return self._get_frame(recv_hdr, True)
        else:
            raise ValueError(f"unknown command: {recv_hdr['cmd']}")


if __name__ == "__main__":
    import argparse, json
    from hex_zmq_servers.zmq_base import hex_server_helper

    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", type=str, required=True)
    args = parser.parse_args()
    cfg = json.loads(args.cfg)

    hex_server_helper(cfg, HexE3DesktopMujocoServer)
