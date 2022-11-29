import pytest
from loguru import logger
import pathlib
import pickle
from decimal import Decimal
from typing import Dict, List
import datetime as dt
import shioaji as sj
from shioaji import Exchange

from coverbot.cover import CoverBot

from .quote import QuoteSTKv1


contract_filename = f"{pathlib.Path(__file__).parent.absolute()}/data/contracts.pkl"


@pytest.fixture
def deal_data() -> List[Dict]:
    deal_filename = f"{pathlib.Path(__file__).parent.absolute()}/data/_deals.pkl"
    with open(deal_filename, "rb") as f:
        test_data = pickle.load(f)
    return test_data


@pytest.fixture
def quote_data():
    quote = QuoteSTKv1(
        code="1795",
        datetime=dt.datetime(2022, 7, 1, 10, 43, 15, 840092),
        open=Decimal("471.5"),
        avg_price=Decimal("467.9"),
        close=Decimal("461"),
        high=Decimal("474"),
        low=Decimal("461"),
        amount=Decimal("9220000"),
        total_amount=Decimal("11843696000"),
        volume=1,
        total_volume=25312,
        tick_type=2,
        chg_type=4,
        price_chg=Decimal("-15"),
        pct_chg=Decimal("-3.15"),
        bid_side_total_vol=9350,
        ask_side_total_vol=15962,
        bid_side_total_cnt=2730,
        ask_side_total_cnt=2848,
        closing_oddlot_shares=0,
        closing_oddlot_close=Decimal("0.0"),
        closing_oddlot_amount=Decimal("0"),
        closing_oddlot_bid_price=Decimal("0.0"),
        closing_oddlot_ask_price=Decimal("0.0"),
        fixed_trade_vol=0,
        fixed_trade_amount=Decimal("0"),
        bid_price=[
            Decimal("461"),
            Decimal("460.5"),
            Decimal("460"),
            Decimal("459.5"),
            Decimal("459"),
        ],
        bid_volume=[201, 141, 994, 63, 132],
        diff_bid_vol=[0, 1, 0, 0, 0],
        ask_price=[
            Decimal("461.5"),
            Decimal("462"),
            Decimal("462.5"),
            Decimal("463"),
            Decimal("463.5"),
        ],
        ask_volume=[123, 101, 103, 139, 95],
        diff_ask_vol=[0, 0, 0, 0, 0],
        avail_borrowing=9579699,
        suspend=0,
        simtrade=0,
    )
    exchange = Exchange("TSE")
    return exchange, quote


@pytest.fixture
def mock_api() -> sj.Shioaji:
    api: sj.Shioaji = sj.Shioaji(simulation=False)
    with open(contract_filename, "rb") as f:
        api.Contracts = pickle.load(f)
    return api


@pytest.fixture
def cover_bot(mock_api: sj.Shioaji) -> CoverBot:
    sut = CoverBot(mock_api)
    return sut
