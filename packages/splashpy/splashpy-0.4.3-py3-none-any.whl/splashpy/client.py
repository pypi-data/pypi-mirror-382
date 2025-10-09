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

from splashpy import const, Framework
from splashpy.componants import unpack, pack
from splashpy.soap.client import SoapClient, SoapFault


class SplashClient(Framework):

    # Splash Soap Client
    __soap_client = None

    # List of all Commits done inside this current session
    __commited = []

    def ping(self):
        """
        Ping Splash Server, No Encryption, Just Say Hello!!

        :rtype: bool
        """

        # Create Soap Client
        soap_client = self.__get_client()
        wsId, wsKey, wsHost = self.config().identifiers()

        # Execute Ping Request
        try:
            soap_response = soap_client.Ping(id=wsId, data="test")
        # Catch Potential Errors
        except SoapFault as fault:
            Framework.log().on_fault(fault)
            return False
        except Exception as exception:
            Framework.log().fromException(exception)
            return False

        # Decode Response
        ping_response = unpack(soap_response.children().children().children().__str__(), False)

        # Verify Response
        if ping_response is False:
            return False

        return ping_response["result"] == "1"

    def connect(self):
        """
        Connect Splash Server, With Encryption, Just Say Hello!!

        :rtype: bool
        """

        # Create Soap Client
        soap_client = self.__get_client()
        wsId, wsKey, wsHost = self.config().identifiers()
        # Execute Connect Request
        try:
            soap_response = soap_client.Connect(id=wsId, data=pack({"connect": True}))
        # Catch Potential Errors
        except SoapFault as fault:
            Framework.log().on_fault(fault)
            return False
        except Exception as exception:
            Framework.log().fromException(exception)
            return False
        # Decode Response
        connect_response = unpack(soap_response.children().children().children().__str__())

        # Verify Response
        if connect_response is False:
            return False

        return connect_response["result"] == "1"

    def commit(self, object_type, object_ids = None, action = None, user = None, comment = None):
        """
        Submit an Update for a Local Object

        :param object_type: str             Object Type Name
        :param object_ids: str|int|list     Object Local Id or Array of Local Id
        :param action: str                  Action Type (SPL_A_UPDATE, or SPL_A_CREATE, or SPL_A_DELETE)
        :param user: str
        :param comment: str

        :rtype: bool
        """

        # ====================================================================
        # Verify this Object Class is Valid ==> No Action on this Node
        if not Framework.getObject(object_type):
            Framework.log().warn("Object "+object_type+" Not Found => Commit Skipped")
            Framework.log().to_logging().clear()
            return True
        # ====================================================================
        # Initiate Tasks parameters array
        params = SplashClient.__get_commit_parameters(object_type, object_ids, action, user, comment)
        # ====================================================================
        # Add This Commit to Session Logs
        SplashClient.__commited.append(params)
        # ====================================================================
        # Verify if Server Mode (Soap Request) ==> No Commit Allowed
        if Framework.isServerMode():
            Framework.log().notice("Server Mode => Commit Skipped")
            return False
        # ====================================================================
        # Verify this Object is Locked ==> No Action on this Node
        if not SplashClient.is_commit_allowed(object_type, object_ids, action):
            Framework.log().notice('Module Commit Skipped (' + object_type + ', ' + action + ')')
            return True
        # ====================================================================//
        # Create Soap Client
        soap_client = self.__get_client()
        ws_id, ws_key, ws_host = self.config().identifiers()
        # ====================================================================#
        # Initiate File Request Contents
        request = {
            "tasks": {
                "task": {
                    "id": 1,
                    "name": const.__SPL_F_COMMIT__,
                    "desc": "Commit changes from Python Module",
                    "params": params,
                }
            }
        }
        # ====================================================================//
        # Execute Commit Request
        try:
            soap_response = soap_client.Objects(id=ws_id, data=pack(request))
        # Catch Potential Errors
        except SoapFault as fault:
            Framework.log().on_fault(fault)
            Framework.log().to_logging().clear()
            return False
        except Exception as exception:
            Framework.log().fromException(exception)
            Framework.log().to_logging().clear()
            return False
        # Decode Response
        commit_response = unpack(soap_response.children().children().children().__str__())
        # Push Logs to Console
        Framework.log().to_logging().clear()
        # Verify Response
        if commit_response is False:
            return False

        return commit_response

    def file(self, request):
        """Send File Request to Splash Server"""
        # Create Soap Client
        soap_client = self.__get_client()
        wsId, wsKey, wsHost = self.config().identifiers()
        # Execute Connect Request
        try:
            soap_response = soap_client.Files(id=wsId, data=pack(request))
        # Catch Potential Errors
        except SoapFault as fault:
            Framework.log().on_fault(fault)
            return False
        except Exception as exception:
            Framework.log().fromException(exception)
            return False
        # Decode Response
        connect_response = unpack(soap_response.children().children().children().__str__())

        # Verify Response
        if connect_response is False:
            return False

        return connect_response

    def __get_client(self):
        """
        Build Soap Client with Host Configuration

        :rtype: SoapClient
        """
        if not isinstance(self.__soap_client, SoapClient):
            wsId, wsKey, wsHost = self.config().identifiers()
            self.__soap_client = SoapClient(
                location=wsHost, ns=False, exceptions=True,
                soap_server="jetty",
                http_headers={
                    'Content-type': 'application/x-www-form-urlencoded',
                }
            )

        return self.__soap_client

    @staticmethod
    def __get_commit_parameters(object_type, object_ids=None, action=None, user=None, comment=None):
        """
        Build Call Parameters Array

        :param object_type: str             Object Type Name
        :param object_ids: str|int|list     Object Local Id or Array of Local Id
        :param action: str                  Action Type (SPL_A_UPDATE, or SPL_A_CREATE, or SPL_A_DELETE)
        :param user: str
        :param comment: str

        :rtype: dict
        """
        return {
            'type':  str(object_type),
            'id':    object_ids if isinstance(object_ids, list) else [ str(object_ids) ],
            'action': str(action),
            'user':     str(user),
            'comment': str(comment),
        }

    @staticmethod
    def is_commit_allowed(object_type, object_ids=None, action=None):
        """
        Check if Commit is Allowed Local Object

        :param object_type: str             Object Type Name
        :param object_ids: str|int|list     Object Local Id or Array of Local Id
        :param action: str                  Action Type (SPL_A_UPDATE, or SPL_A_CREATE, or SPL_A_DELETE)

        :rtype: bool
        """
        # ====================================================================
        # Verify if Server Mode (Soap Request) ==> No Commit Allowed
        if Framework.isServerMode():
            return False
        # ====================================================================
        # Verify this Object is Locked ==> No Action on this Node
        if isinstance(object_ids, list):
            for object_id in object_ids:
                if Framework.getObject(object_type).islocked(object_id):
                    return False
        elif Framework.getObject(object_type).islocked(object_ids):
            return False
        # ====================================================================
        # Verify Create Object is Locked ==> No Action on this Node
        if (const.__SPL_A_CREATE__ is action) and Framework.getObject(object_type).islocked():
            return False
        # ====================================================================//
        # Verify if Travis Mode (PhpUnit) ==> No Commit Allowed
        return not SplashClient.is_travis_mode(object_type, action)

    @staticmethod
    def is_travis_mode(object_type, action=None):
        """
        Check if Commit we Are in Travis Mode

        :param object_type: str             Object Type Name
        :param action: str                  Action Type (SPL_A_UPDATE, or SPL_A_CREATE, or SPL_A_DELETE)

        :rtype: bool
        """
        # ====================================================================
        # Detect Travis from Framework
        if not Framework.isDebugMode():
            return False

        return True

    @staticmethod
    def getInstance():
        """
        Safe Access to Splash WebService Client

        :rtype: SplashClient
        """
        wsId, wsKey, wsHost = Framework.config().identifiers()

        return SplashClient(wsId, wsKey, None, None, Framework.getClientInfo(), Framework.getServerDetails(), Framework.config())


if __name__ == "__main__":
    import sys

    client = SplashClient("ThisIsSplashWsId", "ThisIsYourEncryptionKeyForSplash")
    client.config().force_host("http://localhost:8008/")

    if '--ping' in sys.argv:
        if client.ping() is True:
            print("Ping Test =>> Success")
        else:
            print("Ping Test =>> Fail")

        client.log().to_logging()

    if '--connect' in sys.argv:
        if client.connect() is True:
            print("Connect Test =>> Success")
        else:
            print("Connect Test =>> Fail")

        client.log().to_logging()
