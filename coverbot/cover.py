from loguru import logger
from typing import Dict, List, Any, Union
from dataclasses import dataclass, field, fields
import shioaji as sj
from shioaji.contracts import Contract

from shioaji.constant import (
    OrderState,
    Action,
    StockOrderCond,
    QuoteType,
    QuoteVersion,
    TFTStockPriceType,
    TFTOrderType,
)
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
            code = msg["code"]
            if code not in self.deals.keys():
                self.subscribe_quote(code)
            self.deal_action(msg)
        elif order_state == OrderState.TFTOrder:
            code = msg["contract"]["code"]
            if code not in self.deals.keys():
                self.subscribe_quote(code)

    def quote_handler(self, exchange: Exchange, quote: QuoteSTKv1):
        deal = self.deals.get(quote.code)
        if deal:
            need_cover = deal.apply_quote(exchange, quote)
            if need_cover:
                self.cover_order(deal)
            return need_cover
        return False

    def cover_order(self, deal: Deal):
        contract = deal.contract

        action, price = (
            (Action.Sell, contract.limit_down)
            if deal.first_action == Action.Buy
            else (Action.Buy, contract.limit_up)
        )
        logger.info(f"{action} {price} {deal.quantity}")

        order = sj.Order(
            price=price,
            quantity=abs(deal.quantity),
            action=action,
            price_type=TFTStockPriceType.LMT,
            order_type=TFTOrderType.ROD,
            custom_field="Cover",
        )
        self.api.place_order(contract, order, timeout=0)
        logger.info(f"{contract.code} {contract.name} | {order}")
