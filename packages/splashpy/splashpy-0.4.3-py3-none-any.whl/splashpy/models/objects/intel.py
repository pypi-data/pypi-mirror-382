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

import copy


class IntelParser:
    """Splash intelligent data parser"""

    __build_methods = None
    __get_methods = None
    __set_methods = None

    # ====================================================================#
    # Object Parsing features
    # ====================================================================#
    _in = {}
    _out = {}
    object = {}

    def __init__(self):
        pass

    # ====================================================================#
    # OBJECT DEFINITION
    # ====================================================================#

    def fields(self):
        from splashpy.componants.fieldfactory import FieldFactory

        # Walk on Field Building Functions
        for method in self.identify_build_methods():
            method()

        # Publish Fields from Factory
        return FieldFactory.publish()

    # ====================================================================#
    # OBJECT CRUD
    # ====================================================================#

    def get(self, object_id, fields):
        # ====================================================================#
        # Init Reading
        self._in = fields
        # ====================================================================#
        # Load Object
        self.object = False
        self.object = self.load(object_id)
        if self.object is False:
            return False
        # ====================================================================#
        # Init Response
        self._out = {'id': object_id}
        # ====================================================================#
        # Run Through All Requested Fields
        for index, field in copy.copy(fields).items():
            # Read Requested Fields
            for method in self.identify_get_methods():
                method(index, field)
        # ====================================================================#
        # Verify Requested Fields List is now Empty => All Fields Read Successfully
        if self._in.__len__():
            from splashpy.core.framework import Framework
            for field in self._in.values():
                Framework.log().error("Get Object - Requested field not found => " + field)
            return False
        # ====================================================================#
        # Return Object Data
        return self._out

    def set(self, object_id, fields ):
        # ====================================================================#
        # Init Writing
        self._in = fields       # Store List of Field to Write in Buffer
        new_object_id = None    # If Object Created, we MUST Return Object Id
        self.isUpdated()        # Clear Updated Flag before Writing
        # ====================================================================#
        # Load or Create Requested Object
        if object_id is None or len(object_id) < 1:
            self.object = self.create()
        else:
            self.object = self.load(object_id)
        if self.object is False:
            return False
        # ====================================================================#
        # New Object Created => Store new Object Identifier
        if not object_id:
            new_object_id = self.getObjectIdentifier()
        # ====================================================================#
        # Execute Write Operations on Object
        if not self.setObjectData():
            if new_object_id:
                return new_object_id
            return False
        # ====================================================================#
        # Update Requested Object
        updated = self.update(self.isToUpdate())
        # Update Fail ?
        if not updated:
            if new_object_id:
                return new_object_id
            return False
        # Return Updated ID
        return updated

    def setObjectData( self ):
        """Execute Fields Update"""
        # ====================================================================#
        # Walk on All Requested Fields
        for field_id, field_data in copy.copy(self._in).items():
            # Write Requested Fields
            for method in self.identify_set_methods():
                method(field_id, field_data)
        # ====================================================================#
        # Verify Requested Fields List is now Empty => All Fields Read Successfully
        if self._in.__len__():
            from splashpy.core.framework import Framework
            for field in self._in.keys():
                Framework.log().error("Set Object - Requested field not found => " + field)
            return False

        return True

    # ====================================================================#
    # PRIVATE CORE METHODS
    # ====================================================================#

    def identify_build_methods( self ):
        """Identify Generic Fields Building Functions"""
        if self.__build_methods is None:
            self.__build_methods = self.identify_methods('build')

        return self.__build_methods

    def identify_get_methods( self ):
        """Identify Generic Fields Getter Functions"""
        if self.__get_methods is None:
            self.__get_methods = self.identify_methods('get')

        return self.__get_methods

    def identify_set_methods( self ):
        """Identify Generic Fields Setter Functions"""
        if self.__set_methods is None:
            self.__set_methods = self.identify_methods('set')

        return self.__set_methods

    def identify_methods( self, prefix ):
        """Identify Generic Functions"""
        # Prepare List of Available Methods
        result = []
        for method in dir(self):
            if method.find(prefix) != 0:
                continue
            if method.find("Fields") is not (method.__len__() - 6):
                continue
            result.append(getattr(self, method))

        return result
