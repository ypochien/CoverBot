import pytest
from loguru import logger
import shioaji as sj
from shioaji.constant import OrderState, StockOrderCond, Action

# from coverbot.deal import TFTDeal
from coverbot.cover import CoverBot, TFTDeal


deal = {
    "trade_id": "eb6055e4",
    "seqno": "425813",
    "ordno": "IE324",
    "exchange_seq": "430956",
    "broker_id": "9A9S",
    "account_id": "0291589",
    "action": "Buy",
    "code": "5871",
    "order_cond": "Cash",
    "order_lot": "Common",
    "price": 191.5,
    "quantity": 1,
    "web_id": "137",
    "custom_field": "",
    "ts": 1668482197,
    "name": "中租-KY",
    "time": "2022-11-15 11:16:37",
}
deal_sell = {
    "trade_id": "eb6055e4",
    "seqno": "425813",
    "ordno": "IE324",
    "exchange_seq": "430956",
    "broker_id": "9A9S",
    "account_id": "0291589",
    "action": "Sell",
    "code": "5871",
    "order_cond": "Cash",
    "order_lot": "Common",
    "price": 191.5,
    "quantity": 1,
    "web_id": "137",
    "custom_field": "",
    "ts": 1668482197,
    "name": "中租-KY",
    "time": "2022-11-15 11:16:37",
}


def test_sell_deal_action(sut: CoverBot):
    sut.deal_action(deal_sell)
    sut.show()
    assert sut.deals[deal_sell["code"]].quantity == -1


def test_deal_action(sut: CoverBot):
    assert sut.deals.get(deal["code"], None) == None
    sut.deal_action(deal)
    assert sut.deals[deal["code"]].quantity == 1
    sut.deal_action(deal_sell)
    assert sut.deals[deal["code"]].quantity == 0
    sut.deal_action(deal_sell)
    assert sut.deals[deal["code"]].quantity == -1


def test_deal_date(sut: CoverBot):
    sut.order_handler(OrderState.TFTDeal, deal)
    assert sut.deals[deal["code"]].quantity == 1


def test_show(sut, deal_data):
    for d in deal_data:
        if d["action"] == "Sell":
            sut.order_handler(OrderState.TFTDeal, d)
    logger.info(sut.show())
