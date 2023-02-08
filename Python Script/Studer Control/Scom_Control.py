# -*- coding: utf-8 -*-
"""
Description: the following script is dedicated to communicate and
             control (retrieve info and send commands) Xtender via scom
Developing Operating System: Windows 7 Enterprise SP1
Developing Environment: Anaconda Python 2.7.13
First created: 10/03/2017 (10th March 2017)
Last modified: 20/07/2018
Author: Minghao Xu
Scom Version: 1.6.26
Xtender Version: 1.6.22
BSP Version: 1.6.14
Script Version: 0.9
Update Note: This script is created to test the SOC curve of the batteries
        during charging and store the data in a database
"""
# ------------------------------------------------------------------------
# 1. Import packages and set logger
import ScomCommand as scom
sc = scom.ScomCommand
import os
import sqlite3
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler

import logging
dir(si)
log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.INFO)  # DEBUG

fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)

# 2. Set pre-defined paramets and paths
# ------------------------------------------
# paths
# cwd = os.getcwd()
dir_scom = sc.dir_scom
cwd = 'H:\\Profiles_Do_Not_Delete\\campus\\Desktop\\SoLa Kit'
# fid info of Xtender
fid_list = ['345c8cde', '3460c9e3', '3460caac', '345c9111']
fid_dict = {fid_list[0]: 'unit1',
            fid_list[1]: 'unit2',
            fid_list[2]: 'unit3',
            fid_list[3]: 'unit4'}

# whether to chech port
chech_port = True
# whether to test communication protocol with serial port
test_comm = True
# open Xtender
Xtender_open = True
# close Xtender
Xtender_close = False
# Xtender initialization
extender_init = True
# RCC initialization
rcc_init = True
# BSP initialization
bsp_init = False
# battery setting
# 1 : demonstration kit;
# 2 : smart grid lab
battery_setting = 2


# 3. Set and open serial port
# ----------------------------
# 3.1 Check which port is used
# -----------------------------
# display ports in use by executing shell commands
if chech_port:
  py2output = subprocess.Popen(['mode'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  for line in py2output.stdout.readlines():
    print line
  retval = py2output.wait()

# 3.2 Test serial port connection and scom
# -----------------------------------------
# test if scom protocol is working with current serial port
if test_comm:
  sc.test_comm()

# 4 System Initialization
# ------------------------
def data_collection(port_index):
  global i
  global sample_no
  port_list = [1, 3, 7, 6]
  current_loc = port_list.index(port_index)

  DB_dir = cwd + '\\DB\\'
  if not os.path.exists(DB_dir):
    os.makedirs(DB_dir)

  table_name = 'Unit' + str(port_index) + '_Charging'
  DB_name = DB_dir + 'StuderOperation4.db'
  conn = sqlite3.connect(DB_name)
  c = conn.cursor()
  execution_str = """CREATE TABLE IF NOT EXISTS {}(
                      sample_time text,
                      battery_SOC real,
                      battery_current real,
                      battery_voltage real,
                      battery_power real,
                      ac_in_current real,
                      ac_in_voltage real,
                      ac_in_power real
                      )"""
  c.execute(execution_str.format(table_name))

  current_datetime, battery_SOC, battery_current, \
      battery_voltage, battery_power, AC_in_current, \
      AC_in_voltage, AC_in_power = scom.read_data(port_index)

  c.execute('INSERT INTO {} Values(?,?,?,?,?,?,?,?)'.format(table_name), (current_datetime, float(battery_SOC),
                                                                          float(battery_current), float(battery_voltage), float(battery_power), float(AC_in_current), float(AC_in_voltage), float(AC_in_power)))

  conn.commit()
  print str(port_index) + ': ' + str(current_datetime)
  i[current_loc] += 1

  if i[current_loc] == sample_no:
    id_of_job = 'datacollection' + str(port_index)
    sched.remove_job(id_of_job)
    print 'Data collection for ' + str(port_index) + ' terminated!'
    conn.close()
  # scheduler.shutdown(wait=False)


def main():
  # parameter and varibale init
  global i
  global sample_no

  i = [0, 0, 0, 0]
  sample_no = 4 * 60 * 24
#     sample_no = 4
  # system init
  scom.system_init(1)
  scom.xtender_open(1, Xtender_open)
  scom.rcc_time_sync(1, rcc_init)
  scom.bsp_init(1, bsp_init, battery_setting)

  scom.system_init(3)
  scom.xtender_open(3, Xtender_open)
  scom.rcc_time_sync(3, rcc_init)
  scom.bsp_init(3, bsp_init, battery_setting)

  scom.system_init(7)
  scom.xtender_open(7, Xtender_open)
  scom.rcc_time_sync(7, rcc_init)
  scom.bsp_init(7, bsp_init, battery_setting)

  scom.system_init(6)
  scom.xtender_open(6, Xtender_open)
  scom.rcc_time_sync(6, rcc_init)
  scom.bsp_init(6, bsp_init, battery_setting)

#     scom.battery_charge(1,22)
#     scom.battery_charge(3,22)
#     scom.battery_charge(7,22)
#     scom.battery_charge(6,22)

#     scom.force_equalization(1)
#     scom.force_equalization(3)
#     scom.force_equalization(7)
#     scom.force_equalization(6)

  scom.grid_feeding_enable(1, 5, 0, 1440)
  scom.grid_feeding_enable(3, 5, 0, 1440)
  scom.grid_feeding_enable(7, 5, 0, 1440)
  scom.grid_feeding_enable(6, 5, 0, 1440)

  job_data_collection = sched.add_job(data_collection, 'cron', args=[1], id='datacollection1', second='0,15,30,45')
  job_data_collection = sched.add_job(data_collection, 'cron', args=[3], id='datacollection3', second='0,15,30,45')
  job_data_collection = sched.add_job(data_collection, 'cron', args=[7], id='datacollection7', second='0,15,30,45')
  job_data_collection = sched.add_job(data_collection, 'cron', args=[6], id='datacollection6', second='0,15,30,45')
  sched.start()


if __name__ == '__main__':
  sched = BackgroundScheduler()
  main()
