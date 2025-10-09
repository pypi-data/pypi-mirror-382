# import sys, os
# import clr
import re
from IntelligencePy import DT
# assembly_path = os.path.dirname(__file__)
# sys.path.append(assembly_path)
# clr.AddReference("Package")     #必要引用dll
from System import Decimal

class PackageBase:
    Key_pattern = r'^__.*__$'
    def __init__(self, pkg):
        # everything = {k: getattr(pkg, k) for k in dir(pkg)}
        self.__dict__ = dict()
        for key in dir(pkg):
            attr = getattr(pkg, key)
            if not callable(attr) and \
                not re.match(self.Key_pattern, key) and \
                type(attr) in (int, float, bool, str, type(None), Decimal):                
                self.__dict__[key] = attr
            # print(key, attr, type(attr))
            if 'Package.FIVE_LEVEL_PRICE' in str(type(attr)):
                # print(key, attr, type(attr))
                self.__dict__[key] = attr
    
    def __str__(self):
        return str(self.__dict__)

    def ToLog(self, Columns=[]):
        Log = {}
        for col in Columns:
            Log[col] = self.__dict__.get(col, None)
        return Log
    
#region Code Tool
class PackageCode(PackageBase):
    def __init__(self, pkg):
        super().__init__(pkg)
        print(self.__dict__)
        for key in self.__dict__:
            _type = type(self.__dict__[key])
            # print("self.{key} = pkg.{key} # {type}".format(key=key,type=_type))
            # if _type in (float, Decimal):
            if 'System.Decimal' in str(_type):
                print(f'self.{key} = float(str(pkg.{key}))')
            elif 'Package.FIVE_LEVEL_PRICE' in str(_type):
                print(f'self.{key} = FIVE_LEVEL_PRICE.Build(pkg.{key})')
            else:
                print(f'self.{key} = pkg.{key}')

from Package import PI30002
def PaserPkg(package):
    pkg = package.__dict__
    for key in pkg:
        value = pkg.get(key)
        types = str(type(value))
        if key.count('__') > 1:
            pass
        elif 'CLR.MethodObject' in types:
            pass
        else:
            # print(key, value, type(value))        
            if 'System.Decimal' in str(value):
                print(f'self.{key} = float(str(pkg.{key})) #{value}')
            elif 'Package.FIVE_LEVEL_PRICE' in str(value):
                print(f'self.{key} = FIVE_LEVEL_PRICE.Build(pkg.{key})')
            else:
                print(f'self.{key} = pkg.{key} #{value}')

# PaserPkg(PI30002)
#endregion

#region 登入
class P001503(PackageBase):
    def __init__(self, pkg):
        self.Code = pkg.Code
        self.Name = pkg.Name
        self.TEMP = pkg.TEMP
        self.Count = pkg.Count
        self.ID = pkg.ID
        self.EncryID = pkg.EncryID
        self.CA_YMD = pkg.CA_YMD
        self.CA_FLAG = pkg.CA_FLAG
        self.CA_TYPE = pkg.CA_TYPE
        self.CA_YMDW = pkg.CA_YMDW
        self.Qnum = pkg.Qnum
        self.Layout = pkg.Layout
        self.LoginType = pkg.LoginType
        self.FixIP = pkg.FixIP
        self.FixPort = pkg.FixPort
        self.FixSessID = pkg.FixSessID
        self.QIdx = pkg.QIdx
        self.ActCntMatch = pkg.ActCntMatch
        self.PWD_REMIND = pkg.PWD_REMIND
        self.ID_PWD = pkg.ID_PWD
        self.p001503_2 = [P001503_2(p1503_2) for p1503_2 in pkg.p001503_2]

