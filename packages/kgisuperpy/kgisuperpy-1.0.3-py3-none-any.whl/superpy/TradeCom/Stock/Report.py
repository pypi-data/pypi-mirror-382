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
    
    def Stock_RcvMessage(self, pkgDT:DT, pkg):
        if pkgDT in [DT.SECU_ORDER_ACK_N, DT.SECU_ORDER_ACK]:            
            SECU_ORDER_ACK_N = PT06002(pkg)
            self.callback(pkgDT, SECU_ORDER_ACK_N)
            if SECU_ORDER_ACK_N.ErrorCode != 0:
                SECU_ORDER_ACK_N.ErrMsg=self.tradecom.GetMessageMap(SECU_ORDER_ACK_N.ErrorCode)
                self.__RequestIdDict[pkg.RequestId].put(SECU_ORDER_ACK_N)
            else:
                self.__CNTDict[pkg.CNT] = pkg.RequestId

        elif pkgDT == DT.SECU_ORDER_RPT:
            SECU_ORDER_RPT = PT04010(pkg)
            self.callback(pkgDT, SECU_ORDER_RPT)
            if self.__ORDER_RPT_List.get(SECU_ORDER_RPT.OrderNo) is None:
                self.__ORDER_RPT_List[SECU_ORDER_RPT.OrderNo] = [SECU_ORDER_RPT]
            else:
                self.__ORDER_RPT_List[SECU_ORDER_RPT.OrderNo].append(SECU_ORDER_RPT)
            
            RequestId = self.__CNTDict.pop(pkg.CNTN, None)    #檢查是否來自ACK
            if RequestId : self.__RequestIdDict[RequestId].put(SECU_ORDER_RPT)

        elif pkgDT == DT.SECU_DEAL_RPT:
            SECU_DEAL_RPT = PT04011(pkg)
            self.callback(pkgDT, SECU_DEAL_RPT)
            if self.__DEAL_RPT_List.get(SECU_DEAL_RPT.OrderNo) is None:
                self.__DEAL_RPT_List[SECU_DEAL_RPT.OrderNo] = [SECU_DEAL_RPT]
            else:
                self.__DEAL_RPT_List[SECU_DEAL_RPT.OrderNo].append(SECU_DEAL_RPT)
        else:
            return False
        return True