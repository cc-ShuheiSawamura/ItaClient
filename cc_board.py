# -*- coding: utf-8 -*-
import board_base

class CCBoard(board_base.Orderbook):

    ENDPOINT = 'wss://ws-api.coincheck.com/'
    PAIR =  'btc_jpy'

    def __init__(self):
        super().__init__(self.ENDPOINT)
        self.CHANNEL = f'{self.PAIR}-orderbook'

    def initialize(self):
        return

# よく考えるとwsでなくRESTで良いので一旦終了