# -*- coding: utf-8 -*-
"""
Description: the following script is dedicated to communicate and
             control (retrieve info and send commands) Variotrack and Xtender via scom
Created by: Yunjie Gu, Date: 09-02-2023
"""

import sqlite3
import time
import scom
from datetime import datetime
from datetime import timedelta

port_name = 'COM5'
verbose = 3
src_addr = 1
rcc_addr = 500 #Xcom-232i = RCC 
bsp_addr = 600
xtm_addr = 100
vtk_addr = 300

#info object type and property id (read-only)
user_info_object_object_type = 1
user_info_object_property_id = 1
#parameter object type and property id (read-write)
parameter_object_object_type = 2
parameter_object_flash_property_id = 5 #stored in flash
parameter_object_ram_property_id = 13  #stored in ram

# vtk_info = scom.ScomTarget(port_name,verbose,0,src_addr,vtk_addr+1,user_info_object_object_type,user_info_object_property_id)
# vtk_setting = scom.ScomTarget(port_name,verbose,0,src_addr,vtk_addr+1,parameter_object_object_type,parameter_object_ram_property_id)

class xtm_target: 
  def __init__(self,port_name,door_num):
    self.door_num = door_num
    self.port_name = port_name
    self.xtm_info = scom.ScomTarget(self.port_name,verbose,0,src_addr,xtm_addr+1,user_info_object_object_type,user_info_object_property_id)
    self.xtm_setting = scom.ScomTarget(self.port_name,verbose,0,src_addr,xtm_addr+1,parameter_object_object_type,parameter_object_ram_property_id)
    self.xtm_setting_flash = scom.ScomTarget(self.port_name,verbose,1,src_addr,xtm_addr+1,parameter_object_object_type,parameter_object_flash_property_id)

  def disable_watchdog(self):
    self.xtm_setting_flash.write(1628,0,'BOOL') #disable watch dog
  
  def open(self):
    self.xtm_setting.write(1415,1,'INT32')

  def close(self):
    self.xtm_setting.write(1399,1,'INT32')

  def data_log(self):
    current_datetime = datetime.now()
    battery_SOC  = self.xtm_info.read(3007,'FLOAT') 
    battery_current = self.xtm_info.read(3005,'FLOAT')
    battery_voltage = self.xtm_info.read(3000,'FLOAT')
    battery_power = self.xtm_info.read(3023,'FLOAT')
    AC_in_current = self.xtm_info.read(3011,'FLOAT')
    AC_in_voltage = self.xtm_info.read(3012,'FLOAT')
    AC_in_power = self.xtm_info.read(3013,'FLOAT')
    print('battery power' + str(battery_voltage))
    return(current_datetime,battery_SOC,battery_current,battery_voltage,battery_power,AC_in_current,AC_in_voltage,AC_in_power)

  def grid_feeding_enable(self, max_current, start_time, end_time):
    # Time used in the protocol is in minutes.
    # Min is 0, i.e., 00:00
    # Max is 1440, i.e., 24:00
    # To read the time more easily, the function takes the hours as input
    # and do the convertion to minutes within the function.
    Vbat_force_feed = 23.6
    start_time_in_min = round(start_time * 60)
    end_time_in_min = round(end_time * 60)
    
    self.xtm_setting.write(1523,1,max_current,'FLOAT')
    self.xtm_setting.write(1524,1,Vbat_force_feed,'FLOAT')
    self.xtm_setting.write(1525,1,start_time_in_min,'FLOAT')
    self.xtm_setting.write(1526,1,end_time_in_min,'FLOAT')
    self.xtm_setting.write(1128,1,'BOOL') #transfer relay allowed
    self.xtm_setting.write(1127,1,'BOOL') #grid-feeding allowed

  def grid_feeding_disable(self):
    self.xtm_setting.write(1127,0,'BOOL') #grid-feeding not allowed

  def charge_set_current(self,current):
    self.xtm_setting.write(1138,current,'FLOAT')

  def charge_enable(self):
    self.xtm_setting.write(1140,27.6,'FLOAT')
    self.xtm_setting.write(1155,1,'BOOL') # absorption phase disabled
    self.xtm_setting.write(1163,1,'BOOL') # equalization phase disabled
    self.xtm_setting.write(1170,1,'BOOL') # reduced floating phase disabled
    self.xtm_setting.write(1173,1,'BOOL') # periodic absorption phase disabled
    self.xtm_setting.write(1125,1,'BOOL') # charge enabled

if __name__ == '__main__':

  xtm = xtm_target(port_name,1)
  xtm.open()
  #xtm.charge_enable()

  conn = sqlite3.connect('datalog.db')
  c = conn.cursor()
  c.execute("""CREATE TABLE IF NOT EXISTS datalog(
                sample_time text,
                battery_SOC real,
                battery_current real,
                battery_voltage real,
                battery_power real,
                ac_in_current real,
                ac_in_voltage real,
                ac_in_power real
              )""")
  
  i = 0
  sample_no = 5

  while i < sample_no:
    current_datetime, battery_SOC, battery_current, \
        battery_voltage, battery_power, AC_in_current, \
        AC_in_voltage, AC_in_power = xtm.data_log()

    with conn:
      c.execute('INSERT INTO datalog Values(?,?,?,?,?,?,?,?)', (current_datetime, battery_SOC,
                                                                        battery_current, battery_voltage, battery_power, AC_in_voltage, AC_in_current, AC_in_power))

    print(str(i))
    i += 1
    #time.sleep(1)

  print('Data collection terminated!')
  conn.close()

  xtm.close()