from loguru import logger
from typing import Dict, List, Optional
import math
import polars as pl
from dataclasses import dataclass, field, fields
from shioaji.constant import OrderState, Action, StockOrderCond
from shioaji.contracts import Contract
from shioaji import Exchange, QuoteSTKv1


@dataclass
class TFTDeal:
    code: str
    action: Action
    price: float
    quantity: int
    order_cond: StockOrderCond
    web_id: str
    custom_field: str
    time: str

    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)


class Deal:
    def __init__(self, contract: Contract):
        self.contract: Contract = contract
        self.is_cover: bool = False
        self.buy_quantity: int = 0
        self.sell_quantity: int = 0
        self.amount: float = 0
        self.stop_price: float = 0.0
        self.first_action: Optional[Action] = None
        self.entry_price: float = 0.0
        self.stop_loss_pct: float = 0.03
        self.buy_collection: List[TFTDeal] = []
        self.sell_collection: List[TFTDeal] = []

    @property
    def quantity(self):
        return self.buy_quantity - self.sell_quantity

    # def __repr__(self) -> str:
    #     return f"Code : {self.contract}\n quantity:{self.quantity} buy: {len(self.buy_collection)} sell: {len(self.sell_collection)}"
    def to_dict(self):
        d = {
            "contract": f"{self.contract.code} {self.contract.name}",
            "action": self.first_action,
            "quantity": self.quantity,
            "amount": self.amount,
            "entry_price": self.entry_price,
            "stop_price": self.stop_price,
            "buy_records": len(self.buy_collection),
            "sell_records": len(self.sell_collection),
        }
        return d

    def df(self):
        df = (
            pl.DataFrame(data=[d for d in self.buy_collection + self.sell_collection])
            .select(pl.col(["code", "name", "action", "price", "quantity", "ordno"]))
            .with_columns(
                [(pl.col("price") * pl.col("quantity") * 1000).alias("amount")]
            )
            .groupby(
                [pl.col("code"), pl.col("name"), pl.col("ordno"), pl.col("action")]
            )
            .agg([pl.col("quantity").sum(), pl.col("amount").sum()])
            .with_columns(
                [
                    (pl.col("amount") * 0.001425 * 0.2).apply(math.floor).alias("fee"),
                    (
                        pl.when(pl.col("action") == "Sell")
                        .then((pl.col("amount") * 0.0015).apply(math.floor))
                        .otherwise(0)
                        .alias("tax")
                    ),
                ]
            )
        )

    def apply_quote(self, exchange: Exchange, quote: QuoteSTKv1):
        if self.is_cover == True:
            return False
        if quote.simtrade == 0 and quote.volume > 0:
            if self.quantity == 0:
                return False
            if self.first_action == Action.Sell and quote.close >= self.stop_price:
                logger.info(
                    f"[{self.contract.code} {self.contract.name}] 均價 {round(self.entry_price,2)} {self.quantity}張  賣單停損買回 現價 {quote.close} >= 停損價 {self.stop_price}"
                )
                self.is_cover = True
                return True
            elif self.first_action == Action.Buy:
                logger.info(
                    f"[{self.contract.code} {self.contract.name}] 均價 {round(self.entry_price)} {self.quantity}張  買單停損賣出 現價 {quote.close} <= 停損價 {self.stop_price}"
                )
                self.is_cover = True
                return True
        return False

    def apply(self, tftdeal: Dict):
        deal = TFTDeal(**tftdeal)
        amount = deal.quantity * deal.price * 1000
        if not self.first_action:
            self.first_action = deal.action

        if deal.action == Action.Buy:
            self.buy_quantity += deal.quantity
            self.buy_collection.append(deal)

        elif deal.action == Action.Sell:
            self.sell_quantity += deal.quantity
            self.sell_collection.append(deal)

        if self.first_action == deal.action:
            self.amount += amount
            quantity = (
                self.buy_quantity
                if self.first_action == Action.Buy
                else self.sell_quantity
            )
            self.entry_price = round(self.amount / quantity / 1000.0, 2)
            stop_dvalue = round(self.entry_price * self.stop_loss_pct, 2)
            if self.first_action == Action.Buy:
                self.stop_price = self.entry_price - stop_dvalue
            elif self.first_action == Action.Sell:
                self.stop_price = self.entry_price + stop_dvalue
