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

import unittest
import random
import string
from splashpy.componants.encoder import *
from splashpy.client import SplashClient

rawIn = "ThisIsForTestingEncryption"
rawOut = "ckVrUmhwNVdsOUFvMXd2N2FJdWkvRW13ako5Zm50MDMxckE1QzRMYWZVVT0="


class EncodingTests(unittest.TestCase):

    # ====================================================================#
    # Encoding & Deciding Tests
    # ====================================================================#
    def testDecode(self):
        """Test Xml Decoding"""
        xmlString = '<?xml version="1.0" ?><SPLASH><result>MQ==</result></SPLASH>'
        rawData = XmlManager.to_object(xmlString)
        print(rawData)
        self.assertEqual('1', rawData["result"])

    def testEncode(self):
        """Test Xml Encoding"""
        rawData = {
            "bool": True,
            "string": "TEST"
        }
        xmlString = XmlManager.to_xml(rawData)
        self.assertEqual('<?xml version="1.0" ?><SPLASH><bool>MQ==</bool><string>VEVTVA==</string></SPLASH>', xmlString)

    def testEncodeDecode(self):
        """Test Xml Encoding & Decoding"""
        rawData = {
            u"string1": "TEST1",
            u"string2": "TEST2"
        }
        xmlString = XmlManager.to_xml(rawData)
        self.assertEqual(rawData, XmlManager.to_object(XmlManager.to_xml(rawData)))

    # ====================================================================#
    # Encrypt & Decrypt Tests
    # ====================================================================#
    def testEncrypt(self):
        """Test Encrypt of a Know Packet"""
        self.force_security()
        self.assertEqual(rawOut, Encryption.encrypt(rawIn))

    def testDecrypt(self):
        """Test Decrypt of a Know Packet"""
        self.force_security()
        self.assertEqual(rawIn, Encryption.decrypt(rawOut))

    def testEncryptAndDecrypt(self):
        """Test Encrypt & Decrypt of a Know Packet"""
        for x in range(6):
            data = ''.join(
                random.choice(string.ascii_letters + string.digits) for i in range(random.randrange(10, 1000)))
            self.assertEqual(data, Encryption.decrypt(Encryption.encrypt(data)))

    @staticmethod
    def force_security():
        SplashClient("ThisIsSplashWsId", "ThisIsYourEncryptionKeyForSplash")



if __name__ == '__main__':
    unittest.main()
