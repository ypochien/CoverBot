from dataclasses import dataclass
import datetime as dt
from decimal import Decimal
from typing import List


@dataclass
class QuoteSTKv1:
    """Quote Stock v1
    Attributes:
        code (str): code
        datetime (datetime.datetime): datetime
        open (Decimal): open
        avg_price (Decimal): average price
        close (Decimal): deal price
        high (Decimal): high since market open
        low (Decimal): low since market open
        amount (Decimal): amount (NTD)
        total_amount (Decimal): total amount (NTD)
        volume (int): volume (K shares)
        total_volume (int): total volume (K shares)
        tick_type (int): tick type (內外盤別)
            {1: buy deal, 2: sell deal, 0: can't judge}
        chg_type (int): (漲跌註記)
            {1: limit up, 2: up, 3: unchanged, 4: down, 5: limit down}
        price_chg (Decimal): price change
        pct_chg (Decimal): percentage change (%)
        bid_side_total_vol(int): total bid deal volume (K shares, 買盤成交總量)
        ask_side_total_vol (int): total ask deal volume (K shares, 賣盤成交總量)
        bid_side_total_cnt (int): total number of buy deal (買盤成交筆數)
        ask_side_total_cnt (int): total number of sell deal (賣盤成交筆數)
        closing_oddlot_shares (int): (share, 盤後零股成交股數)
        closing_oddlot_close (Decimal): closing oddlot close
        closing_oddlot_amount (Decimal): closing oddlot amount
        closing_oddlot_bid_price (Decimal): closing oddlot bid price
        closing_oddlot_ask_price (Decimal): closing oddlot ask price
        fixed_trade_vol (int): fixed trade volume (K shares, 定盤成交量)
        fixed_trade_amount (Decimal): fixed trade amount
        bid_price (list of Decimal): bid price
        bid_volume (list of int): bid volume (lot), (張)
        diff_bid_vol (list of int): (lot), (張, 買價增減量)
        ask_price (list of Decimal): ask price
        ask_volume (list of int): ask volume (lot), (張)
        diff_ask_vol (list of int): (lot), (張, 賣價增減量)
        avail_borrowing (int): avail borrowing
        suspend (bool): suspend (暫停交易)
        simtrade (bool): simulated trade (試撮)
    """

    code: str
    datetime: dt.datetime
    open: Decimal
    avg_price: Decimal
    close: Decimal
    high: Decimal
    low: Decimal
    amount: Decimal
    total_amount: Decimal
    volume: int
    total_volume: int
    tick_type: int
    chg_type: int
    price_chg: Decimal
    pct_chg: Decimal
    bid_side_total_vol: int
    ask_side_total_vol: int
    bid_side_total_cnt: int
    ask_side_total_cnt: int
    closing_oddlot_shares: int
    closing_oddlot_close: Decimal
    closing_oddlot_amount: Decimal
    closing_oddlot_bid_price: Decimal
    closing_oddlot_ask_price: Decimal
    fixed_trade_vol: int
    fixed_trade_amount: Decimal
    bid_price: List[Decimal]
    bid_volume: List[int]
    diff_bid_vol: List[int]
    ask_price: List[Decimal]
    ask_volume: List[int]
    diff_ask_vol: List[int]
    avail_borrowing: int
    suspend: int
    simtrade: int
