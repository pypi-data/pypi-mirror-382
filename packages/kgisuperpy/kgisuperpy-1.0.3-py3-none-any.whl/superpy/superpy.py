from TradeCom import TradeCom as tradeCom
from QuoteCom import Quote as quoteCom
from IntelligencePy import *
from PackagePy import *

from account import Account, AccountType, FutureAccount, StockAccount
from contracts import (
    # BaseContract,
    # ComboContract,
    Contract,
    Contracts,
    FetchStatus,
    Future,
    Index,
    Option,
    Stock,
)
from order import (
    # ComboOrder,
    Order,
    # OrderDealRecords,
    # StrictInt,
    Trade,
    # ComboTrade,
    # conint,
    OrderStatus,
    Deal
)
from constant import (
    Action,
    Exchange,
    OrderState,
    SecurityType,
    Status,
    Unit,
    ScannerType,
    TicksQueryType,
    QuoteType,
    QuoteVersion,
    OrderType,
    StockPriceType,
    StockOrderLot,
    StockOrderCond,
    FuturesPriceType,
    FuturesOCType,
)

from stream_data_type import *

import typing
from datetime import datetime
import time

from quote import Quote
from report import OrderReport

class SuperPy:
    """SuperPy api

    Functions:
        login
        logout
        activate_ca
        list_accounts
        set_default_account
        get_account_margin
        get_account_openposition
        get_account_settle_profitloss
        get_stock_account_funds
        get_stock_account_unreal_profitloss
        get_stock_account_real_profitloss
        place_order
        update_order
        update_status
        list_trades

    Objects:
        Quote
        Contracts
        Order
    """
    def __init__(self, simulation: bool = True, **kwargs):
        self.quote: Quote
        self.stock_account = None
        self.futopt_account = None
        self.Order = Order
        self.trade_host = 'itrade.kgi.com.tw'   #交易正式環境
        self.quote_host = 'iquote.kgi.com.tw'   #行情正式環境
        self.simulation = simulation
        self.__update_status_condition = {}
        self.__setup_com(**kwargs)

    def __setup_com(self, **kwargs):
        if self.simulation: #僅用測試環境domain
            self.trade_host = 'itradetest.kgi.com.tw'
            self.quote_host = 'iquotetest.kgi.com.tw'
        
        #手動修改
        self.trade_host = kwargs.get('trade_host') if kwargs.get('trade_host') else self.trade_host
        self.quote_host = kwargs.get('quote_host') if kwargs.get('quote_host') else self.quote_host

        sid = 'API'
        token = 'b6eb'   
        port = 8000

        self.__tradeCom = tradeCom(self.trade_host, port, sid, callback=lambda dt,dic : {})
        self.__quoteCom = quoteCom(self.quote_host, port, sid, token)
        self.Contracts = Contracts(Com=self.__quoteCom)
        self.quote = Quote(self.__quoteCom)
        self.__orderReport = OrderReport(self.__tradeCom)

    def fetch_contracts(
        self,
        contract_download: bool = False,
        contracts_timeout: int = 0,
        contracts_cb: typing.Callable[[], None] = None,
    ):
        if contract_download and self.Contracts.status == FetchStatus.Unfetch:
            self.Contracts.status = FetchStatus.Fetching

            if self.stock_account is not None:
                for market in ["TSE","OTC"]:
                    self.__quoteCom.RetriveProduct(market)
            if self.futopt_account is not None:
                self.__quoteCom.LoadTaifexProductXML()

            self.Contracts.status = FetchStatus.Fetched

    #region Login

    def login(
        self,
        userID: str,
        password: str,
        fetch_contract: bool = True,
        contracts_timeout: int = 0,
        contracts_cb: typing.Callable[[], None] = None,
        subscribe_trade: bool = True,
        receive_window: int = 30000,
        loginInfos = None,
    ) -> typing.List[Account]:
        
        self.__uid = userID
        self.__tradeCom.Login(userID, password, subscribe_trade, loginInfos=loginInfos)
        self.__quoteCom.Login(userID, password)
        accounts = self.list_accounts()

        if fetch_contract:
            self.fetch_contracts(fetch_contract, contracts_timeout, contracts_cb)

        return accounts

    def logout(self) -> bool:
        self.__tradeCom.Logout()
        self.__tradeCom.Dispose()

        self.__quoteCom.Logout()
        self.__quoteCom.Dispose()
    
    #endregion

    #region Account

    def list_accounts(self) -> typing.List[Account]:
        """list all account you have"""
        accounts = []
        for acc in self.__tradeCom.accounts:
            _acc = (self.__uid, acc.BrokeId, acc.Account, bool(acc.ISCASIGN), acc.TRADER)
            if AccountType(acc.AccountFlag) == AccountType.Stock:
                _account = StockAccount(*_acc)
            elif AccountType(acc.AccountFlag) == AccountType.Future:
                _account = FutureAccount(*_acc)
            else:
                pass
            self.set_default_account(_account)
            accounts.append(_account)
        
        return accounts
    
    def set_default_account(self, account):
        """set default account for trade when place order not specific

        Args:
            account (:obj:Account):
                choice the account from listing account and set as default
        """
        if isinstance(account, StockAccount):
            self.stock_account = account
        elif isinstance(account, FutureAccount):
            self.futopt_account = account

    #endregion

    #region Order

    def place_order(
        self,
        contract: Contract,
        order: Order,
        timeout: int = 5000,
        cb: typing.Callable[[Trade], None] = None,
    ) -> Trade:
        
        if not order.account:
            if isinstance(contract, Future) or isinstance(contract, Option):
                order.account = self.futopt_account
            elif isinstance(contract, Stock):
                order.account = self.stock_account
            else:
                # log.error("Please provide the account place to.")
                return None
        
        if isinstance(contract, Stock):
            #region 證券下單
            SECU_ORDER_RPT = self.__tradeCom.Order(
                ordtype=Security_OrdType.OT_NEW,
                ordlot=order.order_lot.MapTo(),
                ordclass=order.order_cond.MapTo() if not order.daytrade_short else Security_Class.SC_DayTrade,
                BrokerId=order.account.broker_id, 
                Account=order.account.account_id, 
                stockid=contract.code, 
                bs= order.action.MapTo(),
                qty=order.quantity, 
                Price=order.price,
                PF=order.price_type.MapTo(),
                subAccount="", 
                AgentID="", 
                OrderNo="", 
                TIF=order.order_type.MapTo()
                )
            # print("Order: {Log}".format(Log=SECU_ORDER_RPT))
            if not SECU_ORDER_RPT:
                return None
            order.ordno=SECU_ORDER_RPT.OrderNo
            order.id=SECU_ORDER_RPT.CNTN

            status=OrderStatus()
            status.id = order.id
            status.status = Status.Submitted if SECU_ORDER_RPT.ErrCode == '0' else Status.Failed
            status.status_code = SECU_ORDER_RPT.ErrCode
            if status.status == Status.Failed:
                status.ErrMsg = SECU_ORDER_RPT.ErrMsg
            status.order_datetime = datetime.strptime(SECU_ORDER_RPT.ClientOrderTimeN, "%Y%m%d%H%M%S%f")
            status.order_quantity = SECU_ORDER_RPT.Qty

            trade = Trade(contract=contract,order=order,status=status)
            #endregion
        elif isinstance(contract, Future) or isinstance(contract, Option):
            #region 期貨下單
            FUT_ORDER_RPT = self.__tradeCom.FutOrder(
                type=ORDER_TYPE.OT_NEW, 
                market=MARKET_FLAG.MF_FUT if isinstance(contract, Future) else MARKET_FLAG.MF_OPT,
                brokerId=order.account.broker_id, 
                account=order.account.account_id, 
                subAccount=order.account.trader,
                symbolId=contract.code, 
                BS=order.action.MapTo(),
                pricefl=order.price_type.MapTo(),
                price=order.price,
                TIF=order.order_type.MapTo(),
                qty=order.quantity,
                pf=order.octype.MapTo(), 
                off=OFFICE_FLAG.OF_AS400
            )            
            # print("Order: {Log}".format(Log=FUT_ORDER_RPT))
            if not FUT_ORDER_RPT:
                return None
            order.ordno=FUT_ORDER_RPT.OrderNo
            order.id=FUT_ORDER_RPT.CNT

            status=OrderStatus()
            status.id = order.id
            status.status = Status.Submitted if FUT_ORDER_RPT.Code == '0' else Status.Failed
            status.status_code = FUT_ORDER_RPT.Code
            if status.status == Status.Failed:
                status.ErrMsg = FUT_ORDER_RPT.ErrMsg
            status.order_datetime = datetime.strptime(FUT_ORDER_RPT.TradeDate + FUT_ORDER_RPT.ReportTime, "%Y%m%d%H%M%S%f")
            status.order_quantity = FUT_ORDER_RPT.AfterQty
            status.web_id = FUT_ORDER_RPT.WebID

            trade = Trade(contract=contract,order=order,status=status)
            #endregion
        return trade

    def update_order(
        self,
        trade: Trade,
        price: float = None,
        qty: int = None,
        timeout: int = 5000,
        cb: typing.Callable[[Trade], None] = None,
    ) -> Trade:
        order=trade.order
        contract=trade.contract
        if price is not None:
            ordtype=Security_OrdType.OT_MODIFY_PRICE
            fut_ordtype=ORDER_TYPE.OT_MODIFY_PRICE
            qty = order.quantity
        elif qty is not None:
            ordtype=Security_OrdType.OT_MODIFY_QTY
            fut_ordtype=ORDER_TYPE.OT_MODIFY_QTY
            price = order.price
        else:
            return None
        
        if isinstance(contract, Stock):
            #region 證券改單
            SECU_ORDER_RPT = self.__tradeCom.Order(
                ordtype=ordtype,
                ordlot=order.order_lot.MapTo(),
                ordclass=order.order_cond.MapTo(),
                BrokerId=order.account.broker_id, 
                Account=order.account.account_id, 
                stockid=contract.code, 
                bs= order.action.MapTo(),
                qty=qty, 
                Price=price,
                PF=order.price_type.MapTo(),
                subAccount="", 
                AgentID="", 
                OrderNo=order.ordno, 
                TIF=order.order_type.MapTo()
                )
            # print("Modify_Order: {Log}".format(Log=SECU_ORDER_RPT.__dict__))

            trade.status.status = Status.Submitted if SECU_ORDER_RPT.ErrCode == '0' else Status.Failed
            trade.status.status_code = SECU_ORDER_RPT.ErrCode
            trade.status.order_datetime = datetime.strptime(SECU_ORDER_RPT.ClientOrderTimeN, "%Y%m%d%H%M%S%f")
            if ordtype == Security_OrdType.OT_MODIFY_PRICE:
                trade.status.modified_price = price
            if ordtype == Security_OrdType.OT_MODIFY_QTY:
                trade.status.cancel_quantity = qty
            #endregion
        elif isinstance(contract, Future) or isinstance(contract, Option):
            #region 期貨改單
            FUT_ORDER_RPT = self.__tradeCom.FutOrder(
                type=fut_ordtype, 
                market=MARKET_FLAG.MF_FUT if isinstance(contract, Future) else MARKET_FLAG.MF_OPT,
                brokerId=order.account.broker_id, 
                account=order.account.account_id, 
                subAccount=order.account.trader,
                symbolId=contract.code, 
                BS=order.action.MapTo(),
                pricefl=order.price_type.MapTo(),
                price=price,
                TIF=order.order_type.MapTo(),
                qty=qty,
                pf=order.octype.MapTo(), 
                off=OFFICE_FLAG.OF_AS400,
                webid=trade.status.web_id,
                cnt=order.id, 
                orderno=order.ordno
            )            
            # print("Order: {Log}".format(Log=FUT_ORDER_RPT))

            trade.status.status = Status.Submitted if FUT_ORDER_RPT.Code == '0' else Status.Failed
            trade.status.status_code = FUT_ORDER_RPT.Code
            trade.status.order_datetime = datetime.strptime(FUT_ORDER_RPT.TradeDate + FUT_ORDER_RPT.ReportTime, "%Y%m%d%H%M%S%f")
            if fut_ordtype == ORDER_TYPE.OT_MODIFY_PRICE:
                trade.status.modified_price = price
            if fut_ordtype == ORDER_TYPE.OT_MODIFY_QTY:
                trade.status.cancel_quantity = qty
            #endregion

        return trade

    def cancel_order(
        self,
        trade: Trade,
        timeout: int = 5000,
        cb: typing.Callable[[Trade], None] = None,
    ) -> Trade:
        order=trade.order
        contract=trade.contract
        if isinstance(contract, Stock):
            #region 證券刪單
            SECU_ORDER_RPT = self.__tradeCom.Order(
                ordtype=Security_OrdType.OT_CANCEL,
                ordlot=order.order_lot.MapTo(),
                ordclass=order.order_cond.MapTo(),
                BrokerId=order.account.broker_id, 
                Account=order.account.account_id, 
                stockid=contract.code, 
                bs= order.action.MapTo(),
                qty=order.quantity, 
                Price=order.price,
                PF=order.price_type.MapTo(),
                subAccount="", 
                AgentID="", 
                OrderNo=order.ordno, 
                TIF=order.order_type.MapTo()
                )
            # print("Cancel_Order: {Log}".format(Log=SECU_ORDER_RPT.__dict__))

            trade.status.status_code = SECU_ORDER_RPT.ErrCode
            trade.status.order_datetime = datetime.strptime(SECU_ORDER_RPT.ClientOrderTimeN, "%Y%m%d%H%M%S%f")
            trade.status.status = Status.Cancelled if SECU_ORDER_RPT.ErrCode == '0' else Status.Failed
            trade.status.cancel_quantity = SECU_ORDER_RPT.BeforeQtyN
            #endregion
        elif isinstance(contract, Future) or isinstance(contract, Option):
            #region 期貨刪單
            FUT_ORDER_RPT = self.__tradeCom.FutOrder(
                type=ORDER_TYPE.OT_CANCEL, 
                market=MARKET_FLAG.MF_FUT if isinstance(contract, Future) else MARKET_FLAG.MF_OPT,
                brokerId=order.account.broker_id, 
                account=order.account.account_id, 
                subAccount=order.account.trader,
                symbolId=contract.code, 
                BS=order.action.MapTo(),
                pricefl=order.price_type.MapTo(),
                price=order.price,
                TIF=order.order_type.MapTo(),
                qty=order.quantity,
                pf=order.octype.MapTo(), 
                off=OFFICE_FLAG.OF_AS400,
                webid=trade.status.web_id,
                cnt=order.id, 
                orderno=order.ordno
            )            
            # print("Order: {Log}".format(Log=FUT_ORDER_RPT))

            trade.status.status_code = FUT_ORDER_RPT.Code
            trade.status.order_datetime = datetime.strptime(FUT_ORDER_RPT.TradeDate + FUT_ORDER_RPT.ReportTime, "%Y%m%d%H%M%S%f")
            trade.status.status = Status.Cancelled if FUT_ORDER_RPT.Code == '0' else Status.Failed
            trade.status.cancel_quantity = FUT_ORDER_RPT.BeforeQty
            #endregion

        return trade

    def update_status(
        self,
        account: Account = None,
        trade: Trade = None,
        orderno: str = None,
    ):
        """update status of all trades you have"""

        if trade:
            self.__update_status_condition = { 'trade' : trade }
        elif account:
            if account.signed or self.simulation:
                self.__update_status_condition = { 'account' : account }
        elif orderno:
            self.__update_status_condition = { 'orderno' : orderno }
        else:
            if self.stock_account:
                if self.stock_account.signed or self.simulation:
                    self.__update_status_condition = { 'account' : self.stock_account }
            if self.futopt_account:
                if self.futopt_account.signed or self.simulation:
                    self.__update_status_condition = { 'account' : self.futopt_account }

    def list_trades(self) -> typing.List[Trade]:
        """list all trades"""
        trade = self.__update_status_condition.get('trade')
        orderNo = trade.order.ordno if trade else self.__update_status_condition.get('orderno')
        account = self.__update_status_condition.get('account')

        trades = [self.__combine_trade_by_orderNo(ordNo) \
                  for ordNo in self.__tradeCom.ORDER_RPT_List.keys() \
                    if orderNo is None or orderNo == ordNo]

        if account:
            trades = [trade for trade in trades if vars(trade.order.account) == vars(account)]

        return trades

    def __combine_trade_by_orderNo(self, orderNo) -> Trade:
        trade: Trade = None
        rpt_list = self.__tradeCom.ORDER_RPT_List.get(orderNo, [])
        is_future_report = False
        for rpt in rpt_list:
            if rpt.OrderFunc == 'I':
                trade = self.__build_trade_by_report(rpt)
                is_future_report = (DT(rpt.DT) == DT.FUT_ORDER_RPT)

        if trade is None:
            raise ValueError("order report not found.")        

        if is_future_report:
            rpt_list = sorted(rpt_list, key=lambda rpt: rpt.ReportTime)
        else:
            rpt_list = sorted(rpt_list, key=lambda rpt: rpt.ReportTimeN)

        for rpt in rpt_list:
            if rpt.OrderFunc == 'I':
                continue
            else:
                status = Status.Cancelled if rpt.OrderFunc == 'D' else Status.Submitted
                if isinstance(trade.contract, Stock):
                    trade.status.status = status if rpt.ErrCode == '0' else Status.Failed
                    trade.status.status_code = rpt.ErrCode
                    trade.status.order_datetime = datetime.strptime(rpt.ClientOrderTimeN, "%Y%m%d%H%M%S%f")
                elif isinstance(trade.contract, Future) or isinstance(trade.contract, Option):
                    trade.status.status = status if rpt.Code == '0' else Status.Failed
                    trade.status.status_code = rpt.Code
                    trade.status.order_datetime = datetime.strptime(rpt.TradeDate + rpt.ReportTime, "%Y%m%d%H%M%S%f")

                if rpt.OrderFunc in ['M','R']:
                    trade.status.modified_price = rpt.Price
                else:
                    if isinstance(trade.contract, Stock):
                        trade.status.cancel_quantity += int(rpt.Qty)
                    elif isinstance(trade.contract, Future) or isinstance(trade.contract, Option):
                        trade.status.cancel_quantity += int(rpt.BeforeQty) - int(rpt.AfterQty)

        deal_list = self.__tradeCom.DEAL_RPT_List.get(orderNo, [])
        
        for rpt in deal_list:
            deal = Deal()
            deal.seq = rpt.MarketNo
            if is_future_report:
                deal.price = rpt.DealPrice
                deal.quantity = rpt.DealQty                
            else:
                deal.price = rpt.PriceN
                deal.quantity = rpt.DealQtyN
                
            trade.status.status = Status.Filled if trade.status.order_quantity == deal.quantity else Status.PartFilled                
            if trade.status.deals is None:
                trade.status.deals = []
            trade.status.deals.append(deal)

        return trade

    def __build_trade_by_report(self, orderRpt) -> Trade:
        match DT(orderRpt.DT):
            case DT.SECU_ORDER_RPT:
                contract = self.Contracts.Stocks[orderRpt.StockID]
                orderRpt: PT04010 = orderRpt
            case DT.FUT_ORDER_RPT:
                contract = self.Contracts.Futures[orderRpt.Symbol]
                if contract is None or contract.exchange == 'O':
                    contract = self.Contracts.Options[orderRpt.Symbol]                
                orderRpt: PT02010 = orderRpt

        order_account = [acc for acc in self.list_accounts() \
                         if acc.broker_id == orderRpt.BrokerId and \
                            acc.account_id == orderRpt.Account].pop()

        if isinstance(contract, Stock):
            order = self.Order(
                price=orderRpt.Price,
                quantity=orderRpt.Qty,
                action={'B' : Action.Buy , 'S' : Action.Sell}.get(orderRpt.Side, None),
                price_type={'1' : StockPriceType.MKT , '2' : StockPriceType.LMT , '0' : 'MKP'}.get(orderRpt.PriceFlagN, None),
                order_type={'R':OrderType.ROD, 'I':OrderType.IOC, 'F':OrderType.FOK}.get(orderRpt.TimeInForceN, None),
                order_lot={'0' : StockOrderLot.Common, '2' : StockOrderLot.Fixing, '1' : StockOrderLot.Odd, '4' : StockOrderLot.IntradayOdd}.get(orderRpt.OrdLot, None),
                order_cond={'0' : StockOrderCond.Cash, '3' : StockOrderCond.MarginTrading, '4' : StockOrderCond.ShortSelling}.get(orderRpt.OrdClass, None),
                daytrade_short=True if orderRpt.OrdClass == '9' else False,
                account=order_account
            )
            order.id=orderRpt.CNTN
            order.ordno=orderRpt.OrderNo

            status=OrderStatus()
            status.id = order.id
            status.status = Status.Submitted if orderRpt.ErrCode == '0' else Status.Failed
            status.status_code = orderRpt.ErrCode
            status.order_datetime = datetime.strptime(orderRpt.ClientOrderTimeN, "%Y%m%d%H%M%S%f")
            status.order_quantity = orderRpt.Qty
        elif isinstance(contract, Future) or isinstance(contract, Option):
            order = self.Order(
                price=orderRpt.Price,
                quantity=orderRpt.AfterQty,
                action={'B' : Action.Buy , 'S' : Action.Sell}.get(orderRpt.Side, None),
                price_type={'1' : FuturesPriceType.MKT , '2' : FuturesPriceType.LMT , '0' : FuturesPriceType.MKP}.get(orderRpt.PriceMark, None),
                order_type={'R':OrderType.ROD, 'I':OrderType.IOC, 'F':OrderType.FOK}.get(orderRpt.TimeInForce, None),                
                octype={
                    'A' : FuturesOCType.Auto, 
                    'O' : FuturesOCType.New, 
                    'C' : FuturesOCType.Cover,
                    'T' : FuturesOCType.DayTrade
                    }.get(orderRpt.PositionEffect, None),
                daytrade_short=True if orderRpt.PositionEffect == 'T' else False,
                account=order_account
            )
            order.id=orderRpt.CNT
            order.ordno=orderRpt.OrderNo
            
            status=OrderStatus()
            status.id = order.id
            status.status = Status.Submitted if orderRpt.Code == '0' else Status.Failed
            status.status_code = orderRpt.Code
            status.order_datetime = datetime.strptime(orderRpt.TradeDate + orderRpt.ReportTime, "%Y%m%d%H%M%S%f")
            status.order_quantity = orderRpt.AfterQty
            status.web_id = orderRpt.WebID

        trade = Trade(contract=contract,order=order,status=status)
        return trade

    def set_order_callback(
        self, func: typing.Callable[[OrderState, dict], None]
    ) -> None:
        self.__orderReport.set_order_callback(func)

    #endregion

    #region Quote

    def on_tick_stk_v1(
        self, bind: bool = False
    ) -> typing.Callable[[Exchange, TickSTKv1], None]:
        def wrap_deco(
            func: typing.Callable[[Exchange, TickSTKv1], None]
        ) -> typing.Callable[[Exchange, TickSTKv1], None]:
            self.quote.set_on_tick_stk_v1_callback(func, bind)
            return func

        return wrap_deco

    def on_tick_fop_v1(
        self, bind: bool = False
    ) -> typing.Callable[[Exchange, TickFOPv1], None]:
        def wrap_deco(
            func: typing.Callable[[Exchange, TickFOPv1], None]
        ) -> typing.Callable[[Exchange, TickFOPv1], None]:
            self.quote.set_on_tick_fop_v1_callback(func, bind)
            return func

        return wrap_deco

    def on_bidask_stk_v1(
        self, bind: bool = False
    ) -> typing.Callable[[Exchange, BidAskSTKv1], None]:
        def wrap_deco(
            func: typing.Callable[[Exchange, BidAskSTKv1], None]
        ) -> typing.Callable[[Exchange, BidAskSTKv1], None]:
            self.quote.set_on_bidask_stk_v1_callback(func, bind)
            return func

        return wrap_deco

    def on_bidask_fop_v1(
        self, bind: bool = False
    ) -> typing.Callable[[Exchange, BidAskFOPv1], None]:
        def wrap_deco(
            func: typing.Callable[[Exchange, BidAskFOPv1], None]
        ) -> typing.Callable[[Exchange, BidAskFOPv1], None]:
            self.quote.set_on_bidask_fop_v1_callback(func, bind)
            return func

        return wrap_deco

    #endregion
