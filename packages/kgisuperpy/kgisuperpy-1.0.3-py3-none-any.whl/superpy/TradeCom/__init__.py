import sys, os
import clr
from queue import Queue, Empty
import datetime, time
import json
from System import Decimal as CSDecimal

assembly_path = os.path.dirname(__file__)
sys.path.append(assembly_path)
clr.AddReference("TradeCom")     #必要引用dll

from Smart import TaiFexCom
from IntelligencePy import DT
from IntelligencePy import COM_STATUS
from IntelligencePy import RECOVER_STATUS

from PackagePy import *
from Login import Login
from Stock.Order import Order
from Stock.Report import Report
from Future.Order import Order as FutOrder
from Future.Report import Report as FutReport

class TradeCom(Login, Order, Report, FutOrder, FutReport):
    def __init__(self, host, port, sid, timeout=5000, callback = lambda dt, dic: print(dt, dic)) -> None:
        """程式初始化

        Args:
            host (str): 主機連線的host
            port (num): 主機連線的port
            sid (str):  主機連線的sid
        """
        self.__RequestIdDict = dict()
        self.__CNTDict = dict()
        self.__ORDER_RPT_List = dict()
        self.__DEAL_RPT_List = dict()

        Login.__init__(self, host, port)
        Order.__init__(self, self.__RequestIdDict)
        Report.__init__(self, self.__RequestIdDict, self.__CNTDict, self.__ORDER_RPT_List, self.__DEAL_RPT_List)
        FutOrder.__init__(self, self.__RequestIdDict)
        FutReport.__init__(self, self.__RequestIdDict, self.__CNTDict, self.__ORDER_RPT_List, self.__DEAL_RPT_List)

        self.sid = sid
        self.callback = callback
        self.tradecom = TaiFexCom("", port, sid)
        self.tradecom.ConnectTimeout = timeout
        print("TradeCom API 初始化 Version (%s) ........" % (self.tradecom.version))
        # register event handler
        #狀態通知事件KGI Tradecom API message event
        self.tradecom.OnRcvMessage += self.onTradeRcvMessage
        #資料接收事件KGI Tradecom API status event
        self.tradecom.OnGetStatus += self.onTradeGetStatus
        #資料回補事件KGI Tradecom API Recover event
        self.tradecom.OnRecoverStatus += self.onTradeRecoverStatus
        #資料回補事件KGI Tradecom API Server Time event
        self.tradecom.OnRcvServerTime += self.onTradeRcvServerTime

        #是否回下載商品檔
        # self.tradecom.AutoRetriveProductInfo=True

        self.debug = True   #正式/模擬環境

        self.com_status = None
        self.Com_StatusDict = dict()
        self.GetStatusQueue = Queue()
        self.RcvMessageQueue = Queue()
        # self.RecoverTopic = list()
    
    #region 回報
    def onTradeRcvMessage(self, sender, pkg): 
        try:
            pkgDT = DT(pkg.DT)
            if self.Login_RcvMessage(pkgDT, pkg):                
                pass
            elif self.Stock_RcvMessage(pkgDT, pkg):
                pass
            elif self.Future_RcvMessage(pkgDT, pkg):
                pass
            else:
                self.callback(pkgDT, PackageBase(pkg))
                pass
        except Exception as e:
            print('Exception.RcvMessage', e)

    def onTradeGetStatus(self, sender, status, msg):
        try:            
            self.com_status = COM_STATUS(status)
            if self.com_status == COM_STATUS.ACK_REQUESTID:
                python_bytes = bytes(msg)
                smsg = int.from_bytes(python_bytes[0:8], "little")
            else:
                smsg = bytes(msg).decode('UTF-8','strict')
            self.Com_StatusDict[self.com_status] = { 'Time' : datetime.datetime.now() , 'Msg' : smsg }
            # print('onTradeGetStatus:[' + str(status) + ']:' + smsg)
            self.Login_GetStatus(self.com_status, smsg)
        except Exception as e:
            print('Exception.GetStatus', status, e)

    def onTradeRecoverStatus(self, sender, topic, status, count):
        try:
            status = RECOVER_STATUS(status)
            if (status==RECOVER_STATUS.RS_DONE):
                #回補資料結束
                if (count==0):
                    print("結束回補 Topic:["+topic+"]")
                else: 
                    print("結束回補 Topic=[{tp}], 筆數=[{count}]".format(tp=topic, count=count))
                # self.RecoverTopic.append(topic)
            elif (status==RECOVER_STATUS.RS_BEGIN):
                #開始回補資料
                print("開始回補 Topic:["+topic+"]")
            else:
                print("OnRecoverStatus Topic=[{tp}], Status=[{status}], 筆數=[{count}]".format(tp=topic, status=status, count=count))
        except Exception as e:
            print('Exception.RecoverStatus', e)

    def onTradeRcvServerTime(self, sender, time, quality):
        try:
            # print('onTradeRcvServerTime', time, quality)
            self.callback(DT.NOTICE, f'onTradeRcvServerTime, {time}, {quality}')
        except Exception as e:
            print('Exception.RcvServerTime', e)
    #endregion

    def getPkg(self, queue, timeout: float = 3):
        try:            
            pkg = queue.get(timeout=timeout)            
        except Empty:
            print('Receive Ack Timeout')
            return None
        
        return pkg
    
    @property
    def ORDER_RPT_List(self):
        return self.__ORDER_RPT_List
    
    @property
    def DEAL_RPT_List(self):
        return self.__DEAL_RPT_List