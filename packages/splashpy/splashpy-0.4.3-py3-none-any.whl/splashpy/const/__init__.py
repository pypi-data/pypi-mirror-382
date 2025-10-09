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

# ====================================================================
# Global Definitions
__VERSION__ = '0.3.1'
__NAME__ = "Splash Python Core Module"
__DESC__ = "Splash Open-Source & Universal Synchronisation WebService."
__AUTHOR__ = 'Splash Official <www.splashsync.com>'

# ====================================================================
# Webservice Parameters
__HOST__ = "https://www.splashsync.com/ws/soap"
__TIMEOUT__ = 30
__CRYPT_METHOD__ = "AES-256-CBC"
__ENCODE__ = "XML"

# ====================================================================
# Various Parameters
__LANG__ = 'en_US'
__SMART_NOTIFY__ = False

# ====================================================================
# ====================================================================
#  CONSTANTS DEFINITION
# ====================================================================
# ====================================================================

__SPL_PROTOCOL__ = '1.0'

# ====================================================================
# ====================================================================
# SPL Objects Operations
# List of all available operations on objects modes
# ====================================================================
# ====================================================================
__SPL_A_IMPORT__ = 'import'         # Object is imported from a remote Node
__SPL_A_EXPORT__ = 'export'         # Object is exported to a remote Node
__SPL_A_UPDATE__ = 'update'         # Object was locally modified
__SPL_A_UCREATE__ = 'ucreate'       # Object was locally modified but doesn't exist on remote
__SPL_A_CREATE__ = 'create'         # Object locally created
__SPL_A_DELETE__ = 'delete'         # Object locally deleted
__SPL_A_RUPDATE__ = 'rupdate'       # Object was locally modified
__SPL_A_RUCREATE__ = 'rucreate'     # Object was remotly modified but doesn't exist locally
__SPL_A_RCREATE__ = 'rcreate'       # Object remotly created
__SPL_A_RDELETE__ = 'rdelete'       # Object remotly deleted
__SPL_A_RENAME__ = 'rename'         # Object Identifier Was Modified
__SPL_A_UNLINK__ = 'unlink'         # Object Link Deleted

# ====================================================================
# ====================================================================
# SplashSync Data Types
# List of all available data type used in transactions
# ====================================================================
# These Data Types are used to define available data on slave side.
# For any objects, remote slave will return a complete list of all
# available data. These list is used to setup synchronisation
# ====================================================================
# ====================================================================

# ====================================================================
# Single Fields, Shared in a single named variable
# Sample :
# $data["name"] = $value
# ====================================================================
__SPL_T_BOOL__ = 'bool'                 # Boolean, stored as 0 or 1
__SPL_T_INT__ = 'int'                   # Signed Integer
__SPL_T_DOUBLE__ = 'double'             # Signed Double, used for all float values
__SPL_T_VARCHAR__ = 'varchar'           # Short texts (Inf 256 char)
__SPL_T_TEXT__ = 'text'                 # Long text
__SPL_T_EMAIL__ = 'email'               # Email Address
__SPL_T_PHONE__ = 'phone'               # Phone Number
__SPL_T_DATE__ = 'date'                 # Day Timestamps
__SPL_T_DATECAST__ = '%Y-%m-%d'            # Day Timestamps Format
__SPL_T_DATETIME__ = 'datetime'         # Timestamps
__SPL_T_DATETIMECAST__ = '%Y-%m-%d %H:%M:%S'  # Timestamps Format
__SPL_T_LANG__ = 'lang'                 # Iso Language code (en_US / fr_FR ...)
__SPL_T_COUNTRY__ = 'country'           # Iso country code (FR / US ...)
__SPL_T_STATE__ = 'state'               # Iso state code (CA / FR ...)
__SPL_T_CURRENCY__ = 'currency'         # Iso Currency code (EUR / USD ... )
__SPL_T_URL__ = 'url'                   # External Url
__SPL_T_INLINE__ = 'inline'             # Inline Simple Json List

# ====================================================================
# ====================================================================
# Structured Fields, Shared in a standard array of named variable
# ====================================================================
# ====================================================================

# ====================================================================
# File Structure
# ====================================================================
# Sample :
# $data["file"]["name"]           =>      File Name/Description
# $data["file"]["file"]           =>      File Identifier to Require File from Server
# $data["file"]["filename"]       =>      Filename with Extension
# $data["file"]["path"]           =>      Full File path on client system
# $data["file"]["url"]            =>      Complete Public Url, Usable for Direct Download
# $data["file"]["md5"]            =>      File Md5 Checksum
# $data["file"]["size"]           =>      File Size in Bytes
# ====================================================================
__SPL_T_FILE__ = 'file'

# ====================================================================
# Image Structure
# ====================================================================
# Sample :
# $data["image"]["name"]           =>      Image Name
# $data["image"]["file"]           =>      Image Identifier to Require File from Server
# $data["image"]["filename"]       =>      Image Filename with Extension
# $data["image"]["path"]           =>      Image Full path on local system
# $data["image"]["url"]            =>      Complete Public Url, Used to display image
# $data["image"]["t_url"]          =>      Complete Thumb Public Url, Used to display image
# $data["image"]["width"]          =>      Image Width In Px
# $data["image"]["height"]         =>      Image Height In Px
# $data["image"]["md5"]            =>      Image File Md5 Checksum
# $data["image"]["size"]           =>      Image File Size
# ====================================================================
__SPL_T_IMG__ = 'image'                       # Image file

