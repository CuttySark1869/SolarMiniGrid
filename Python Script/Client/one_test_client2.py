
import jsonrpclib
import Models_HEMS
from pprint import pprint
import random
import threading
import time
import json

history = jsonrpclib.history.History()
# server = jsonrpclib.ServerProxy('http://138.38.64.38:8080',history=history)
server = jsonrpclib.Server('http://localhost:8002', history=history)

newHES = {}
n = 10
random.seed(a=100)
for i in range(0, n):
    newHES[i] = Models_HEMS.HomeEnergyStatus()
    newHES[i].uid = 'UID' + str(i + 1).zfill(3)
    # newHEMS[i].latitude = random.randint(-90, 90)
    # newHEMS[i].longitude = random.randint(-180, 180)
random.seed(a=None)


def send_one(hes=None):
    if hes is None:
        hes = Models_HEMS.HomeEnergyStatus()
    hes.energyStorageSOC = random.randint(1, 100)
    hes.EVSOC = random.randint(10, 100)
    hes.PVOutPower = random.randint(1, 10)
    hes.loadPower = random.randint(1, 20)
    # hes.uid='uid123456'

    data = vars(hes)
    k = Models_HEMS.HomeEnergyStatus(data)
    result = server.rpc_json_info_poll(data)

    print('------Returned Result:')
    print(result)
    print('######Request:')
    print(history.request)
    print('######Response:')
    print(history.response)


def fun_timer():
    for i in range(0, n):
        # newBat[i].IMEI='356774078508298'
        send_one(newHES[i])
    global timer
    timer = threading.Timer(20, fun_timer)
    timer.start()


timer = threading.Timer(1, fun_timer)
timer.start()

time.sleep(15000)
timer.cancel()
