#!/usr/bin/env python
# pip install jsonrpclib-pelix
import jsonrpclib
import Models_HEMS
from pprint import pprint
import random
import threading
import time
import json
import datetime

"""
For GUI test
"""
def gui_test():
    import tkinter as tk
    window = tk.Tk()
    window.title('zhuyuanlu-jacky')
    window.geometry('500x300')
    var = tk.StringVar()
    l = tk.Label(window, textvariable=var, bg='green', font='Arial,12', width=30, height=2)
    l.pack()
    on_hit = False

    def hit_me():
        global on_hit
        if on_hit == False:
            on_hit = True  # 第13步
            var.set('you hit me')
        else:
            on_hit = False  # 第14步
            var.set('')

    b = tk.Button(window, text="hit me", width=15, height=2, command=hit_me)
    # 第15步
    b.pack()  # 把button放在label下面的位置
    window.mainloop()


"""
Read data form xlsx
"""
def read_sim_data():
    from openpyxl import load_workbook
    wb = load_workbook(filename='D:\Projects Data\Bath\P2P\DataServer_Sim\Compare different matching result.xlsx')
    # print(wb.get_sheet_names())
    sim_data = []
    for i in range(1, 6):
        ws = wb.get_sheet_by_name('S' + str(i))
        rows = ws.rows
        # 行迭代
        content = []
        for row in rows:
            line = [col.value for col in row]
            content.append(line)
        sim_data.append(content[1:])
    return sim_data


def fun_timer(time_id,mode=1):
    for i in range(0, n):
        # send_one(newHES[i])
        sim_send_one(data=sim_data, mode=mode, user_no=i + 1,time_id=time_id, hes=newHES[i])
    x=time_id+1
    next_time_id=x-int(x/288)*288
    global timer
    timer = threading.Timer(20, fun_timer(next_time_id))  # 20s
    timer.start()


def send_one(hes=None):
    if hes is None:
        hes = Models_HEMS.HomeEnergyStatus()
    hes.energyStorageSOC = random.randint(1, 100)
    hes.EVSOC = random.randint(10, 100)
    hes.PVOutPower = random.randint(1, 10)
    hes.loadPower = random.randint(1, 20)
    hes.lastUpdateTime = time.time()
    # hes.uid='uid123456'
    data = vars(hes)
    # k = Models_HEMS.HomeEnergyStatus(data)
    result = server.rpc_json_info_poll(data)
    print('------Returned Result:')
    print(result)
    print('######Request:')
    print(history.request)
    print('######Response:')
    print(history.response)


def sim_send_one(data, mode, user_no, time_id, hes=None):
    if hes is None:
        hes = Models_HEMS.HomeEnergyStatus()

    hes.energyStorageSOC = random.randint(1, 100)
    hes.EVSOC = random.randint(10, 100)
    if user_no == 1:
        hes.PVOutPower = data[mode - 1][time_id][5]
    else:
        hes.PVOutPower = 0
    hes.loadPower = random.randint(1, 20)
    hes.timeID=data[mode - 1][time_id][0]
    hes.datetime = datetime.datetime.timestamp(data[mode - 1][time_id][1])
    hes.operateState=mode
    hes.lastUpdateTime = time.time()
    # hes.uid='uid123456'
    data = vars(hes)
    result = server.rpc_sim_poll(data)
    print('------Returned Result:')
    print(result)
    print('######Request:')
    print(history.request)
    print('######Response:')
    print(history.response)


"""
Main()
"""
history = jsonrpclib.history.History()
# server = jsonrpclib.ServerProxy('http://138.38.64.38:8080',history=history)
server = jsonrpclib.ServerProxy('http://localhost:8002', history=history)

sim_data=read_sim_data()

n = 3  # number of HEMS
start_time_id=100
mode=1

newHES = {}
random.seed(a=100)
for i in range(0, n):
    newHES[i] = Models_HEMS.HomeEnergyStatus()
    newHES[i].uid = 'UID' + str(i + 1).zfill(3)
    # newHEMS[i].latitude = random.randint(-90, 90)
    # newHEMS[i].longitude = random.randint(-180, 180)
random.seed(a=None)

timer2 = threading.Timer(1, fun_timer(time_id=start_time_id, mode=mode))  # 1s
timer2.start()
time.sleep(15000)  # 15000秒后停止定时器
timer2.cancel()
