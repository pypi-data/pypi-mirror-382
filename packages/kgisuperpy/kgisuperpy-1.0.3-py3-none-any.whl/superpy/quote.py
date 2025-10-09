import typing, abc

from QuoteCom import Quote as quoteCom
from PackagePy import *

from contracts import (
    Contract,
    Contracts,
    Future,
    Index,
    Option,
    Stock,
)
from constant import *
from stream_data_type import (
    TickSTKv1,
    TickFOPv1,
    BidAskSTKv1,
    BidAskFOPv1,
    QuoteSTKv1,
    NewIndex,
)

class Quote:
    def __init__(self, QuoteCom) -> None:
        self.__quoteCom : quoteCom = QuoteCom
        self.__quoteCom.callback = self.__quoteCom_callback

        self.__on_tick_stk_v1_callback = None
        self.__tick_idx = {
            DT.QUOTE_STOCK_INDEX1 : [],
            DT.QUOTE_STOCK_INDEX2 : []
        }    #暫存訂閱Tick的指數商品代號
        self.__on_bidask_stk_v1_callback = None

        self.__on_tick_fop_v1_callback = None
        self.__tick_fop = []    #暫存訂閱Tick的期權商品代號
        self.__on_bidask_fop_v1_callback = None
        self.__bidask_fop = []  #暫存訂閱BidAsk的期權商品代號

        self.__on_new_index_callback = None
        self.__new_idx = [] #暫存訂閱新編指數商品代號

    def __quoteCom_callback(self, pkgDT:DT, pkg):
        # 證券Tick
        if self.__on_tick_stk_v1_callback is not None:
            if pkgDT==DT.QUOTE_STOCK_MATCH1 or pkgDT==DT.QUOTE_STOCK_MATCH2 or \
                pkgDT==DT.QUOTE_ODD_MATCH1 or pkgDT==DT.QUOTE_ODD_MATCH2:
                    Tick = TickSTKv1()
                    pkg = PI31001(pkg)
                    Tick.code = pkg.StockNo
                    Tick.datetime = pkg.Match_Time
                    Tick.amount = pkg.Match_Price
                    Tick.volume = pkg.Match_Qty
                    Tick.total_volume = pkg.Total_Qty
                    Tick.simtrade = not bool(pkg.Status)    #Status 0=試撮 1=非試撮
                    Tick.intraday_odd = 1 if pkgDT==DT.QUOTE_ODD_MATCH1 or pkgDT==DT.QUOTE_ODD_MATCH2 else 0
                    exchange = Exchange.OTC if pkgDT==DT.QUOTE_STOCK_MATCH2 or pkgDT==DT.QUOTE_ODD_MATCH2 else Exchange.TSE
                    self.__on_tick_stk_v1_callback(exchange, Tick)
                    return
            
        # 證券BidAsk
        if self.__on_bidask_stk_v1_callback is not None:
            if pkgDT==DT.QUOTE_STOCK_DEPTH1 or pkgDT==DT.QUOTE_STOCK_DEPTH2 or \
                pkgDT==DT.QUOTE_ODD_DEPTH1 or pkgDT==DT.QUOTE_ODD_DEPTH2:
                    BidAsk = BidAskSTKv1()
                    pkg = PI31002(pkg)
                    # print(pkg)
                    BidAsk.code = pkg.StockNo
                    BidAsk.datetime = pkg.Match_Time
                    BidAsk.bid_price = [level.PRICE for level in pkg.BUY_DEPTH] # 委買價
                    BidAsk.bid_volume = [level.QUANTITY for level in pkg.BUY_DEPTH] # 委買量 (張)
                    # diff_bid_vol (:List:int): 買價增減量 (張)
                    BidAsk.ask_price = [level.PRICE for level in pkg.SELL_DEPTH] # 委賣價
                    BidAsk.ask_volume = [level.QUANTITY for level in pkg.SELL_DEPTH]# 委賣量
                    # diff_ask_vol (:List:int): 賣價增減量 (張)
                    # suspend (bool): 暫停交易
                    BidAsk.simtrade = not bool(pkg.Status)    #Status 0=試撮 1=非試撮
                    BidAsk.intraday_odd = 1 if pkgDT==DT.QUOTE_ODD_DEPTH1 or pkgDT==DT.QUOTE_ODD_DEPTH2 else 0
                    exchange = Exchange.OTC if pkgDT==DT.QUOTE_ODD_DEPTH1 or pkgDT==DT.QUOTE_ODD_DEPTH2 else Exchange.TSE
                    self.__on_bidask_stk_v1_callback(Exchange.TSE, BidAsk)
                    return
            
        # 期貨Tick
        if self.__on_tick_fop_v1_callback is not None:
             if pkgDT in [DT.QUOTE_I020, DT.QUOTE_I022]:
                if pkg.Symbol not in self.__tick_fop:   
                    return
                pkg = PI20020(pkg)
                Tick = TickFOPv1()
                Tick.code = pkg.Symbol
                Tick.datetime = pkg.MatchTime
                Tick.amount = pkg.Price
                Tick.volume = pkg.MatchQuantity
                Tick.total_volume = pkg.MatchTotalQty
                Tick.bid_side_total_vol = pkg.MatchBuyCnt
                Tick.ask_side_total_vol = pkg.MatchSellCnt
                Tick.simtrade = 1 if pkgDT == DT.QUOTE_I022 else 0  #試撮
                
                self.__on_tick_fop_v1_callback(Exchange.TAIFEX, Tick)
                return
        
        # 期貨BidAsk
        if self.__on_bidask_fop_v1_callback is not None:
            if pkgDT in [DT.QUOTE_I080, DT.QUOTE_I082]: 
                if pkg.Symbol not in self.__bidask_fop: 
                    return
                pkg = PI20080(pkg)
                BidAsk = BidAskFOPv1()
                BidAsk.code = pkg.Symbol
                BidAsk.datetime = pkg.DATA_TIME
                BidAsk.bid_price = [level.PRICE for level in pkg.BUY_DEPTH] # 委買價
                BidAsk.bid_volume = [level.QUANTITY for level in pkg.BUY_DEPTH] # 委買量
                BidAsk.ask_price = [level.PRICE for level in pkg.SELL_DEPTH] # 委賣價
                BidAsk.ask_volume = [level.QUANTITY for level in pkg.SELL_DEPTH] # 委賣量
                BidAsk.first_derived_bid_price = pkg.FIRST_DERIVED_BUY_PRICE # 衍生一檔委買價
                BidAsk.first_derived_ask_price = pkg.FIRST_DERIVED_SELL_PRICE # 衍生一檔委賣價
                BidAsk.first_derived_bid_vol = pkg.FIRST_DERIVED_BUY_QTY # 衍生一檔委買量
                BidAsk.first_derived_ask_vol = pkg.FIRST_DERIVED_SELL_QTY # 衍生一檔委賣量
                BidAsk.simtrade = 1 if pkgDT == DT.QUOTE_I082 else 0  #試撮
                
                self.__on_bidask_fop_v1_callback(Exchange.TAIFEX, BidAsk)
                return

        # 指數
        if self.__on_tick_stk_v1_callback is not None:
            if pkgDT in [DT.QUOTE_STOCK_INDEX1, DT.QUOTE_STOCK_INDEX2]:
                _PI31011 = PI31011(pkg)
                PI31011_IDX = _PI31011.IDX
                for contract in self.__tick_idx[pkgDT]:
                    index = int(contract.code) - 1
                    # print(_PI31011.__dict__, _PI31011.Match_Time, PI31011_IDX[index].VALUE)
                    Tick = TickSTKv1()
                    Tick.code = contract.code
                    Tick.datetime = _PI31011.Match_Time
                    Tick.amount = PI31011_IDX[index].VALUE
                    Tick.volume = PI31011_IDX[index].VALUE
                    Tick.total_volume = PI31011_IDX[index].VALUE
                    Tick.symbol = contract.symbol
                    Tick.name = contract.name
                    exchange = Exchange.TSE if pkgDT==DT.QUOTE_STOCK_INDEX1 else Exchange.OTC
                    
                    self.__on_tick_stk_v1_callback(exchange, Tick)
                return

        # 新編指數
        if self.__on_new_index_callback is not None:
            if pkgDT in [DT.QUOTE_STOCK_NEWINDEX1, DT.QUOTE_STOCK_NEWINDEX2]:
                
                if pkg.IndexNo not in self.__new_idx : return

                exchange = Exchange.TSE if pkgDT==DT.QUOTE_STOCK_NEWINDEX1 else Exchange.OTC
                newIndex = NewIndex()
                
                newIndex.IndexNo = pkg.IndexNo
                newIndex.IndexTime = pkg.IndexTime
                newIndex.LastestIndex = pkg.LatestIndex
                
                self.__on_new_index_callback(exchange, newIndex)
                return

    def subNewIndex(
        self,
        code
    ):        
        if len(self.__new_idx) == 0: 
            self.__quoteCom.quoteCom.SubQuotesNewIndex()
        if code not in self.__new_idx : 
            self.__new_idx.append(code)
        

    def unsubNewIndex(
        self,
        code
    ):
        if code in self.__new_idx : 
            self.__new_idx.remove(code)
        if len(self.__new_idx) == 0: 
            self.__quoteCom.quoteCom.UnSubQuotesNewIndex()

    # @abc.abstractmethod
    def subscribe(
        self,
        contract: Contract,
        quote_type: QuoteType = QuoteType.Tick,
        intraday_odd: bool = False,
        # version: QuoteVersion = QuoteVersion.v1,
    ):
        if isinstance(contract, Future) or isinstance(contract, Option):
            self.__quoteCom.quoteCom.SubQuote(contract.code)    # 訂閱報價
            match(quote_type):
                case QuoteType.Tick:
                    if contract.code not in self.__tick_fop : self.__tick_fop.append(contract.code)
                case QuoteType.BidAsk:                    
                    if contract.code not in self.__bidask_fop : self.__bidask_fop.append(contract.code)            
            return
        
        if isinstance(contract, Index):
            self.__quoteCom.quoteCom.SubQuotesIndex()
            if contract.exchange == 'TSE':
                exchange = DT.QUOTE_STOCK_INDEX1
            elif contract.exchange == 'OTC':
                exchange = DT.QUOTE_STOCK_INDEX2
            match(quote_type):
                case QuoteType.Tick:
                    if contract not in self.__tick_idx[exchange] : self.__tick_idx[exchange].append(contract)
            return
        
        if not intraday_odd:
            match(quote_type):
                case QuoteType.Tick:
                    self.__quoteCom.quoteCom.SubQuotesMatch(contract.code) ##訂閱成交資料
                case QuoteType.BidAsk:
                    self.__quoteCom.quoteCom.SubQuotesDepth(contract.code) ##訂閱五檔資料
                case QuoteType.Quote:
                    self.__quoteCom.quoteCom.RetriveLastPriceStock(contract.code) ##查詢整股最新行情資料
        else :
            match(quote_type):
                case QuoteType.Tick:
                    self.__quoteCom.quoteCom.SubQuotesMatchOdd(contract.code) ##訂閱盤中零股成交資料
                case QuoteType.BidAsk:
                    self.__quoteCom.quoteCom.SubQuotesDepthOdd(contract.code)  ##訂閱盤中零股五檔資料
                case QuoteType.Quote:
                    self.__quoteCom.quoteCom.RetriveLastPriceStockOdd(contract.code) ##查詢盤中零股最新行情資料

    # @abc.abstractmethod
    def unsubscribe(
        self,
        contract: Contract,
        quote_type: QuoteType = QuoteType.Tick,
        intraday_odd: bool = False,
        # version: QuoteVersion = QuoteVersion.v1,
    ):
        if isinstance(contract, Future) or isinstance(contract, Option):            
            match(quote_type):
                case QuoteType.Tick:
                    if contract.code in self.__tick_fop : self.__tick_fop.remove(contract.code)
                case QuoteType.BidAsk:                    
                    if contract.code in self.__bidask_fop : self.__bidask_fop.remove(contract.code)
            
            # QuoteCom解訂閱會Tick, BidAsk一起解，先檢查都不使用在解除
            if contract.code not in self.__tick_fop and contract.code not in self.__bidask_fop:            
                self.__quoteCom.quoteCom.UnsubQuotes(contract.code)    # 解除訂閱報價

            return
        
        if isinstance(contract, Index):
            if contract.exchange == 'TSE':
                exchange = DT.QUOTE_STOCK_INDEX1
            elif contract.exchange == 'OTC':
                exchange = DT.QUOTE_STOCK_INDEX2
            match(quote_type):
                case QuoteType.Tick:
                    if contract in self.__tick_idx[exchange] : self.__tick_idx[exchange].remove(contract)

            if len(self.__tick_idx[DT.QUOTE_STOCK_INDEX1]) == 0 and \
                len(self.__tick_idx[DT.QUOTE_STOCK_INDEX2]) == 0:
                #無任一訂閱指數 則解除訂閱
                self.__quoteCom.quoteCom.UnSubQuotesIndex()# 解除訂閱指數
            return

        if not intraday_odd:
            match(quote_type):
                case QuoteType.Tick:
                    self.__quoteCom.quoteCom.UnSubQuotesMatch(contract.code) ##解除訂閱成交資料
                case QuoteType.BidAsk:                    
                    self.__quoteCom.quoteCom.UnSubQuotesDepth(contract.code) ##解除訂閱五檔資料 
                # case QuoteType.Quote:
                    # self.__quoteCom.quoteCom.RetriveLastPriceStock(contract.code) ##查詢整股最新行情資料
        else :
            match(quote_type):
                case QuoteType.Tick:
                    self.__quoteCom.quoteCom.UnSubQuotesMatchOdd(contract.code) ##解除訂閱盤中零股成交資料
                case QuoteType.BidAsk:                    
                    self.__quoteCom.quoteCom.UnSubQuotesDepthOdd(contract.code)  ##解除訂閱盤中零股五檔資料
                # case QuoteType.Quote:
                    # self.__quoteCom.quoteCom.RetriveLastPriceStockOdd(contract.code) ##查詢盤中零股最新行情資料
        
        print('unsubscribe', contract.code, quote_type)

    # @abc.abstractmethod
    def set_on_tick_stk_v1_callback(
        self,
        func: typing.Callable[[Exchange, TickSTKv1], None],
        bind: bool = False,
    ) -> None:
        self.__on_tick_stk_v1_callback = func

    # @abc.abstractmethod
    def set_on_tick_fop_v1_callback(
        self,
        func: typing.Callable[[Exchange, TickFOPv1], None],
        bind: bool = False,
    ) -> None:
        self.__on_tick_fop_v1_callback = func

    # @abc.abstractmethod
    def set_on_bidask_stk_v1_callback(
        self,
        func: typing.Callable[[Exchange, BidAskSTKv1], None],
        bind: bool = False,
    ) -> None:
        self.__on_bidask_stk_v1_callback = func

    # @abc.abstractmethod
    def set_on_bidask_fop_v1_callback(
        self,
        func: typing.Callable[[Exchange, BidAskFOPv1], None],
        bind: bool = False,
    ) -> None:
        self.__on_bidask_fop_v1_callback = func

    def set_on_new_index_callback(
        self,
        func: typing.Callable[[Exchange, NewIndex], None],
        bind: bool = False,
    ) -> None:
        self.__on_new_index_callback = func