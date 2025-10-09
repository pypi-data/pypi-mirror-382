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
import hashlib
from splashpy import const


class AbstractConfigurator:
    """Base Functionnal Class for Configuration Managers"""

    # ====================================================================#
    # List of Parameters that are Not Allowed
    # on Custom Files Configurations
    __UNSECURED_PARAMETERS = [
        "WsIdentifier", "WsEncryptionKey", "WsHost", "WsCrypt"
    ]

    # ====================================================================#
    # List of Description Keys that are Not Allowed
    # on Custom Files Configurations
    __UNSECURED_DESCRIPTION = [
        "type", "fields"
    ]

    # ====================================================================#
    # ACCESS TO LOCAL CONFIGURATION
    # ====================================================================#

    @abstractmethod
    def getConfiguration(self):
        """Return Local Configuration Array"""
        raise NotImplementedError("Not implemented yet.")

    # ====================================================================#
    # CONFIGURE LOCAL SERVER
    # ====================================================================#

    def getParameters(self):
        """
        Get Custom Server Parameters Array
        This Event is Triggered by Splash Core during Configuration Reading
        """
        # ====================================================================#
        # Load Parameters from Configurator
        customParameters = self.getConfigurationValue("parameters")
        # ====================================================================#
        # Custom Parameters were Found
        if isinstance(customParameters, dict) and len(customParameters) > 0:
            # ====================================================================#
            # Remove Unsecure Parameters & Return Values
            return self.sercureParameters(customParameters)

        return {}

    # ====================================================================#
    # CONFIGURE LOCAL OBJECTS
    # ====================================================================#

    def isDisabled(self, objectType, isDisabled=False):
        """
        Override Object is Disabled Flag
        This Event is Triggered by Abstract Object during isDisabled Flag Reading
        """

        # ====================================================================#
        # Check if Configuration is Empty
        if len(self.getConfiguration()) > 0:
            # ====================================================================#
            # Load Configuration from Configurator
            disabled = self.getConfigurationValue(objectType, "disabled")
            # ====================================================================#
            # Configuration Exists
            if disabled is not None:
                return bool(disabled)

        return isDisabled

    def overrideDescription(self, objectType, description):
        """
        Override Object is Description Array
        This Event is Triggered by Abstract Object during Descritpion Reading
        """
        # ====================================================================#
        # Check if Configuration is Empty
        if len(self.getConfiguration()) == 0:
            return description
        # ====================================================================#
        # Load Configuration from Configurator
        overrides = self.getConfigurationValue(objectType)
        # ====================================================================#
        # Check if Configuration is an Array
        if not isinstance(overrides, dict):
            return description
        # ====================================================================#
        # Walk on Description Keys
        for key, value in overrides.items():
            # ====================================================================#
            # Check if Configuration Key is Allowed
            if key in self.__UNSECURED_DESCRIPTION:
                continue
            # ====================================================================#
            # Check if Configuration Key Exists
            if key not in description:
                continue
            # ====================================================================#
            # Update Configuration Key
            description[key] = value

        return description;

    def overrideFields(self, objectType, fields):
        """
        Override Object Fields Array using Field Factory
        This Event is Triggered by Object Class during Field Publish Action
        """
        # ====================================================================#
        # Check if Configuration is Empty
        if len(self.getConfiguration()) == 0:
            return fields
        # ====================================================================#
        # Load Configuration from Configurator
        overrides = self.getConfigurationValue(objectType, "fields")
        # ====================================================================#
        # Check if Configuration is an Array
        if not isinstance(overrides, dict):
            return fields
        # ====================================================================#
        # Walk on Defined Fields
        for index, field in enumerate(fields):
            # ====================================================================#
            # Check if Configuration Key Exists
            if field['id'] not in overrides:
                continue

            # ====================================================================#
            # Update Field Definition
            fields[index] = self.updateField(field, overrides[field['id']])

        return fields

    # ====================================================================#
    # PRIVATE FUNCTIONS
    # ====================================================================#

    def getConfigurationValue(self, key1, key2 = None):
        """Read Configuration Value"""
        # ====================================================================#
        # Load Configuration from Configurator
        config = self.getConfiguration()
        # ====================================================================#
        # Check Configuration is Valid
        if not isinstance(config, dict) or len(config) == 0:
            return None
        # ====================================================================#
        # Check Main Configuration Key Exists
        if key1 not in config:
            return None
        # ====================================================================#
        # Check Second Configuration Key Required
        if key2 is None:
            return config[key1]
        # ====================================================================#
        # Check Second Configuration Key Exists
        if key2 not in config[key1]:
            return None

        return config[key1][key2]

    def sercureParameters(self, parameters):
        """Remove Potentially Unsecure Parameters from Configuration"""
        # ====================================================================#
        # Detect Travis from SERVER CONSTANTS => Allow Unsecure for Testing
        #if (!empty(Splash::input('SPLASH_TRAVIS'))) {
        #    return;
        # ====================================================================#
        # Walk on Unsecure Parameter Keys
        for index in self.__UNSECURED_PARAMETERS:
            # ====================================================================#
            # Remove Parameter if Exists
            parameters.pop(index, None)

        return parameters

    def updateField(self, field, values):
        """Override a Field Definition"""
        # ====================================================================#
        # Check New Configuration is an Array
        if not isinstance(values, dict):
            return field
        # ====================================================================#
        # Field Type
        self.updateFieldStrVal(field, values, "type")
        # Field Name
        self.updateFieldStrVal(field, values, "name")
        # Field Description
        self.updateFieldStrVal(field, values, "desc")
        # Field Group
        self.updateFieldStrVal(field, values, "group")
        # Field MetaData
        self.updateFieldMeta(field, values)
        # ====================================================================#
        # Field Favorite Sync Mode
        self.updateFieldStrVal(field, values, "syncmode")
        # ====================================================================#
        # Field is Required Flag
        self.updateFieldBoolVal(field, values, "required")
        # ====================================================================#
        # Field is Index Flag
        self.updateFieldBoolVal(field, values, "index")
        # ====================================================================#
        # Field Read Allowed
        self.updateFieldBoolVal(field, values, "read")
        # ====================================================================#
        # Field Write Allowed
        self.updateFieldBoolVal(field, values, "write")
        # ====================================================================#
        # Field is Listed Flag
        self.updateFieldBoolVal(field, values, "inlist")
        # ====================================================================#
        # Field is No Tests Flag
        self.updateFieldBoolVal(field, values, "notest")
        # ====================================================================#
        # Field is Logged Flag
        self.updateFieldBoolVal(field, values, "log")
        # ====================================================================#
        # Field Values Choices
        self.updateFieldListVal(field, values, "choices")

        return field

    @staticmethod
    def updateFieldStrVal(field, values, key ):
        """Override a Field String Definition"""
        if key in values and isinstance(values[key], str):
            field[key] = values[key]

    @staticmethod
    def updateFieldBoolVal(field, values, key ):
        """Override a Field Bool Definition"""
        if key in values:
            field[key] = bool(values[key])

    def updateFieldMeta(self, field, values):
        """Override a Field Meta Definition"""
        # ====================================================================#
        # Update Field Meta ItemType
        self.updateFieldStrVal(field, values, "itemtype")
        # ====================================================================#
        # Update Field Meta ItemProp
        self.updateFieldStrVal(field, values, "itemprop")
        # ====================================================================#
        # Update Field Meta Tag
        if "itemprop" not in values and "itemtype" not in values:
            return

        if isinstance(field["itemprop"], str) and isinstance(field["itemtype"], str):
            tagString = field['itemprop'] + const.__IDSPLIT__ + field['itemtype']
            field['tag'] = hashlib.md5(tagString.encode()).hexdigest()

    @staticmethod
    def updateFieldListVal(field, values, key):
        """Override a Dict Definition"""
        if key not in values or not isinstance(values[key], dict):
            return
        field[key] = []
        for index, value in values[key].items():
            field[key].append({
                'key': index,
                'value': value
            })