# ====================================================================
# Multi-langual Fields, Shared as Single Fields with Iso Language code #tag
# ====================================================================
# Sample :
# $data["name"]["iso_code"]            =>      Value
# Where name is field name and code is a valid SPL_T_LANG Iso Language Code
# ====================================================================
__SPL_T_MVARCHAR__ = 'mvarchar'               # Multi-langual Short texts (Inf 256 char)
__SPL_T_MTEXT__ = 'mtext'                     # Multi-langual Long text

# ====================================================================
# Price Fields, Shared as an array including all price information
# ====================================================================
# Price Definition Array
# Sample : Required Informations
# $data["price"]["base"]           =>  BOOL      Reference Price With or Without Tax? True => With VAT
# $data["price"]["ht"]             =>  DOUBLE    Price Without Tax
# $data["price"]["ttc"]            =>  DOUBLE    Price With Tax
# $data["price"]["vat"]            =>  DOUBLE    VAT Tax in Percent
# $data["price"]["tax"]            =>  DOUBLE    VAT Tax amount
# Sample : Optionnal Informations
# $data["price"]["symbol"]         =>  STRING    Currency Symbol
# $data["price"]["code"]           =>  STRING    Currency Code
# $data["price"]["name"]           =>  STRING    Currency Name
# Where code field is a valid SPL_T_CURRENCY Iso Currency Code
# ====================================================================
__SPL_T_PRICE__ = 'price'                         # Price definition array

# ====================================================================
# Fields Lists
# ====================================================================
# Declared as SPL_T_XX@SPL_T_LIST
# Shared as fieldname@listname
# Multiple Fields may be attached to same List Name
# ====================================================================
__SPL_T_LIST__ = 'list'                           # Object List
__LISTSPLIT__ = '@'                               # Object List Splitter

# ====================================================================
# Object Identifier Field
# ====================================================================
# Declared as any other field type, this type is used to identify Objects
# links between structures.
#
# How does it works :
#
#    - Identifier uses a specific format : ObjectId:@@:TypeName
#      where ObjectId is Object Identifier on Local System and
#      TypeName is the standard OsWs Type of this object.
#      => ie : Product with Id 56 is : 56:@@:Products
#
#    - When reading an object, you can add Object identifiers field
#      in any data structure, or list.
#
#    - Before Data CheckIn or CheckOut, OsWs Scan all data and :
#      => Translate already linked object from Local to Remote Server
#      => Import or Export Missing Objects on Local or Remote Server
#      => Return Translated Objects Id to requested server
#
# ====================================================================
__SPL_T_ID__ = 'objectid'                         # Object Id
__IDSPLIT__ = '::'                                # Object Id Splitter

# ====================================================================
# ====================================================================
# SPL Sync Mode
# List of all available synchronisation modes
# ====================================================================
# ====================================================================
__SPL_M_NOSYNC__ = 'sync-none'                    # This type of objects are not sync
__SPL_M_MINE__ = 'sync-mine'                      # Only modifications done on Master are exported to Slave
__SPL_M_THEIRS__ = 'sync-theirs'                  # Only modifications done on Slave are imported to Master
__SPL_M_BOTH__ = 'sync-both'                      # All modifications done are sync between Master and Slave

# ====================================================================
# Main Available WebServices
# ====================================================================
__SPL_S_PING__ = "Ping"                           # Connexion tests, only to check availabilty & access of remote server
__SPL_S_CONNECT__ = "Connect"                     # Connect to remote and read server informations
__SPL_S_ADMIN__ = "Admin"                         # Global Remote Shop information retrieval
__SPL_S_OBJECTS__ = "Objects"                     # Common Data Transactions
__SPL_S_FILE__ = "Files"                          # Files exchenges functions
__SPL_S_WIDGETS__ = "Widgets"                     # Information Blocks Retieval functions

# ====================================================================
# Webservice : Admin
# ====================================================================
#  Available Functions
# ====================================================================
__SPL_F_GET_INFOS__ = 'infos'                     # Get Server Information (Name, Address and more...)
__SPL_F_GET_OBJECTS__ = 'objects'                 # Get List of Available Objects
__SPL_F_GET_SELFTEST__ = 'selftest'               # Get Result of SelfTest Sequence
__SPL_F_GET_WIDGETS__ = 'widgets'                 # Get List of Available Widgets

# ====================================================================
# Webservice : Objects
# ====================================================================
#  Available Functions
# ====================================================================
__SPL_F_OBJECTS__ = 'Objects'                     # Get List of Available Objects
__SPL_F_COMMIT__ = 'Commit'                       # Commit Object Change on Server
__SPL_F_DESC__ = 'Description'                    # Read Object Description
__SPL_F_FIELDS__ = 'Fields'                       # Read Object Available Fields List
__SPL_F_LIST__ = 'ObjectsList'                    # Read Object List
__SPL_F_IDENTIFY__ = 'Identify'                   # Identify Object by Primary Keys
__SPL_F_GET__ = 'Get'                             # Read Object Data
__SPL_F_SET__ = 'Set'                             # Write Object Data
__SPL_F_DEL__ = 'Delete'                          # Delete An Object

# ====================================================================
# Webservice : File
# ====================================================================
#  Available Functions
# ====================================================================
__SPL_F_ISFILE__ = 'isFile'                       # Check if file exist
__SPL_F_GETFILE__ = 'ReadFile'                    # Download file from slave
__SPL_F_SETFILE__ = 'SetFile'                     # Upload file to slave
__SPL_F_DELFILE__ = 'DeleteFile'                  # Delete file from slave

# ====================================================================
# Webservice : Widgets
# ====================================================================
# Available Functions
# ====================================================================
__SPL_F_WIDGET_LIST__ = 'WidgetsList'             # Get List of Available Widgets
__SPL_F_WIDGET_DEFINITION__ = 'Description'       # Get Widget Definition
__SPL_F_WIDGET_GET__ = 'Get'                      # Get Information
