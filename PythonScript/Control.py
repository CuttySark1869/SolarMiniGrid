# -*- coding: utf-8 -*-
"""
Description: the following script is dedicated to communicate and
             control (retrieve info and send commands) Variotrack and Xtender via scom
Created by: Yunjie Gu, Date: 09-02-2023
"""

import sqlite3
import time
import os
import scom
from db2csv import db2csv
from datetime import datetime
from datetime import timedelta
import pandas as pd
from read_control_signals import secondary_control_signal

# info object type and property id (read-only)
user_info_object_object_type = 1
user_info_object_property_id = 1
# parameter object type and property id (read-write)
parameter_object_object_type = 2
parameter_object_flash_property_id = 5  # stored in flash
parameter_object_ram_property_id = 13  # stored in ram

verbose = 3
src_addr = 1
rcc_addr = 500  # Xcom-232i = RCC
bsp_addr = 600
xtm_addr = 100
vtk_addr = 300

class bsp_target:
    def __init__(self, port_name, door_num):
        self.door_num = door_num
        self.port_name = port_name
        self.info = scom.ScomTarget(self.port_name, verbose, 0, src_addr, bsp_addr + 1, user_info_object_object_type,
                                    user_info_object_property_id)
        self.setting_flash = scom.ScomTarget(self.port_name, verbose, 0, src_addr, bsp_addr + 1,
                                             parameter_object_object_type, parameter_object_flash_property_id)

    # Get measurement from battery monitor
    def data_log(self):
        bat_voltage = self.info.read(7000, 'FLOAT')
        # bat_current = self.info.read(7001, 'FLOAT')
        bat_soc = self.info.read(7002, 'FLOAT')
        bat_power = self.info.read(7003, 'FLOAT')
        return (bat_soc, bat_voltage, bat_power)
    
    # def calibrate(self):
    #     self.setting_flash.write(6017, 520, 'FLOAT') #A,  shunt nominal current
    #     self.setting_flash.write(6018, 50, 'FLOAT')  #mV, shunt nominal voltage

class vtk_target:
    def __init__(self, port_name, door_num):
        self.door_num = door_num
        self.port_name = port_name
        self.info = scom.ScomTarget(self.port_name, verbose, 0, src_addr, vtk_addr + 1, user_info_object_object_type,
                                    user_info_object_property_id)
        self.setting = scom.ScomTarget(self.port_name, verbose, 0, src_addr, vtk_addr + 1, parameter_object_object_type,
                                       parameter_object_ram_property_id)
        self.setting_flash = scom.ScomTarget(self.port_name, verbose, 0, src_addr, vtk_addr + 1,
                                             parameter_object_object_type, parameter_object_flash_property_id)

    # Set the battery charging current (A) from from solar (pv generator)
    def charge_set_current(self, current):
        self.setting.write(10002, max(min(current,10),0), 'FLOAT')

    # Get measurement from variotrack device (dc-dc converter)
    # pv_power in W, pv_voltage in V
    def data_log(self):
        pv_power = self.info.read(11004, 'FLOAT')
        pv_power = str(float(pv_power)*1000)
        pv_voltage = self.info.read(11002, 'FLOAT')
        return (pv_voltage, pv_power)

