#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2025 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2025-09-12
################################################################

from ..mujoco_base import HexMujocoClientBase

NET_CONFIG = {
    "ip": "127.0.0.1",
    "port": 12345,
    "client_timeout_ms": 200,
    "server_timeout_ms": 1_000,
    "server_num_workers": 4,
}


class HexE3DesktopMujocoClient(HexMujocoClientBase):

    def __init__(
        self,
        net_config: dict = NET_CONFIG,
    ):
        HexMujocoClientBase.__init__(self, net_config)
        self._camera_seq = {
            "head_rgb": 0,
            "head_depth": 0,
            "left_rgb": 0,
            "left_depth": 0,
            "right_rgb": 0,
            "right_depth": 0,
        }

    def reset(self):
        HexMujocoClientBase.reset(self)
        self._camera_seq = {
            "head_rgb": 0,
            "head_depth": 0,
            "left_rgb": 0,
            "left_depth": 0,
            "right_rgb": 0,
            "right_depth": 0,
        }

    def _process_frame(
        self,
        camera_name: str | None = None,
        depth_flag: bool = False,
    ):
        if camera_name is None:
            raise ValueError("camera_name is required")

        req_cmd = f"get_{'depth' if depth_flag else 'rgb'}_{camera_name}"
        seq_key = f"{camera_name}_{'depth' if depth_flag else 'rgb'}"

        hdr, img = self.request({
            "cmd":
            req_cmd,
            "args": (1 + self._camera_seq[seq_key]) % self._max_seq_num,
        })

        try:
            cmd = hdr["cmd"]
            if cmd == f"{req_cmd}_ok":
                self._camera_seq[seq_key] = hdr["args"]
                return hdr, img
            else:
                return None, None
        except KeyError:
            print(f"\033[91m{hdr['cmd']} requires `cmd`\033[0m")
            return None, None
        except Exception as e:
            print(f"\033[91m__process_frame failed: {e}\033[0m")
            return None, None
