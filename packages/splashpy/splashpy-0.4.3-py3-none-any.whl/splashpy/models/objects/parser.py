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

from datetime import date, datetime
from splashpy.core.framework import Framework
from splashpy import const


class SimpleFields:

    def __getSimpleValue(self, index, field_id, target=None):
        """Read Simple Raw Field Value"""
        try:
            # ====================================================================#
            # Get attribute value
            value = getattr(target if target is not None else self.object, field_id)

            # ====================================================================#
            # Mark Field as Processed
            self._in.__delitem__(index)
        except Exception as exception:
            # ====================================================================#
            # Log Error if not in Debug Mode
            if not Framework.isDebugMode():
                Framework.log().fromException(exception)
            return None

        return value

    def __setSimpleValue(self, field_id, field_data, target=None):
        """Write Simple Raw Field Value"""
        try:
            # ====================================================================#
            # Get current attribute value before change
            current_value = getattr(target if target is not None else self.object, field_id)

            # ====================================================================#
            # Only set if attribute value has changed
            if current_value != field_data:
                if target is None:
                    setattr(self.object, field_id, field_data)
                else:
                    setattr(target, field_id, field_data)

            # ====================================================================#
            # Mark Field as Processed
            self._in.__delitem__(field_id)
        except Exception as exception:
            return Framework.log().fromException(exception)

    def getSimple(self, index, field_id, target=None):
        """Read Simple Raw Field"""
        self._out[field_id] = self.__getSimpleValue(index, field_id, target)

    def setSimple( self, field_id, field_data, target=None ):
        """Read Simple Raw Field"""
        self.__setSimpleValue(field_id, field_data, target)

    def getSimpleStr( self, index, field_id, target=None ):
        """Read Simple String Field"""
        value = self.__getSimpleValue(index, field_id, target)
        if value is None or value is False:
            value = ""
        self._out[field_id] = str(value)

    def setSimpleBool( self, field_id, field_data, target=None ):
        """Write Simple Bool Field"""
        if not isinstance(field_data, bool) and field_data == "0":
            field_data = False
        self.__setSimpleValue(field_id, bool(field_data), target)

    def getSimpleDate( self, index, field_id, target=None ):
        """Read Simple Date Field"""
        value = self.__getSimpleValue(index, field_id, target)
        if isinstance(value, datetime) or isinstance(value, date):
            self._out[field_id] = value.strftime(const.__SPL_T_DATECAST__)
        else:
            self._out[field_id] = ""

    def setSimpleDate( self, field_id, field_data, target=None ):
        """Write Simple Date Field"""
        if field_data is None:
            return self.__setSimpleValue(field_id, None, target)
        try:
            field_date = datetime.strptime(field_data, const.__SPL_T_DATECAST__).date()
        except Exception as exception:
            return Framework.log().fromException(exception)
        self.__setSimpleValue(field_id, field_date, target)

    def getSimpleDateTime( self, index, field_id, target=None ):
        """Read Simple DateTime Field"""
        value = self.__getSimpleValue(index, field_id, target)
        if isinstance(value, datetime) or isinstance(value, date):
            self._out[field_id] = value.strftime(const.__SPL_T_DATETIMECAST__)
        else:
            self._out[field_id] = ""

    def setSimpleDateTime( self, field_id, field_data, target=None ):
        """Write Simple DateTime Field"""
        if field_data is None:
            return self.__setSimpleValue(field_id, None, target)
        try:
            field_date = datetime.strptime(field_data, const.__SPL_T_DATETIMECAST__)
        except ValueError:
            return Framework.log().error("Invalid DateTime: " + field_data)
        except Exception as exception:
            return Framework.log().fromException(exception)

        self.__setSimpleValue(field_id, field_date, target)

class GenericFields(SimpleFields):

    def __getSimpleValue( self, index, field_id, target=None ):
        """Read Generic Raw Field Value"""
        try:
            if target is None:
                value = self.object.get(field_id)
            else:
                value = target.get(field_id)
            self._in.__delitem__(index)
        except Exception as exception:
            Framework.log().fromException(exception)
            return None

        return value

    def __setSimpleValue(self, field_id, field_data, target=None):
        """Write Simple Raw Field Value"""
        try:
            if target is None:
                self.object.set(field_id, field_data)
            else:
                target.set(field_id, field_data)
            self._in.__delitem__(field_id)
        except Exception as exception:
            return Framework.log().fromException(exception)