class xtm_target:
    def __init__(self, port_name, door_num):
        self.door_num = door_num
        self.port_name = port_name
        self.info = scom.ScomTarget(self.port_name, verbose, 0, src_addr, xtm_addr + 1, user_info_object_object_type,
                                    user_info_object_property_id)
        self.setting = scom.ScomTarget(self.port_name, verbose, 0, src_addr, xtm_addr + 1, parameter_object_object_type,
                                       parameter_object_ram_property_id)
        self.setting_flash = scom.ScomTarget(self.port_name, verbose, 0, src_addr, xtm_addr + 1,
                                             parameter_object_object_type, parameter_object_flash_property_id)

    # Open xtender device (inverter)
    def open(self):
        self.setting.write(1415, 1, 'INT32')
        self.__grid_feeding_enable()
        self.__charge_enable()

    # Close xtender device (inverter)
    def close(self):
        self.setting.write(1399, 1, 'INT32')

    # Get measurement from xtender device (inverter)
    def data_log(self):
        ac_in_voltage = self.info.read(3012, 'FLOAT')
        ac_in_power = self.info.read(3137, 'FLOAT')
        ac_out_voltage = self.info.read(3021, 'FLOAT')
        ac_out_power = self.info.read(3136, 'FLOAT')
        ac_out_power = float(ac_out_power)*1000
        ac_in_power = float(ac_in_power)*1000 - ac_out_power        
        return (ac_in_voltage, str(ac_in_power), ac_out_voltage, str(ac_out_power))
    
    # Set the inverter output voltage (V) in stand alone mode
    def ac_set_voltage_out(self, volt):
        self.__transfer_relay_disable()
        self.setting.write(1286, max(min(volt,240),0), 'FLOAT')

    # Set the battery charging current (A, 24V) from from grid (ac generator)
    def charge_set_current(self, current):
        self.__transfer_relay_enable()
        if current > 0:
            self.__grid_feeding_set_current(0)
            self.__grid_feeding_control(0)
            self.__charge_set_current(max(min(current,20),0))
        else:
            self.__charge_set_current(0)
            self.__grid_feeding_control(1)
            self.__grid_feeding_set_current(max(min(-current*24/240,2),0))

    # def disable_watchdog(self):
    #     self.setting_flash.write(1628, 0, 'BOOL')  # disable watch dog

    def __charge_set_current(self, current):
        self.setting.write(1138, max(min(current,10),0), 'FLOAT')

    def __grid_feeding_set_current(self, current):
        self.setting.write(1523, current, 'FLOAT')
    
    def __transfer_relay_enable(self):
        self.setting.write(1128, 1, 'BOOL')

    def __transfer_relay_disable(self):
        self.setting.write(1128, 0, 'BOOL')    

    def __grid_feeding_enable(self):
        # Time used in the protocol is in minutes.
        # Min is 0, i.e., 00:00
        # Max is 1440, i.e., 24:00
        # To read the time more easily, the function takes the hours as input
        # and do the convertion to minutes within the function.
        Vbat_force_feed = 23.6
        start_time_in_min = round(0.0*60)
        end_time_in_min = round(23.9*60)

        self.setting.write(1550, 1, 'BOOL')         # save to flash
        self.setting_flash.write(1523, 0, 'FLOAT')
        self.setting_flash.write(1524, Vbat_force_feed, 'FLOAT')
        self.setting_flash.write(1525, start_time_in_min, 'INT32')
        self.setting_flash.write(1526, end_time_in_min, 'INT32')
        self.setting_flash.write(1128, 1, 'BOOL')   # transfer relay allowed
        self.setting_flash.write(1127, 1, 'BOOL')   # grid-feeding allowed

    def __grid_feeding_control(self,enabled):
        self.setting.write(1127, enabled, 'BOOL')   # grid-feeding not allowed

    def __charge_enable(self):
        self.setting.write(1140, 27.6, 'FLOAT')
        self.setting.write(1155, 1, 'BOOL')  # absorption phase disabled
        self.setting.write(1163, 1, 'BOOL')  # equalization phase disabled
        self.setting.write(1170, 1, 'BOOL')  # reduced floating phase disabled
        self.setting.write(1173, 1, 'BOOL')  # periodic absorption phase disabled
        self.setting.write(1125, 1, 'BOOL')  # charge enabled

if __name__ == '__main__':

    ctrl_mode = 1       # 1: generator connected mode; 2: islanded mode
    port_name = 'COM5'  # the port name can be find in device manager
    ems_signal_name = 'ems_log'
    data_log_name = 'data_log'
    sampling_time = 5  # in seconds
    
    vtk = vtk_target(port_name, 1)
    xtm = xtm_target(port_name, 1)
    bsp = bsp_target(port_name, 1)

    """ prepare database for data logging """
    try: 
        os.remove(data_log_name + '.db')
    except:
        pass
    
    conn = sqlite3.connect(data_log_name + '.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS data_log(
                sample_time text,
                battery_SOC real,
                battery_voltage real,
                battery_power real,
                pv_voltage real,
                pv_power real,
                ac_in_voltage real,
                ac_in_power real,
                ac_out_voltage real,
                ac_out_power real
              )""")
    
    """ read csv file for ems commands """
    control_io = secondary_control_signal(ems_signal_name)
    ems_signals = control_io.read_control_log()
    total_steps = len(ems_signals.time_slots)

    """ start and configure the device """
    xtm.open()

    """ execute the control and data logging """
    i = 0
    try:
        while i < total_steps:
            # data logging
            current_datetime = datetime.now()
            ac_in_voltage, ac_in_power, ac_out_voltage, ac_out_power = xtm.data_log()
            battery_soc, battery_voltage, battery_power = bsp.data_log()
            pv_voltage, pv_power = vtk.data_log()

            with conn:
                c.execute('INSERT INTO data_log Values(?,?,?,?,?,?,?,?,?,?)', (current_datetime, battery_soc,
                                                                              battery_voltage, battery_power,
                                                                              pv_voltage, pv_power, ac_in_voltage,
                                                                              ac_in_power, ac_out_voltage,
                                                                              ac_out_power))

            vtk.charge_set_current(ems_signals.pv_current[i])  # Set the PV current
            if ctrl_mode == 1:
                xtm.charge_set_current(ems_signals.ac_in_current[i])
            elif ctrl_mode == 2:
                xtm.ac_set_voltage_out(ems_signals.ac_out_voltage[i])

            print(str(i))
            i += 1
            if sampling_time > 1:
                time.sleep(sampling_time - 1)

        print('Converting data base to csv.')
        try:
            db2csv(data_log_name)
        except:
            pass
        print('Data collection terminated!')

    except KeyboardInterrupt:
        print('Data collection interrupted!')

    conn.close()
    xtm.close()
