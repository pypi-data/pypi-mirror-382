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
import logging


class Config:
    # ====================================================================#
    # Define Module Core Configuration
    # ====================================================================#
    wsIdentifier = None
    wsEncryptionKey = None
    wsTimeout = const.__TIMEOUT__
    wsCrypt = const.__CRYPT_METHOD__
    wsEncode = const.__ENCODE__
    wsHost = const.__HOST__

    # ====================================================================#
    # Various User Configurations
    # ====================================================================#
    lang = const.__LANG__
    smartNotify = const.__SMART_NOTIFY__

    def __init__(self, identifier, key, host=False):
        """Init Base Configuration"""
        self.wsIdentifier = identifier
        self.wsEncryptionKey = key
        if isinstance(host, str):
            self.wsHost = host

    def is_valid(self):
        """Validate Ws Minimal Configuration"""

        # if not isinstance(self.wsIdentifier, (str, unicode)):
        if not isinstance(self.wsIdentifier, str):
            logging.warning("Ws Identifier is Missing")
            return False

        # if not isinstance(self.wsEncryptionKey, (str, unicode)):
        if not isinstance(self.wsEncryptionKey, str):
            logging.warning("Ws Encryption Key is Missing")
            return False

        # if not isinstance(self.wsHost, (str, unicode)):
        if not isinstance(self.wsHost, str):
            logging.warning("Ws Host is Missing")
            return False

        return True

    def identifiers(self):
        return self.wsIdentifier, self.wsEncryptionKey, self.wsHost

    def method(self):
        return self.wsCrypt

    def timeout(self):
        return self.wsTimeout

    def force_host(self, host):
        self.wsHost = host

