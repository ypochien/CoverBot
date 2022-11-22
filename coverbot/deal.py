from typing import Dict, List, Optional
from dataclasses import dataclass, field, fields
from shioaji.constant import OrderState, Action, StockOrderCond
from shioaji.contracts import Contract


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
        self.buy_quantity: int = 0
        self.sell_quantity: int = 0
        self.amount: float = 0
        self.stop_price: float = 0.0
        self.first_action: Optional[Action] = None
        self.entry_price: float = 0.0
        self.stop_loss_pct: float = 0.09
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
            "entry_price": self.entry_price,
            "buy_records": len(self.buy_collection),
            "sell_records": len(self.sell_collection),
        }
        return d

    # def __dict__(self):

    def __str__(self) -> str:
        return str(
            {
                "contract": f"{self.contract.code} {self.contract.name}",
                "action": self.first_action,
                "quantity": self.quantity,
                "entry_price": self.entry_price,
                "buy_records": len(self.buy_collection),
                "sell_records": len(self.sell_collection),
            }
        )

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
            self.entry_price = self.amount / quantity / 1000.0
