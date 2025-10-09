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


class PricesHelper:
    """Helper for Prices Fields Management"""

    @staticmethod
    def encode(tax_excl, vat, tax_incl=None, code="", symbol="", name=""):
        """
        Build a new price field array
        :param tax_excl: None|float     Price Without VAT (Or Null if Price Send with VAT)
        :param vat: float               VAT percentile
        :param tax_incl: None|float     Price With VAT
        :param code: str                Price Currency Code
        :param symbol: str              Price Currency Symbol
        :param name: str                Price Currency Name
        :return: hash|None
        """
        # ==================================================================== #
        # Safety Checks
        if not isinstance(tax_excl, float) and not isinstance(tax_incl, float):
            Framework.log().error("Price Invalid: No Amount Given")
            return None
        if isinstance(tax_excl, float) and isinstance(tax_incl, float):
            Framework.log().error("Price Invalid: Too Much Input Values")
            return None
        if not isinstance(vat, float) :
            Framework.log().error("Price Invalid: VAT is NOT a Float")
            return None
        if not isinstance(code, str) or len(code) < 2:
            Framework.log().error("Price Invalid: no Currency Code")
            return None
        # ==================================================================== #
        # Build Price Array
        if isinstance(tax_excl, float):
            return {
                "vat": vat,
                "code": code,
                "symbol": symbol,
                "name": name,
                "base": 0,
                "ht": tax_excl,
                "tax": (tax_excl * (vat / 100)),
                "ttc": (tax_excl * (1 + vat / 100)),
            }

        return {
            "vat": vat,
            "code": code,
            "symbol": symbol,
            "name": name,
            "base": 1,
            "ht": (tax_incl / (1 + vat / 100)),
            "tax": tax_incl - (tax_incl / (1 + vat / 100)),
            "ttc": tax_incl,
        }

    @staticmethod
    def compare(price1, price2):
        """
        Compare Two Price Array
        :param price1: dict
        :param price2: dict
        :return: bool
        """
        # ==================================================================== #
        # Check Both Prices are valid
        if not PricesHelper.isValid(price1) or not PricesHelper.isValid(price2):
            Framework.log().error("Price Compare: Given Prices are invalid")
            if Framework.isDebugMode() and not PricesHelper.isValid(price1):
                Framework.log().dump( price1, " Price 1")
            if Framework.isDebugMode() and not PricesHelper.isValid(price1):
                Framework.log().dump( price2, " Price 2")

            return False
        # ==================================================================== #
        # Compare Base Price
        if bool(price1["base"]) != bool(price2["base"]):
            return False
        # ==================================================================== #
        # Compare Price Amounts
        return PricesHelper.compareAmounts(price1, price2)

    @staticmethod
    def compareAmounts(price1, price2):
        """
        Compare Two Price Array without Validation
        :param price1: dict
        :param price2: dict
        :return: bool
        """
        # ==================================================================== #
        # Compare Price
        if bool(price1["base"]):
            if abs(price1["ttc"] - price2["ttc"]) > 1E-6:
                return False
        else:
            if abs(price1["ht"] - price2["ht"]) > 1E-6:
                return False
        # ==================================================================== #
        # Compare VAT
        if abs(price1["vat"] - price2["vat"]) > 1E-6:
            return False
        # ==================================================================== #
        # Compare Currency If Set on Both Sides
        if len(price1["code"]) == 0 or len(price2["code"]) == 0:
            return True
        if price1["code"] != price2["code"]:
            return False
        # ==================================================================== #
        # Prices Are Identical
        return True

    @staticmethod
    def isValid(price):
        """
        Verify Price field array
        :param price: mixed
        :return: bool
        """
        # ==================================================================== #
        # Check Contents Available
        if not isinstance(price, dict):
            return False
        if "base" not in price.keys():
            return False
        if "ht" not in price.keys() or "ttc" not in price.keys() or "vat" not in price.keys():
            return False
        # ==================================================================== #
        # Check Amounts
        if not PricesHelper.isValidAmount(price):
            return False
        # ==================================================================== #
        # Check Currency
        if not PricesHelper.isValidCurrency(price):
            return False

        return True

    @staticmethod
    def extract(price, key = "ht"):
        """
        Extract Data from Price Array
        :param price: dict
        :param key: str
        :return: None|float
        """
        # Check Contents
        if key not in price.keys():
            return None
        # Return Result
        try:
            return float(price[key])
        except:
            return None

    @staticmethod
    def taxExcluded(price):
        """Extract Price without VAT from Price Array"""
        return PricesHelper.extract(price, 'ht')

    @staticmethod
    def taxIncluded(price):
        """Extract Price with VAT from Price Array"""
        return PricesHelper.extract(price, 'ttc')

    @staticmethod
    def taxPercent(price):
        """Extract Price with VAT from Price Array"""
        return PricesHelper.extract(price, 'vat')

    @staticmethod
    def taxRatio(price):
        """Extract Price VAT Ratio from Price Array"""
        vatRate = PricesHelper.extract(price, 'vat')
        if isinstance(vatRate, float):
            return vatRate / 100
        return 0

    @staticmethod
    def taxAmount(price):
        """Extract Price Tax Amount from Price Array"""
        return PricesHelper.extract(price, 'tax')

    @staticmethod
    def isValidAmount(price):
        """
        Verify Price Array Amount Infos are Available
        :param price: dict
        :return: bool
        """
        # ==================================================================== #
        # Check Contents Available
        for key in ["ht", "ttc", "vat"]:
            if key not in price.keys() or not isinstance(price[key], [str, int, float]):
                return False
        return True

    @staticmethod
    def isValidCurrency(price):
        """
        Verify Price Array Currency Infos are Available
        :param price: dict
        :return: bool
        """
        # ==================================================================== #
        # Check Contents Available
        for key in ["tax", "symbol", "code", "name"]:
            if key not in price.keys():
                return False
        return True
