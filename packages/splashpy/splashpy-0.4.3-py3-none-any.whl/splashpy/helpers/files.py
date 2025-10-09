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

import base64
import hashlib


class FilesHelper:

    @staticmethod
    def encodeFromRaw(contents, name, filename, path, public_url, b64=False):
        """Encode Splash File from Raw Contents"""
        # ====================================================================#
        # Detect Base64 Files
        if b64 is True:
            file = base64.b64decode(contents)
        else:
            file = contents
        # ====================================================================#
        # Build Splash File Data
        return {
            "name": name,
            "filename": filename,
            "md5": FilesHelper.md5(contents, b64),
            "path": path,
            "size": len(file),
        }

    @staticmethod
    def md5(contents, b64=False):
        """Detect File Md5"""
        if not isinstance(contents, (bytes, str)):
            return None
        if b64 is True:
            return hashlib.md5(base64.b64decode(contents)).hexdigest()
        else:
            return hashlib.md5(contents).hexdigest()


class ImagesHelper(FilesHelper):

    @staticmethod
    def encodeFromRaw(contents, name, filename, path, public_url, b64=False):
        """Encode Splash Image from Raw Contents"""
        if not isinstance(contents, (bytes, str)):
            return None
        # ====================================================================#
        # Detect Base64 Images
        if b64 is True:
            image = base64.b64decode(contents)
        else:
            image = contents
        # ====================================================================#
        # Detect Image Dimensions
        dims = ImagesHelper.get_pil_dims(image)
        # ====================================================================#
        # Build Splash Image Data
        return {
            "name": name,
            "filename": filename,
            "md5": ImagesHelper.md5(contents, b64),
            "path": path,
            "size": len(image),
            "url": public_url,
            "width": dims[0],
            "height": dims[1],
        }

    @staticmethod
    def encodeFromFile (base64_content):
        """Encode Splash Image from File """
        raise NotImplementedError("Not implemented yet.")

    @staticmethod
    def is_image(contents, b64=False):
        """Check if File Contents is an Image"""
        if ImagesHelper.get_extension(contents, b64) is None:
            return False

        return True

    @staticmethod
    def get_extension(contents, b64=False):
        """Detect Extension if Raw File Contents is an Image"""
        if not isinstance(contents, (bytes, str)):
            return None
        import imghdr
        if b64 is True:
            return imghdr.what(None, h=base64.b64decode(contents))
        else:
            return imghdr.what(None, h=contents)

    @staticmethod
    def get_pil_dims(raw_contents):
        """
        Detect Image Dimensions using PIL

        :param raw_contents: str
        :return: int
        """
        try:
            from PIL import Image
            import io
        except ImportError:
            return 0
        image = Image.open(io.BytesIO(raw_contents))

        return image.size






