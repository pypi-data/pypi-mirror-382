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

import logging


class WerkzeugHelper():

    @staticmethod
    def is_installed():
        try:
            from werkzeug.wrappers import Request
        except ImportError:
            logging.warning("Werkzeug module not found on server...")
            return False
        return True

    @staticmethod
    def is_valid_request(request):
        from werkzeug.wrappers import Request

        return isinstance(request, Request)