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


class Framework:
    """Base Class for Splash Client & Server"""

    __debug = False     # Debug Mode
    __serve = False     # Server Mode
    __config = None     # Framework general Configuration
    __logger = None     # Splash Logger
    __client = None     # Client module info/description
    __server = None     # Server technical details
    __objects = {}      # Shared Objects Classes
    __widgets = {}      # Shared Widgets Classes

    def __init__(self, identifier, key, objects=None, widgets=None, info=False, server=False, config=False):
        """Init of Splash Mini Framework"""
        from splashpy.componants.config import Config
        from splashpy.componants.logger import Logger
        from splashpy.models.client import ClientInfo
        from splashpy.models.server import ServerInfo
        # ====================================================================#
        # Init Splash Client Configuration
        if isinstance(config, Config):
            Framework.__config = config
        else:
            Framework.__config = Config(identifier, key)
        # Init Logger
        Framework.__logger = Logger()
        # ====================================================================#
        # Init Client Information
        if isinstance(info, ClientInfo):
            Framework.__client = info
        else:
            Framework.__client = ClientInfo(info)
        # ====================================================================#
        # Init Server Information
        if isinstance(server, ServerInfo):
            Framework.__server = server
        else:
            Framework.__server = ServerInfo(server)
        # ====================================================================#
        # Init Client Available Objects
        if isinstance(objects, list):
            for ws_object in objects:
                Framework.addObject(ws_object)
        # ====================================================================#
        # Init Client Available Widgets
        if isinstance(widgets, list):
            for ws_widget in widgets:
                Framework.addWidget(ws_widget)

    @staticmethod
    def config():
        """
        Safe Access to Local Configuration

        :return: Splash Config
        :rtype:splashpy.componants.config.Config
        """
        return Framework.__config

    @staticmethod
    def log():
        """
        Safe Access to Splash Logger

        :return: Splash Logger
        :rtype: splashpy.componants.logger.Logger
        """
        if Framework.__logger is None:
            from splashpy.componants.logger import Logger
            Framework.__logger = Logger()
        return Framework.__logger

    # ====================================================================#
    # Client Module Management
    # ====================================================================#

    @staticmethod
    def getClientInfo():
        """
        Safe Access to Client Module Information

        :return: Splash Logger
        :rtype: splashpy.models.client.ClientInfo
        """
        return Framework.__client

    @staticmethod
    def setClientInfo(info):
        """Safe Access to Client Module Information"""
        from splashpy.models.client import ClientInfo
        if isinstance(info, ClientInfo):
            Framework.__client = info

    # ====================================================================#
    # Server Details Management
    # ====================================================================#

    @staticmethod
    def getServerDetails():
        """Safe Access to Server Details"""
        return Framework.__server

    @staticmethod
    def setServerDetails(info):
        """
        Safe Access to Server Details

        :return: Splash Logger
        :rtype: splashpy.models.client.ServerInfo
        """
        from splashpy.models.server import ServerInfo
        if isinstance(info, ServerInfo):
            Framework.__server = info

    # ====================================================================#
    # Objects Management
    # ====================================================================#

    @staticmethod
    def addObject(ws_object):
        """Safe Add Objects to Framework"""
        from splashpy.models.object import BaseObject
        if isinstance(ws_object, BaseObject):
            Framework.__objects[ws_object.getType()] = ws_object

    @staticmethod
    def getObjects():
        """
        Get List of Available Objects Types

        :rtype: list
        """
        return list(Framework.__objects.keys())

    @staticmethod
    def getObject(object_type):
        """
        Safe Get Object Class

        :rtype: splashpy.models.object.BaseObject
        """
        if object_type not in Framework.__objects:
            return False
        return Framework.__objects[object_type]

    # ====================================================================#
    # Widgets Management
    # ====================================================================#

    @staticmethod
    def addWidget(ws_widget):
        """Safe Add Widget to Framework"""
        from splashpy.models.widget import BaseWidget
        if isinstance(ws_widget, BaseWidget):
            Framework.__widgets[ws_widget.getType()] = ws_widget

    @staticmethod
    def getWidgets():
        """
        Get List of Available Widget Types

        :rtype: list
        """
        return list(Framework.__widgets.keys())

    @staticmethod
    def getWidget(widget_type):
        """
        Safe Get Widget Class

        :rtype: splashpy.models.widget.BaseWidget
        """
        if widget_type not in Framework.__widgets:
            return False
        return Framework.__widgets[widget_type]

    # ====================================================================#
    # Server Debug Mode Management
    # ====================================================================#

    @staticmethod
    def isDebugMode():
        """Check if Server is in Debug Mode"""
        return Framework.__debug

    @staticmethod
    def setDebugMode(state=True):
        """Set Debug Mode"""
        Framework.__debug = bool(state)

    # ====================================================================#
    # Server Calls Mode Management
    # ====================================================================#

    @staticmethod
    def isServerMode():
        """Check if Module is in Server Mode"""
        return Framework.__serve

    @staticmethod
    def setServerMode(state=True):
        """Set Server Mode"""
        Framework.__serve = bool(state)

