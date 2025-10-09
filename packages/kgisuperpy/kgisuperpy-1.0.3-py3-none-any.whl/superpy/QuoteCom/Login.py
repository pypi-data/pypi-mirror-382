from IntelligencePy import DT 
from IntelligencePy import COM_STATUS
from PackagePy import *
from queue import Queue, Empty
import datetime

class Login:
    def __init__(self, host, port):
        self.quoteCom = None
        self.host = host
        self.port = port

        self.__com_status = None
        self.__Com_StatusDict = dict()
        self.__GetStatusQueue = Queue()
        self.__RcvMessageQueue = Queue()

    def Dispose(self):
        """關閉API的元件
        """
        self.quoteCom.Dispose()

    def Logout(self):
        """登出API平台
        """
        self.quoteCom.Logout()

    def Login(self, uid, pwd):
        """自行登入
        Args:
            uid (_type_): _description_
            pwd (_type_): _description_
        """
        self.quoteCom.Connect2Quote(self.host, self.port, uid, pwd, ' ', '')
        accounts = []
        try:
            status = self.__GetStatusQueue.get(timeout=15)
            # print(status, self.Com_StatusDict[status])  
            match status:
                case COM_STATUS.LOGIN_READY:
                    pkg = self.__RcvMessageQueue.get(timeout=5)
                    # print(datetime.datetime.now(), "DT=[{dt}] {Log}".format(dt=pkg.DT,Log=pkg.ToLog())) 
                    P1503 = P001503(pkg)
                    if (P1503.Code==0):
                        print("QuoteCom登入成功")
                        accounts = P1503.p001503_2
                case _:
                    print('QuoteCom登入失敗' , status, self.__Com_StatusDict.get(status))
        except Empty:
            print('QuoteCom登入失敗 Timeout' ,self.__com_status, self.__Com_StatusDict.get(self.__com_status))
        
        return accounts

    def Login_RcvMessage(self, dt:DT, pkg):
        if dt == DT.LOGIN:
            self.__RcvMessageQueue.put(pkg)
            return True
        else:
            return False
        
    def Login_GetStatus(self, status:COM_STATUS, msg):
        if status in [COM_STATUS.LOGIN_READY, COM_STATUS.CONNECT_FAIL, COM_STATUS.NOVALIDCERT, COM_STATUS.LOGIN_FAIL, COM_STATUS.DISCONNECTED]:
            self.__com_status = status
            self.__Com_StatusDict[self.__com_status] = { 'Time' : datetime.datetime.now() , 'Msg' : msg }
            self.__GetStatusQueue.put(status)