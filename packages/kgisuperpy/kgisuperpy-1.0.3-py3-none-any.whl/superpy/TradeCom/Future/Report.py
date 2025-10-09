from IntelligencePy import DT
from PackagePy import *

class Report:
    def __init__(self,
                 RequestIds = dict(),
                 CNTs = dict(),
                 ORDER_RPTs = dict(),
                 DEAL_RPTs = dict(),
                 callback = lambda dt, dic: print(dt, dic)):
        
        self.callback = callback        
        self.__RequestIdDict = RequestIds
        self.__CNTDict = CNTs
        self.__ORDER_RPT_List = ORDER_RPTs
        self.__DEAL_RPT_List = DEAL_RPTs

    def Future_RcvMessage(self, pkgDT:DT, pkg):
        if pkgDT == DT.FUT_ORDER_ACK:
            FUT_ORDER_ACK = PT02002(pkg)
            self.callback(pkgDT, FUT_ORDER_ACK)
            if FUT_ORDER_ACK.ErrorCode != 0:
                FUT_ORDER_ACK.ErrMsg = self.tradecom.GetMessageMap(FUT_ORDER_ACK.ErrorCode)
                self.__RequestIdDict[pkg.RequestId].put(FUT_ORDER_ACK)
            else:
                self.__CNTDict[pkg.CNT] = pkg.RequestId

        elif pkgDT == DT.FUT_ORDER_RPT:
            FUT_ORDER_RPT = PT02010(pkg)
            self.callback(pkgDT, FUT_ORDER_RPT)
            if self.__ORDER_RPT_List.get(FUT_ORDER_RPT.OrderNo) is None:
                self.__ORDER_RPT_List[FUT_ORDER_RPT.OrderNo] = [FUT_ORDER_RPT]
            else:
                self.__ORDER_RPT_List[FUT_ORDER_RPT.OrderNo].append(FUT_ORDER_RPT)
            
            RequestId = self.__CNTDict.pop(pkg.CNT, None)    #檢查是否來自ACK
            if RequestId : self.__RequestIdDict[RequestId].put(FUT_ORDER_RPT)

        elif pkgDT == DT.FUT_DEAL_RPT:
            FUT_DEAL_RPT = PT02011(pkg)
            self.callback(pkgDT, FUT_DEAL_RPT)
            if self.__DEAL_RPT_List.get(FUT_DEAL_RPT.OrderNo) is None:
                self.__DEAL_RPT_List[FUT_DEAL_RPT.OrderNo] = [FUT_DEAL_RPT]
            else:
                self.__DEAL_RPT_List[FUT_DEAL_RPT.OrderNo].append(FUT_DEAL_RPT)
        
        else:
            return False
        return True