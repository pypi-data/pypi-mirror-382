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
import hashlib
from splashpy import const
from splashpy import const, Framework

class FieldFactory:
    """Splash Objects Fields Definitions Generator"""

    # ====================================================================#
    # Favorites Sync Modes
    # ====================================================================#
    __MODE_BOTH__ = "both"
    __MODE_READ__ = "export"
    __MODE_WRITE__ = "import"
    __MODE_NONE__ = "none"

    # ====================================================================#
    # Meta Data Access MicroDatas
    # ====================================================================#
    __META_URL__ = "http://splashync.com/schemas"  # Splash Specific Schemas Url.
    __META_OBJECT_ID__ = "ObjectId"  # Splash Object Id.
    __META_DATE_CREATED__ = "DateCreated"  # Splash Object Create Date.
    __META_ORIGIN_NODE_ID__ = "SourceNodeId"  # Object Source Server Identifier

    # ====================================================================#
    # Default Field Definition
    # ====================================================================#
    __DEFAULT_FIELD = {
        # ====================================================================#
        #      GENERAL FIELD PROPS
        "required": False,      # Field is Required to Create a New Object (Bool)
        "type": None,           # Field Format Type Name
        "id": None,             # Field Object Unique Identifier
        "name": None,           # Field Humanized Name (String)
        "desc": None,           # Field Description (String)
        "group": None,          # Field Section/Group (String)
        # ====================================================================#
        #      ACCESS PROPS
        "read": True,           # Field is Readable (Bool)
        "write": True,          # Field is Writable (Bool)
        "index": False,         # Field Should be Indexed for Text Search (Bool)
        "inlist": False,        # Field is Available in Object List Response (Bool)
        "hlist": False,         # Field is Available in Object List but Hidden (Bool)
        # ====================================================================#
        #      SYNC MODE
        "primary": False,       # Field is a Primary Key (Bool)
        "syncmode": "both",     # Field Favorite Sync Mode (read|write|both)
        # ====================================================================#
        #      SCHEMA.ORG IDENTIFICATION
        "itemprop": None,       # Field Unique Schema.Org "Like" Property Name
        "itemtype": None,       # Field Unique Schema.Org Object Url
        "tag": None,            # Field Unique Linker Tags (Self-Generated)
        # ====================================================================#
        #      DATA SPECIFIC FORMATS PROPS
        "choices": [],          # Possible Values used in Editor & Debugger Only  (Array)
        # ====================================================================#
        #      DATA LOGGING PROPS
        "log": False,           # Field is To Log (Bool)
        # ====================================================================#
        #      DEBUGGER PROPS
        "asso": {},             # Associated Fields. Fields to Generate with this field.
        "options": {},          # Fields Constraints to Generate Fake Data during Tests
        "notest": False,        # Do No Perform Tests for this Field
    }

    # Field Types Allowed for Multilang
    __MULTILANG_TYPES__ = [
        const.__SPL_T_VARCHAR__,
        const.__SPL_T_VARCHAR__+"@list",
        const.__SPL_T_TEXT__,
        const.__SPL_T_TEXT__ + "@list"
    ]

    # ====================================================================#
    # STATIC VARIABLES
    # ====================================================================#

    new = None
    fields = []
    dfLanguage = None

    def __init__( self ):
        pass

    # ====================================================================#
    # FIELDS DECLARATION
    # ====================================================================#

    @staticmethod
    def create(field_type, field_id=None, field_name=None):
        """Create a new Field Definition with default parameters"""

        # Commit Last Created if not already done
        if FieldFactory.new is not None:
            FieldFactory.commit()
        # Create new empty field
        FieldFactory.new = copy.copy(FieldFactory.__DEFAULT_FIELD)
        FieldFactory.new['choices'] = []
        FieldFactory.new['asso'] = {}
        FieldFactory.new['options'] = {}
        # Set Field Type
        FieldFactory.new['type'] = field_type
        # Set Field Identifier
        if isinstance(field_id, str) and field_id.__len__() >= 2:
            FieldFactory.identifier(field_id)
        # Set Field Name
        if isinstance(field_name, str) and field_name.__len__() >= 2:
            FieldFactory.name(field_name)

    @staticmethod
    def identifier( field_id ):
        """Set Current New Field Identifier"""
        FieldFactory.new['id'] = field_id

    @staticmethod
    def name( field_name ):
        """Set Current New Field Name"""
        FieldFactory.new['name'] = field_name
        if FieldFactory.new['desc'] is None:
            FieldFactory.new['desc'] = field_name

    @staticmethod
    def description( field_name ):
        """Set Current New Field Description"""
        FieldFactory.new['desc'] = field_name

    @staticmethod
    def inlist(list_name):
        """Update Current New Field set as it inside a list"""
        # Safety Check
        if not isinstance(list_name, str) or list_name.__len__() < 3:
            return False
        # Update New Field Identifier
        FieldFactory.new['id'] = FieldFactory.new['id'] + const.__LISTSPLIT__ + list_name
        # Update New Field Type
        FieldFactory.new['type'] = FieldFactory.new['type'] + const.__LISTSPLIT__ + const.__SPL_T_LIST__

    @staticmethod
    def group(group_name):
        """Update Current New Field with Field Group Name"""
        # Update New Field Group
        FieldFactory.new['group'] = group_name.strip()
        return FieldFactory

    @staticmethod
    def isReadOnly(read_only=True):
        """Update Current New Field set as Read Only Field"""
        if not read_only:
            return FieldFactory
        # Update New Field structure
        FieldFactory.new['read'] = True
        FieldFactory.new['write'] = False
        return FieldFactory

    @staticmethod
    def isWriteOnly(write_only=True):
        """Update Current New Field set as Write Only Field"""
        if not write_only:
            return FieldFactory
        # Update New Field structure
        FieldFactory.new['read'] = False
        FieldFactory.new['write'] = True
        return FieldFactory

    @staticmethod
    def isRequired(required=True):
        """Update Current New Field set as required for creation"""
        # Update New Field structure
        FieldFactory.new['required'] = bool(required)
        return FieldFactory

    @staticmethod
    def isPrimary(primary=True):
        """Update Current New Field set as primary key"""
        # Update New Field structure
        FieldFactory.new['primary'] = bool(primary)
        # Update New Field structure
        if bool(primary):
            FieldFactory.isIndexed(True)

        return FieldFactory

    @staticmethod
    def setPreferRead():
        """Signify Server Current New Field Prefer ReadOnly Mode"""
        # Update New Field structure
        FieldFactory.new['syncmode'] = FieldFactory.__MODE_READ__
        return FieldFactory

    @staticmethod
    def setPreferWrite():
        """Signify Server Current New Field Prefer WriteOnly Mode"""
        # Update New Field structure
        FieldFactory.new['syncmode'] = FieldFactory.__MODE_WRITE__
        return FieldFactory

    @staticmethod
    def setPreferNone():
        """Signify Server Current New Field Prefer No Sync Mode"""
        # Update New Field structure
        FieldFactory.new['syncmode'] = FieldFactory.__MODE_WRITE__
        return FieldFactory

    @staticmethod
    def association( *args ):
        """Update Current New Field set list of associated fields"""
        # Field Clear Fields Associations
        if not args.__len__():
            FieldFactory.new['asso'] = None
            return FieldFactory
        # Set New Field Associations
        FieldFactory.new['asso'] = list(args)
        return FieldFactory

    @staticmethod
    def isListed(listed=True):
        """Update Current New Field set as available in objects list"""
        # Update New Field structure
        FieldFactory.new['inlist'] = bool(listed)
        return FieldFactory

    @staticmethod
    def isIndexed(indexed=True):
        """
        Update Current New Field set as indexed for text search
        :param indexed: bool
        :return: self
        """
        FieldFactory.new['indexed'] = bool(indexed)
        return FieldFactory

    @staticmethod
    def isLogged(logged=True):
        """
        Update Current New Field set as recommended for logging
        :param logged: bool
        :return: self
        """
        FieldFactory.new['log'] = bool(logged)
        return FieldFactory

    @staticmethod
    def microData( item_type, item_prop ):
        """Update Current New Field set as recommended for logging"""
        # Update New Field structure
        FieldFactory.new['itemtype'] = item_type
        FieldFactory.new['itemprop'] = item_prop
        FieldFactory.setTag(item_prop + const.__IDSPLIT__ + item_type)
        return FieldFactory

    @staticmethod
    def setTag(tag):
        """Update Current New Field set its unik tag for autolinking"""
        FieldFactory.new['tag'] = hashlib.md5(tag.encode()).hexdigest()
        return FieldFactory

    @staticmethod
    def isNotTested( not_tested=True ):
        """Update Current New Field set as not possible to test"""
        # Update New Field structure
        FieldFactory.new['notest'] = bool(not_tested)
        return FieldFactory

    @staticmethod
    def addChoices( choices ):
        """Add Possible Choice to Current New Field Name"""
        for key, value in choices:
            # Update New Field structure
            FieldFactory.addChoice(key, value)
        return FieldFactory

    @staticmethod
    def addChoice( key, value ):
        """Add Possible Choice to Current New Field Name"""
        # Update New Field structure
        FieldFactory.new['choices'].append({
            'key': key,
            'value': value
        })
        return FieldFactory

    @staticmethod
    def addOptions( options ):
        """Add New Options Array for Current Field"""
        for key, value in options:
            # Update New Field structure
            FieldFactory.addOption(key, value)
        return FieldFactory

    @staticmethod
    def addOption( key, value ):
        """Add New Option for Current Field"""
        # Safety Check
        if not isinstance(key, str) or key.__len__() < 3:
            return False
        # Update New Field structure
        FieldFactory.new['options'][key] = value
        return FieldFactory

    @staticmethod
    def setDefaultLanguage( iso_code ):
        """Select Default Language for Field List"""
        from splashpy.core.framework import Framework
        # Safety Check ==> Verify Language ISO Code
        if not isinstance(iso_code, str) or iso_code.__len__() < 2:
            return Framework.log().error("Default Language ISO Code is Invalid")
        # Store Default Language ISO Code
        FieldFactory.dfLanguage = iso_code

    @staticmethod
    def setMultilang(iso_code):
        """
        Configure Current Field with Multilangual Options
        :param iso_code: str
        :return: void
        """
        from splashpy.core.framework import Framework
        # Safety Check ==> Verify Language ISO Code
        if not isinstance(iso_code, str) or iso_code.__len__() < 2:
            return Framework.log().error("Default Language ISO Code is Invalid")

        # Safety Check ==> Verify Field Type is Allowed
        if not FieldFactory.new['type'] in FieldFactory.__MULTILANG_TYPES__:
            return Framework.log().error("This field type is not Multi-lang: " + FieldFactory.new['type'])

        # Default Language ==> Only Setup Language Option
        FieldFactory.addOption("language", iso_code)
        # Other Language ==> Complete Field Setup
        if not iso_code == FieldFactory.dfLanguage:
            FieldFactory.identifier(FieldFactory.new['id'] + "_" + iso_code)
            if FieldFactory.new['itemtype']:
                FieldFactory.microData(
                    FieldFactory.new['itemtype'] + "/" + iso_code,
                    FieldFactory.new['itemprop']
                )

    # ====================================================================#
    # FIELDS LIST MANAGEMENT
    # ====================================================================#

    @staticmethod
    def validate():
        """Validate Field Definition"""
        from splashpy.core.framework import Framework
        # Verify - Field Type is Not Empty.
        if not isinstance(FieldFactory.new['type'], str) or FieldFactory.new['type'].__len__() < 3:
            return Framework.log().error("Field type is not defined")
        # Verify - Field Id is Not Empty.
        if not isinstance(FieldFactory.new['id'], str) or FieldFactory.new['id'].__len__() < 2:
            return Framework.log().error("Field ID is not defined")
        # # Verify - Field Id No Spacial Chars.
        # if not isinstance(FieldFactory.new.id, str) or FieldFactory.new.id.__len__() < 2:
        #     Framework.log().error("Field IS is not defined")
        #     return False
        # Verify - Field Name is Not Empty.
        if not isinstance(FieldFactory.new['name'], str) or FieldFactory.new['name'].__len__() < 3:
            return Framework.log().error("Field name is not defined")
        # Verify - Field Desc is Not Empty.
        if not isinstance(FieldFactory.new['desc'], str) or FieldFactory.new['desc'].__len__() < 3:
            return Framework.log().error("Field Description is not defined")

        return True

    @staticmethod
    def commit():
        # Safety Check
        if FieldFactory.new is None:
            return True
        # Create Field List
        if FieldFactory.fields is None:
            FieldFactory.fields = []
        #  Validate New Field
        if not FieldFactory.validate():
            FieldFactory.new = None
            return False
        # Insert Field List
        FieldFactory.fields.append(FieldFactory.new)
        FieldFactory.new = None

        return True

    @staticmethod
    def publish():
        from splashpy.core.framework import Framework
        # Commit Last Created if not already done
        if FieldFactory.new is not None:
            FieldFactory.commit()
        # Safety Check
        if not FieldFactory.fields.__len__():
            return Framework.log().error("Fields List is Empty")

        buffer = copy.copy(FieldFactory.fields)
        FieldFactory.fields = None
        return buffer