class P001503_2(PackageBase):
    def __init__(self, p1503_2):
        self.BrokeId = p1503_2.BrokeId
        self.Account = p1503_2.Account
        self.AccountFlag = p1503_2.AccountFlag
        self.AE = p1503_2.AE
        self.Center = p1503_2.Center
        self.AUTHORIZED = p1503_2.AUTHORIZED
        self.ACClass = p1503_2.ACClass
        self.AC_CREDITION = p1503_2.AC_CREDITION
        self.ISCASIGN = p1503_2.ISCASIGN
        self.AC_SBL_STUS = p1503_2.AC_SBL_STUS
        self.InternalOrder = p1503_2.InternalOrder
        self.InternalOrderIP = p1503_2.InternalOrderIP
        self.DayTrade = p1503_2.DayTrade
        self.MIT = p1503_2.MIT
        self.IB = p1503_2.IB
        self.NoCertIP = p1503_2.NoCertIP
        self.GROUP = p1503_2.GROUP
        self.TRADER = p1503_2.TRADER
        self.TRDNAME = p1503_2.TRDNAME
        self.OrderRoute = p1503_2.OrderRoute
        self.isSpeedy = p1503_2.isSpeedy
        self.bForbidenOrder = p1503_2.bForbidenOrder
        self.ID = p1503_2.ID
#endregion
        
#region 證券回報
class PT04002(PackageBase):
    def __init__(self, pkg):
        pass

class PT06002(PackageBase):
    def __init__(self, pkg):
        self.CNT = pkg.CNT
        self.DT = pkg.DT
        self.ErrorCode = pkg.ErrorCode
        self.RequestId = pkg.RequestId
        self.TOPIC = pkg.TOPIC
        self.UserNo = pkg.UserNo
        self.WEBID = pkg.WEBID

class PT04010(PackageBase):
    def __init__(self, pkg):
        self.Account = pkg.Account
        self.AfterQty = pkg.AfterQty
        self.AfterQtyN = pkg.AfterQtyN
        self.AgentId = pkg.AgentId
        self.BeforeQty = pkg.BeforeQty
        self.BeforeQtyN = pkg.BeforeQtyN
        self.BrokerId = pkg.BrokerId
        self.CNT = pkg.CNT
        self.CNTN = pkg.CNTN
        self.Channel = pkg.Channel
        self.ChannelN = pkg.ChannelN
        self.ClientOrderTime = pkg.ClientOrderTime
        self.ClientOrderTimeN = pkg.ClientOrderTime.ljust(20, '0') if len(pkg.ClientOrderTimeN) == 6 else pkg.ClientOrderTimeN
        self.DT = pkg.DT
        self.ErrCode = pkg.ErrCode
        self.ErrMsg = pkg.ErrMsg
        self.Market = pkg.Market
        self.OmniAccount = pkg.OmniAccount
        self.OrdClass = pkg.OrdClass
        self.OrdLot = pkg.OrdLot
        self.OrderFunc = pkg.OrderFunc
        self.OrderNo = pkg.OrderNo
        self.Price = pkg.Price
        self.PriceFlagN = pkg.PriceFlagN
        self.PriceN = pkg.PriceN
        self.Qty = pkg.Qty
        self.ReportTime = pkg.ReportTime
        self.ReportTimeN = pkg.ReportTimeN
        self.Side = pkg.Side
        self.StockID = pkg.StockID
        self.SubAccount = pkg.SubAccount
        self.TOPIC = pkg.TOPIC
        self.TimeInForceN = pkg.TimeInForceN
        self.TradeDate = pkg.TradeDate
        self.UserNo = pkg.UserNo
    
    def ToLog(self):
        Columns = ['OrderNo','OrderFunc','StockID','Side','Price','Qty','TimeInForceN','ReportTimeN','CNTN']
        Log = {}
        for col in Columns:
            Log[col] = self.__dict__.get(col, None)
        return Log

