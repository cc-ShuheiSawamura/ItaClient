# -*- coding: utf-8 -*-
import pybitflyer
from coincheck import market
from pyliquid import pyliquid
import numpy as np
from time import time, sleep
import sqlite3


def get_cc_depth(ccboard_res, n_btc):
    ask_prices = [float(i[0]) for i in ccboard_res['asks']]
    bid_prices =  [float(i[0]) for i in ccboard_res['bids']]
    ask_sizes = [float(i[1]) for i in ccboard_res['asks']]
    bid_sizes =  [float(i[1]) for i in ccboard_res['bids']]
    mid = float((ask_prices[0]+bid_prices[0])/2)
    ask_distance = get_nbtc_distance(mid, ask_prices, ask_sizes, n_btc)
    bid_distance = get_nbtc_distance(mid, bid_prices, bid_sizes, n_btc)
    return ask_distance, bid_distance


def get_bf_depth(bfboard_res, n_btc):
    ask_prices = [float(i['price']) for i in bfboard_res['asks']]
    bid_prices =  [float(i["price"]) for i in bfboard_res['bids']]
    ask_sizes = [float(i['size']) for i in bfboard_res['asks']]
    bid_sizes =  [float(i['size']) for i in bfboard_res['bids']]
    mid = float((ask_prices[0]+bid_prices[0])/2)
    ask_distance = get_nbtc_distance(mid, ask_prices, ask_sizes, n_btc)
    bid_distance = get_nbtc_distance(mid, bid_prices, bid_sizes, n_btc)
    return ask_distance, bid_distance


def get_liquid_depth(liquidboard_res, n_btc):
    ask_prices = [float(i[0]) for i in liquidboard_res['sell_price_levels']]
    bid_prices =  [float(i[0]) for i in liquidboard_res['buy_price_levels']]
    ask_sizes = [float(i[1]) for i in liquidboard_res['sell_price_levels']]
    bid_sizes =  [float(i[1]) for i in liquidboard_res['buy_price_levels']]
    mid = float((ask_prices[0]+bid_prices[0])/2)
    ask_distance = get_nbtc_distance(mid, ask_prices, ask_sizes, n_btc)
    bid_distance = get_nbtc_distance(mid, bid_prices, bid_sizes, n_btc)
    return ask_distance, bid_distance


def get_nbtc_distance(mid_price, board_prices, board_sizes, nbtc):
    '''
    board_prices and board_sizes should be sorted as the best quote comes the first value
    '''
    cumsum_size = np.cumsum(board_sizes)
    try:
        above_nbtc_price = board_prices[cumsum_size[cumsum_size<nbtc].shape[0]+1]
    except IndexError as e:
        return 10**9 * 1.0
    distance = abs(mid_price-above_nbtc_price)
    return distance





# Initialize api clients
sql_client = sqlite3.connect('depth.db')
cur = sql_client.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS depth (timestamp real, 
            bf_ask_1 real, bf_bid_1 real, cc_ask_1 real, cc_bid_1 real, liquid_ask_1 real, liquid_bid_1 real,
            bf_ask_10 real, bf_bid_10 real, cc_ask_10 real, cc_bid_10 real, liquid_ask_10 real, liquid_bid_10 real,
            bf_ask_50 real, bf_bid_50 real, cc_ask_50 real, cc_bid_50 real, liquid_ask_50 real, liquid_bid_50 real,
            bf_ask_100 real, bf_bid_100 real, cc_ask_100 real, cc_bid_100 real, liquid_ask_100 real, liquid_bid_100 real,
            bf_ask_300 real, bf_bid_300 real, cc_ask_300 real, cc_bid_300 real, liquid_ask_300 real, liquid_bid_300 real,
            bf_ask_500 real, bf_bid_500 real, cc_ask_500 real, cc_bid_500 real, liquid_ask_500 real, liquid_bid_500 real,
            bf_ask_1000 real, bf_bid_1000 real, cc_ask_1000 real, cc_bid_1000 real, liquid_ask_1000 real, liquid_bid_1000 real);''')
cc_client = market.Market()
bf_client = pybitflyer.API()
liquid_client = pyliquid.API()
# get board of each exchange
bf_board = bf_client.board()
cc_board = cc_client.orderbooks()  # you can only get 200 orders from best using cc REST api
liquid_board =liquid_client.get_orderbook(id=5)


def save_task():
    while True:
        ts = time()
        bf_board = bf_client.board()
        cc_board = cc_client.orderbooks()
        liquid_board =liquid_client.get_orderbook(id=5)
        values = [ts, ]
        for s in [1, 10, 50, 100, 300, 500, 1000]:
            d_cc_ask, d_cc_bid = get_cc_depth(cc_board, s)
            d_liquid_ask, d_liquid_bid = get_liquid_depth(liquid_board, s)
            d_bf_ask, d_bf_bid = get_bf_depth(bf_board, s)
            print(f'bf_ask_{s}:', d_bf_ask, f'bf_bid_{s}:', d_bf_bid)
            print(f'liquid_ask_{s}:', d_liquid_ask, f'liquid_bid_{s}:', d_liquid_bid)
            print(f'cc_ask_{s}:', d_cc_ask, f'cc_bid_{s}:', d_cc_bid)
            print()
            values += [d_bf_ask, d_bf_bid, d_cc_ask, d_cc_bid, d_liquid_ask, d_liquid_bid]
        cur.execute(f"INSERT INTO depth VALUES {tuple(values)};")
        sql_client.commit()
        sleep(10)


def test():
    print('Liquid')
    print('1BTC:', get_liquid_depth(liquid_board, 1))
    print('10BTC:', get_liquid_depth(liquid_board, 10))
    print('50BTC:', get_liquid_depth(liquid_board, 50))
    print()
    print("bF")
    print('1BTC:', get_bf_depth(bf_board, 1))
    print('10BTC:', get_bf_depth(bf_board, 10))
    print('50BTC:', get_bf_depth(bf_board, 50))
    print()
    print("CC")
    print('1BTC:', get_cc_depth(cc_board, 1))
    print('10BTC:', get_cc_depth(cc_board, 10))
    print('50BTC:', get_cc_depth(cc_board, 50))
    print()


save_task()