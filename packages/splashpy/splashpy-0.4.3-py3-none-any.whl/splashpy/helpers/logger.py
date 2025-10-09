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


class HtmlLogExporter:
    """Splash Logger: Html Exports Management"""

    @staticmethod
    def to_html(logs):
        """
        Return All WebServer current Log WebServer in Html format
        :param logs: dict
        :return: str
        """
        raw_html = ""
        # ====================================================================#
        # Read All Messages as Html
        raw_html += HtmlLogExporter.get_html_block(logs["err"], 'Errors', '#FF3300')
        raw_html += HtmlLogExporter.get_html_block(logs["war"], 'Warning', '#FF9933')
        raw_html += HtmlLogExporter.get_html_block(logs["msg"], 'Messages', '#006600')
        raw_html += HtmlLogExporter.get_html_block(logs["deb"], 'Debug', '#003399')
        return raw_html

    @staticmethod
    def to_html_list(logs):
        """
        Return All WebServer current Log WebServer in Html Checklist format
        :param logs: dict
        :return: str
        """
        raw_html = ""
        # ====================================================================#
        # Read All Messages as Html
        raw_html += HtmlLogExporter.get_html_list_block(logs["err"], 'Error')
        raw_html += HtmlLogExporter.get_html_list_block(logs["war"], 'Warning')
        raw_html += HtmlLogExporter.get_html_list_block(logs["msg"], 'Message')
        raw_html += HtmlLogExporter.get_html_list_block(logs["deb"], 'Debug')
        return raw_html

    @staticmethod
    def get_html_block(messages, title='', color='#000000'):
        """
        Return WebServer Log Block in Html format
        :param messages: dict
        :param title: str
        :param color: str
        :return: str
        """
        raw_html = '<font color="'+color+'">'
        if isinstance(messages, dict):
            if len(str(title)) > 0:
                raw_html += '<u><b>'+str(title)+'</b></u></br> '
            for text in messages.values():
                raw_html += str(text)+'</br>'

        return raw_html + '</font>'

    @staticmethod
    def get_html_list_block(messages, msg_type):
        """
        Return WebServer Log Block in Html Checklist format
        :param messages: dict
        :param msg_type: str
        :return: str
        """
        # ====================================================================#
        # Setup Result Text & Color
        if msg_type == "Error":
            color = '#FF3300'
            status = '&nbsp;KO&nbsp;'
        elif msg_type == 'Warning':
            color = '#FF9933'
            status = '&nbsp;WAR&nbsp;'
        else:
            color = '#006600'
            status = '&nbsp;OK&nbsp;'
        # ====================================================================#
        # Parse Items
        raw_html = ""
        if isinstance(messages, dict):
            for text in messages.values():
                raw_html += '[<font color="'+color+'">'+status+'</font>]&nbsp;&nbsp;&nbsp;'+str(text)+'</br>'

        return raw_html
