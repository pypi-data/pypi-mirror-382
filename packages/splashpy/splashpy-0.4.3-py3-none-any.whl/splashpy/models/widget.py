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

from splashpy.models.widgets.interfaces import WidgetInterface


class BaseWidget(WidgetInterface):

    # ====================================================================#
    # Constants Definition
    # ====================================================================#

    __SIZE_XS__ = "col-sm-6 col-md-4 col-lg-3"
    __SIZE_SM__ = "col-sm-6 col-md-6 col-lg-4"
    __SIZE_DEFAULT__ = "col-sm-12 col-md-6 col-lg-6"
    __SIZE_M__ = "col-sm-12 col-md-6 col-lg-6"
    __SIZE_L__ = "col-sm-12 col-md-6 col-lg-8"
    __SIZE_XL__ = "col-sm-12 col-md-12 col-lg-12"

    # ====================================================================#
    # Widget Definition
    # ====================================================================#

    name = "Widget"
    desc = "Widget"
    icon = "fas fa-info"
    fields = {}
    blocks = {}
    options = {}
    parameters = {}
    out = {
        "title": "",
        "subtitle": "",
        "icon": "",
        "blocks": {}
    }
    disabled = False

    def __init__(self):
        self.setTitle(self.name).setIcon(self.icon)

    # ====================================================================#
    # COMMON CLASS INFORMATION
    # ====================================================================#

    def getType( self ):
        """Get Widget Type"""
        return self.__class__.__name__

    def getName( self ):
        """Get Widget Type Name"""
        return self.name

    def getDescription( self ):
        """Get Widget Type Description"""
        return self.desc

    def getIcon( self ):
        """Get Widget Type FontAwesome 5 Icon"""
        return self.icon

    def getOptions( self ):
        """Get Widget Default Options"""
        return self.options

    def getParameters(self):
        """Get Widget Default Parameters"""
        return self.parameters

    # ====================================================================#
    # COMMON CLASS SERVER ACTIONS
    # ====================================================================#

    def description(self):
        """Get Ws Widget Description"""
        # Build & Return Widget Description Array
        return {
            # ====================================================================#
            # General Widget definition
            # ====================================================================#
            # Widget Type Name
            "type": self.getType(),
            # Widget Display Name
            "name": self.getName(),
            # Widget Description
            "description": self.getDescription(),
            # Widget Icon Class (Font Awesome 5. ie "fas fa-user")
            "icon": self.getIcon(),
            # Is This Widget Enabled or Not?
            "disabled": self.isDisabled(),
            # Widget Options
            "options": self.getOptions(),
            # Widget Parameters
            "parameters": self.getParameters()
        }

    def render(self):
        """Render / Return Widget Data Array"""
        return self.out

    def isDisabled(self):
        """Check if Object is Disabled"""
        return self.disabled

    # ====================================================================#
    # COMMON CLASS SETTERS
    # ====================================================================#

    def setTitle(self, text):
        """Set Widget Title"""
        self.out["title"] = text

        return self

    def setSubTitle(self, text):
        """Set Widget Subtitle"""
        self.out["subtitle"] = text

        return self

    def setIcon(self, text):
        """Set Widget Icon"""
        self.out["icon"] = text

        return self

    def setBlocks(self, blocks):
        """Set Widget Icon"""
        self.out["blocks"] = blocks

        return self