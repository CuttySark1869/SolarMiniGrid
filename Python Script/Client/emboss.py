import json
class Json_Serializable:
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)
	#def dumper(object):
	#	try:
	#		return object.toJSON()
	#	except:
	#		return object.__dict__

class Power_Outage(Json_Serializable):
	def __init__(self):
		self.timestamp=0;
		self.duration=0;
	def setTimestamp(self,timestamp):
		self.timestamp=timestamp
	def getTimestamp(self):
		return self.timestamp
	def setDuration(self,duration):
		self.duration=duration
	def getDuration(self):
		return self.duration	

class Error(Json_Serializable):
	def __init__(self):	
		self.code=0
		self.message='Error'
		self.data=None
	def setCode(self,code):
		self.code=code
	def getCode(self):
		return self.code
	def setMessage(self,message):
		self.message=message
	def getMessage(self):
		return self.message
	def setData(self,data):
		self.data=data
	def getData(self):
		return self.data
	
class Location(Json_Serializable):
	def __init__(self):
		self.latitude=0; #[-90,90]
		self.longitude=0; #[-180,180]
	def setLatitude(self,latitude):
		self.latitude=latitude
	def getLatitude(self):
		return self.latitude
	def setLongitude(self,longitude):
		self.longitude=longitude
	def getLongitude(self):
		return self.longitude

class Poll_Result(Json_Serializable):
	def __init__(self):
		self.chargeable=True;
		self.nextPowerOutage= Power_Outage();
	def setChargeable(self,chargeable):
		self.chargeable=chargeable
	def getChargeable(self):
		return self.chargeable
	def setNextPowerOutage(self,nextPowerOutage):
		self.nextPowerOutage=nextPowerOutage
	def getNextPowerOutage(self):
		return self.nextPowerOutage

class Emboss_Battery(Json_Serializable):
	def __init__(self):
		self.IMEI='a123456789'
		self.location=Location()
		self.capacity=10000; #[0,10000]
		self.stateOfCharge=10000; #[0,10000]
		self.stateOfHealth=100; #[0,100]
		self.mainsState=True;
		self.emergencyLightingState=True;
		self.errors=[]
	def setIMEI(self,IMEI):
		self.IMEI=IMEI
	def getIMEI(self):
		return self.IMEI
	def errorAppend(self,erorr):
		self.errors.append(erorr)

