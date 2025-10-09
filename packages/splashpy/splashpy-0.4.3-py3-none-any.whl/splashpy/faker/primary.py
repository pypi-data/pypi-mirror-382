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

from peewee import *
import datetime
from splashpy import const
from splashpy.componants.fieldfactory import FieldFactory
from splashpy.faker.model import FakeObject
from splashpy.core.framework import Framework

fakerDb = SqliteDatabase('faker.db')


class PrimaryData(Model):
    # ====================================================================#
    # Faker Object Model
    primary = CharField(default="")
    varchar = CharField(default="")
    varchar2 = CharField(default="")
    bool = BooleanField(default=False)
    integer = IntegerField(default=0)
    date = DateField(default=datetime.datetime.now)
    datetime = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = fakerDb


class Primary(FakeObject):
    # ====================================================================#
    # Splash Object Definition
    name = "Primary"
    desc = "Py Core Faker Primary Object"
    icon = "fa fa-search"

    def __init__( self ):
        pass

    @staticmethod
    def getObjectClass():
        return PrimaryData

    @staticmethod
    def toListData(faker_object ):
        """Get Class of Faker Object"""
        return {
            'id': str(faker_object.id),
            'primary': faker_object.primary,
            'varchar': faker_object.varchar,
            'date': faker_object.date.__str__()
        }

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create( self ):
        """Create a Faker Object """
        try:
            return PrimaryData.create(primary=self._in["primary"])
        except Exception as exception:
            return Framework.log().error(exception)

    # ====================================================================#
    # Field Parsing Functions
    # ====================================================================#

    def buildCoreFields(self):

        # ====================================================================#
        # Primary
        FieldFactory.create(const.__SPL_T_VARCHAR__, "primary", "Primary Key")
        FieldFactory.isListed().isRequired().isPrimary()
        # ====================================================================#
        # Varchar
        FieldFactory.create(const.__SPL_T_VARCHAR__, "varchar", "Varchar 1")
        FieldFactory.isListed().isIndexed()
        # ====================================================================#
        # Varchar 2
        FieldFactory.create(const.__SPL_T_VARCHAR__, "varchar2", "Varchar 2")
        FieldFactory.isIndexed()
        # ====================================================================#
        # Bool
        FieldFactory.create(const.__SPL_T_BOOL__, "bool", "Bool")
        # ====================================================================#
        # Integer
        FieldFactory.create(const.__SPL_T_INT__, "integer", "Integer")
        # ====================================================================#
        # Date
        FieldFactory.create(const.__SPL_T_DATE__, "date", "Date")
        # ====================================================================#
        # DateTime
        FieldFactory.create(const.__SPL_T_DATETIME__, "datetime", "Date Time")

    def getCoreFields(self, index, field_id):

        if field_id in ['primary', 'varchar', 'varchar2']:
            self.getSimpleStr(index, field_id)

        if field_id in ['bool', 'integer']:
            self.getSimple(index, field_id)

        if field_id in ['date']:
            self.getSimpleDate(index, field_id)

        if field_id in ['datetime']:
            self.getSimpleDateTime(index, field_id)

    def setCoreFields(self, field_id, field_data ):

        if field_id in ['primary', 'varchar', 'varchar2', 'integer']:
            self.setSimple(field_id, field_data)

        if field_id in ['bool']:
            self.setSimpleBool(field_id, field_data)

        if field_id in ['date']:
            self.setSimpleDate(field_id, field_data)

        if field_id in ['datetime']:
            self.setSimpleDateTime(field_id, field_data)

    def getByPrimary(self, keys):
        # ====================================================================#
        # Safety Check
        if not hasattr(keys, '__iter__') or 'primary' not in keys:
            return None
        try:
            # ====================================================================#
            # Execute Search by Primary Query
            query = self.getObjectClass().select().limit(5).where(
                (PrimaryData.primary == keys['primary'])
            )
            if query.count() != 1:
                return None
            # ====================================================================#
            # Get First Result ID
            return query.get().id
        except Exception as exception:
            Framework.log().fromException(exception)

        return None
