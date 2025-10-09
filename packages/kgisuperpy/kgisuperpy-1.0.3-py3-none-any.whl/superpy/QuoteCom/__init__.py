import sys, os
import clr
from queue import Queue, Empty
import datetime

assembly_path = os.path.dirname(__file__)
sys.path.append(assembly_path)
clr.AddReference("QuoteCom")     #必要引用dll

from Intelligence import QuoteCom   #from namespace import class
from IntelligencePy import DT 
from IntelligencePy import COM_STATUS, RECOVER_STATUS
from PackagePy import *
from QuoteCom.Login import Login
from QuoteCom.Stock import Stock
from QuoteCom.Future import Future

class Quote(Login, Stock, Future):
    """KGI期貨國內報價的Python API範例程式。
    """
    def __init__(self, host, port, sid, token, callback = lambda dt, dic: print(dt, dic)) -> None:
        """程式初始化

        Args:
            host (str): 主機連線的host
            port (num): 主機連線的port
            sid (str):  主機連線的sid
            token (str): 主機連線的token
        """
        Login.__init__(self, host, port)
        Future.__init__(self)
        Stock.__init__(self)
        self.sid = sid
        self.token = token
        self.callback = callback        
        self.quoteCom = QuoteCom("", port, sid, token)
        print("QuoteCom API 初始化 Version (%s) ........" % (self.quoteCom.version))
        # register event handler
        #資料回補事件KGI QuoteCom API status event
        self.quoteCom.OnRecoverStatus += self.onQuoteRecoverStatus
        #狀態通知事件KGI QuoteCom API message event
        self.quoteCom.OnRcvMessage += self.onQuoteRcvMessage
        #資料接收事件KGI QuoteCom API status event
        self.quoteCom.OnGetStatus += self.onQuoteGetStatus

        self.com_status = None
        self.Com_StatusDict = {}
        self.GetStatusQueue = Queue()
        self.RcvMessageQueue = Queue()
        # self.DTlist = []

    #region 回報
    def onQuoteRecoverStatus(self, sender, topic, status, count):
        try:
            print("onQuoteRecoverStatus: [{topic}] {status} , {count}".format(topic=topic,status=status,count=count))
            status = RECOVER_STATUS(status)
            self.RecoverStatus[status] = { 'topic' : topic, 'count' : count }
            # self.Stock_RecoverStatus(topic, status, count)
            # self.Future_RecoverStatus(topic, status, count)
        except Exception as e:
            print(e)  

    def onQuoteRcvMessage(self, sender, pkg):
        try:
            pkgDT = DT(pkg.DT)
            if self.Login_RcvMessage(pkgDT, pkg):
                pass
            elif self.Stock_RcvMessage(pkgDT, pkg):
                pass
            # elif self.Future_RcvMessage(pkgDT, pkg):
            #     pass
            else:
                self.callback(pkgDT, PackageBase(pkg))
                # if pkgDT not in self.DTlist:
                #     self.DTlist.append(pkgDT)
                #     print(self.DTlist)
                #     PackageCode(pkg)
                
                # print("onTradeRcvMessage: DT=[{DT}({dt})] {Log} ".format(dt=pkg.DT,DT=DT(pkg.DT),Log=pkg.ToLog()))

                # now = datetime.datetime.now()
                # formatted_time = "{:02}{:02}{:02}{:03}".format(now.hour, now.minute, now.second, now.microsecond//1000)
                # time_int = int(formatted_time)
                # diff = time_int - pkg.Match_Time
                # self.callback("1.[{stock}] 資料時間:[{time} - {now}] = {diff}".format(stock=pkg.StockNo,time=pkg.Match_Time,now=time_int,diff=diff))

                pass
        except Exception as e:
            print(e)  
    
    def onQuoteGetStatus(self, sender, status, msg) :
        try:
            self.com_status = COM_STATUS(status)
            smsg = bytes(msg).decode('UTF-8','strict')
            self.Com_StatusDict[self.com_status] = { 'Time' : datetime.datetime.now() , 'Msg' : smsg }
            # print('onTradeGetStatus:[' + str(status) + ']:' + smsg)
            self.Login_GetStatus(self.com_status, smsg)
            self.Future_GetStatus(self.com_status, smsg)
        except Exception as e:
            print(e)
    #endregion
