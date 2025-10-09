from enum import Enum
from IntelligencePy import *

ACTION_BUY = "Buy"
ACTION_SELL = "Sell"

STOCK_PRICE_TYPE_LIMITPRICE = "LMT"
STOCK_PRICE_TYPE_MKT = "MKT"
STOCK_PRICE_TYPE_CLOSE = "Close"

STOCK_ORDER_LOT_COMMON = "Common"  # 整股
STOCK_ORDER_LOT_BLOCKTRADE = "BlockTrade"  # 鉅額
STOCK_ORDER_LOT_FIXING = "Fixing"  # 定盤
STOCK_ORDER_LOT_ODD = "Odd"  # 零股
STOCK_ORDER_LOT_INTRADAY_ODD = "IntradayOdd"  # 零股

STOCK_ORDER_TYPE_COMMON = "Common"  # 整股
STOCK_ORDER_TYPE_BLOCKTRADE = "BlockTrade"  # 鉅額
STOCK_ORDER_TYPE_FIXING = "Fixing"  # 定盤
STOCK_ORDER_TYPE_ODD = "Odd"  # 零股

STOCK_ORDER_COND_CASH = "Cash"  # 現股
STOCK_ORDER_COND_NETTING = "Netting"  # 餘額交割
STOCK_ORDER_COND_MARGINTRADING = "MarginTrading"  # 融資
STOCK_ORDER_COND_SHORTSELLING = "ShortSelling"  # 融券
STOCK_ORDER_COND_EMERGING = "Emerging"  # 興櫃

STOCK_FIRST_SELL_YES = "true"
STOCK_FIRST_SELL_NO = "false"

FUTURES_PRICE_TYPE_LMT = "LMT"
FUTURES_PRICE_TYPE_MKT = "MKT"
FUTURES_PRICE_TYPE_MKP = "MKP"

ORDER_TYPE_ROD = "ROD"
ORDER_TYPE_IOC = "IOC"
ORDER_TYPE_FOK = "FOK"

FUTURES_OCTYPE_AUTO = "Auto"
FUTURES_OCTYPE_NEWPOSITION = "New"
FUTURES_OCTYPE_COVER = "Cover"
FUTURES_OCTYPE_DAYTRADE = "DayTrade"

FUTURES_CALLPUT_FUT = "F"
FUTURES_CALLPUT_CALL = "C"
FUTURES_CALLPUT_PUT = "P"

QUOTE_TYPE_TICK = "tick"
QUOTE_TYPE_BIDASK = "bidask"
QUOTE_TYPE_QUOTE = "quote"


class Action(str, Enum):
    Buy = ACTION_BUY
    Sell = ACTION_SELL

    def MapTo(self):
        return {
            Action.Buy : SIDE_FLAG.SF_BUY,
            Action.Sell : SIDE_FLAG.SF_SELL,
        }.get(self, None)

class OrderType(str, Enum):
    ROD = ORDER_TYPE_ROD
    IOC = ORDER_TYPE_IOC
    FOK = ORDER_TYPE_FOK

    def MapTo(self):
        return {
            OrderType.ROD : TIME_IN_FORCE.TIF_ROD,
            OrderType.IOC : TIME_IN_FORCE.TIF_IOC,
            OrderType.FOK : TIME_IN_FORCE.TIF_FOK
        }.get(self, None)

class StockPriceType(str, Enum):
    LMT = STOCK_PRICE_TYPE_LIMITPRICE
    MKT = STOCK_PRICE_TYPE_MKT
    FallStopPrice = Security_PriceFlag.SP_FallStopPrice
    UnchangePrice = Security_PriceFlag.SP_UnchangePrice
    RiseStopPrice = Security_PriceFlag.SP_RiseStopPrice

    def MapTo(self):
        return {
            StockPriceType.LMT : Security_PriceFlag.SP_FixedPrice,  #限價
            StockPriceType.MKT : Security_PriceFlag.SP_MarketPrice, #市價
            StockPriceType.FallStopPrice : Security_PriceFlag.SP_FallStopPrice, #跌停
            StockPriceType.UnchangePrice : Security_PriceFlag.SP_UnchangePrice,  #平盤
            StockPriceType.RiseStopPrice : Security_PriceFlag.SP_RiseStopPrice   #漲停
        }.get(self, None)

class StockOrderLot(str, Enum):
    Common = STOCK_ORDER_LOT_COMMON  # 整股
    BlockTrade = STOCK_ORDER_LOT_BLOCKTRADE  # 鉅額
    Fixing = STOCK_ORDER_LOT_FIXING  # 定盤
    Odd = STOCK_ORDER_LOT_ODD  # 零股
    IntradayOdd = STOCK_ORDER_LOT_INTRADAY_ODD  # 盤中零股

    def MapTo(self):
        return {
            StockOrderLot.Common : Security_Lot.Even_Lot,
            StockOrderLot.Odd : Security_Lot.Odd_Lot,
            StockOrderLot.Fixing : Security_Lot.Fixed_Price,
            StockOrderLot.BlockTrade : Security_Lot.Block_Trade,
            StockOrderLot.IntradayOdd : Security_Lot.Odd_InTraday,
        }.get(self, None)
       

