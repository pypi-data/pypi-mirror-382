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

class ListHelper:
    """Helper for Objects Fields Management"""

    # ==================================================================== #
    # FIELDS LIST IDENTIFIERS MANAGEMENT
    # ==================================================================== #

    @staticmethod
    def encode(list_name, field_name):
        """
        Create a List Field Identifier String
        :param list_name: str
        :param field_name: str
        :return: None|str
        """
        # ==================================================================== #
        # Safety Checks
        if not isinstance(list_name, str) or len(list_name) < 3:
            return None
        if not isinstance(field_name, str) or len(field_name) < 1:
            return None
        # ==================================================================== #
        # Create & Return List Field Id Data String
        return field_name + const.__LISTSPLIT__ + list_name

    # ==================================================================== #
    # FIELDS LIST DATA MANAGEMENT
    # ==================================================================== #

    @staticmethod
    def initOutput(buffer, list_name, field_name):
        """
        Validate & Init List before Adding Data

        :param buffer: hash
        :param list_name: str
        :param field_name: str
        """
        # ==================================================================== #
        # Check List Name
        if FieldsHelper.listName(field_name) != list_name:
            return None
        # ==================================================================== #
        # Create List Array If Needed
        if list_name not in buffer.keys():
            buffer[list_name] = {}
        # ==================================================================== #
        # Decode Field Name
        return FieldsHelper.fieldName(field_name)

    @staticmethod
    def insert(buffer, list_name, field_id, key, item_data):
        """
        Add Item Data in Given  Output List
        :param buffer: hash
        :param list_name: str
        :param field_id: str
        :param key: str
        :param item_data: mixed
        :return:
        """
        # ==================================================================== #
        # Create List Array If Needed
        if list_name not in buffer.keys():
            buffer[list_name] = {}
        # ==================================================================== #
        # Create Line Array If Needed
        if key not in buffer[list_name].keys():
            buffer[list_name][key] = {}
        # ==================================================================== #
        # Store Data in Array
        field, list_type = list(field_id.split(const.__LISTSPLIT__))
        buffer[list_name][key][field] = item_data