class PT04011(PackageBase):
    def __init__(self, pkg):
        self.Account = pkg.Account
        self.AgentId = pkg.AgentId
        self.AvgPriceN = pkg.AvgPriceN
        self.BrokerId = pkg.BrokerId
        self.CNT = pkg.CNT
        self.CNTN = pkg.CNTN
        self.Channel = pkg.Channel
        self.ChannelN = pkg.ChannelN
        self.DT = pkg.DT
        self.DealQty = pkg.DealQty
        self.DealQtyN = pkg.DealQtyN
        self.Market = pkg.Market
        self.MarketNo = pkg.MarketNo
        self.MarketNoN = pkg.MarketNoN
        self.OmniAccount = pkg.OmniAccount
        self.OrdClass = pkg.OrdClass
        self.OrdLot = pkg.OrdLot
        self.OrderFunc = pkg.OrderFunc
        self.OrderNo = pkg.OrderNo
        self.Price = pkg.Price
        self.PriceFlagN = pkg.PriceFlagN
        self.PriceN = pkg.PriceN
        self.ReportTime = pkg.ReportTime
        self.ReportTimeN = pkg.ReportTimeN
        self.Side = pkg.Side
        self.StockID = pkg.StockID
        self.SubAccount = pkg.SubAccount
        self.SumQtyN = pkg.SumQtyN
        self.TOPIC = pkg.TOPIC
        self.TimeInForceN = pkg.TimeInForceN
        self.TradeDate = pkg.TradeDate
        self.UserNo = pkg.UserNo

    def ToLog(self):
        Columns = ['OrderNo','OrderFunc','StockID','Side','Price','DealQty','TimeInForceN','ReportTimeN','CNTN']
        Log = {}
        for col in Columns:
            Log[col] = self.__dict__.get(col, None)
        return Log
#endregion
    
#region 期貨回報
class PT02002(PackageBase):
    def __init__(self, pkg):
        self.CNT = pkg.CNT
        self.DT = pkg.DT
        self.ErrorCode = pkg.ErrorCode
        self.FrontOffice = pkg.FrontOffice
        self.OrderNo = pkg.OrderNo
        self.RequestId = pkg.RequestId
        self.TOPIC = pkg.TOPIC
        self.UserNo = pkg.UserNo
        self.WEBID = pkg.WEBID
    
    def ToLog(self):
        Columns = ['DT','CNT','ErrorCode','RequestId','UserNo','WEBID']
        Log = super().ToLog(Columns)
        return Log

class PT02010(PackageBase):
    def __init__(self, pkg):
        self.Account = pkg.Account
        self.AfterQty = pkg.AfterQty
        self.BeforeQty = pkg.BeforeQty
        self.BrokerId = pkg.BrokerId
        self.CNT = pkg.CNT
        self.ClientOrderTime = pkg.ClientOrderTime
        self.Code = pkg.Code
        self.DT = pkg.DT
        self.ErrMsg = pkg.ErrMsg
        self.FrontOffice = pkg.FrontOffice
        self.IB = pkg.IB
        self.KeyIn = pkg.KeyIn
        self.OrderFunc = pkg.OrderFunc
        self.OrderNo = pkg.OrderNo
        self.PositionEffect = pkg.PositionEffect
        self.Price = pkg.Price
        self.PriceMark = pkg.PriceMark
        self.ReportTime = pkg.ReportTime
        self.RequestId = pkg.RequestId
        self.Session = pkg.Session
        self.Side = pkg.Side
        self.Symbol = pkg.Symbol
        self.TOPIC = pkg.TOPIC
        self.TaiDelCode = pkg.TaiDelCode
        self.TimeInForce = pkg.TimeInForce
        self.TradeDate = pkg.TradeDate
        self.Trader = pkg.Trader
        self.UserNo = pkg.UserNo
        self.WebID = pkg.WebID
    
    def ToLog(self):
        Columns = ['OrderNo','OrderFunc','Symbol','Side','Price','AfterQty','TimeInForce','ReportTime','CNT','WebID','ErrMsg']
        Log = super().ToLog(Columns)
        return Log

