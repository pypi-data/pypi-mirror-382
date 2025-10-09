from IntelligencePy import DT, MARKET_FLAG, RECOVER_STATUS, COM_STATUS
from PackagePy import *
import time

class Future:
    def __init__(self, callback = lambda dt, dic: print(dt, dic)):
        self.quoteCom = None
        self.callback = callback
        self.ProductList = {}
    
    def Future_RcvMessage(self, pkgDT:DT, pkg):
        if pkgDT == DT.QUOTE_I020:
            self.callback(pkgDT, PI20020(pkg))                
        elif pkgDT == DT.QUOTE_I021:                 
            self.callback(pkgDT, PI20021(pkg))
        elif pkgDT == DT.QUOTE_I030: 
            self.callback(pkgDT, PI20030(pkg))
        elif pkgDT == DT.QUOTE_I080: 
            self.callback(pkgDT, PI20080(pkg))
        elif pkgDT == DT.QUOTE_BASE_P08:
            # _PI20008 = PI20008(pkg)
            # self.callback(pkgDT, PI20008(pkg))
            # market = self.ProductList.get(_PI20008.Market, None)
            # if market is None:
            #     market = {}
            # market[_PI20008.Symbol] = _PI20008
            # self.ProductList[_PI20008.Market] = market
            # .append({ _PI20008.Symbol : _PI20008._PROD_NAME})
            # print(_PI20008)
            pass
        else:
            return False
        return True
    
    def Future_GetStatus(self, status:COM_STATUS, msg):
        if status == COM_STATUS.RECOVER_DATA:            
            # print('Future_GetStatus:[' + str(status) + ']:', msg)
            topic = str(msg)[1:]
            if topic not in self.future_RecoverStatus.keys():
                self.future_RecoverStatus[topic] = RECOVER_STATUS.RS_BEGIN
                print('開始回補', topic)
            else:
                self.future_RecoverStatus[topic] = RECOVER_STATUS.RS_DONE
                print('結束回補', topic)

    def Future_RecoverStatus(self, topic, status, count):
        status = RECOVER_STATUS(status)
        self.RecoverStatus[status] = { 'topic' : topic, 'count' : count }
        print(f"Future_RecoverStatus: [{status}] {self.RecoverStatus[status]}")

    def LoadTaifexProductXML(self):
        self.quoteCom.LoadTaifexProductXML()
        for i in range(3000):
            recover_status = self.RecoverStatus.get(RECOVER_STATUS.RS_DONE, None)
            if recover_status is not None:
                return RECOVER_STATUS.RS_DONE
            time.sleep(0.001)
        raise ValueError("download timeout")

    def GetTaifexProductBase(self, symbolId) -> PT01805:
        res = self.quoteCom.GetTaifexProductBase(symbolId)
        if res is None:
            raise ValueError("Need Download")
        return PT01805(res)

    def GetTaifexProductDetail(self, symbolId) -> PT01802:
        res = self.quoteCom.GetTaifexProductDetail(symbolId)
        if res is None:
            raise ValueError("Need Download")
        return PT01802(res)
    
    def RetriveQuoteList(self):
        self.future_RecoverStatus = {}
        res = self.quoteCom.RetriveQuoteList()
        if res < 0:
            errMsg = self.quoteCom.GetSubQuoteMsg(res)
            print(errMsg)
        time.sleep(0.1)
        double_Check = 0    #檢查是否有第二筆下載
        for _ in range(3000):
            if RECOVER_STATUS.RS_BEGIN in self.future_RecoverStatus.values():                
                double_Check = 0
            elif double_Check > 1:
                return 
            else:
                double_Check += 1
            time.sleep(0.001)
        raise ValueError("download timeout")
                

    def GetProdcutBase(self, symbolId) -> PI20008:
        res = self.quoteCom.GetProdcutBase(symbolId)
        if res is None:
            raise ValueError("Need Download")
        return PI20008(res)