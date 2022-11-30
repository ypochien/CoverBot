import pytest
from loguru import logger
import shioaji as sj
from shioaji import Exchange
from shioaji.constant import OrderState, StockOrderCond, Action
from typing import Tuple

# from coverbot.deal import TFTDeal
from coverbot.cover import CoverBot, TFTDeal
from .quote import QuoteSTKv1

deal_buy = {
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


def test_sell_deal_action(cover_bot: CoverBot):
    cover_bot.deal_action(deal_sell)
    cover_bot.show()
    assert cover_bot.deals[deal_sell["code"]].quantity == -1


def test_deal_action(cover_bot: CoverBot):
    assert cover_bot.deals.get(deal_buy["code"], None) == None
    cover_bot.deal_action(deal_buy)
    assert cover_bot.deals[deal_buy["code"]].quantity == 1
    cover_bot.deal_action(deal_sell)
    assert cover_bot.deals[deal_buy["code"]].quantity == 0
    cover_bot.deal_action(deal_sell)
    assert cover_bot.deals[deal_buy["code"]].quantity == -1


def test_deal_date(cover_bot: CoverBot, mocker):
    mocker_place_order = mocker.patch.object(cover_bot.api.quote, "subscribe")
    cover_bot.order_handler(OrderState.TFTDeal, deal_buy)
    mocker_place_order.assert_called_once()
    assert cover_bot.deals[deal_buy["code"]].quantity == 1


def test_show(cover_bot: CoverBot, deal_data, mocker):
    mocker_place_order = mocker.patch.object(cover_bot.api.quote, "subscribe")

    for deal in deal_data:
        if deal["action"] == "Sell":
            cover_bot.order_handler(OrderState.TFTDeal, deal)
    # logger.info(cover_bot.show())


def test_non_deal_quote_should_be_None(
    cover_bot: CoverBot, quote_data: Tuple[Exchange, QuoteSTKv1]
):
    exchange, quote = quote_data
    result = cover_bot.quote_handler(exchange=exchange, quote=quote)  # type: ignore
    assert result == False


def test_coverbot_set_stop_loss_pct(cover_bot: CoverBot):
    cover_bot.deal_action(deal_sell)
    code = deal_sell["code"]
    deal = cover_bot.deals[code]
    assert deal.stop_loss_pct == 0.03
    cover_bot.set_stop_loss_pct(code, 0.05)
    assert deal.stop_loss_pct == 0.05


def test_in_deal_quote_should_be_(
    cover_bot: CoverBot, mock_api, quote_data: Tuple[Exchange, QuoteSTKv1], mocker
):
    cover_bot.deal_action(deal_sell)
    exchange, quote = quote_data
    quote.code = "5871"
    mocker_place_order = mocker.patch.object(mock_api, "place_order")
    result = cover_bot.quote_handler(exchange=exchange, quote=quote)  # type: ignore
    mocker_place_order.assert_called_once()
    assert result == True
    result = cover_bot.quote_handler(exchange=exchange, quote=quote)  # type: ignore
    result = cover_bot.quote_handler(exchange=exchange, quote=quote)  # type: ignore
    result = cover_bot.quote_handler(exchange=exchange, quote=quote)  # type: ignore


def test_tftorder(cover_bot: CoverBot, mocker):
    mocker_place_order = mocker.patch.object(cover_bot.api.quote, "subscribe")
    tftorder = {"contract": {"code": "5871"}}
    cover_bot.order_handler(OrderState.TFTOrder, tftorder)