class PT02011(PackageBase):
    def __init__(self, pkg):
        self.Account = pkg.Account
        self.BS1 = pkg.BS1
        self.BS2 = pkg.BS2
        self.BrokerId = pkg.BrokerId
        self.CNT = pkg.CNT
        self.CumQty = pkg.CumQty
        self.DT = pkg.DT
        self.DealPrice = pkg.DealPrice
        self.DealPrice1 = pkg.DealPrice1
        self.DealPrice2 = pkg.DealPrice2
        self.DealQty = pkg.DealQty
        self.FrontOffice = pkg.FrontOffice
        self.IB = pkg.IB
        self.KeyIn = pkg.KeyIn
        self.LeaveQty = pkg.LeaveQty
        self.Market = pkg.Market
        self.MarketNo = pkg.MarketNo
        self.OrderFunc = pkg.OrderFunc
        self.OrderNo = pkg.OrderNo
        self.Qty1 = pkg.Qty1
        self.Qty2 = pkg.Qty2
        self.ReportTime = pkg.ReportTime
        self.RequestId = pkg.RequestId
        self.Session = pkg.Session
        self.Side = pkg.Side
        self.Symbol = pkg.Symbol
        self.Symbol1 = pkg.Symbol1
        self.Symbol2 = pkg.Symbol2
        self.TOPIC = pkg.TOPIC
        self.TradeDate = pkg.TradeDate
        self.Trader = pkg.Trader
        self.UserNo = pkg.UserNo
        self.WebID = pkg.WebID

    def ToLog(self):
        Columns = ['OrderNo','OrderFunc','Symbol','Side','DealPrice','DealQty','TimeInForce','ReportTime','CNT','WebID','ErrMsg']
        Log = super().ToLog(Columns)
        return Log
#endregion
    
class FIVE_LEVEL_PRICE:
    def __init__(self, pkg):
        self.PRICE = float(str(pkg.PRICE))
        self.QUANTITY = pkg.QUANTITY

    @staticmethod
    def Build(DEPTH):
        return [FIVE_LEVEL_PRICE(FIVE_LEVEL) for FIVE_LEVEL in DEPTH]

class INDEX:
    def __init__(self, pkg):
        self.VALUE = pkg.VALUE

    @staticmethod
    def Build(IDX):
        return [INDEX(idx) for idx in IDX]

#region 證券報價

class PI30001(PackageBase):
    def __init__(self, pkg):
        self.DT = pkg.DT
        self.Market = pkg.Market
        self.StockNo = pkg.StockNo
        self.StockName = pkg.StockName
        self.Bull_Price = float(str(pkg.Bull_Price))
        self.Ref_Price = float(str(pkg.Ref_Price))
        self.Bear_Price = float(str(pkg.Bear_Price))
        self.LastTradeDate = pkg.LastTradeDate
        self.IndCode = pkg.IndCode
        self.StkType = pkg.StkType

class PI31001(PackageBase):
    def __init__(self, pkg):
        self.DT = pkg.DT
        self.StockNo = pkg.StockNo
        self.Status = pkg.Status
        self.Match_Time = pkg.Match_Time
        self.Match_Price = float(str(pkg.Match_Price))
        self.Match_Qty = float(str(pkg.Match_Qty))
        self.Total_Qty = float(str(pkg.Total_Qty))
        self.Source = pkg.Source

class PI31002(PackageBase):
    def __init__(self, pkg):
        self.DT = pkg.DT
        self.StockNo = pkg.StockNo
        self.Status = pkg.Status
        self.Match_Time = pkg.Match_Time
        self.Source = pkg.Source
        self.BUY_DEPTH = FIVE_LEVEL_PRICE.Build(pkg.BUY_DEPTH)
        self.SELL_DEPTH = FIVE_LEVEL_PRICE.Build(pkg.SELL_DEPTH)

class PI31011(PackageBase):
    def __init__(self, pkg):
        self.DT = pkg.DT
        self.COUNT = pkg.COUNT
        self.Match_Time = pkg.Match_Time
        self.IDX = INDEX.Build(pkg.IDX)
        # self.IDXs = [pkg.IDX[idx].VALUE for idx in range(pkg.COUNT)]
        self.TOPIC = pkg.TOPIC
        self.UserNo = pkg.UserNo

