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
from peewee import *
from splashpy.models.object import BaseObject
from splashpy.core.framework import Framework
from splashpy.models.objects.parser import SimpleFields

fakerDb = SqliteDatabase('faker.db')

class FakeObject(BaseObject, SimpleFields):

    # ====================================================================#
    # Generic Fields Definition
    simpleFields =[]
    boolFields =[]
    intFields =[]

    def __init__( self ):
        pass

    @abstractmethod
    def getObjectClass(self):
        """Get Class of Faker Object"""
        raise NotImplementedError("Not implemented yet.")

    @staticmethod
    def toListData(faker_object):
        """Convert Faker Object to List Data"""
        raise NotImplementedError("Not implemented yet.")

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def load( self, object_id ):
        """Load Faker Object with Id"""
        try:
            return self.getObjectClass().get_by_id(object_id)
        except DoesNotExist:
            return False
        except Exception as exception:
            return Framework.log().error(exception.message)

    def update( self, needed ):
        """Update Current Faker Object"""
        try:
            self.object.save()
            return self.object.id
        except Exception as exception:
            return Framework.log().error(exception)

    def delete( self, object_id ):
        """Delete Faker Object with Id"""
        try:
            fake_object = self.getObjectClass().get_by_id(object_id)
            fake_object.delete_instance()
            return True
        except DoesNotExist:
            return True
        except Exception as exception:
            return Framework.log().error(exception)

    def getObjectIdentifier(self):
        return self.object.id

    def objectsList( self, filter, params ):

        # ====================================================================#
        # Prepare Search Settings
        try:
            limit = params["max"]
        except:
            limit = 25
        try:
            offset = params["offset"]
        except:
            offset = 0
        # ====================================================================#
        # Execute Search Query
        query = self.getObjectClass().select().limit(limit).offset(offset)
        # ====================================================================#
        # Init Results
        objects = {}
        # ====================================================================#
        # Walk on Results
        try:
            for faker_object in query:
                objects["short-" + str(faker_object.id)] = self.toListData(faker_object)
        except Exception as exception:
            Framework.log().error(exception.message)
        # ====================================================================#
        # Add Metadata
        objects['meta'] = {
            'current': query.count(),
            'total': self.getObjectClass().select().count()
        }

        return objects

