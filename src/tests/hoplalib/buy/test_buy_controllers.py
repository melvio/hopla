#!/usr/bin/env python3
from hopla.hoplalib.buy.buy_controllers import BuyEnchantedArmoireRequest


class TestBuyEnchantedArmoireRequest:
    def test_url(self):
        request = BuyEnchantedArmoireRequest()

        result: str = request.url

        assert result == "https://habitica.com/api/v3/user/buy-armoire"
