import typing
from TradeCom import TradeCom
from IntelligencePy import *
from PackagePy import *
from constant import OrderState

class OrderReport:
    def __init__(self, tradeCom) -> None:
        self.__tradeCom : TradeCom = tradeCom
        self.__tradeCom.callback = self.__tradeCom_callback
        self.order_callback = None
    
    def set_order_callback(
        self, func: typing.Callable[[OrderState, dict], None]
    ) -> None:
        self.order_callback = func

    def __tradeCom_callback(self, pkgDT:DT, pkg):
        if self.order_callback == None:
            return

        match pkgDT :
            case DT.SECU_ORDER_RPT:
                self.order_callback(OrderState.StockOrder, StockOrder(pkg).__dict__)
                return
            case DT.SECU_DEAL_RPT:
                self.order_callback(OrderState.StockDeal, StockDeal(pkg).__dict__)
                return
            case DT.FUT_ORDER_RPT:
                self.order_callback(OrderState.FuturesOrder, FuturesOrder(pkg).__dict__)
                return
            case DT.FUT_DEAL_RPT:                
                self.order_callback(OrderState.FuturesDeal, FuturesDeal(pkg).__dict__)
                return
            case _:
                # print(pkgDT, pkg)
                return

#region OrderRPT

class PackageConvert:
    def op_type(OrderFunc):
        return { "I": "New", "D": "Cancel", "M": "UpdatePrice", "R": "UpdatePrice", "C": "UpdateQty" }.get(OrderFunc, None)
    
    def action(Side):
        return { 'B' : "Buy" , 'S' : "Sell"}.get(Side, None)
    
    def order_type(TimeInForceN):
        return { 'F' : "FOK" , 'I' : "IOC" , 'R' : "ROD" }.get(TimeInForceN, None)
    
    def price_type(PriceFlagN): 
        return { '1' : "MKT" , '2' : "LMT" , '0' : "MKP" }.get(PriceFlagN, None)
    
    def order_cond(OrdClass): 
        return { '0' : "CASH", '3' : "MarginTrading", '4' : "ShortSelling", '6' : "ShortUnLimit", 'A' : "EDN" }.get(OrdClass, None)
    
    def order_lot(OrdLot):
        return { '0' : "Common", '2' : "Fixing", '1' : "Odd", '4' : "IntradayOdd" }.get(OrdLot, None)
    
    def oc_type(PositionEffect):
        return { 'O':"New", 'C':"Cover", 'A':"Auot" }.get(PositionEffect, None)

class Operation:
    op_type: (str) #"New": 新單, "Cancel": 刪單, "UpdatePrice": 改價, "UpdateQty": 改量
    op_code: (str) #{"00": 成功, others: 失敗}
    op_msg: (str) #錯誤訊息

class Order:
    id: (str)# 與成交回報的trade_id相同
    seqno: (str)# 平台單號
    ordno: (str)# 委託單號
    account: (dict)# 帳號資訊
    action: (str)# 買賣別 {Buy, Sell}
    price: (float)# 委託價格
    quantity: (int)# 委託數量
    order_type: (str)# 委託類別 {ROD, IOC, FOK}
    price_type: (str)# {LMT: 限價, MKT: 市價, MKP: 範圍市價}
    order_cond: (str)# {Cash: 現股, MarginTrading: 融資, ShortSelling: 融券, ShortUnLimit:借券賣出, EDN:賣出擔保品 }
    #證券
    order_lot: (str)# { Common: 整股, Fixing: 定盤, Odd: 盤後零股, IntradayOdd: 盤中零股 }
    custom_field: (str)# 自訂欄位
    #期貨
    market_type : (str) # 市場別 {Day:日盤, Night:夜盤}
    oc_type : (str) # {New: 新倉, Cover: 平倉, Auto: 自動}
    subaccount : (str) # 子帳號
    combo : (bool) # 是否為組合單

class Status:
    id: (str)#: 與成交回報的trade_id相同
    exchange_ts: (int)#: 交易所時間
    modified_price: (float)#: 改價
    cancel_quantity:(int)#: 取消數量
    order_quantity: (int)#: 委託數量
    web_id: (str)#: 下單平台代碼

class Contract:
    security_type: (str)# 商品類別
    exchange: (str)# 交易所
    code: (str)# 商品代碼
    #證券
    symbol: (str)# 符號
    name: (str)# 商品名稱
    currency: (str)# 幣別
    #期貨
    delivery_month : (str) # 交割月份
    delivery_date : (str) # 交割日期
    strike_price : (float) # 履約價
    option_right : (str) # {Future, OptionCall, OptionPut}

class OrderRPT:
    operation: (dict)
    order: (dict)
    status: (dict)
    contract: (dict)

    def __str__(self) -> str:
        return str(self.__dict__)