class PI30026(PackageBase):
    def __init__(self, pkg):
        self.DT = pkg.DT
        self.StockNo = pkg.StockNo
        self.LastMatchPrice = float(str(pkg.LastMatchPrice))
        self.DayHighPrice = float(str(pkg.DayHighPrice))
        self.DayLowPrice = float(str(pkg.DayLowPrice))
        self.FirstMatchPrice = float(str(pkg.FirstMatchPrice))
        self.FirstMatchQty = pkg.FirstMatchQty
        self.ReferencePrice = float(str(pkg.ReferencePrice))
        self.LastMatchQty = pkg.LastMatchQty
        self.TotalMatchQty = pkg.TotalMatchQty
        self.BUY_DEPTH = FIVE_LEVEL_PRICE.Build(pkg.BUY_DEPTH)
        self.SELL_DEPTH = FIVE_LEVEL_PRICE.Build(pkg.SELL_DEPTH)
        self.DayTradeMark = pkg.DayTradeMark

class PI31026(PackageBase):
    class _IDX:
        __INDEX_TSE = {
            '1' : '加權指數',
            '2' : '不含金融指數',
            '3' : '不含電子指數',
            '4' : '化學工業',
            '5' : '生技醫療業',
            '6' : '水泥窯製',
            '7' : '食品',
            '8' : '塑膠化工',
            '9' : '紡織纖維',
            '10' : '機電',
            '11' : '造紙',
            '12' : '營造建材',
            '13' : '雜項',
            '14' : '金融保險',
            '15' : '水泥工業',
            '16' : '食品工業',
            '17' : '塑膠工業',
            '18' : '紡織纖維',
            '19' : '電機機械',
            '20' : '電器電纜',
            '21' : '化學生技醫療',
            '22' : '玻璃陶瓷',
            '23' : '造紙工業',
            '24' : '鋼鐵工業',
            '25' : '橡膠工業',
            '26' : '汽車工業',
            '27' : '電子工業',
            '28' : '建材營造',
            '29' : '航運業',
            '30' : '觀光事業',
            '31' : '金融保險',
            '32' : '貿易百貨',
            '33' : '其他',
            '34' : '未含金電股發行量加權股價指數',
            '35' : '油電燃氣業',
            '36' : '半導體業',
            '37' : '電腦及週邊設備業',
            '38' : '光電業',
            '39' : '通信網路業',
            '40' : '電子零組件業',
            '41' : '電子通路業',
            '42' : '資訊服務業',
            '43' : '其他電子業'
        }
        __INDEX_OTC = {
            '1' : '櫃檯買賣發行量加權股價指數',
            '2' : '電子工業類指數',
            '3' : '食品工業類指數',
            '4' : '塑膠工業類指數',
            '5' : '紡織纖維類指數',
            '6' : '電機機械類指數',
            '7' : '電器電纜類指數',
            '8' : '玻璃陶瓷類指數',
            '9' : '鋼鐵工業類指數',
            '10' : '橡膠工業類指數',
            '11' : '建材營造類指數',
            '12' : '航運業指數',
            '13' : '觀光事業類指數',
            '14' : '金融業指數',
            '15' : '貿易百貨類指數',
            '16' : '化學工業類指數',
            '17' : '生技醫療類指數',
            '18' : '油電燃氣業指數',
            '19' : '半導體業指數',
            '20' : '電腦及週邊設備業指數',
            '21' : '光電業指數',
            '22' : '通信網路業指數',
            '23' : '電子零組件業指數',
            '24' : '電子通路業指數',
            '25' : '資訊服務業指數'
        }
        def __init__(self, dt, index, IDX):
            self.code = str(index)
            _INDEX = self.__INDEX_TSE if dt == DT.QUOTE_LAST_INDEX1 else self.__INDEX_OTC
            self.name = _INDEX.get(self.code, None)            
            self.ref = IDX.RefIndex
            self.open = IDX.FirstIndex
            self.last = IDX.LastIndex
            self.high = IDX.DayHighIndex
            self.low = IDX.DayLowIndex

        def __str__(self):
            return str(self.__dict__)
        
        @staticmethod
        def Build(pkg):
            if DT(pkg.DT) == DT.QUOTE_LAST_INDEX1:
                return [PI31026._IDX(DT.QUOTE_LAST_INDEX1, idx+1, pkg.IDX[idx]) for idx in range(pkg.COUNT)]
            elif DT(pkg.DT) == DT.QUOTE_LAST_INDEX2:
                return [PI31026._IDX(DT.QUOTE_LAST_INDEX2, idx+1, pkg.IDX[idx]) for idx in range(pkg.COUNT)]
            else:
                return None

    def __init__(self, pkg):
        self.DT = pkg.DT
        self.COUNT = pkg.COUNT
        self.IDX = self._IDX.Build(pkg)
