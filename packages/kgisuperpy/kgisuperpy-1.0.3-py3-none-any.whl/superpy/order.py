import typing
import datetime

from account import Account
from contracts import Contract
from constant import (
    Action,
    FuturesPriceType,
    OrderType,
    FuturesOCType,
    StockPriceType,
    StockOrderCond,
    StockOrderLot,
    Status,
    OrderState,
)

class BaseModel:
    def __str__(self) -> str:
        return str(self.__dict__)

class Deal(BaseModel):
    seq: str
    price: typing.Union[float]
    quantity: int
    ts: float


class OrderStatus(BaseModel):
    id: str = ""
    status: Status
    status_code: str = ""
    web_id: str = ""
    order_datetime: typing.Optional[datetime.datetime] = None
    msg: str = ""
    modified_time: typing.Optional[datetime.datetime] = None
    modified_price: typing.Union[float] = 0
    order_quantity: int = 0
    deal_quantity: int = 0
    cancel_quantity: int = 0
    deals: typing.List[Deal] = None

class BaseOrder(BaseModel):
    action: Action
    price: typing.Union[float]
    quantity: int
    id: str = ""
    seqno: str = ""
    ordno: str = ""
    account: Account = None
    custom_field: str = ""
    ca: str = ""

    # def __repr_args__(self):
    #     return [
    #         (k, v)
    #         for k, v in self._iter(to_dict=False, exclude_defaults=True, exclude={"ca"})
    #     ]

    def __init__(self, action: Action, price: typing.Union[float], quantity: int, **kwargs):
        self.action = action
        self.price = price
        self.quantity = quantity
        # self.id = ""
        # self.seqno = ""
        # self.ordno = ""
        self.account = kwargs.get("account",None)
        self.custom_field = kwargs.get("custom_field","")
        # self.ca = ""

class FuturesOrder(BaseOrder):
    price_type: FuturesPriceType
    order_type: OrderType
    octype: FuturesOCType = FuturesOCType.Auto

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        price_type = kwargs.get('price_type')
        if not isinstance(price_type, FuturesPriceType):
            return
        self.price_type = price_type
        self.order_type = kwargs.get('order_type')
        self.octype = kwargs.get('octype', self.octype)
                

class StockOrder(BaseOrder):
    price_type: StockPriceType
    order_type: OrderType
    order_lot: StockOrderLot = StockOrderLot.Common
    order_cond: StockOrderCond = StockOrderCond.Cash
    daytrade_short: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        price_type = kwargs.get('price_type')
        if not isinstance(price_type, StockPriceType):
            return
        self.price_type = price_type
        self.order_type = kwargs.get('order_type')
        self.order_lot = kwargs.get('order_lot', self.order_lot)
        self.order_cond = kwargs.get('order_cond', self.order_cond)
        self.daytrade_short = kwargs.get('daytrade_short', False)
        

class Order(StockOrder, FuturesOrder):
    price_type: typing.Union[StockPriceType, FuturesPriceType]
    order_type: OrderType

    def __init__(
        self,
        price: typing.Union[float],
        quantity: int,
        action: Action,
        price_type: typing.Union[StockPriceType, FuturesPriceType],
        order_type: OrderType,
        **kwargs
    ):
        super().__init__(
            **{
                **dict(
                    price=price,
                    quantity=quantity,
                    action=action,
                    price_type=price_type,
                    order_type=order_type,
                ),
                **kwargs,
            }
        )

OrderTypeVar = typing.Union[Order, StockOrder, FuturesOrder]

class Trade:
    contract: Contract
    order: OrderTypeVar
    status: OrderStatus

    def __init__(self, contract: Contract, order: OrderTypeVar, status: OrderStatus):
        # super().__init__(**dict(contract=contract, order=order, status=status))
        self.contract=contract
        self.order=order
        self.status=status

