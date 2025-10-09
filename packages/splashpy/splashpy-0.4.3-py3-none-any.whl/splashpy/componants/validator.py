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


class Validator():

    def __init__( self ):
        pass

    @staticmethod
    def isValidObjectId( object_id ):
        # Checks Id is Null
        if object_id is None:
            return True
        # Checks Id is String or Int
        if not isinstance(object_id, (str, int)):
            return False

        return True

    @staticmethod
    def isValidObjectFieldsList( fields ):
        from splashpy.core.framework import Framework
        # Checks List Type
        if not hasattr(fields, '__iter__'):
            return Framework.log().error("Wrong Field List Type")
        # Checks List Not Empty
        if not fields.__len__():
            return Framework.log().error("Field List is Empty")

        return True