#endregion
    
#region 期貨報價
class PI20020(PackageBase):
    def __init__(self, pkg):
        self.DT = pkg.DT
        self.InfoSeq = pkg.InfoSeq
        self.LastItem = pkg.LastItem
        self.Market = pkg.Market
        self.MatchBuyCnt = pkg.MatchBuyCnt
        self.MatchQuantity = pkg.MatchQuantity
        self.MatchSellCnt = pkg.MatchSellCnt
        self.MatchTime = pkg.MatchTime
        self.MatchTotalQty = pkg.MatchTotalQty
        self.PriceDecimal = pkg.PriceDecimal
        self.PriceSign = pkg.PriceSign
        self.Price = float(str(pkg.Price))
        self.Symbol = pkg.Symbol
        self.TOPIC = pkg.TOPIC
        self.UserNo = pkg.UserNo

class PI20021(PackageBase):
    def __init__(self, pkg):
        self.DT = pkg.DT
        self.Market = pkg.Market
        self.Symbol = pkg.Symbol
        self.DayHighPrice = float(str(pkg.DayHighPrice))
        self.DayLowPrice = float(str(pkg.DayLowPrice))
        self.MatchTime = pkg.MatchTime
        self.PriceDecimal = pkg.PriceDecimal        
        self.TOPIC = pkg.TOPIC
        self.UserNo = pkg.UserNo

class PI20030(PackageBase):
    def __init__(self, pkg):
        self.BUY_ORDER = pkg.BUY_ORDER
        self.BUY_QUANTITY = pkg.BUY_QUANTITY
        self.DT = pkg.DT
        self.Market = pkg.Market
        self.SELL_ORDER = pkg.SELL_ORDER
        self.SELL_QUANTITY = pkg.SELL_QUANTITY
        self.Symbol = pkg.Symbol
        self.TOPIC = pkg.TOPIC
        self.UserNo = pkg.UserNo

class PI20080(PackageBase):
    def __init__(self, pkg):        
        self.DT = pkg.DT
        self.Market = pkg.Market
        self.Symbol = pkg.Symbol
        self.BUY_DEPTH = FIVE_LEVEL_PRICE.Build(pkg.BUY_DEPTH)
        self.SELL_DEPTH = FIVE_LEVEL_PRICE.Build(pkg.SELL_DEPTH)
        self.FIRST_DERIVED_BUY_PRICE = float(str(pkg.FIRST_DERIVED_BUY_PRICE))
        self.FIRST_DERIVED_BUY_QTY = pkg.FIRST_DERIVED_BUY_QTY
        self.FIRST_DERIVED_SELL_PRICE = float(str(pkg.FIRST_DERIVED_SELL_PRICE))
        self.FIRST_DERIVED_SELL_QTY = pkg.FIRST_DERIVED_SELL_QTY        
        self.PriceDecimal = pkg.PriceDecimal
        self.DATA_TIME = pkg.DATA_TIME
        self.TOPIC = pkg.TOPIC
        self.UserNo = pkg.UserNo
    
    def ToLog(self):
        Columns = ['DT','Market','Symbol',
                   'FIRST_DERIVED_BUY_PRICE','FIRST_DERIVED_BUY_QTY',
                   'FIRST_DERIVED_SELL_PRICE','FIRST_DERIVED_SELL_QTY',
                   'PriceDecimal','DATA_TIME','TOPIC','UserNo']
        Log = {}
        for col in Columns:
            Log[col] = self.__dict__.get(col, None)
        return Log
