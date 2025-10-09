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


class ObjectsRouter(BaseRouter):
    """Objects WebService Actions Router"""

    def execute(self, task):
        """Execute Objects Actions"""
        response = self.empty_response(task)

        # READING OF SERVER OBJECT LIST
        if task['name'] == const.__SPL_F_OBJECTS__:
            response['data'] = Framework.getObjects()
            response['result'] = True
            return response

        # Validate Received Task
        if not self.isValidTask(task):
            return response

        # Execute Admin Actions
        if task['name'] in [const.__SPL_F_DESC__, const.__SPL_F_FIELDS__, const.__SPL_F_LIST__]:
            return self.doAdminActions(task)

        # Execute Sync Actions
        if task['name'] in [const.__SPL_F_GET__, const.__SPL_F_SET__, const.__SPL_F_DEL__]:
            return self.doSyncActions(task)

        # Execute Primary Actions
        if task['name'] in [const.__SPL_F_IDENTIFY__]:
            return self.doPrimaryActions(task)

        # Wrong Request Task
        Framework.log().error("Object Router - Requested task not found => " + task['name'])

        return response

    def doAdminActions(self, task):
        """Execute Admin Objects Actions"""
        response = self.empty_response(task)
        # Load Object Class
        ws_object = Framework.getObject(task["params"]['type'])

        # READING OF OBJECT DESCRIPTION
        if task['name'] == const.__SPL_F_DESC__:
            if ws_object:
                response['data'] = ws_object.description()
                response['result'] = bool(response['data'].__len__())

        # READING OF OBJECT FIELDS
        if task['name'] == const.__SPL_F_FIELDS__:
            if ws_object:
                response['data'] = ws_object.fields()
                response['result'] = bool(response['data'].__len__())

        # READING OF OBJECTS LIST
        if task['name'] == const.__SPL_F_LIST__:
            try:
                filters = task["params"]["filters"]
            except:
                filters = None
            try:
                parameters = task["params"]["params"]
            except:
                parameters = None
            if ws_object:
                response['data'] = ws_object.objectsList(filters, parameters)
                response['result'] = bool(response['data'].__len__())

        return response

    def doSyncActions( self, task ):
        """Execute Admin Objects Actions"""
        from splashpy.componants.validator import Validator
        response = self.empty_response(task)
        # Load Object Class
        ws_object = Framework.getObject(task["params"]['type'])
        ws_object_id = task["params"]['id']

        # Verify Object Id
        if not Validator.isValidObjectId(ws_object_id):
            return response

        # READING OF OBJECT DATA
        if task['name'] == const.__SPL_F_GET__:
            ws_fields = task["params"]['fields']
            if ws_object and Validator.isValidObjectFieldsList(ws_fields):
                response['data'] = ws_object.get(ws_object_id, ws_fields)
                response['result'] = (response['data'] != False)

        # WRITING OF OBJECT DATA
        if task['name'] == const.__SPL_F_SET__:
            ws_fields = task["params"]['fields']
            if ws_object and Validator.isValidObjectFieldsList(ws_fields):
                # Take Lock for this object => No Commit Allowed for this Object
                ws_object.lock(ws_object_id)
                # Write Data on local system
                response['data'] = ws_object.set(ws_object_id, ws_fields)
                # Release Lock for this object
                ws_object.unlock(ws_object_id)
                response['result'] = (response['data'] != False)

        # DELETE OBJECT
        if task['name'] == const.__SPL_F_DEL__:
            if ws_object:
                # Take Lock for this object => No Commit Allowed for this Object
                ws_object.lock(ws_object_id)
                response['data'] = ws_object.delete(ws_object_id)
                response['result'] = response['data']

        return response

    def doPrimaryActions(self, task):
        """Execute Admin Objects Actions"""
        from splashpy.componants.validator import Validator
        response = self.empty_response(task)
        # Load Object Class
        ws_object = Framework.getObject(task["params"]['type'])

        # IDENTIFY OF OBJECT BY PRIMARY KEY
        if task['name'] == const.__SPL_F_IDENTIFY__:
            keys = task["params"]['keys']
            if ws_object and Validator.isValidObjectFieldsList(keys):
                try:
                    response['data'] = ws_object.getByPrimary(keys)
                    response['result'] = True
                except Exception as exception:
                    Framework.log().fromException(exception, False)

        return response

    @staticmethod
    def isValidTask(task):
        """Verify Received Task"""
        # Verify Requested Object Type is Available
        if not hasattr(task["params"], '__iter__'):
            return Framework.log().error("Object Router - Missing Task Parameters... ")
        # Verify Requested Object Type is Available
        if 'type' not in task["params"]:
            return Framework.log().error("Object Router - Missing Object Type... ")
        # Verify Requested Object Type is Valid
        if not task["params"]['type'] in Framework.getObjects():
            return Framework.log().error("Object Router - Object Type is Invalid... ")

        return True
