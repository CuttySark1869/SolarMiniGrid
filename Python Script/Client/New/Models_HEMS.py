import json
import time
from  collections import namedtuple


class Json_Serializable:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def toObject(self,data):
        return namedtuple(self.__class__.__name__, data.keys())(*data.values())


class Homes(Json_Serializable):
    def __init__(self):
        self.uid = 'uid123456'
        self.latitude = 80
        self.longitude = 88.7
        self.maxLoadPower = 0
        self.maxFlexibleLoadPower = 0
        self.minFlexibleLoadPower = 0
        self.mainsState = True
        self.description = 'This is a test home'
        self.error = False
        self.lastUpdateTime=time.time()

    def setUid(self, uid):
        self.uid = uid

    def getUid(self):
        return self.uid


class ControllableGenerator(Json_Serializable):
    def __init__(self):
        self.uid='uid123456'
        self.capacity=0
        self.maxPower=0
        self.minPower=0
        self.lastUpdateTime=time.time()


class EV(Json_Serializable):
    def __init__(self):
        self.uid='uid123456'
        self.type='X'
        self.maxChargePower=0
        self.minChargePower=0
        self.capacity=0
        self.stateOfCharge=0
        self.lastUpdateTime=time.time()


class EnergyStorage(Json_Serializable):
    def __init__(self):
        self.uid='uid123456'
        self.capacity=0
        self.maxChargePower=0
        self.maxDischargePower=0
        self.maxSOC=0
        self.minSOC=0
        self.lastUpdateTime=time.time()


class HomeEnergyStatus(Json_Serializable):
    def __init__(self,data=None):
        if data is not None:
            for key in data:
                setattr(self, key, data[key])
        else:
            self.uid='uid123456'
            self.PVOutPower=0
            self.EVSOC=0
            self.energyStorageSOC=0
            self.loadPower=0
            self.operateState=0
            self.timeID = 0
            self.datetime=0
            self.lastUpdateTime=time.time()


class OperateParameter(Json_Serializable):
    def __init__(self,data=None):
        if data is not None:
            for key in data:
                setattr(self, key, data[key])
        else:
            self.uid='uid123456'
            self.EleDmdFct=0
            self.ConGenPow=0
            self.ConGenStu=0
            self.ConGenPrc=0
            self.StoChgPow=0
            self.StoDchPow=0
            self.StoSOCVal=0
            self.startTime=time.time()
            self.duration=0
            self.lastUpdateTime=time.time()


class PV(Json_Serializable):
    def __init__(self):
        self.uid='uid123456'
        self.capacity=0
        self.lastUpdateTime=time.time()


import numpy as np
class Forecasting(Json_Serializable):
    def __init__(self):
        self.uid = 'uid123456'
        self.CalLodFct = np.zeros(96)
        self.PVFctVal = np.zeros(96)
        self.PVUncSD = np.zeros(96)
        self.PVPrice =np.zeros(96)
        self.startTime=time.time()
        self.duration=0
        self.span=30*60
        self.lastUpdateTime = time.time()
        self.length=96

    def get_data(self):
        self.data = np.empty((self.length, 7))
        self.data[:, 0]=self.CalLodFct[0:self.length]
        self.data[:, 1] = self.PVFctVal[0:self.length]
        self.data[:, 2] = self.PVUncSD[0:self.length]
        self.data[:, 3] = self.PVPrice[0:self.length]
        self.data[:, 4] = self.startTime+self.span*np.linspace(0,self.length-1,self.length)
        self.data[:, 5] = self.span
        self.data[:, 6] = self.lastUpdateTime
        return  self.data


