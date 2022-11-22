from loguru import logger
from typing import Dict, List, Any, Union
from dataclasses import dataclass, field, fields
import shioaji as sj
from shioaji.contracts import Contract

from shioaji.constant import OrderState, Action, StockOrderCond
from .deal import TFTDeal, Deal


class CoverBot:
    def __init__(self, api: sj.Shioaji):
        self.api = api
        self.api.set_order_callback(self.order_handler)
        self.deals: Dict[str, Deal] = {}

    def set_stop_loss_pct(self, code: str):
        contract = self.api.Contracts.Stocks[code]
        deal = self.deals[code] = self.deals.get(code, Deal(contract))

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

    def order_handler(self, order_state: OrderState, msg: Dict) -> None:
        if order_state == OrderState.TFTDeal:
            self.deal_action(msg)
