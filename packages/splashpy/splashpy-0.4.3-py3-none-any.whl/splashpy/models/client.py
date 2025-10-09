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

from abc import abstractmethod
from splashpy import const
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable


class ClientInfo:
    """Define General Information about this Splash Client"""

    # ====================================================================#
    # Server General Description
    short_desc = const.__NAME__
    long_desc = const.__DESC__

    # ====================================================================#
    # Company Information
    company = ""
    address = ""
    zip = ""
    town = ""
    country = ""
    www = ""
    email = ""
    phone = ""

    # ====================================================================#
    # Server Logo & Images
    ico_raw = ""
    logo_url = ""
    logo_raw = ""

    # ====================================================================#
    # Server Information
    server_type = const.__NAME__
    server_url = "localhost"

    # ====================================================================#
    # Module Informations
    module_author = const.__AUTHOR__
    module_version = const.__VERSION__

    def __init__(self, info=False):
        """Init Base Configuration if Given"""
        # No Init Data Provided
        if info is False or not isinstance(info, Iterable):
            return
        # Walk on Any Iterable Object to Add Child Elements
        for key, value in info.items():
            self.__setattr__(key, value)

    def loadDefaultIcons(self):
        """Override this function to change Client Server Icons"""
        from splashpy.componants.files import Files
        self.ico_raw = Files.getRawContents(Files.getAssetsPath() + "/img/python.ico")
        self.logo_raw = Files.getRawContents(Files.getAssetsPath() + "/img/python.png")

    @abstractmethod
    def complete(self):
        """Override this function to complete Client Information Dynamically"""
        self.loadDefaultIcons()

        return

    @abstractmethod
    def get(self):
        """Detect & Return Client Information"""
        self.complete()

        return {
            # Server General Description
            "shortdesc": self.short_desc,
            "longdesc": self.long_desc,
            # Company Information
            "company": self.company,
            "address": self.address,
            "zip": self.zip,
            "town": self.town,
            "country": self.country,
            "www": self.www,
            "email": self.email,
            "phone": self.phone,
            # Server Logo & Images
            "icoraw": self.ico_raw,
            "logourl": self.logo_url,
            "logoraw": self.logo_raw,
            # Server Information
            "servertype": self.server_type,
            "serverurl": self.server_url,
            # Module Information
            "moduleauthor": self.module_author,
            "moduleversion": self.module_version,
        }




