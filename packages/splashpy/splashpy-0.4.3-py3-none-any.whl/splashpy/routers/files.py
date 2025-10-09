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


class FilesRouter(BaseRouter):

    def execute(self, task):

        response = self.empty_response(task)
        try:
            path = task["params"]["path"]
            md5 = task["params"]["md5"]
        except:
            Framework.log().error("Files Router - Missing Task Parameters... ")

            return response

        # READING A FILE INFORMATIONS
        if task['name'] == const.__SPL_F_ISFILE__:
            response['data'] = False
            response['result'] = True

        # READING A FILE CONTENTS
        if task['name'] == const.__SPL_F_GETFILE__:
            response['data'] = self.get_file(path, md5)
            response['result'] = True

        return response

    def get_file(self, path, md5):
        # Walk for File on All Registered Objects
        for object_type in Framework.getObjects():
            object_class = Framework.getObject(object_type)
            file = object_class.getFile(path, md5)
            # Verify File was Found
            if file is None or not isinstance(file, dict):
                continue
            # Verify File Md5
            if file['md5'] != md5:
                continue

            return file

        Framework.log().error("File Not Found")


        return None
