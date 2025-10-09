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
from splashpy.core.framework import Framework
from splashpy.soap.server import HTTPServer, SoapDispatcher, SOAPHandler, SoapFault
from splashpy.componants.encoder import unpack, pack
from splashpy.routers import AdminRouter, ObjectsRouter, WidgetsRouter, FilesRouter


class SplashServer(Framework):

    __dispatcher = None
    __inputs = None
    __outputs = None

    def ping( self, param0, param1):
        """Ping Splash Server"""
        # Clean Logs
        self.log().clear()
        # Add Log Message
        self.log().info("Ping Successful.")
        # Return Unsecured Response
        return pack({'result': True}, False)

    def connect( self, param0, param1):
        """Connect Splash Server"""
        # Receive Message
        message = self.__receive(param0, param1)
        if message is False:
            return SoapFault(0, "Internal Server Error")
        # Add Log Message
        self.log().info("Connection Successful.")
        # Return Secured Response
        return pack({'result': True})

    def admin(self, param0, param1):
        """Serve Admin Request from Splash Server"""
        # Return Router Response
        return self.__run(AdminRouter(), param0, param1)

    def objects(self, param0, param1):
        """Serve Objects Request from Splash Server"""
        # Return Router Response
        return self.__run(ObjectsRouter(), param0, param1)

    def widgets(self, param0, param1):
        """Serve Widgets Request from Splash Server"""
        # Return Router Response
        return self.__run(WidgetsRouter(), param0, param1)

    def files(self, param0, param1):
        """Serve Files Request from Splash Server"""
        # Return Router Response
        return self.__run(FilesRouter(), param0, param1)

    def serve(self):
        httpd = HTTPServer(("", 8008), SOAPHandler)
        httpd.dispatcher = self.__get_server()
        httpd.serve_forever()

    def fromWerkzeug(self, request, complete=True):
        """Handle Werkzeug Requests"""
        from splashpy.componants.werkzeug import WerkzeugHelper

        # Verify Werkzeug is Installed
        if not WerkzeugHelper.is_installed():
            return False
        # Verify Request Format
        if not WerkzeugHelper.is_valid_request(request):
            return False
        # Complete Server Info from Request
        if complete:
            self.getServerDetails().loadWerkzeugInformation(request)
        # POST >> Handle Soap Request
        if request.method == 'POST':
            Framework.setServerMode(True)
            return self.__get_server().dispatch(str(request.data, 'UTF-8'))
        # POST >> Handle Soap Request
        if "node" in request.args:
            # Load Server Info
            wsId, wsKey, wsHost = self.config().identifiers()
            if request.args["node"] == wsId:
                return "TODO: Show Server Debug Information"

        return "This Server Provide no Description"

    def __get_server( self ):
        """Build Soap Server with Host Configuration"""
        if self.__dispatcher is None:
            # ====================================================================#
            # Create Soap Actions Dispatcher
            self.__dispatcher = SoapDispatcher(
                name="SplashPyServer",
                documentation='This webservice provide no description',
                debug=True,
                ns=True
            )
            # ====================================================================#
            # Ping Service
            self.__dispatcher.register_function(
                const.__SPL_S_PING__, self.ping,
                # returns={'return': str}, args={'id': str, 'data': str}
                returns={'return': str}, args={'param0': str, 'param1': str}
            )
            # ====================================================================#
            # Connect Service
            self.__dispatcher.register_function(
                const.__SPL_S_CONNECT__, self.connect,
                returns={'return': str}, args={'param0': str, 'param1': str}
            )
            # ====================================================================#
            # Admin Service
            self.__dispatcher.register_function(
                const.__SPL_S_ADMIN__, self.admin,
                returns={'return': str}, args={'param0': str, 'param1': str}
            )
            # ====================================================================#
            # Objects Service
            self.__dispatcher.register_function(
                const.__SPL_S_OBJECTS__, self.objects,
                returns={'return': str}, args={'param0': str, 'param1': str}
            )
            # ====================================================================#
            # Widgets Service
            self.__dispatcher.register_function(
                const.__SPL_S_WIDGETS__, self.widgets,
                returns={'return': str}, args={'param0': str, 'param1': str}
            )
            # ====================================================================#
            # Files Service
            self.__dispatcher.register_function(
                const.__SPL_S_FILE__, self.files,
                returns={'return': str}, args={'param0': str, 'param1': str}
            )

        return self.__dispatcher

    def __receive(self, id, data):
        # Load Server Info
        wsId, wsKey, wsHost = self.config().identifiers()
        # Verify Server Id
        if id != wsId:
            import logging
            logging.warning("Wrong server Id...")
            return False
        # Clean Logs
        self.log().clear()
        # Unpack Message
        return unpack(data)

    def __run( self, router, id, data ):
        """Execute Routers Actions"""
        # Receive Message
        self.__inputs = self.__receive(id, data)
        self.__outputs = {}
        if self.__inputs is False:
            return SoapFault(0, "Internal Server Error")
        # Detect Debug Mode
        if "debug" in self.__inputs and self.__inputs["debug"] == "1":
            Framework.setDebugMode(True)
        # Execute Router Tasks
        try:
            result = router.run(self.__inputs, self.__outputs)
        except Exception as exception:
            result = Framework.log().fromException(exception)
        # Push Server Log to Console
        self.log().to_logging()
        # Return Router Response
        return self.__transmit(result)

    def __transmit(self, result):
        """Return Tasks Results"""
        # Add Global Result
        self.__outputs['result'] = result
        # print "Tasks Outputs:", self.__outputs
        # Return packaged response
        return pack(self.__outputs)


if __name__ == "__main__":
    import sys
    import logging

    if '--serve' in sys.argv:
        from peewee import SqliteDatabase
        from splashpy.faker.short import Short, ShortData
        from splashpy.faker.primary import Primary, PrimaryData
        from splashpy.faker.client import FakerClient
        from splashpy.templates.widgets import Dummy, Basic, Morris
        from splashpy.models.server import ServerInfo

        logging.warning("Starting Sqlite Database...")
        fakerDb = SqliteDatabase('faker.db')
        fakerDb.create_tables([ShortData, PrimaryData])

        logging.warning("Starting server...")
        server = SplashServer(
            "ThisIsSplashWsId"+str(sys.version_info.major)+"p"+str(sys.version_info.minor),
            "ThisIsYourEncryptionKeyForSplash",
            [Short(), Primary()],
            [Dummy(), Basic(), Morris()],
            info=FakerClient(),
            server=ServerInfo({
                "server_host":"http://localhost:8008",
                "server_path":"/"
            })
        )

        server.serve()
