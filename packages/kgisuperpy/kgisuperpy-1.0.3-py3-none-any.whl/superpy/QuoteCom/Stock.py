from IntelligencePy import DT, RECOVER_STATUS
from PackagePy import *
import time
import random
from queue import Queue, Empty
from Intelligence import IdxKind

class Stock:
    def __init__(self, callback = lambda dt, dic: print(dt, dic)):
        self.quoteCom = None
        self.callback = callback
        self.RecoverStatus = {}
    
    def Stock_RcvMessage(self, pkgDT:DT, pkg):
        if pkgDT==DT.QUOTE_STOCK_MATCH1 or pkgDT==DT.QUOTE_STOCK_MATCH2 or \
            pkgDT==DT.QUOTE_ODD_MATCH1 or pkgDT==DT.QUOTE_ODD_MATCH2:
            self.callback(pkgDT, PI31001(pkg))
            pass
        elif pkgDT==DT.QUOTE_STOCK_DEPTH1 or pkgDT==DT.QUOTE_STOCK_DEPTH2 or \
                pkgDT==DT.QUOTE_ODD_DEPTH1 or pkgDT==DT.QUOTE_ODD_DEPTH2:
            self.callback(pkgDT, PI31002(pkg))
            pass
        elif pkgDT==DT.QUOTE_LAST_PRICE_STOCK or pkgDT==DT.QUOTE_LAST_PRICE_ODD:
            self.callback(pkgDT, PI30026(pkg))
            pass
        elif pkgDT==DT.QUOTE_LAST_INDEX1 or pkgDT==DT.QUOTE_LAST_INDEX2:
            _PI31026 = PI31026(pkg)
            if self.__LastIndexQueue:
                self.__LastIndexQueue.put(_PI31026)
            self.callback(pkgDT, _PI31026)
            pass
        elif pkgDT==DT.QUOTE_STOCK_INDEX1 or pkgDT==DT.QUOTE_STOCK_INDEX2:
            self.callback(pkgDT, PI31011(pkg))
            pass
        else:
            return False
        return True
    
    def Stock_RecoverStatus(self, topic, status, count):
        status = RECOVER_STATUS(status)
        self.RecoverStatus[status] = { 'topic' : topic, 'count' : count }
        # print(f"Stock_RecoverStatus: [{status}] {self.RecoverStatus[status]}")

    def RetriveProduct(self, market="TSE"):
        match market:
            case "TSE":
                status = self.quoteCom.RetriveProductTSE()
            case "OTC":
                status = self.quoteCom.RetriveProductOTC() 

        if (status<0): 
            errmsg= self.quoteCom.GetSubQuoteMsg(status)
            raise ValueError(f"'RetriveProduct' market: {market}, Error: {errmsg}")

        for i in range(3000):
            recover_status = self.RecoverStatus.get(RECOVER_STATUS.RS_DONE, None)
            if recover_status is not None:
                return RECOVER_STATUS.RS_DONE
            time.sleep(0.001)
        raise ValueError(f"'RetriveProduct' market: {market}, timeout")
    
    def RetriveLastIndex(self, market="TSE"):
        self.__LastIndexQueue = Queue()     
        match market:
            case "TSE":
                status = self.quoteCom.RetriveLastIndex(IdxKind.IdxKind_List)
            case "OTC":
                status = self.quoteCom.RetriveLastIndex(IdxKind.IdxKind_OTC)         
            case _:
                raise TypeError("market type is wrong.")
            
        if (status<0): 
            errmsg= self.quoteCom.GetSubQuoteMsg(status)            
            raise ValueError(f"'RetriveLastIndex' market: {market}, Error: {errmsg}")

        try:
            pkg:PI31026 = self.__LastIndexQueue.get()
            return pkg
        except Empty:
            raise ValueError(f"'RetriveLastIndex' market: {market}, timeout")

        

    def GetProductList(self, symbolId=None, market="TSE"):
        symbols:list[str]
        match market:
            case "TSE":
                symbols = self.quoteCom.GetProductListTSE()#代碼|名稱|漲停價|參考價|跌停價|上次成交日
            case "OTC":
                symbols = self.quoteCom.GetProductListOTC()#代碼|名稱|漲停價|參考價|跌停價|上次成交日
        
        
        start = time.process_time()
        # for stock in symbols:
        #     temp = stock.split('|')
        #     symbolId = temp[0]
        #     self.GetProductSTOCK(symbolId)
        

        symbolIds = []
        while(len(symbolIds) < 10):
            temp = random.choice(symbols).split('|')
            symbolId = temp[0]
            # if len(symbolId) != 4:
            #     continue
            symbolIds.append(symbolId)
            # Product = self.GetProductSTOCK(symbolId)
            # StockInfo = self.StockInfo(temp)
            # if Product.Bull_Price != StockInfo['Bull_Price'] or \
            #     Product.Ref_Price != StockInfo['Ref_Price'] or \
            #     Product.Bear_Price != StockInfo['Bear_Price'] :
            #     print(Product.StockNo, StockInfo['StockNo'])

        end = time.process_time()
        print("GetProductListTSC process_time 測量時間：%f 秒" % (end - start))
        return symbolIds

    def GetProductSTOCK(self,symbolId) -> PI30001:
        res = self.quoteCom.GetProductSTOCK(symbolId)
        if res is None:            
            raise ValueError("Need Download")
        return PI30001(res)

    def StockInfo(self, pkg):
        #代碼|名稱|漲停價|參考價|跌停價|上次成交日
        return {
            'StockNo' : pkg[0],
            'StockName' : pkg[1],            
            'Bull_Price' : float(str(pkg[2])),
            'Ref_Price' : float(str(pkg[3])),
            'Bear_Price' : float(str(pkg[4])),
            'LastTradeDate' : pkg[5]
        }