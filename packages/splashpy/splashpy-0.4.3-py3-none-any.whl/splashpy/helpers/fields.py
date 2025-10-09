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


class FieldsHelper:
    """
    Fields Definition & Data Manager
    Collection of Basic STATIC Functions to Manage Splash Fields
    """

    # //==============================================================================
    # //      FIELDS LIST FUNCTIONS
    # //==============================================================================
    #
    # /**
    #  * Filter a Fields List to keap only given Fields Ids
    #  *
    #  * @param array $fieldsList Object Field List
    #  * @param array $filters    Array of Fields Ids
    #  *
    #  * @return array
    #  */
    # public static function filterFieldList($fieldsList, $filters = array())
    # {
    #     $result = array();
    #
    #     foreach ($fieldsList as $field) {
    #         if (in_array($field->id, $filters, true)) {
    #             $result[] = $field;
    #         }
    #     }
    #
    #     return $result;
    # }
    #
    # /**
    #  * Filter a Fields List to keap only given Fields Tags
    #  *
    #  * @param array  $fieldsList Object Field List
    #  * @param string $itemType   Field Microdata Type Url
    #  * @param string $itemProp   Field Microdata Property Name
    #  *
    #  * @return array
    #  */
    # public static function filterFieldListByTag($fieldsList, $itemType, $itemProp)
    # {
    #     $result = array();
    #     $tag = md5($itemProp.IDSPLIT.$itemType);
    #
    #     foreach ($fieldsList as $field) {
    #         if ($field->tag !== $tag) {
    #             continue;
    #         }
    #         if (($field->itemtype !== $itemType) || ($field->itemprop !== $itemProp)) {
    #             continue;
    #         }
    #         $result[] = $field;
    #     }
    #
    #     return $result;
    # }
    #
    # /**
    #  * Find a Field Definition in List by Id
    #  *
    #  * @param array $fieldsList Object Field List
    #  * @param array $fieldId    Field Id
    #  *
    #  * @return null|ArrayObject
    #  */
    # public static function findField($fieldsList, $fieldId)
    # {
    #     $fields = self::filterFieldList($fieldsList, $fieldId);
    #
    #     if (1 != count($fields)) {
    #         return null;
    #     }
    #
    #     return array_shift($fields);
    # }
    #
    # /**
    #  * Find a Field Definition in List by Id
    #  *
    #  * @param array  $fieldsList Object Field List
    #  * @param string $itemType   Field Microdata Type Url
    #  * @param string $itemProp   Field Microdata Property Name
    #  *
    #  * @return null|ArrayObject
    #  */
    # public static function findFieldByTag($fieldsList, $itemType, $itemProp)
    # {
    #     $fields = self::filterFieldListByTag($fieldsList, $itemType, $itemProp);
    #
    #     if (1 != count($fields)) {
    #         return null;
    #     }
    #
    #     return array_shift($fields);
    # }
    #
    # /**
    #  * Redure a Fields List to an Array of Field Ids
    #  *
    #  * @param array $fieldsList Object Field List
    #  * @param bool  $isRead     Filter non Readable Fields
    #  * @param bool  $isWrite    Filter non Writable Fields
    #  *
    #  * @return string[]
    #  */
    # public static function reduceFieldList($fieldsList, $isRead = false, $isWrite = false)
    # {
    #     $result = array();
    #
    #     foreach ($fieldsList as $field) {
    #         //==============================================================================
    #         //      Filter Non-Readable Fields
    #         if ($isRead && !$field->read) {
    #             continue;
    #         }
    #         //==============================================================================
    #         //      Filter Non-Writable Fields
    #         if ($isWrite && !$field->write) {
    #             continue;
    #         }
    #         $result[] = $field->id;
    #     }
    #
    #     return $result;
    # }
    #

    # ==================================================================== #
    # LISTS FIELDS MANAGEMENT
    # ==================================================================== #

    @staticmethod
    def isListField(identifier):
        """
        Check if this id is a list identifier
        :param identifier: str
        :return: None|hash
        """
        # ==================================================================== #
        # Safety Check
        if not isinstance(identifier, str) or len(identifier) < 3:
            return None
        # ==================================================================== #
        # Detects Lists
        try:
            field_name, list_name = list(identifier.split(const.__LISTSPLIT__))
            return {'fieldname': field_name, 'listname': list_name }
        except:
            return None

    @staticmethod
    def fieldName(identifier):
        """
        Retrieve Field Identifier from an List Field String
        :param identifier: str
        :return: None|str
        """
        # ==================================================================== #
        # Decode
        result = FieldsHelper.isListField(identifier)
        if result is None:
            return None
        # ==================================================================== #
        # Return Field Identifier
        return result['fieldname']

    @staticmethod
    def listName(identifier):
        """
        Retrieve Field Identifier from an List Field String
        :param identifier: str
        :return: None|str
        """
        # ==================================================================== #
        # Decode
        result = FieldsHelper.isListField(identifier)
        if result is None:
            return None
        # ==================================================================== #
        # Return List Name
        return result['listname']

    @staticmethod
    def baseType(identifier):
        """
        Retrieve Base Field Type from Field Type|Id String
        :param identifier: str
        :return: str
        """
        # ==================================================================== #
        # Detect List Id Fields
        if FieldsHelper.isListField(identifier) is not None:
            identifier = FieldsHelper.fieldName(identifier)
        # ==================================================================== #
        # Detect Objects Id Fields
        if FieldsHelper.isIdField(identifier) is not None:
            identifier = FieldsHelper.objectType(identifier)

        return identifier

    # ==================================================================== #
    # OBJECT ID FIELDS MANAGEMENT
    # ==================================================================== #

    @staticmethod
    def isIdField(identifier):
        """
        Identify if field is Object Identifier Data & Decode Field
        :param identifier: str
        :return: None|hash
        """
        # ==================================================================== #
        # Safety Check
        if not isinstance(identifier, str) or len(identifier) < 3:
            return None
        # ==================================================================== #
        # Detects ObjectId
        try:
            object_id, object_type = list(identifier.split(const.__IDSPLIT__))
            return {'ObjectId': object_id, 'ObjectType': object_type }
        except:
            return None

    @staticmethod
    def objectId(identifier):
        """
        Retrieve Object Id Name from an Object Identifier String
        :param identifier: str
        :return: None|str
        """
        # ==================================================================== #
        # Decode
        result = FieldsHelper.isIdField(identifier)
        if result is None:
            return None
        # ==================================================================== #
        # Return Object Id
        return result['ObjectId']

    @staticmethod
    def objectType(identifier):
        """
        Retrieve Object Type Name from an Object Identifier String
        :param identifier: str
        :return: None|str
        """
        # ==================================================================== #
        # Decode Identifier
        result = FieldsHelper.isIdField(identifier)
        if result is None:
            return None
        # ==================================================================== #
        # Return Field Identifier
        return result['ObjectType']
