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

from splashpy import const
from splashpy.helpers import FieldsHelper

class ObjectsHelper:
    """Helper for Objects Fields Management"""

    @staticmethod
    def encode(object_type, object_id):
        """
        Create an Object Identifier String
        :param object_type: str
        :param object_id: int|str
        :return: None|str
        """
        # ==================================================================== #
        # Safety Checks
        if not isinstance(object_type, str) or len(object_type) < 3:
            return None
        if not isinstance(object_id, (int, str)) or len(str(object_id)) < 1:
            return None
        # ==================================================================== #
        # Create & Return Field Id Data String
        return str(object_id) + const.__IDSPLIT__ + object_type

    @staticmethod
    def id(identifier):
        """
        Retrieve Identifier from an Object Identifier String
        :param identifier: str
        :return: None|str
        """
        # ==================================================================== #
        # Forward to Fields Manager
        return FieldsHelper.objectId(identifier)

    @staticmethod
    def type(identifier):
        """
        Retrieve Object Type Name from an Object Identifier String
        :param identifier: str
        :return: None|str
        """
        # ==================================================================== #
        # Forward to Fields Manager
        return FieldsHelper.objectType(identifier)
