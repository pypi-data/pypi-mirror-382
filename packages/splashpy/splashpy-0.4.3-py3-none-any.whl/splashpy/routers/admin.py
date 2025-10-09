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
from splashpy.routers.base import BaseRouter
from splashpy.core.framework import Framework


class AdminRouter(BaseRouter):

    def execute(self, task):

        response = self.empty_response(task)

        # READING OF SERVER OBJECT LIST
        if task['name'] == const.__SPL_F_GET_OBJECTS__:
            response['data'] = Framework.getObjects()
            response['result'] = True

        # READING OF SERVER WIDGETS LIST
        if task['name'] == const.__SPL_F_GET_WIDGETS__:
            response['data'] = {}
            response['result'] = True

        # READING OF SERVER SELFTEST RESULTS
        if task['name'] == const.__SPL_F_GET_SELFTEST__:
            response['data'] = True
            response['result'] = True

        # READING OF SERVER INFORMATIONS
        if task['name'] == const.__SPL_F_GET_INFOS__:
            response['data'] = Framework.getClientInfo().get()
            response['result'] = True

        return response
