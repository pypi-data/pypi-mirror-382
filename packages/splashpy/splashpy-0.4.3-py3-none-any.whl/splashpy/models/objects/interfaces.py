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


class ObjectInterface:
    """Common Functions Interfaces for Objects Classes"""

    def __init__(self):
        pass

    # ====================================================================#
    #  Object Definition
    # ====================================================================#

    @abstractmethod
    def description(self):
        """Get Description Array for requested Object Type"""
        raise NotImplementedError("Not implemented yet.")

    @abstractmethod
    def fields(self):
        """
        Return List Of Available Fields for Splash Object
        All data must match with Splash Data Types
        """
        raise NotImplementedError("Not implemented yet.")

    # ====================================================================#
    #  Object CRUD
    # ====================================================================#
    @abstractmethod
    def objectsList(self, filter, params):
        """
        Data That May be Send on Parameters Array
        =>  params["max"]                   Maximum Number of results
        =>  params["offset"]                List Start Offset
        =>  params["sortfield"]             Field name for sort list (Available fields listed below)
        =>  params["sortorder"]             List Order Constrain (Default = ASC)

        Meta Data That Must be Included On Result Array
        =>  response["meta"]["total"]       Total Number of results
        =>  response["meta"]["current"]     Total Number of results
        """
        raise NotImplementedError("Not implemented yet.")

    @abstractmethod
    def get(self, object_id, fields):
        """
        Read Requested Object Data
        Splash will send a list of Fields Ids to Read.
        Objects Class will Retun Data Array Indexed with those Fields Ids
        """
        raise NotImplementedError("Not implemented yet.")

    @abstractmethod
    def set(self, object_id, object_data):
        """
        Update or Create requested Object Data
        Splash Sends an Array of Fields Data to Create or Update
        Data are indexed by Fields Ids
        """
        raise NotImplementedError("Not implemented yet.")

    @abstractmethod
    def delete(self, object_id):
        """
        Delete requested Object
        """
        raise NotImplementedError("Not implemented yet.")

    @abstractmethod
    def getObjectIdentifier(self):
        """
        Return the Identifier of Currently Written Object
        """
        raise NotImplementedError("Not implemented yet.")

    # ====================================================================#
    #  Object Primary Keys Management
    # ====================================================================#

    @abstractmethod
    def getByPrimary(self, keys):
        """
        Identify Object Using Primary Keys
        :param keys: hash
        :return: None|string
        """
        return None

    # ====================================================================#
    #  Object LOCK Management
    # ====================================================================#

    @abstractmethod
    def lock(self, object_id):
        """
        Set Lock for a specific object
        """
        raise NotImplementedError("Not implemented yet.")

    @abstractmethod
    def islocked(self, object_id):
        """
        Get Lock Status for a specific object
        """
        raise NotImplementedError("Not implemented yet.")

    @abstractmethod
    def unlock(self, object_id):
        """
        Delete Current active Lock
        """
        raise NotImplementedError("Not implemented yet.")

    # ====================================================================#
    #  Object FILES Management
    # ====================================================================#

    @abstractmethod
    def getFile(self, path, md5):
        """
        Custom Reading of a File from Local System (Database or any else)
        """
        raise NotImplementedError("Not implemented yet.")
