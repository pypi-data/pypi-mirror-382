# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2020 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

import base64
from pathlib import Path
from splashpy.client import SplashClient

class Files():
    """Various Function to Work with Files"""

    @staticmethod
    def getFile(file, md5):
        """Read a file from Splash Server"""
        # ====================================================================#
        # Initiate File Request Contents
        request = {
            "tasks": {
                "task": {
                    "id": 1,
                    "name": "ReadFile",
                    "desc": "Read file",
                    "params": {"file": file, "md5": md5},
                }
            }
        }
        # ====================================================================#
        # Execute Task
        response = SplashClient.getInstance().file(request)
        # ====================================================================#
        # Verify Response
        if response is False:
            return None
        if "result" not in response or response["result"] != "1":
            return None
        try:
            task = response["tasks"]['task']
            return task["data"]
        except Exception:
            return None

    @staticmethod
    def getAssetsPath():
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        return base_path + "/assets"

    @staticmethod
    def getRawContents(path):
        if not Path(path).exists():
            return ""

        with open(path, 'rb') as file:
            return str(base64.b64encode(file.read()), "UTF-8")