class TradingDispatch(Json_Serializable):
    def __init__(self):
        self.uid = 'uid123456'
        self.FleLodTrdPow = np.zeros(96)
        self.FleLodTrdPrc = np.zeros(96)
        self.ClaLodTrdPow = np.zeros(96)
        self.ClaLodTrdPrc = np.zeros(96)
        self.PVTrdPow = np.zeros(96)
        self.PVTrdPrc = np.zeros(96)
        self.ConGenTrdPow = np.zeros(96)
        self.ConGenTrdPrc = np.zeros(96)
        self.StoTrdPow = np.zeros(96)
        self.StoTrdPrc = np.zeros(96)
        self.startTime = time.time()
        self.duration = 0
        self.span = 30 * 60
        self.lastUpdateTime = time.time()
        self.length = 96

    def get_data(self):
        self.data = np.empty((self.length, 13))
        self.data[:, 0] = self.FleLodTrdPow[0:self.length]
        self.data[:, 1] = self.FleLodTrdPrc[0:self.length]
        self.data[:, 2] = self.ClaLodTrdPow[0:self.length]
        self.data[:, 3] = self.ClaLodTrdPrc[0:self.length]
        self.data[:, 4] = self.PVTrdPow[0:self.length]
        self.data[:, 5] = self.PVTrdPrc[0:self.length]
        self.data[:, 6] = self.ConGenTrdPow[0:self.length]
        self.data[:, 7] = self.ConGenTrdPrc[0:self.length]
        self.data[:, 8] = self.StoTrdPow[0:self.length]
        self.data[:, 9] = self.StoTrdPrc[0:self.length]
        self.data[:, 10] = self.startTime + self.span*np.linspace(0,self.length-1,self.length)
        self.data[:, 11] = self.span
        self.data[:, 12] = self.lastUpdateTime
        return self.data


class Faults(Json_Serializable):
    def __init__(self,code=0, message='Error', data=None):
        self.code=code
        self.message=message
        self.data=data

class Interchange_Results(Json_Serializable):
    def __init__(self,error=False,errorData=None,operateParameter=None):
        self.error=error
        self.errorData=errorData
        self.operateParameter=operateParameter

# For test
class Power_Outage(Json_Serializable):
    def __init__(self):
        self.start_time = 0
        self.duration = 0

    def setStartTime(self, timestamp):
        self.start_time = timestamp

    def getStartTime(self):
        return self.start_time

    def setDuration(self, duration):
        self.duration = duration

    def getDuration(self):
        return self.duration


class Error(Json_Serializable):
    def __init__(self):
        self.code = 0
        self.message = 'Error'
        self.data = None

    def setCode(self, code):
        self.code = code

    def getCode(self):
        return self.code

    def setMessage(self, message):
        self.message = message

    def getMessage(self):
        return self.message

    def setData(self, data):
        self.data = data

    def getData(self):
        return self.data


class Location(Json_Serializable):
    def __init__(self):
        self.latitude = 0  # [-90,90]
        self.longitude = 0  # [-180,180]

    def setLatitude(self, latitude):
        self.latitude = latitude

    def getLatitude(self):
        return self.latitude

    def setLongitude(self, longitude):
        self.longitude = longitude

    def getLongitude(self):
        return self.longitude


class Poll_Result(Json_Serializable):
    def __init__(self):
        self.chargeable = True
        self.nextPowerOutage = Power_Outage()

    def setChargeable(self, chargeable):
        self.chargeable = chargeable

    def getChargeable(self):
        return self.chargeable

    def setNextPowerOutage(self, nextPowerOutage):
        self.nextPowerOutage = nextPowerOutage

    def getNextPowerOutage(self):
        return self.nextPowerOutage

    def __iter__(self):
        yield 'chargeable', self.chargeable
        yield 'nextPowerOutage', self.nextPowerOutage


class Emboss_Battery(Json_Serializable):
    def __init__(self):
        self.IMEI = 'a123456789'
        self.location = Location()
        self.capacity = 1000  # [0,10000]
        self.stateOfCharge = 1000  # [0,10000]
        self.stateOfHealth = 100  # [0,100]
        self.mainsState = True
        self.emergencyLightingState = True
        self.errors = []

    def setIMEI(self, IMEI):
        self.IMEI = IMEI

    def getIMEI(self):
        return self.IMEI

    def errorAppend(self, error):
        self.errors.append(error)


from collections import namedtuple
class Parse_Json(object):
    def _json_object_hook(d):
        return namedtuple('Emboss_Battery', d.keys())(*d.values(), rename=True)
    def json2obj(data):
        return json.loads(data, object_hook=lambda d: namedtuple('Emboss_Battery', d.keys())(*d.values()))
