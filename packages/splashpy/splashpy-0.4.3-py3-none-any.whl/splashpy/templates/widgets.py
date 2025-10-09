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

from splashpy.models.widget import BaseWidget
from splashpy.componants.blockfactory import BlocksFactory


class Dummy(BaseWidget):

    name = "Dummy Widget"
    desc = "Just a Dummy/Empty Widget"

    def get(self, parameters):
        """Return requested Widget Data"""
        self.setSubTitle(self.desc)

        return self.render()


class Basic(BaseWidget):

    name = "Basic Widget"
    desc = "Just Text & Notifications Block"

    def get(self, parameters):
        """Return requested Widget Data"""
        self.setSubTitle(self.desc)

        BlocksFactory.addTextBlock("This is a Dummy text Block")
        blockContents = {
            "success": "I'm a Success Notification",
            "warning": "I'm a warning...",
            "info": "I'm an info...",
            "error": "And this is an error!!! Boooo!!!!"
        }
        BlocksFactory.addNotificationsBlock(blockContents)

        self.setBlocks(BlocksFactory.render())

        return self.render()


class Morris(BaseWidget):

    name = "Morris Charts Widget"
    desc = "Just Demo Graph Block"

    def get(self, parameters):
        """Return requested Widget Data"""
        self.setSubTitle(self.desc)

        BlocksFactory.addTextBlock("This is a Morris Chart Block")

        blockContents = {}
        for x in range(1, 10):
            blockContents[x] = {"value": x, "label": "Label"}
        BlocksFactory.addMorrisGraphBlock(blockContents, 'Bar')

        self.setBlocks(BlocksFactory.render())

        return self.render()