#endregion

class PI20008(PackageBase):
    def __init__(self, pkg):
        self.DT = pkg.DT
        self.END_DATE = pkg.END_DATE
        self.Market = pkg.Market
        self.PriceDecimal = pkg.PriceDecimal
        self.StrikePriceDecimal = pkg.StrikePriceDecimal
        self.Symbol = pkg.Symbol
        self.SymbolIdx = pkg.SymbolIdx
        self.TOPIC = pkg.TOPIC
        self.UserNo = pkg.UserNo
        self._FALL_LIMIT_PRICE1 = float(str(pkg._FALL_LIMIT_PRICE1))
        self._FALL_LIMIT_PRICE2 = float(str(pkg._FALL_LIMIT_PRICE2))
        self._FALL_LIMIT_PRICE3 = float(str(pkg._FALL_LIMIT_PRICE3))
        self._PROD_KIND = pkg._PROD_KIND
        self._PROD_NAME = pkg._PROD_NAME
        self._REFERENCE_PRICE = float(str(pkg._REFERENCE_PRICE))
        self._RISE_LIMIT_PRICE1 = float(str(pkg._RISE_LIMIT_PRICE1))
        self._RISE_LIMIT_PRICE2 = float(str(pkg._RISE_LIMIT_PRICE2))
        self._RISE_LIMIT_PRICE3 = float(str(pkg._RISE_LIMIT_PRICE3))

class PI30001(PackageBase):
    def __init__(self, pkg):    
        self.Bear_Price = float(str(pkg.Bear_Price)) / 10000
        self.Bull_Price = float(str(pkg.Bull_Price)) / 10000
        self.DT = pkg.DT
        self.IndCode = pkg.IndCode
        self.LastTradeDate = pkg.LastTradeDate
        self.Market = pkg.Market
        self.Ref_Price = float(str(pkg.Ref_Price)) / 10000
        self.StkType = pkg.StkType
        self.StockName = pkg.StockName
        self.StockNo = pkg.StockNo
        self.TOPIC = pkg.TOPIC
        self.UserNo = pkg.UserNo

class PT01802(PackageBase):
    def __init__(self, pkg):
        self.ComId = pkg.ComId
        self.ComType = pkg.ComType
        self.DT = pkg.DT
        self.EndDate = pkg.EndDate
        self.FallPrice = float(str(pkg.FallPrice))
        self.Hot = pkg.Hot
        self.PriceDecimal = pkg.PriceDecimal
        self.RisePrice = float(str(pkg.RisePrice))
        self.StkPriceDecimal = pkg.StkPriceDecimal
        self.TOPIC = pkg.TOPIC
        self.UserNo = pkg.UserNo
        self.isFrom1802PKG = pkg.isFrom1802PKG

class PT01805(PackageBase):
    def __init__(self, pkg):
        self.ComCName = pkg.ComCName
        self.ComEName = pkg.ComEName
        self.ComId = pkg.ComId
        self.ComType = pkg.ComType
        self.ContractType = pkg.ContractType
        self.ContractValue = float(str(pkg.ContractValue))
        self.Currency = pkg.Currency
        self.DDSCComID = pkg.DDSCComID
        self.DDSCExchange = pkg.DDSCExchange
        self.DT = pkg.DT
        self.Exchange = pkg.Exchange
        self.NorValue = pkg.NorValue
        self.PMultiplier = pkg.PMultiplier
        self.PriceDecimal = pkg.PriceDecimal
        self.SPTick = float(str(pkg.SPTick))
        self.StkPriceDecimal = pkg.StkPriceDecimal
        self.TOPIC = pkg.TOPIC
        self.TasType = pkg.TasType
        self.TaxRate = float(str(pkg.TaxRate))
        self.Tick = float(str(pkg.Tick))
        self.UserNo = pkg.UserNo