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

import hashlib
import base64
import logging
import xml.dom.minidom
from collections.abc import Iterable
from Crypto.Cipher import AES
from splashpy import Framework

def unpack( rawdata, secured=True ):
    """Unpack Received Splash Data to Object"""

    # Decode using correct method
    if secured is True:
        xmlString = Encryption.decrypt(rawdata)
    else:
        xmlString = str(base64.b64decode(rawdata, None, True), 'UTF-8')
    # Verify received message is a string
    if not isinstance(xmlString, str):
        return False
    # Decode Message to Object
    xmlData = XmlManager.to_object(xmlString)

    # Import Logs to Logger
    if 'log' in xmlData:
        Framework.log().append(xmlData['log'])

    return xmlData


def pack(rawdata, secured=True):
    """Package Splash Data before Transmission"""
    # Complete Message with System Information
    rawdata['debug'] = int(Framework.isDebugMode())
    rawdata['verbose'] = int(Framework.isDebugMode())
    # Complete Message with Log
    rawdata['log'] = Framework.log().export()
    # Encode Message to Xml
    xmlString = XmlManager.to_xml(rawdata)
    # Verify message is a string
    if not isinstance(xmlString, str):
        logging.error("Unable to convert Data to Xml")
        return False
    # Encode using correct method
    if secured is True:
        rawMessage = Encryption.encrypt(xmlString)
    else:
        rawMessage = str(base64.b64encode(xmlString.encode()), "UTF-8")

    # Verify message is a string
    if not isinstance(rawMessage, str):
        logging.error("Unable to Encrypt Xml String")
        return False

    return rawMessage


# ====================================================================#
# Encryption: Manage Crypt & Decrypt of Raw Splash Messages
# ====================================================================#
class Encryption:
    """Encrypt & Decrypt Splash Encoded Messages"""

    def __init__( self ):
        pass

    @staticmethod
    def encrypt( data ):
        """Encrypt Splash Messages"""

        # ====================================================================#
        # Safety Checks
        if not Encryption.verify(data):
            return False

        # ====================================================================#
        # Encrypt Data
        if Framework.config().method() == "AES-256-CBC":
            logging.debug("Encrypt using AES-256-CBC Method")
            wsId, wsKey, wsHost = Framework.config().identifiers()
            return AESCipher(wsKey, wsId).encrypt(data)

        return False

    @staticmethod
    def decrypt( data ):
        """Decrypt Splash Messages"""

        # ====================================================================#
        # Safety Checks
        if not Encryption.verify(data):
            return False
        # ====================================================================#
        # Encrypt Data
        if Framework.config().method() == "AES-256-CBC":
            wsId, wsKey, wsHost = Framework.config().identifiers()
            return AESCipher(wsKey, wsId).decrypt(data)

        return False

    @staticmethod
    def verify( data ):
        """Verify Client Configuration & Input Data"""
        # Check Configuration
        if not Framework.config().is_valid():
            return False
        # Check Inputs
        if not isinstance(data, str):
            return False

        return True


# ====================================================================#
# Xml Manager: Manage Encoding & Decoding of Raw Splash Messages
# ====================================================================#
class XmlManager:
    """Convert Objects <<>> Xml"""

    def __init__( self ):
        pass

    @staticmethod
    def to_object( xml_string ):
        """Convert Raw Xml String to mini DOM & Extract Contents as Object"""

        # Parse String to Xml a Extract Contents
        xml_data = xml.dom.minidom.parseString(xml_string).firstChild
        # Verify Splash Contents are here
        if xml_data.nodeName != "SPLASH":
            return False

        # Recursively Convert Contents to Object
        return XmlManager.__to_object(xml_data)

    @staticmethod
    def __to_object( element ):
        """Recursive Decoding of Xml DOM to Object"""

        # Convert Single Text Nodes to String Value
        if element.childNodes.length == 1 and element.firstChild.nodeType is xml.dom.minidom.Node.TEXT_NODE:
            return str(base64.b64decode(element.firstChild.data), "utf-8")

        # If Element has no Child Node
        if element.childNodes.length == 0:
            return None

        # Walk on Child Node Elements
        result = {}
        for child in element.childNodes:
            if child.nodeType is xml.dom.minidom.Node.ELEMENT_NODE:
                result[child.nodeName] = XmlManager.__to_object(child)


        return result

    @staticmethod
    def to_xml( object ):
        """Generate Xml String from Raw Object"""

        # Create a new Xml miniDOM
        xmlDoc = xml.dom.minidom.getDOMImplementation().createDocument(None, "SPLASH", None)
        # Convert Object to Xml DOM
        XmlManager.__to_xml(xmlDoc, xmlDoc.documentElement, object)

        # Return Raw Xml String
        return xmlDoc.toxml()

    @staticmethod
    def __to_xml( xmlDoc, xmlElement, object ):
        """Recursive Encoding Object to Xml DOM"""

        # Add Bool Object
        if isinstance(object, bool):
            if object:
                newNode = xmlDoc.createTextNode(str(base64.b64encode("1".encode()), "utf-8"))
            else:
                newNode = xmlDoc.createTextNode(str(base64.b64encode("0".encode()), "utf-8"))
            xmlElement.appendChild(newNode)
            return

        # Add Int or Float Object
        if isinstance(object, int) or isinstance(object, float):
            newNode = xmlDoc.createTextNode(str(base64.b64encode(str(object).encode()), "utf-8"))
            xmlElement.appendChild(newNode)
            return

        # Add String Object
        if isinstance(object, str):
            newNode = xmlDoc.createTextNode(str(base64.b64encode(object.encode()), "utf-8"))
            xmlElement.appendChild(newNode)
            return

        # Add Bytes Object
        if isinstance(object, bytes):
            newNode = xmlDoc.createTextNode(str(base64.b64encode(object), "utf-8"))
            xmlElement.appendChild(newNode)
            return

        # Walk on List to Add Child Elements
        if isinstance(object, list):
            for key, value in enumerate(object):
                element = xmlDoc.createElement("item-" + key.__str__())
                XmlManager.__to_xml(xmlDoc, element, value)
                xmlElement.appendChild(element)
            return

        # Walk on Any Iterable Object to Add Child Elements
        if isinstance(object, Iterable):
            for key, value in object.items():
                element = xmlDoc.createElement(str(key))
                XmlManager.__to_xml(xmlDoc, element, object[key])
                xmlElement.appendChild(element)
            return


# ====================================================================#
# AES Cipher: Crypt & Decrypt AES 256 OpenSsl Messages
# ====================================================================#
class AESCipher:
    """OpenSsl "Like" AES 256  Cipher"""

    def __init__( self, key, iv ):
        self.key = hashlib.sha256(key.encode('utf-8')).hexdigest()[:32].encode("utf-8")
        self.iv = hashlib.sha256(iv.encode('utf-8')).hexdigest()[:16].encode("utf-8")

    @staticmethod
    def __pad( s ):
        return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

    @staticmethod
    def __unpad( s ):
        return s[0:-ord(s[-1])]

    def encrypt( self, raw ):
        raw = self.__pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return str(base64.b64encode(base64.b64encode(cipher.encrypt(raw.encode()))), "utf-8")

    def decrypt( self, enc ):
        enc = base64.b64decode(base64.b64decode(enc))
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self.__unpad(cipher.decrypt(enc).decode("utf-8"))