class StockOrder(OrderRPT):
    def __init__(self, pkg:PT04010):
        # print(pkg)
        operation = Operation()
        operation.op_type = PackageConvert.op_type(pkg.OrderFunc)
        operation.op_code = pkg.ErrCode
        operation.op_msg = pkg.ErrMsg    
        self.operation = operation.__dict__
        
        order = Order()
        order.id = pkg.CNTN
        # order.seqno 
        order.ordno = pkg.OrderNo
        order.account= {
            'account_type': 'S', 
            'broker_id': pkg.BrokerId, 
            'account_id': pkg.Account, 
        }
        order.action = PackageConvert.action(pkg.Side)
        order.price = pkg.Price
        order.quantity = pkg.Qty
        order.order_type = PackageConvert.order_type(pkg.TimeInForceN)
        order.price_type = PackageConvert.price_type(pkg.PriceFlagN)
        order.order_cond = PackageConvert.order_cond(pkg.OrdClass)
        order.order_lot = PackageConvert.order_lot(pkg.OrdLot)
        # order.custom_field = 
        self.order = order.__dict__

        status = Status()
        status.id = pkg.CNTN
        # status.exchange_ts
        status.modified_price = pkg.Price if pkg.OrderFunc == 'M' else 0
        status.cancel_quantity = pkg.Qty if pkg.OrderFunc in ['C','D'] else 0
        status.order_quantity = pkg.Qty if pkg.OrderFunc == 'I' else 0
        # status.web_id
        self.status = status.__dict__

        contract = Contract()
        contract.security_type = "STK"
        contract.exchange = { '0' : "TSE" , '1' : "OTC" }.get(pkg.Market, None)
        contract.code = pkg.StockID
        contract.symbol = ''
        contract.name = ''
        contract.currency = 'TWD'
        self.contract = contract.__dict__

class FuturesOrder(OrderRPT):
    def __init__(self, pkg:PT02010):
        operation = Operation()
        operation.op_type = PackageConvert.op_type(pkg.OrderFunc)
        operation.op_code = pkg.Code
        operation.op_msg = pkg.ErrMsg    
        self.operation = operation.__dict__

        order = Order()
        order.id = pkg.CNT
        # order.seqno 
        order.ordno = pkg.OrderNo
        order.account= {
            'account_type': 'F', 
            'broker_id': pkg.BrokerId, 
            'account_id': pkg.Account, 
        }
        order.action = PackageConvert.action(pkg.Side)
        order.price = pkg.Price
        order.quantity = pkg.AfterQty
        order.order_type = PackageConvert.order_type(pkg.TimeInForce)
        order.price_type = PackageConvert.price_type(pkg.PriceMark)
        # order.market_type 
        order.oc_type = PackageConvert.oc_type(pkg.PositionEffect)
        # order.subaccount
        # order.combo
        self.order = order.__dict__

        status = Status()
        status.id = pkg.CNT
        # status.exchange_ts
        status.modified_price = pkg.Price if pkg.OrderFunc == 'R' else 0
        status.cancel_quantity = { 'D' : pkg.BeforeQty, 'C' : int(pkg.BeforeQty)-int(pkg.AfterQty) }.get(pkg.OrderFunc, 0)
        status.order_quantity = pkg.AfterQty if pkg.OrderFunc == 'I' else 0
        status.web_id = pkg.WebID
        self.status = status.__dict__

        contract = Contract()
        contract.security_type = "FUT"
        contract.exchange = "TAIFEX"
        contract.code = pkg.Symbol
        # contract.delivery_month
        # contract.delivery_date
        # contract.strike_price
        # contract.option_right
        self.contract = contract.__dict__

#endregion

class DealRPT:
    trade_id : (str) # 與委託回報id相同
    seqno : (str) # 平台單號
    ordno : (str) # 前五碼為同委託回報委託單號，後三碼為同筆委託成交交易序號。
    exchange_seq : (str) # 回報序號
    broker_id : (str) # 分行代碼
    account_id : (str) # 帳號
    action : (str) # 買賣別 {Buy, Sell}
    code : (str) # 商品代碼
    price : (float) # 成交價
    quantity : (int) # 成交量
    ts : (int) # 成交時間戳
    
    def __str__(self) -> str:
        return str(self.__dict__)

class StockDeal(DealRPT):
    order_cond : (str) # { Cash: 現股, MarginTrading: 融資, ShortSelling: 融券 }
    order_lot : (str) # { Common: 整股, Fixing: 定盤, Odd: 盤後零股, IntradayOdd: 盤中零股 }
    web_id : (str) # 平台代碼
    custom_field : (str) # 自訂欄位

    def __init__(self, pkg:PT04011):
        self.trade_id = pkg.CNTN
        # self.seqno
        self.ordno = pkg.OrderNo
        # self.exchange_seq
        self.broker_id = pkg.BrokerId
        self.account_id = pkg.Account
        self.action = PackageConvert.action(pkg.Side)
        self.code = pkg.StockID
        self.order_cond = PackageConvert.order_cond(pkg.OrdClass)
        self.order_lot = PackageConvert.order_lot(pkg.OrdLot)
        self.price = pkg.PriceN
        self.quantity = pkg.DealQtyN
        # self.web_id
        # self.custom_field
        # self.ts

class FuturesDeal(DealRPT):
    subaccount : (str) # 子帳號
    security_type : (str) # 商品類別
    delivery_month : (str) # 交割月份
    strike_price : (float) # 履約價
    option_right : (str) # {Future, OptionCall, OptionPut}
    market_type : (str) # {Day, Night}

    def __init__(self, pkg:PT02011):
        # print(pkg)
        self.trade_id = pkg.CNT
        # self.seqno
        self.ordno = pkg.OrderNo
        self.exchange_seq = pkg.MarketNo
        self.broker_id = pkg.BrokerId
        self.account_id = pkg.Account
        self.action = PackageConvert.action(pkg.Side)
        self.code = pkg.Symbol
        self.price = pkg.DealPrice
        self.quantity = pkg.DealQty
        # self.subaccount
        self.security_type = pkg.Market
        # self.delivery_month 
        # self.strike_price
        # self.option_right
        # self.market_type
        # self.ts