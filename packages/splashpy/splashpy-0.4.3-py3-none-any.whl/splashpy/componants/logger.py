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

from collections.abc import Iterable

class Logger:
    """Splash Logger: Collect & Return Remote Logs"""

    def __init__(self, debug=False):
        """Init Splash Logger"""
        self.debug = debug
        self.prefix = "Splash Py Client"
        self.msg = []
        self.war = []
        self.err = []
        self.deb = []

    def set_debug(self, debug):
        """
        Setup Debug Mode

        :return self
        """
        self.debug = debug
        return self

    def set_prefix(self, prefix):
        """
        Set Logs Messages Prefix

        :return self
        """
        self.prefix = prefix
        return self

    def notice(self, text ):
        """Add an Debug Message to Log"""
        self.__add("deb", text)
        return True

    def info(self, text ):
        """Add an Info / Success Message to Log"""
        self.__add("msg", text)
        return True

    def warn(self, text):
        """Add an Warning Message to Log"""
        self.__add("war", text)

    def error(self, text):
        """Add an Error Message to Log"""
        self.__add("err", text)
        return False

    def fromException(self, exception, trace=True):
        """Add an Exception to Log"""
        import traceback
        # Detect Error Main Message
        if hasattr(exception, "message"):
            self.__add("err", exception.message)
        else:
            self.__add("err", exception)
        # Detect Error Trace
        if trace:
            self.__add("err", "".join(traceback.TracebackException.from_exception(exception).format()))

        return False

    def dump(self, data, name=None):
        """Dump Data and Add to Logs"""
        from json import dump
        from io import StringIO
        if name is None:
            prefix = "Dump " + str(type(data)) + " : "
        else:
            prefix = name + " " + str(type(data)) + " : "
        if isinstance(data, bool):
            return self.__add("war", prefix + str(data))
        if isinstance(data, int) or isinstance(data, float) or isinstance(data, str):
            return self.__add("war", prefix + str(data))
        try:
            buffer = StringIO()
            dump(data, buffer)
            return self.__add("war", prefix + buffer.getvalue())
        except Exception as exception:
            return self.__add("war", exception)

    def vvv( self, text ):
        if self.debug is True:
            self.__add("deb", text)
        return True

    def clear(self):
        """
        Clear Log Queue

        :return: self
        """
        self.msg = []
        self.war = []
        self.err = []
        self.deb = []
        return self

    def __add( self, msg_type, text ):
        message = "[" + self.prefix + "] " + text.__str__()
        getattr(self, msg_type).append(message)

    def to_logging(self):
        """
        Push All Messages to Logging

        :return self
        """
        import logging

        # Force Logger Level to Show All Messages
        level = logging.getLogger().level
        logging.getLogger().setLevel(logging.DEBUG)

        # Push All Messages to Logger
        for msg in self.msg:
            logging.info(msg)
        # Push All Warnings to Logger
        for war in self.war:
            logging.warning(war)
        # Push All Errors to Logger
        for err in self.err:
            logging.error(err)
        # Push All Debug to Logger
        for deb in self.deb:
            logging.debug(deb)

        # Restore Logger Level
        logging.getLogger().setLevel(level)
        return self


    def export( self ):
        """Export All Messages for Messages Packing"""
        # Init Response
        logs = { "msg": {}, "war": {}, "err": {}, "deb": {} }
        # Add All Messages
        for index, text in enumerate(self.msg):
            logs['msg']['msg-'+index.__str__()] = text
        # Add All Warnings
        for index, text in enumerate(self.war):
            logs['war']['war-'+index.__str__()] = text
        # Add All Errors
        for index, text in enumerate(self.err):
            logs['err']['err-'+index.__str__()] = text
        # Add All Debug
        for index, text in enumerate(self.deb):
            logs['deb']['deb-'+index.__str__()] = text

        return logs

    def append(self, raw_logs):
        """Import All Messages from Splash Message"""

        # Import All Messages
        if 'msg' in raw_logs and isinstance(raw_logs['msg'], Iterable):
            for message in raw_logs['msg']:
                getattr(self, "msg").append(raw_logs['msg'][message])
        # Import All Warnings
        if 'war' in raw_logs and isinstance(raw_logs['war'], Iterable):
            for message in raw_logs['war']:
                getattr(self, "war").append(raw_logs['war'][message])
        # Import All Errors
        if 'err' in raw_logs and isinstance(raw_logs['err'], Iterable):
            for message in raw_logs['err']:
                getattr(self, "err").append(raw_logs['err'][message])
        # Import All Debug
        if 'deb' in raw_logs and isinstance(raw_logs['deb'], Iterable):
            for message in raw_logs['deb']:
                getattr(self, "deb").append(raw_logs['deb'][message])

    def on_fault(self, soap_fault):
        """Import Error Message from Soap Fault"""
        getattr(self, "err").append(soap_fault.faultstring)

    def to_html(self,  clean=False):
        """
        Return All WebServer current Log WebServer in Html format
        :param clean: bool
        :return: str
        """
        from splashpy.helpers import HtmlLogExporter
        raw_html = HtmlLogExporter.to_html(self.export())
        if clean:
            self.clear()
        return raw_html

    def to_html_list(self,  clean=False):
        """
        Return All WebServer current Log WebServer in Html Checklist format
        :param clean: bool
        :return: str
        """
        from splashpy.helpers import HtmlLogExporter
        raw_html = HtmlLogExporter.to_html_list(self.export())
        if clean:
            self.clear()
        return raw_html


if __name__ == "__main__":
    # import logging

    logger = Logger()
    logger.info("Test Info Message")
    logger.error("Test Error Message")
    logger.warn("Test Warning Message")
    logger.vvv("Test Debug Message")

    # print logger.msg

    logger.to_logging()

    print (logger.export())
