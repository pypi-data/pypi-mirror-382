from queue import Queue, Empty
from System import Decimal as CSDecimal
from datetime import datetime

from IntelligencePy import Security_OrdType
from IntelligencePy import Security_Lot
from IntelligencePy import Security_Class
from IntelligencePy import Security_PriceFlag
from IntelligencePy import SIDE_FLAG
from IntelligencePy import TIME_IN_FORCE

from PackagePy import PT04010, PT06002

class Order:
    def __init__(self, RequestIds = dict(), callback = lambda dt, dic: print(dt, dic)):
        self.tradecom = None
        self.__RequestIdDict = RequestIds
        self.callback = callback

    def Order(self, ordtype: Security_OrdType, ordlot: Security_Lot, ordclass: Security_Class,
                BrokerId, Account, stockid, bs: SIDE_FLAG, qty, Price, 
                PF: Security_PriceFlag, subAccount, AgentID, OrderNo, TIF: TIME_IN_FORCE) -> PT04010:
        ordQty=int(qty)
        ordPrz=CSDecimal(float(Price))

        ##取得送單序號,以便回報時對應
        requestId=self.tradecom.GetRequestId()
        # requestId = Int64(rid)
        print("送單 RequestId=[{rid}]".format(rid=requestId))
        rtn = self.tradecom.SecurityOrder(
            requestId, 
            ordtype, 
            ordlot, 
            ordclass, 
            BrokerId, 
            Account, 
            stockid, 
            bs, 
            ordQty, 
            ordPrz, 
            PF, 
            subAccount, 
            AgentID, 
            OrderNo, 
            TIF
        )
        if (rtn != 0):
            print("SecurityOrder Error :"+str(rtn))
            print(self.tradecom.GetOrderErrMsg(rtn))
            raise SyntaxError(f"SecurityOrder Error : {str(rtn)} , {self.tradecom.GetOrderErrMsg(rtn)}")

        self.__RequestIdDict[requestId] = Queue()
        SECU_ORDER_RPT = self.getPkg(self.__RequestIdDict[requestId])
        if isinstance(SECU_ORDER_RPT, PT04010):
            return PT04010(SECU_ORDER_RPT)
        elif isinstance(SECU_ORDER_RPT, PT06002):
            SECU_ORDER_RPT.OrderNo = ""
            SECU_ORDER_RPT.CNTN = SECU_ORDER_RPT.CNT
            SECU_ORDER_RPT.ErrCode = SECU_ORDER_RPT.ErrorCode
            SECU_ORDER_RPT.ClientOrderTimeN = datetime.now().strftime("%Y%m%d%H%M%S%f")
            SECU_ORDER_RPT.Qty = 0
            return SECU_ORDER_RPT
        else:
            return None
