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
from abc import abstractmethod
from collections.abc import Iterable
from splashpy import const


class ServerInfo:
    """Define Technical Details about this Splash Server"""

    # ====================================================================#
    # Server Info
    # ====================================================================#
    server_type = "Python"                      # INFO - Server Language Type
    server_version = None                       # INFO - Server Language Version
    server_protocol = const.__SPL_PROTOCOL__    # INFO - Server Protocol Version
    server_address = None                       # INFO - Server IP Address or Main Url
    server_root = ""                            # INFO - Server Root Directory
    user_agent = "undefined"                    # INFO - Browser User Agent
    ws_method = "pysimplesoap"                  # INFO - Current Splash WebService Component

    # ====================================================================#
    # Server URLs
    # ====================================================================#
    server_ip = None                            # INFO - Server IP Address
    server_host = "undefined"                   # CRITICAL - Server Host Name
    server_path = "undefined"                   # CRITICAL - Server WebService Path (EndPoint)

    def __init__(self, info=False):
        """Init Base Configuration if Given"""
        # No Init Data Provided
        if info is False or not isinstance(info, Iterable):
            return
        # Walk on Any Iterable Object to Add Child Elements
        for key, value in info.items():
            self.__setattr__(key, value)

    def loadOsInformation(self):
        """Load Server Platform Information"""
        import sys
        import socket
        self.server_version = sys.version
        try:
            self.server_host = socket.gethostname()
            self.server_ip = self.server_address = socket.gethostbyname(self.server_host)
        except Exception:
            from splashpy.core.framework import Framework
            Framework.log().error("Unable to get Hostname and IP")

    def loadWerkzeugInformation(self, request):
        """Load Server Urls Information from Werkzeug Request"""
        if request.host.__len__() > 3:
            self.server_host = request.host
        if request.path.__len__() > 3:
            self.server_path = request.path

    @abstractmethod
    def complete(self):
        """Override this function to complete Server Information Dynamically"""
        self.loadOsInformation()

        return

    @abstractmethod
    def get(self):
        """Detect & Return Server Information"""
        self.complete()

        return {
            # Server Info
            "ServerType": self.server_type,
            "ServerVersion": self.server_version,
            "ProtocolVersion": self.server_protocol,
            "ServerAddress": self.server_address,
            "ServerRoot": self.server_root,
            "UserAgent": self.user_agent,
            "WsMethod": self.ws_method,
            # Server URLs
            "ServerIP": self.server_ip,
            "ServerHost": self.server_host,
            "ServerPath": self.server_path,
        }




