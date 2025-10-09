import sys, os
import clr
from enum import Enum

assembly_path = os.path.dirname(__file__)
sys.path.append(assembly_path)
clr.AddReference("Package")     #必要引用dll

from Intelligence import COM_STATUS
from Intelligence import RECOVER_STATUS

from Intelligence import Security_OrdType
from Intelligence import Security_Lot
from Intelligence import Security_Class
from Intelligence import Security_PriceFlag
from Intelligence import SIDE_FLAG
from Intelligence import TIME_IN_FORCE
from Intelligence import ORDER_TYPE
from Intelligence import MARKET_FLAG
from Intelligence import PRICE_FLAG
from Intelligence import POSITION_EFFECT
from Intelligence import OFFICE_FLAG

from DT import *

class COM_STATUS(Enum):    
    CONNECT_READY = COM_STATUS.CONNECT_READY
    CONNECT_FAIL = COM_STATUS.CONNECT_FAIL
    DISCONNECTED = COM_STATUS.DISCONNECTED
    LOGIN_READY = COM_STATUS.LOGIN_READY
    LOGIN_FAIL = COM_STATUS.LOGIN_FAIL
    LOGIN_UNKNOW = COM_STATUS.LOGIN_UNKNOW
    SUBSCRIBE = COM_STATUS.SUBSCRIBE
    UNSUBSCRIBE = COM_STATUS.UNSUBSCRIBE
    HEART_BEAT = COM_STATUS.HEART_BEAT
    ACK_REQUESTID = COM_STATUS.ACK_REQUESTID
    RECOVER_DATA = COM_STATUS.RECOVER_DATA
    LOGIN_FROM_CLOSE = COM_STATUS.LOGIN_FROM_CLOSE
    AS400_CONNECTED = COM_STATUS.AS400_CONNECTED
    AS400_CONNECTFAIL = COM_STATUS.AS400_CONNECTFAIL
    AS400_DISCONNECTED = COM_STATUS.AS400_DISCONNECTED
    QUEUE_WARNING = COM_STATUS.QUEUE_WARNING
    ACCTCNT_NOMATCH = COM_STATUS.ACCTCNT_NOMATCH
    NOVALIDCERT = COM_STATUS.NOVALIDCERT
    NOCGCSPIAPI = COM_STATUS.NOCGCSPIAPI

class RECOVER_STATUS(Enum):
    RS_BEGIN = RECOVER_STATUS.RS_BEGIN
    RS_DONE = RECOVER_STATUS.RS_DONE
    RS_NOAUTHRITY = RECOVER_STATUS.RS_NOAUTHRITY

class Security_OrdType:
    OT_NEW = Security_OrdType.OT_NEW
    OT_CANCEL = Security_OrdType.OT_CANCEL
    OT_MODIFY_QTY = Security_OrdType.OT_MODIFY_QTY
    OT_MODIFY_PRICE = Security_OrdType.OT_MODIFY_PRICE

class Security_Lot:
    Even_Lot = Security_Lot.Even_Lot
    Odd_Lot = Security_Lot.Odd_Lot
    Fixed_Price = Security_Lot.Fixed_Price
    Block_Trade = Security_Lot.Block_Trade
    Odd_InTraday = Security_Lot.Odd_InTraday

class Security_Class:
    SC_Ordinary = Security_Class.SC_Ordinary
    SC_SelfMargin = Security_Class.SC_SelfMargin
    SC_SelfShort = Security_Class.SC_SelfShort
    SC_ShortLimit = Security_Class.SC_ShortLimit
    SC_ShortUnLimit = Security_Class.SC_ShortUnLimit
    SC_DayMargin = Security_Class.SC_DayMargin
    SC_DayShort = Security_Class.SC_DayShort
    SC_DayTrade = Security_Class.SC_DayTrade
    SC_EDN = Security_Class.SC_EDN

class Security_PriceFlag:
    SP_FixedPrice = Security_PriceFlag.SP_FixedPrice
    SP_FallStopPrice = Security_PriceFlag.SP_FallStopPrice
    SP_UnchangePrice = Security_PriceFlag.SP_UnchangePrice
    SP_RiseStopPrice = Security_PriceFlag.SP_RiseStopPrice
    SP_MarketPrice = Security_PriceFlag.SP_MarketPrice

class SIDE_FLAG:
    SF_BUY = SIDE_FLAG.SF_BUY
    SF_SELL = SIDE_FLAG.SF_SELL
    
class TIME_IN_FORCE:
    TIF_ROD = TIME_IN_FORCE.TIF_ROD
    TIF_IOC = TIME_IN_FORCE.TIF_IOC
    TIF_FOK = TIME_IN_FORCE.TIF_FOK

class ORDER_TYPE:
    OT_NEW = ORDER_TYPE.OT_NEW
    OT_CANCEL = ORDER_TYPE.OT_CANCEL
    OT_MODIFY_QTY = ORDER_TYPE.OT_MODIFY_QTY
    OT_MODIFY_PRICE = ORDER_TYPE.OT_MODIFY_PRICE
    OT_MODIFY = ORDER_TYPE.OT_MODIFY

class MARKET_FLAG:
    MF_FUT = MARKET_FLAG.MF_FUT
    MF_OPT = MARKET_FLAG.MF_OPT
    MF_STK = MARKET_FLAG.MF_STK
    MF_FUT_SPREAD = MARKET_FLAG.MF_FUT_SPREAD
    MF_OPT_SPREAD = MARKET_FLAG.MF_OPT_SPREAD

class PRICE_FLAG:
    PF_SPECIFIED = PRICE_FLAG.PF_SPECIFIED
    PF_MARKET = PRICE_FLAG.PF_MARKET
    PF_STOP_MARKET = PRICE_FLAG.PF_STOP_MARKET
    PF_STOP_SPECIFIED = PRICE_FLAG.PF_STOP_SPECIFIED
    PF_MARKET_RANGE = PRICE_FLAG.PF_MARKET_RANGE

class POSITION_EFFECT:
    PE_OPEN = POSITION_EFFECT.PE_OPEN
    PE_CLOSE = POSITION_EFFECT.PE_CLOSE
    PE_DAY_TRADE = POSITION_EFFECT.PE_DAY_TRADE
    PE_AUTO = POSITION_EFFECT.PE_AUTO

class OFFICE_FLAG:
    OF_SPEEDY = OFFICE_FLAG.OF_SPEEDY
    OF_AS400 = OFFICE_FLAG.OF_AS400