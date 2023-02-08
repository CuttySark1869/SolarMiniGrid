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
server = jsonrpclib.ServerProxy('http://138.38.64.38:8080',history=history)
# server = jsonrpclib.ServerProxy('http://localhost:8001', history=history)

newBat = {}
random.seed(a=100)
for i in range(0, 10):
    newBat[i] = emboss.Emboss_Battery()
    newBat[i].IMEI = 'CX' + str(random.randint(10000, 99999))
    newBat[i].location.latitude = random.randint(-90, 90)
    newBat[i].location.longitude = random.randint(-180, 180)
random.seed(a=None)


def send_one(imei="abc12345678", loc=None):
    if loc is None:
        loc = {"latitude": 55, "longitude": 98}
    IMEI = imei
    location = json.loads(loc.toJSON())
    capacity = 1000
    stateOfCharge = random.randint(1, 1000)
    stateOfHealth = random.randint(1, 100)
    mainsState = True
    emergencyLightingState = False
    errors = None
    if random.randint(1, 10) > 9:
        mainsState = False
    if random.randint(1, 10) > 9:
        emergencyLightingState = True
    if random.randint(1, 100) > 90:
        errors = {
            "code": 42,
            "message": "XXX error",
            "data": {"err": "HAHA", "conn": 0
                     }
        }
    result = server.poll(IMEI, location, capacity, stateOfCharge, stateOfHealth, mainsState, emergencyLightingState,
                         errors)
    # result=server.poll(IMEI,location,capacity,stateOfCharge,stateOfHealth,mainsState,emergencyLightingState);
    print('------Returned Result:')
    print(result)
    print('######Request:')
    print(history.request)
    print('######Response:')
    print(history.response)


def fun_timer():
    for i in range(0, 10):
        send_one(newBat[i].IMEI, newBat[i].location)
    global timer
    timer = threading.Timer(150.5, fun_timer)
    timer.start()


timer = threading.Timer(1, fun_timer)
timer.start()

time.sleep(15000)  # 15秒后停止定时器
timer.cancel()




