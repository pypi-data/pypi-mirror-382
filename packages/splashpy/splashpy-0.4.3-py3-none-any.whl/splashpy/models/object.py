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

from splashpy.models.objects.interfaces import ObjectInterface
from splashpy.models.objects.intel import IntelParser


class BaseObject(IntelParser, ObjectInterface):
    # ====================================================================#
    # Object Definition
    # ====================================================================#
    disabled = False
    name = "Object"
    desc = "Object"
    icon = "fas fa-cubes"
    # ====================================================================#
    # Object Global Configuration
    # ====================================================================#
    allow_push_created = True
    allow_push_updated = True
    allow_push_deleted = True
    # ====================================================================#
    # Object Default Configuration
    # ====================================================================#
    # Imports
    enable_pull_created = True
    enable_pull_updated = True
    enable_pull_deleted = True
    # Exports
    enable_push_created = True
    enable_push_updated = True
    enable_push_deleted = True

    # ====================================================================#
    # Object Lock feature
    # ====================================================================#
    __locks = {}

    # ====================================================================#
    # Object Lock feature
    # ====================================================================#
    __updated = {}

    # ====================================================================#
    # Object Parsing features
    # ====================================================================#
    _in = {}
    _out = {}
    object = {}

    def __init__(self):
        pass

    # ====================================================================#
    # COMMON CLASS INFORMATION
    # ====================================================================#

    def getType(self):
        """Get Object Type"""
        return self.__class__.__name__

    def getName(self):
        """Get Object Type Name"""
        return self.name

    def getDescription(self):
        """Get Object Type Description"""
        return self.desc

    def getIcon(self):
        """Get Object Type FontAwesome 5 Icon"""
        return self.icon

    def isDisabled(self):
        """Check if Object is Disabled"""
        return self.disabled

    def description(self):
        """Get Ws Object Description"""
        # Build & Return Object Description Array
        return {
            # ====================================================================#
            # General Object definition
            # ====================================================================#
            # Object Type Name
            "type": self.getType(),
            # Object Display Name
            "name": self.getName(),
            # Object Description
            "description": self.getDescription(),
            # Object Icon Class (Font Awesome 5. ie "fas fa-user")
            "icon": self.getIcon(),
            # Is This Object Enabled or Not?
            "disabled": self.isDisabled(),
            # ====================================================================#
            # Object Limitations
            # ====================================================================#
            "allow_push_created": self.allow_push_created,
            "allow_push_updated": self.allow_push_updated,
            "allow_push_deleted": self.allow_push_deleted,
            # ====================================================================#
            # Object Default Configuration
            # ====================================================================#
            "enable_push_created": self.enable_push_created,
            "enable_push_updated": self.enable_push_updated,
            "enable_push_deleted": self.enable_push_deleted,
            "enable_pull_created": self.enable_pull_created,
            "enable_pull_updated": self.enable_pull_updated,
            "enable_pull_deleted": self.enable_pull_deleted
        }

    # ====================================================================#
    # Manage Lock Feature
    # ====================================================================#

    def lock(self, object_id="new"):
        self.__locks[str(object_id)] = True
        return True

    def islocked(self, object_id="new"):
        if str(object_id) in self.__locks:
            return self.__locks[str(object_id)]
        return False

    def unlock(self, object_id):
        self.__locks[str(object_id)] = False
        return True

    # ====================================================================#
    # Manage Update Flag Feature
    # ====================================================================#

    def needUpdate( self, key="object"):
        self.__updated[key] = True

    def isUpdated( self, key="object"):
        self.__updated[key] = False

    def isToUpdate( self, key="object"):
        try:
            return self.__updated[key]
        except:
            return False

    # ====================================================================#
    #  Object FILES Management
    # ====================================================================#

    def getFile(self, path, md5):
        """
        Custom Reading of a File from Local System (Database or any else)
        """
        return None
