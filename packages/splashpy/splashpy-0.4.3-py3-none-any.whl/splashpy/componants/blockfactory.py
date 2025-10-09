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
from splashpy import Framework


class BlocksFactory:
    """Splash Objects Widgets Blocks Definitions Generator"""

    # ====================================================================#
    # Default Widget Options
    # ====================================================================#
    __DEFAULT_OPTIONS = {
        #      Block BootStrap Width   => 100%
        "Width": BaseWidget.__SIZE_XL__,
        #      Allow Html Contents     => No
        "AllowHtml": False,
    }

    # ====================================================================#
    # STATIC VARIABLES
    # ====================================================================#

    new = None
    blocks = []

    # ====================================================================#
    # CORE BLOCKS ACTIONS
    # ====================================================================#

    @staticmethod
    def setData(name, value):
        """Set Block Data Array Key"""
        if BlocksFactory.new is not None:
            BlocksFactory.new["data"][name] = value

        return BlocksFactory

    @staticmethod
    def extractData(contents, index):
        """Extract Block Data From Content Input Array"""
        if index in contents:
            BlocksFactory.setData(index, contents[index])

        return BlocksFactory

    @staticmethod
    def setOption(name, value):
        """Set Block Options Array Key"""
        if BlocksFactory.new is not None:
            BlocksFactory.new["options"][name] = value

        return BlocksFactory

    @staticmethod
    def render():
        """Save Current New Block, Return List & Clean"""
        # ====================================================================#
        # Commit Last Created if not already done
        if BlocksFactory.new is not None:
            BlocksFactory.commit()
        # ====================================================================#
        # Safety Checks
        if len(BlocksFactory.blocks) < 1:
            return Framework.log().error("Widget Blocks List is Empty")
        # ====================================================================#
        # Return fields List
        buffer = BlocksFactory.blocks
        print(buffer)
        BlocksFactory.blocks = []

        return buffer

    # ====================================================================#
    # BLOCKS CONTENTS MANAGEMENT
    # ====================================================================#

    @staticmethod
    def addBlock(type, options=None):
        """Create a new block with default parameters"""
        # ====================================================================#
        # Commit Last Created if not already done
        if BlocksFactory.new is not None:
            BlocksFactory.commit()
        # ====================================================================#
        # Create new empty block
        BlocksFactory.new = {"type": type, "options": {}, "data": {}}
        # ====================================================================#
        # Set Block Type
        # ====================================================================#
        # Set Block Options
        if options is None:
            options = BlocksFactory.__DEFAULT_OPTIONS
        BlocksFactory.new["options"] = options
        # ====================================================================#
        # Set Block Data
        BlocksFactory.new["data"] = {}

        return BlocksFactory

    @staticmethod
    def commit():
        """Save Current New Block in list & Clean"""
        # ====================================================================#
        # Safety Checks
        if BlocksFactory.new is None:
            return True
        # ====================================================================#
        # Create Blocks List
        if BlocksFactory.blocks is None:
            BlocksFactory.blocks = []
        # ====================================================================#
        # Insert Field List
        BlocksFactory.blocks.append(BlocksFactory.new)
        BlocksFactory.new = None

        return True

    # ====================================================================#
    # BLOCKS || SIMPLE TEXT BLOCK
    # ====================================================================#

    @staticmethod
    def addTextBlock(text, options = None):
        """Create a new Text Block"""
        if options is None:
            options = BlocksFactory.__DEFAULT_OPTIONS
        BlocksFactory.addBlock("TextBlock", options)
        BlocksFactory.setData("text", text)

        return BlocksFactory

    # ====================================================================#
    # BLOCKS || NOTIFICATIONS BLOCK
    # ====================================================================#

    @staticmethod
    def addNotificationsBlock(contents, options = None):
        """Create a new Notification Block"""
        # ====================================================================#
        # Create Block
        BlocksFactory.addBlock("NotificationsBlock", options)
        # ====================================================================#
        # Add Contents
        try: BlocksFactory.setData("error", contents["error"])
        except Exception: pass
        try: BlocksFactory.setData("warning", contents["warning"])
        except Exception: pass
        try: BlocksFactory.setData("info", contents["info"])
        except Exception: pass
        try: BlocksFactory.setData("success", contents["success"])
        except Exception: pass

        return BlocksFactory

    # ====================================================================#
    # BLOCKS || SIMPLE TABLE BLOCK
    # ====================================================================#

    @staticmethod
    def addTableBlock(contents, options = None):
        """Create a new Table Block"""
        # ====================================================================#
        # Create Block
        BlocksFactory.addBlock("TableBlock", options)
        # ====================================================================#
        # Add Contents
        BlocksFactory.setData("rows", contents)

        return BlocksFactory

    # ====================================================================#
    # BLOCKS || SPARK INFOS BLOCK
    # ====================================================================#

    @staticmethod
    def addSparkInfoBlock(contents, options = None):
        """Create a new Table Block"""
        # ====================================================================#
        # Create Block
        BlocksFactory.addBlock("SparkInfoBlock", options)
        # ====================================================================#
        # Add Contents
        BlocksFactory.extractData(contents, "title")
        BlocksFactory.extractData(contents, "fa_icon")
        BlocksFactory.extractData(contents, "glyph_icon")
        BlocksFactory.extractData(contents, "value")
        BlocksFactory.extractData(contents, "chart")

        return BlocksFactory

    # ====================================================================#
    # BLOCKS || MORRIS GRAPHS BLOCK
    # ====================================================================#

    @staticmethod
    def addMorrisGraphBlock(dataSet, chartType="Bar", chartOptions={}, options=None):
        """Create a new Morris Bar Graph Block"""
        # ====================================================================#
        # Verify Chart Type is Allowed
        if chartType not in ["Bar", "Area", "Line"]:
            blockContents = {
                "warning": "Wrong Morris Chart Block Type (ie: Bar, Area, Line)"
            }
            BlocksFactory.addNotificationsBlock(blockContents)

        # ====================================================================#
        # Create Block
        BlocksFactory.addBlock("Morris"+chartType+"Block", options)
        # ====================================================================#
        # Add Set Chart Data
        BlocksFactory.setData("dataset", dataSet)
        # ====================================================================#
        # Add Chart Parameters
        BlocksFactory.extractData(chartOptions, "title")
        BlocksFactory.extractData(chartOptions, "xkey")
        BlocksFactory.extractData(chartOptions, "ykeys")
        BlocksFactory.extractData(chartOptions, "labels")

        return BlocksFactory

    @staticmethod
    def addMorrisDonutBlock(dataSet, chartOptions={}, options=None):
        """Create a new Morris Donut Graph Block"""
        # ====================================================================#
        # Create Block
        BlocksFactory.addBlock("MorrisDonutBlock", options)
        # ====================================================================#
        # Add Set Chart Data
        BlocksFactory.setData("dataset", dataSet)
        # ====================================================================#
        # Add Chart Parameters
        BlocksFactory.extractData(chartOptions, "title")

        return BlocksFactory


