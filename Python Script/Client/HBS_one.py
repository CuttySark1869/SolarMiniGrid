#!/usr/bin/env python
# pip install jsonrpclib-pelix
import jsonrpclib
import emboss
from pprint import pprint
import random
import threading
import time
import json

history = jsonrpclib.history.History()
# server = jsonrpclib.ServerProxy('http://138.38.64.38:8080',history=history)
server = jsonrpclib.ServerProxy('http://localhost:8001', history=history)


class HBS:
    import  time
    def __init__(self):
        self.capacity=1000
        self.soh=100
        self.max_soc=1
        self.min_soc=0.2
        self.ch_power=10
        self.dis_power=30
        self.ch_eff=0.88
        self.dis_eff=0.88
        self.lsst=time.time()
        self.ch_dis=True
        self.chargeable=True
        self.soc=1000
    def charge_discharge(self,times, ch_dis):
        if times>=self.lsst and self.soc<=self.capacity*self.max_soc and self.soc>=self.capacity*self.min_soc:
            if self.ch_dis:
                self.soc=self.soc+(times-self.lsst)*self.ch_eff*self.ch_power/3600
                if self.soc>self.capacity*self.max_soc:
                    self.soc=self.capacity
            else:
                x=random.randrange(0,10)/10
                self.soc = self.soc- (times - self.lsst) * self.dis_eff * self.dis_power*x / 3600
                if self.soc<self.capacity*self.min_soc:
                    self.soc=self.capacity*self.min_soc
        self.lsst=times
        self.ch_dis=ch_dis


newBat = {}
newHbs = {}
n=1
random.seed(a=100)
for i in range(0, n):
    newBat[i] = emboss.Emboss_Battery()
    newHbs[i] = HBS()
    newBat[i].IMEI = 'CX' + str(random.randint(10000, 99999))
    newBat[i].location.latitude = random.randint(-90, 90)
    newBat[i].location.longitude = random.randint(-180, 180)
random.seed(a=None)


def send_one(imei="abc12345678", loc=None, hbs=HBS()):
    if loc is None:
        loc = {"latitude": 55, "longitude": 98}
    IMEI = imei
    location = json.loads(loc.toJSON())
    import time
    times=time.time()
    capacity = hbs.capacity
    stateOfCharge = hbs.soc
    stateOfHealth = hbs.soh
    mainsState = True
    emergencyLightingState = False
    errors = None
    if random.randint(1, 10) > 8:
        mainsState = False
    if random.randint(1, 10) > 9:
        emergencyLightingState = True
    if random.randint(1, 100) > 50:
        errors = {
            "code": 42,
            "message": "XXX error",
            "data": {"err": "HAHA", "conn": 0
                     }
        }
    result = server.poll(IMEI, location, capacity, stateOfCharge, stateOfHealth, mainsState, emergencyLightingState,
                         errors)

    hbs.charge_discharge(times, result['chargeable'])
    hbs.chargeable=result['chargeable']

    data=(times,IMEI,capacity, stateOfCharge,stateOfHealth,mainsState,emergencyLightingState,result['chargeable'])
    import csv
    import os
    csv_file='hbs.csv'
    if not os.path.isfile(csv_file):
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Times", "IMEI", "Capacity","SOC","SOH","SOG","EMLS","Chargeable"])
            writer.writeheader()
            writer = csv.writer(f)
            writer.writerow(data)
    else:
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data)

    # result=server.poll(IMEI,location,capacity,stateOfCharge,stateOfHealth,mainsState,emergencyLightingState);
    print('------Returned Result:')
    print(result)
    print('######Request:')
    print(history.request)
    print('######Response:')
    print(history.response)


def fun_timer(m_hbs=newHbs):
    for i in range(0, n):
        send_one(newBat[i].IMEI, newBat[i].location, hbs=m_hbs[i])
    global timer
    timer = threading.Timer(180, fun_timer)
    timer.start()


timer = threading.Timer(1, fun_timer)
timer.start()

time.sleep(1500000)  # 15秒后停止定时器
timer.cancel()