class StockOrderCond(str, Enum):
    Cash = STOCK_ORDER_COND_CASH  # 現股
    # Netting = STOCK_ORDER_COND_NETTING  # 餘額交割
    MarginTrading = STOCK_ORDER_COND_MARGINTRADING  # 融資
    ShortSelling = STOCK_ORDER_COND_SHORTSELLING  # 融券
    # Emerging = STOCK_ORDER_COND_EMERGING  # 興櫃
    ShortUnLimit = Security_Class.SC_ShortUnLimit   #借券賣出
    EDN = Security_Class.SC_EDN #賣出擔保品

    def MapTo(self):
        return {
            StockOrderCond.Cash : Security_Class.SC_Ordinary,
            StockOrderCond.MarginTrading : Security_Class.SC_SelfMargin,
            StockOrderCond.ShortSelling : Security_Class.SC_SelfShort,
            StockOrderCond.ShortUnLimit : Security_Class.SC_ShortUnLimit,
            StockOrderCond.EDN : Security_Class.SC_EDN
        }.get(self, None)

class FuturesPriceType(str, Enum):
    LMT = FUTURES_PRICE_TYPE_LMT
    MKT = FUTURES_PRICE_TYPE_MKT
    MKP = FUTURES_PRICE_TYPE_MKP

    def MapTo(self):
        return {
            FuturesPriceType.LMT : PRICE_FLAG.PF_SPECIFIED,
            FuturesPriceType.MKT : PRICE_FLAG.PF_MARKET,
            FuturesPriceType.MKP : PRICE_FLAG.PF_MARKET_RANGE,
        }.get(self, None)


class FuturesOCType(str, Enum):
    Auto = FUTURES_OCTYPE_AUTO
    New = FUTURES_OCTYPE_NEWPOSITION
    Cover = FUTURES_OCTYPE_COVER
    DayTrade = FUTURES_OCTYPE_DAYTRADE

    def MapTo(self):
        return {
            FuturesOCType.Auto : POSITION_EFFECT.PE_AUTO,
            FuturesOCType.New : POSITION_EFFECT.PE_OPEN,
            FuturesOCType.Cover : POSITION_EFFECT.PE_CLOSE,
            FuturesOCType.DayTrade : POSITION_EFFECT.PE_DAY_TRADE
        }.get(self, None)

class SecurityType(str, Enum):
    Index = "IND"
    Stock = "STK"
    Future = "FUT"
    Option = "OPT"


class Exchange(str, Enum):
    TSE = "TSE"
    OTC = "OTC"
    OES = "OES"
    TAIFEX = "TAIFEX"


class Currency(str, Enum):
    TWD = "TWD"
    USD = "USD"
    HKD = "HKD"
    GBP = "GBP"
    AUD = "AUD"
    CAD = "CAD"
    SGD = "SGD"
    CHF = "CHF"
    JPY = "JPY"
    ZAR = "ZAR"
    SEK = "SEK"
    NZD = "NZD"
    THB = "THB"
    PHP = "PHP"
    IDR = "IDR"
    EUR = "EUR"
    KRW = "KRW"
    VND = "VND"
    MYR = "MYR"
    CNY = "CNY"


class OptionRight(str, Enum):
    No = ""
    Call = "C"
    Put = "P"


class Status(str, Enum):
    Cancelled = "Cancelled"
    Filled = "Filled"
    # Filling = 'Filling'
    PartFilled = "PartFilled"
    Inactive = "Inactive"
    Failed = "Failed"
    PendingSubmit = "PendingSubmit"
    PreSubmitted = "PreSubmitted"
    Submitted = "Submitted"
    # _DoneStates = {'Cancelled', 'Filled', 'Inactive', 'Failed'}
    # _ActiveStates = {'PendingSubmit', 'PreSubmitted', 'Submitted', 'PartFilled'}


class OrderState(str, Enum):
    StockDeal = "SDEAL"
    StockOrder = "SORDER"
    FuturesOrder = "FORDER"
    FuturesDeal = "FDEAL"


class QuoteType(str, Enum):
    Tick = QUOTE_TYPE_TICK
    BidAsk = QUOTE_TYPE_BIDASK
    Quote = QUOTE_TYPE_QUOTE


class QuoteVersion(str, Enum):
    v1 = "v1"


class DayTrade(str, Enum):
    Yes = "Yes"
    OnlyBuy = "OnlyBuy"
    No = "No"


class TickType(str, Enum):
    No = "None"  # 無法判斷0
    Buy = "Buy"  # 外盤1
    Sell = "Sell"  # 內盤2


class ChangeType(str, Enum):
    LimitUp = "LimitUp"  # 1漲停
    Up = "Up"  # 2漲
    Unchanged = "Unchanged"  # 3平盤
    Down = "Down"  # 4跌
    LimitDown = "LimitDown"  # 5跌停


class Unit(str, Enum):
    Common = "Common"
    Share = "Share"


class TradeType(str, Enum):
    Common = "Common"
    DayTrade = "DayTrade"


class ScannerType(str, Enum):
    ChangePercentRank = "ChangePercentRank"
    ChangePriceRank = "ChangePriceRank"
    DayRangeRank = "DayRangeRank"
    VolumeRank = "VolumeRank"
    AmountRank = "AmountRank"
    TickCountRank = "TickCountRank"


class TicksQueryType(str, Enum):
    AllDay = "AllDay"
    RangeTime = "RangeTime"
    LastCount = "LastCount"
