from loguru import logger
from typing import Dict, List, Any, Union
from dataclasses import dataclass, field, fields
import shioaji as sj
from shioaji.contracts import Contract

from shioaji.constant import OrderState, Action, StockOrderCond, QuoteType, QuoteVersion
from .deal import TFTDeal, Deal
from shioaji import QuoteSTKv1, Exchange


class CoverBot:
    def __init__(self, api: sj.Shioaji):
        self.api: sj.Shioaji = api
        self.api.set_order_callback(self.order_handler)
        self.api.quote.set_on_quote_stk_v1_callback(self.quote_handler)
        self.deals: Dict[str, Deal] = {}

    def set_stop_loss_pct(self, code: str, value: float):
        contract = self.api.Contracts.Stocks[code]
        deal = self.deals[code] = self.deals.get(code, Deal(contract))
        deal.stop_loss_pct = value

    def show(self):
        return [v.to_dict() for _, v in self.deals.items()]

    def deal_action(self, tftdeal: Dict[str, Any]) -> None:
        code = tftdeal.get("code", "")
        contract = self.api.Contracts.Stocks[code]
        if not contract:
            logger.warning(f"[{code}] not exist.")
        else:
            deal = self.deals[code] = self.deals.get(code, Deal(contract))
            deal.apply(tftdeal)

    def subscribe_quote(self, code: str):
        self.api.quote.subscribe(
            self.api.Contracts.Stocks[code],
            quote_type=QuoteType.Quote,
            version=QuoteVersion.v1,
        )

    def order_handler(self, order_state: OrderState, msg: Dict) -> None:
        if order_state == OrderState.TFTDeal:
            if msg["code"] not in self.deals.keys():
                self.subscribe_quote(msg["code"])
            self.deal_action(msg)
        elif order_state == OrderState.TFTOrder:
            if msg["contract"]["code"] not in self.deals.keys():
                self.subscribe_quote(msg["code"])

    def quote_handler(self, exchange: Exchange, quote: QuoteSTKv1):
        deal = self.deals.get(quote.code)
        if deal:
            result = deal.apply_quote(exchange, quote)
            logger.info(result)
            return result
        return None
