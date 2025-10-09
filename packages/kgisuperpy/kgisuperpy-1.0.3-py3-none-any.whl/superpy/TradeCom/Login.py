from IntelligencePy import DT
from IntelligencePy import COM_STATUS
from PackagePy import *
from queue import Queue, Empty
import datetime

class Login:
    def __init__(self, host, port):
        self.tradecom = None
        self.host = host
        self.port = port
        self.accounts = []

        self.__com_status = None
        self.__Com_StatusDict = dict()
        self.__GetStatusQueue = Queue()
        self.__RcvMessageQueue = Queue()

    def Dispose(self):
        """關閉API的元件
        """
        self.tradecom.Dispose()

    def Logout(self):
        """登出API平台
        """
        self.tradecom.Logout()

    def Login(self, uid, pwd, subscribe_report = True, recover_report = True, loginInfos=None):
        """自行登入
        Args:
            uid (_type_): _description_
            pwd (_type_): _description_
        """
        #是否註冊即時回報
        self.tradecom.AutoSubReport = subscribe_report
        self.tradecom.AutoSubReportSecurity = subscribe_report
        #是否回補回報
        self.tradecom.AutoRecoverReport = recover_report
        self.tradecom.AutoRecoverReportSecurity = recover_report

        if loginInfos is None:
            loginInfos = f'{uid},,{pwd}'
        self.tradecom.LoginDirect(self.host, self.port, loginInfos)
        try:
            accountInfos = loginInfos.split("|") #check number of accounts
            for account in accountInfos:
                if len(account) == 0:   #filter empty account
                    continue
                status = self.__GetStatusQueue.get(timeout=5)
                # print(status, self.Com_StatusDict[status])  
                if status is COM_STATUS.LOGIN_READY:
                    pkg = self.__RcvMessageQueue.get(timeout=5)
                    # print(datetime.datetime.now(), "DT=[{dt}] {Log}".format(dt=pkg.DT,Log=pkg.ToLog())) 
                    P1503 = P001503(pkg)
                    if (P1503.Code != 0):
                        continue
                    for _p1503 in P1503.p001503_2:
                        self.accounts.append(_p1503)
                else:
                    print('TradeCom登入失敗' , status, self.__Com_StatusDict.get(status))
        except Empty:
            print('TradeCom登入失敗 Timeout' ,self.__com_status, self.__Com_StatusDict.get(self.__com_status))
        
        # import time
        # for acc in self.accounts:
        #     topic = f'{acc.BrokeId}-{acc.Account}'
        #     while topic not in self.RecoverTopic:
        #         time.sleep(0.01)
        if len(self.accounts) > 0 : print("TradeCom登入成功")
        return self.accounts

    def Login_RcvMessage(self, dt:DT, pkg):
        if dt == DT.LOGIN:
            self.__RcvMessageQueue.put(pkg)
            return True
        else:
            return False
        
    def Login_GetStatus(self, status:COM_STATUS, msg):
        if status in [COM_STATUS.LOGIN_READY, COM_STATUS.CONNECT_FAIL, COM_STATUS.NOVALIDCERT, COM_STATUS.LOGIN_FAIL, COM_STATUS.DISCONNECTED, COM_STATUS.NOCGCSPIAPI]:
            self.__com_status = status
            self.__Com_StatusDict[self.__com_status] = { 'Time' : datetime.datetime.now() , 'Msg' : msg }
            self.__GetStatusQueue.put(status)