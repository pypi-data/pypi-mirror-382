from queue import Queue, Empty
from System import Decimal as CSDecimal
from datetime import datetime

from IntelligencePy import ORDER_TYPE
from IntelligencePy import MARKET_FLAG
from IntelligencePy import SIDE_FLAG
from IntelligencePy import PRICE_FLAG
from IntelligencePy import TIME_IN_FORCE
from IntelligencePy import POSITION_EFFECT
from IntelligencePy import OFFICE_FLAG

from PackagePy import PT02010, PT02002

class Order:
    def __init__(self, RequestIds = dict(), callback = lambda dt, dic: print(dt, dic)):
        self.tradecom = None
        self.__RequestIdDict = RequestIds
        self.callback = callback

    def FutOrder(self, type: ORDER_TYPE, market: MARKET_FLAG, 
                 brokerId, account, subAccount, symbolId, 
                 BS: SIDE_FLAG, pricefl: PRICE_FLAG, price, TIF: TIME_IN_FORCE
              , qty, pf: POSITION_EFFECT, off: OFFICE_FLAG, webid = '', cnt= '', orderno= '') -> PT02010:
        

        QTY = int(qty)
        PRICE = CSDecimal(float(price))
        
        RequestId = self.tradecom.GetRequestId()
        print(f"送單 RequestId=[{RequestId}]")
        if type == ORDER_TYPE.OT_NEW:
            res = self.tradecom.Order(ORDER_TYPE.OT_NEW, market, RequestId, brokerId, account, subAccount, symbolId, BS, pricefl, PRICE, TIF, QTY, pf, OFFICE_FLAG.OF_AS400)
        else:
            res = self.tradecom.Order(type, market, RequestId, brokerId, account, subAccount, symbolId, BS, pricefl, PRICE, TIF, QTY, pf, OFFICE_FLAG.OF_AS400, webid, cnt, orderno)
        if res != 0:
            print("委託失敗: ", self.tradecom.GetOrderErrMsg(res))
        else:
            print("委託成功: ")

        self.__RequestIdDict[RequestId] = Queue()
        FUT_ORDER_RPT = self.getPkg(self.__RequestIdDict[RequestId])
        if isinstance(FUT_ORDER_RPT, PT02010):
            return PT02010(FUT_ORDER_RPT)
        elif isinstance(FUT_ORDER_RPT, PT02002):
            FUT_ORDER_RPT.OrderNo = ""
            FUT_ORDER_RPT.Code = FUT_ORDER_RPT.ErrorCode
            FUT_ORDER_RPT.TradeDate = datetime.now().strftime("%Y%m%d")
            FUT_ORDER_RPT.ReportTime = datetime.now().strftime("%H%M%S%f")
            FUT_ORDER_RPT.AfterQty = 0
            FUT_ORDER_RPT.WebID = FUT_ORDER_RPT.WEBID
            return FUT_ORDER_RPT
        else:
            return None