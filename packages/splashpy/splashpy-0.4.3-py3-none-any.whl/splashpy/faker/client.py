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

from splashpy.models.client import ClientInfo


class FakerClient(ClientInfo):
    """Define General Information about this Splash Client"""

    def __init__( self ):
        pass

    def complete(self):
        # Use Default Icons Set
        self.loadDefaultIcons()

        # ====================================================================#
        # Override Info to Says we are Faker Mode
        self.short_desc = "Splash Py sFake Client"
        self.long_desc = "Fake Client for Testing purpose Only..."

        # ====================================================================#
        # Company Information
        self.company = "Splash Sync"
        self.address = "Street Address"
        self.zip = "12345"
        self.town = "Town"
        self.country = "Country"
        self.www = "www.splashsync.com"
        self.email = "contact@splashsync.com"
        self.phone = "060606060"
