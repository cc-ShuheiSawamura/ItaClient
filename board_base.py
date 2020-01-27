# -*-coding: utf-8-*-
import websocket
from sortedcontainers import SortedDict
import threading
import time

class Orderbook:

    def __init__(self, url):
        self.url = url
        self.sd_bids = SortedDict()
        self.sd_asks = SortedDict()
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.run()

    def bids(self):
        return self.sd_bids.values()

    def asks(self):
        return self.sd_asks.values()

    def run(self):
        while True:
            self.sd_bids, self.sd_asks = SortedDict(), SortedDict()
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=lambda ws: self.on_open(ws),
                on_close=lambda ws: self.on_close(ws),
                on_message=lambda ws, msg: self.on_message(ws, msg),
                on_error=lambda ws, err: self.on_error(ws, err))
            self.ws.run_forever()
            time.sleep(1)

    def on_open(self, ws):
        raise NotImplementedError()

    def on_close(self, ws):
        raise NotImplementedError()

    def on_message(self, ws, msg):
        raise NotImplementedError()

    def on_error(self, ws, err):
        raise NotImplementedError()

def test(ob):
    # import websocket
    # websocket.enableTrace(True)
    try:
        while True:
            for p, s in ob.asks()[10::-1]:
                print(f'{p:<10}{s:>10.3f}')
            print('==== Order Book ====')
            for p, s in ob.bids()[:10]:
                print(f'{p:<10}{s:>10.3f}')
            print('')
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass