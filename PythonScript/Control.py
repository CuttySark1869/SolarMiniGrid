# -*- coding: utf-8 -*-
"""
Description: the following script is dedicated to communicate and
             control (retrieve info and send commands) Variotrack and Xtender via scom
Created by: Yunjie Gu, Date: 09-02-2023
"""
# ------------------------------------------------------------------------
# 1. Import packages and set logger
import serial
import subprocess
import os
import sqlite3
import numpy as np
import pandas as pd
import time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from datetime import timedelta
import time
from IPython.display import clear_output

# import logging

# log = logging.getLogger('apscheduler.executors.default')
# log.setLevel(logging.INFO)  # DEBUG

# fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
# h = logging.StreamHandler()
# h.setFormatter(fmt)
# log.addHandler(h)

# 2. Set pre-defined paramets and functions
# ------------------------------------------
# 2.1 Pre-define Parameters and Paths
# ------------------------------------
# paths
cwd = os.getcwd()
dir_scom = 'scom.exe '
# port
port_name = ['COM0', 'COM4']
# verbose
verbose_num = 3
# src addr
src_addr = 1
# Xcom-232i addr (alias for RCC)
RCC_addr = 501
# BSP addr
BSP_addr = 601
# Xtender addr
XTM_addr = 101
# object_type and property ID
# refer to section 4.4 in protocol specs
user_info_object_object_type = 1
user_info_object_property_Id = 1  # value
parameter_object_object_type = 2
# 5 for real value (save in flash memory);
# 6 for min;
# 7 for max;
# 8 for accessibility level; (0: view only; 10: basic; 20: expert; 30: installer; 40: QSP)
# 13 for saving value on RAM instead of flash memory
parameter_object_property_Id_flash = 5
parameter_object_property_Id_RAM = 13
message__object_object_type = 3
message_object_property_Id = 1
# whether to display full info of fetched info (only for calling function, class calling is excluded)
display_output = False
# whether to chech port
chech_port = False
# whether to test communication protocol with serial port
test_comm = False
# whether to open a serial port
open_port = False
# open Xtender
Xtender_open = False
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


# 2.3 Pre-define Command Class
# -----------------------------
class ScomCommand:
  """
  The class below are created for storing parameters related to certain function.
  The class also includes functions to create commands for reading or writing data
  with Studer device.

  Parameters
  ----------
  port: port name defined in 2.1
  verbose: default 3
  src_addr: address of source
  dst_addr: address of destination
            0: broadcast
            100: a virtual address to access all XTH,XTM, and XTS
            101-109: a single XTH,XTM, or XTS inverter
            501: Xcom-232i
            601: BSP
  object_type : type of object
  object_id: object identifier
  property_id: identify the property in the object
  data_format: format of the data
  """
  # count the number of parameters used to generate command
  display_output = False
  parameter_object_property_Id_RAM = 13
  num_commands = 0

  def __init__(self, port, verbose, src_addr, dst_addr, object_type, object_id, property_id, data_format):
    self.port = port
    self.verbose = verbose
    self.src_addr = src_addr
    self.dst_addr = dst_addr
    self.object_type = object_type
    self.object_id = object_id
    self.property_id = property_id
    self.data_format = data_format
    self.description = 'No Description'
    ScomCommand.num_commands += 1

  @property
  def description(self):
    return self.description

  @description.setter
  def description(self, description):
    self.description = description

  def write_cmd(self, port_index, value):
    write_cmd = ('--port={} --verbose={} write_property src_addr={} dst_addr={} object_type={} '
                 'object_id={} property_id={} format={} value={}'.
                 format(self.port[port_index], self.verbose, self.src_addr, self.dst_addr, self.object_type, self.object_id, self.property_id, self.data_format, value))
    return write_cmd

  def write_cmd_RAM(self, port_index, value):
    write_cmd_RAM = ('--port={} --verbose={} write_property src_addr={} dst_addr={} object_type={} '
                     'object_id={} property_id={} format={} value={}'.
                     format(self.port[port_index], self.verbose, self.src_addr, self.dst_addr, self.object_type, self.object_id, self.parameter_object_property_Id_RAM, self.data_format, value))
    return write_cmd_RAM

  def read_cmd(self, port_index):
    read_cmd = ('--port={} --verbose={} read_property src_addr={} dst_addr={} object_type={} '
                'object_id={} property_id={} format={}'.
                format(self.port[port_index], self.verbose, self.src_addr, self.dst_addr, self.object_type, self.object_id, self.property_id, self.data_format))
    return read_cmd

  def read(self, port_index):
    read_cmd = self.read_cmd(port_index)
    scom_output = subprocess.Popen(dir_scom + read_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    str_output = scom_output.stdout.readlines()
    if ScomCommand.display_output:
      for line in str_output:
        print line
    if str_output[-7] == 'response:\r\n':
      raw_data = str_output[-1]
      raw_data = raw_data[5:]
      try:
        data = int(raw_data)
      except:
        data = raw_data
      return data
    else:
      print 'Fetching Info Failure'

  def write(self, port_index, value):
    write_cmd = self.write_cmd(port_index, value)
    scom_output = subprocess.Popen(dir_scom + write_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    str_output = scom_output.stdout.readlines()
    if ScomCommand.display_output:
      for line in str_output:
        print line
    if str_output[-5] != 'debug: rx bytes:\r\n':
      print 'Sending Command Failure'

  def write_RAM(self, port_index, value):
    write_cmd = self.write_cmd_RAM(port_index, value)
    scom_output = subprocess.Popen(dir_scom + write_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    str_output = scom_output.stdout.readlines()
    if ScomCommand.display_output:
      for line in str_output:
        print line
    if str_output[-5] != 'debug: rx bytes:\r\n':
      print 'Sending Command Failure'


# 2.4 Import Register Dict
# -------------------------
labels = ['property_id', 'description', 'format']
# BSP setting parameters
BSP_setting = [(6000, 'BASIC SETINGS', 'ONLY LEVEL'),
               (6057, '    Voltage of the system', 'LONG ENUM'),
               (6001, '    Nominal capacity', 'FLOAT'),
               (6002, '    Nominal discharge duration (C-rating)', 'FLOAT'),
               (6017, '    Nominal shunt current', 'FLOAT'),
               (6018, '    Nominal shunt voltage', 'FLOAT'),
               (6003, '    Reset of battery history', 'INT32'),
               (6004, '    Restore default settings', 'INT32'),
               (6005, '    Restore factory settings', 'INT32'),
               (6016, 'ADVANCED SETTINGS', 'ONLY LEVEL'),
               (6031, '    Reset of user counters', 'INT32'),
               (6055, '    Manufacturer SOC for 0% diplayed', 'FLOAT'),
               (6056, '    Manufacturer SOC for 100% displayed', 'FLOAT'),
               (6042, '    Activate the end of charge synchronization', 'BOOL'),
               (6024, '    End of charge voltage level', 'FLOAT'),
               (6025, '    End of charge current level', 'FLOAT'),
               (6026, '    Minimum duration before end of charge voltage', 'FLOAT'),
               (6048, '    Temperature correction of the end of charge voltage', 'FLOAT'),
               (6044, '    Activate the state of charge correction by the open circuit voltage', 'BOOL'),
               (6058, '    Battery current limitation activated', 'BOOL'),
               (6059, '    Max battery charge current', 'FLOAT'),
               (6019, '    Self-discharge rate', 'FLOAT'),
               (6020, '    Nominal temperature', 'FLOAT'),
               (6021, '    Temperature coefficient', 'FLOAT'),
               (6022, '    Charge efficiency factor', 'FLOAT'),
               (6023, '    Peukert exponent', 'FLOAT'),
               (6049, '    Use C20 Capacity as reference value', 'BOOL')]
BSP_setting = pd.DataFrame(BSP_setting, columns=labels)
# -----------------------------------------------------
# BSP info parameters
BSP_info = [(7000, 'Battery voltage', 'FLOAT'),
            (7001, 'Battery current', 'FLOAT'),
            (7002, 'State of Charge', 'FLOAT'),
            (7003, 'Power', 'FLOAT'),
            (7004, 'Remaining autonomy', 'FLOAT'),
            (7006, 'Relative capacity', 'FLOAT'),
            (7007, 'Ah charged today', 'FLOAT'),
            (7008, 'Ah discharged today', 'FLOAT'),
            (7009, 'Ah charged yesterday', 'FLOAT'),
            (7010, 'Ah discharged yesterday', 'FLOAT'),
            (7011, 'Total Ah charged', 'FLOAT'),
            (7012, 'Total Ah discharged', 'FLOAT'),
            (7013, 'Total time', 'FLOAT'),
            (7017, 'Custom charge Ah counter', 'FLOAT'),
            (7018, 'Custom discharge Ah counter', 'FLOAT'),
            (7019, 'Custom counter duration', 'FLOAT'),
            (7029, 'Battery temperature', 'FLOAT'),
            (7030, 'Battery voltage (minute avg)', 'FLOAT'),
            (7031, 'Battery current (minute avg)', 'FLOAT'),
            (7032, 'State of Charge (minute avg)', 'FLOAT'),
            (7033, 'Battery temperature (minute avg)', 'FLOAT'),
            (7034, 'ID type', 'FLOAT'),
            (7035, 'ID batt voltage', 'FLOAT'),
            (7036, 'ID HW', 'FLOAT'),
            (7037, 'ID SOFT msb', 'FLOAT'),
            (7038, 'ID SOFT lsb', 'FLOAT'),
            (7039, 'Parameter number (in code)', 'FLOAT'),
            (7040, 'Info user number', 'FLOAT'),
            (7041, 'ID SID', 'FLOAT'),
            (7047, 'SOC manufacturer', 'FLOAT'),
            (7048, 'ID FID msb', 'FLOAT'),
            (7049, 'ID FID lsb', 'FLOAT'),
            (7053, 'Battery Type. With Xcom-CAN', 'FLOAT'),
            (7054, 'BMS Version. With Xcom-CAN', 'FLOAT'),
            (7055, 'Battery Capacity. With Xcom-CAN', 'FLOAT'),
            (7056, 'Reserved Manufacturer ID. With Xcom-CAN', 'FLOAT'),
            (7057, 'State Of Health. With Xcom-CAN', 'FLOAT'),
            (7058, 'High resolution State of Charge. With Xcom-CAN', 'FLOAT'),
            (7059, 'Local daily communication error counter', 'FLOAT'),
            (7060, 'Number of parameters (in flash)', 'FLOAT'),
            (7061, 'Charge voltage limit. With Xcom-CAN', 'FLOAT'),
            (7062, 'Discharge voltage limit. With Xcom-CAN', 'FLOAT'),
            (7063, 'Charge current limit. With Xcom-CAN', 'FLOAT'),
            (7064, 'Discharge current limit. With Xcom-CAN', 'FLOAT')]
BSP_info = pd.DataFrame(BSP_info, columns=labels)
# -----------------------------------------------
# RCC parameters
RCC = [(5000, 'Language', 'INT32'),
       (5036, 'OTHER LANGUAGES', 'ONLY LEVEL'),
       (5038, '    Choice of the second language', 'LONG ENUM'),
       (5039, '    Choice of the third language', 'LONG ENUM'),
       (5040, '    Choice of the fourth language', 'LONG ENUM'),
       (5002, 'Date', 'INT32'),
       (5012, 'User level', 'Not Supported'),
       (5019, 'Force remote control to user BASIC level', 'INT32'),
       (5057, 'DATALOGGER', 'ONLY LEVEL'),
       (5101, '    Datalogger enabled', 'LONG ENUM'),
       (5059, '    Save today datas', 'INT32'),
       (5109, '    Datalogger reset when modifying the installation', 'BOOL'),
       (5120, '    Erase the 30 oldest log files from the SD card', 'INT32'),
       (5076, '    Track 1: device', 'LONG ENUM'),
       (5077, '    Track 1: reference', 'FLOAT'),
       (5078, '    Track 2: device', 'LONG ENUM'),
       (5079, '    Track 2: reference', 'FLOAT'),
       (5080, '    Track 3: device', 'LONG ENUM'),
       (5081, '    Track 3: reference', 'FLOAT'),
       (5082, '    Track 4: device', 'LONG ENUM'),
       (5083, '    Track 4: reference', 'FLOAT'),
       (5013, 'SAVE AND RESTORE FILES', 'ONLY LEVEL'),
       (5041, '    Save all files (system backup)', 'INT32'),
       (5068, '    Restore all files (system recovery)', 'INT32'),
       (5070, '    Apply configuration files (masterfile)', 'INT32'),
       (5032, '    Separator of the .csv files', 'LONG ENUM'),
       (5069, '    Advanced backup functions', 'ONLY LEVEL'),
       (5030, '        Save messages', 'INT32'),
       (5049, '        Save and restore RCC files', 'ONLY LEVEL'),
       (5015, '            Save RCC parameters', 'INT32'),
       (5016, '            Load RCC parameters', 'INT32'),
       (5097, '            Create RCC configuration file (masterfile)', 'INT32'),
       (5098, '            Load RCC configuration file (masterfile)', 'INT32'),
       (5050, '        Save and restore Xtender files', 'ONLY LEVEL'),
       (5017, '            Save Xtender parameters', 'INT32'),
       (5018, '            Load Xtender parameters', 'INT32'),
       (5033, '            Create Xtender configuration file (masterfile)', 'INT32'),
       (5034, '            Load Xtender configuration file (masterfile)', 'INT32'),
       (5045, '            Load Xtender parameters preset', 'Not Supported'),
       (5051, '        Save and restore BSP files', 'ONLY LEVEL'),
       (5052, '            Save BSP parameters', 'INT32'),
       (5053, '            Load BSP parameters', 'INT32'),
       (5054, '            Create BSP configuration file (masterfile)', 'INT32'),
       (5055, '            Load BSP configuration file (masterfile)', 'INT32'),
       (5084, '        Save and restore VarioTrack files', 'ONLY LEVEL'),
       (5085, '            Save VarioTrack parameters', 'INT32'),
       (5086, '            Load VarioTrack parameters', 'INT32'),
       (5087, '            Create VarioTrack configuration file (masterfile)', 'INT32'),
       (5088, '            Load VarioTrack configuration file (masterfile)', 'INT32'),
       (5114, '        Save and restore VarioString files', 'ONLY LEVEL'),
       (5115, '            Save VarioString parameters', 'INT32'),
       (5116, '            Load VarioString parameters', 'INT32'),
       (5117, '            Create VarioString configuration file (masterfile)', 'INT32'),
       (5118, '            Load VarioString configuration file (masterfile)', 'INT32'),
       (5063, '        Save and restore MPPT Tristar files', 'ONLY LEVEL'),
       (5064, '            Save MPPT Tristar parameters', 'INT32'),
       (5065, '            Load MPPT Tristar parameters', 'INT32'),
       (5066, '            Create MPPT Tristar configuration file (masterfile)', 'INT32'),
       (5067, '            Load MPPT Tristar configuration file (masterfile)', 'INT32'),
       (5047, '        Format the SD card', 'INT32'),
       (5061, '        Start update', 'INT32'),
       (5042, 'MODIFICATION OF ACCESS LEVELS OF MANY PARAMETERS', 'ONLY LEVEL'),
       (5043, '    Change all parameters access level to:', 'LONG ENUM'),
       (5044, '    Restore default access level of all parameters', 'INT32'),
       (5007, 'BACKLIGHT', 'ONLY LEVEL'),
       (5093, '    Backlight mode', 'LONG ENUM'),
       (5009, '    Backlight switch off after', 'FLOAT'),
       (5026, '    Red backlight flashing on Xtender off and faulty', 'BOOL'),
       (5021, 'EXTENDED AND SPECIAL FUNCTIONS', 'ONLY LEVEL'),
       (5006, '    Display contrast', 'FLOAT'),
       (5073, '    Choice of standard display', 'LONG ENUM'),
       (5010, '    Come back to standard display after', 'FLOAT'),
       (5011, '    Visibility of the transitory messages', 'FLOAT'),
       (5027, '    Acoustic alarm active', 'BOOL'),
       (5031, '    Remote control acoustic alarm duration', 'FLOAT'),
       (5056, '    Switching ON and OFF of system on level "VIEW ONLY"', 'BOOL'),
       (5071, '    Reset of all the remotes control', 'INT32'),
       (5121, '    Reset all devices of the system', 'INT32'),
       (5090, '    Update FID (only 1 device)', 'ONLY LEVEL'),
       (5091, '        Choose device type', 'LONG ENUM'),
       (5092, '        Choose device id (UID)', 'FLOAT'),
       (5062, '        Update device FID', 'INT32'),
       (5094, 'SCOM', 'ONLY LEVEL'),
       (5105, '    Test of the modem GPRS signal level', 'INT32'),
       (5119, '    Device identification (LEDs) with the SCOM address', 'FLOAT'),
       (5095, '    SCOM watchdog enable', 'BOOL'),
       (5096, '    Delay before Xcom-232i reset', 'FLOAT'),
       (5103, '    Activation of the watchdog hardware (deactivation restarts the RCC)', 'BOOL'),
       (5104, '    Clears the restart flag of RCC', 'INT32'),
       (5035, '    Erase messages', 'INT32')]
RCC = pd.DataFrame(RCC, columns=labels)
# -------------------------------------
# Xtender setting parameters
Xtender_setting = [(1100, 'BASIC SETTINGS', 'ONLY LEVEL'),
                   (1551, '    Basic parameters set by means of the potentiomenter in the XTS', 'BOOL'),
                   (1107, '    Maximum current of AC source (Input limit)', 'FLOAT'),
                   (1138, '    Battery charge current', 'FLOAT'),
                   (1126, '    Smart-Boost allowed', 'BOOL'),
                   (1124, '    Inverter allowed', 'BOOL'),
                   (1552, '    Type of detection of the grid loss (AC-In)', 'LONG ENUM'),
                   (1187, '    Standby level', 'FLOAT'),
                   (1395, '    Restore default settings', 'INT32'),
                   (1287, '    Restore factory settings', 'INT32'),
                   (1137, 'BATTERY MANAGEMENT AND CYCLE', 'ONLY LEVEL'),
                   (1125, '    Charger allowed', 'BOOL'),
                   (1646, '    Charger uses only power from Acout', 'BOOL'),
                   (1138, '    Battery charge current', 'FLOAT'),
                   (1139, '    Temperature compensation', 'FLOAT'),
                   (1615, '    Fast charge/inject regulation', 'BOOL'),
                   (1645, '    Pulses cutting regulation for XT', 'BOOL'),
                   (1568, '    Undervoltage', 'ONLY LEVEL'),
                   (1108, '        Battery undervoltage level without load', 'FLOAT'),
                   (1531, '        Battery undervoltage dynamic compensation', 'ONLY LEVEL'),
                   (1191, '            Battery undervoltage dynamic compensation', 'BOOL'),
                   (1532, '            Kind of dynamic compensation', 'LONG ENUM'),
                   (1632, '            Automatic adaption of dynamic compensation', 'FLOAT'),
                   (1109, '            Battery undervoltage level at full load', 'FLOAT'),
                   (1190, '        Battery undervoltage duration before turn off', 'FLOAT'),
                   (1110, '        Restart voltage after batteries undervoltage', 'FLOAT'),
                   (1194, '        Battery adaptive low voltage (B.L.O)', 'BOOL'),
                   (1195, '        Max voltage for adaptive low voltage', 'FLOAT'),
                   (1307, '        Reset voltage for adaptive correction', 'FLOAT'),
                   (1298, '        Increment step of the adaptive low voltage', 'FLOAT'),
                   (1121, '    Battery overvoltage level', 'FLOAT'),
                   (1122, '    Restart voltage level after an battery overvoltage', 'FLOAT'),
                   (1140, '    FLOATing voltage', 'FLOAT'),
                   (1467, '    Force phase of Foating', 'INT32'),
                   (1141, '    New cycle menu', 'ONLY LEVEL'),
                   (1142, '        Force a new cycle', 'INT32'),
                   (1608, '        Use dynamic compensation of battery level (new cycle)', 'BOOL'),
                   (1143, '        Voltage level 1 to start a new cycle', 'FLOAT'),
                   (1144, '        Time period under voltage level 1 to start a new cycle', 'FLOAT'),
                   (1145, '        Voltage level 2 to start a new cycle', 'FLOAT'),
                   (1146, '        Time period under voltage level 2 to start a new cycle', 'FLOAT'),
                   (1149, '        New cycle priority on absorption and equalization phases', 'BOOL'),
                   (1147, '        Cycling restricted', 'BOOL'),
                   (1148, '        Minimal delay between cycles', 'FLOAT'),
                   (1451, '    Absorption phase', 'ONLY LEVEL'),
                   (1155, '        Absorption phase allowed', 'BOOL'),
                   (1156, '        Absorption voltage', 'FLOAT'),
                   (1157, '        Absorption duration', 'FLOAT'),
                   (1158, '        End of absorption triggered with current', 'BOOL'),
                   (1159, '        Current limit to quit the absorption phase', 'FLOAT'),
                   (1160, '        Maximal frequency of absorption control', 'BOOL'),
                   (1161, '        Minimal delay since last absorption', 'FLOAT'),
                   (1452, '    Equalization phase', 'ONLY LEVEL'),
                   (1163, '        Equalization allowed', 'BOOL'),
                   (1162, '        Force equalization', 'INT32'),
                   (1291, '        Equalization before absorption phase', 'BOOL'),
                   (1290, '        Equalization current', 'FLOAT'),
                   (1164, '        Equalization voltage', 'FLOAT'),
                   (1165, '        Equalization duration', 'FLOAT'),
                   (1166, '        Number of cycles before an equalization', 'FLOAT'),
                   (1284, '        Equalization with fixed interval', 'BOOL'),
                   (1285, '        Weeks between equalizations', 'FLOAT'),
                   (1168, '        End of equalization triggered with current', 'BOOL'),
                   (1169, '        Current threshold to end equalization phase', 'FLOAT'),
                   (1453, '    Reduced Foating phase', 'ONLY LEVEL'),
                   (1170, '        Reduced Foaing allowed', 'BOOL'),
                   (1171, '        Foating duration before reduced Foating', 'FLOAT'),
                   (1172, '        Reduced Foating voltage', 'FLOAT'),
                   (1454, '    Periodic absorption phase', 'ONLY LEVEL'),
                   (1173, '        Periodic absorption allowed', 'BOOL'),
                   (1174, '        Periodic absorption voltage', 'FLOAT'),
                   (1175, '        Reduced Foating duration before periodic absorption', 'FLOAT'),
                   (1176, '        Periodic absorption duration', 'FLOAT'),
                   (1186, 'IVERTER', 'ONLY LEVE'),
                   (1124, '    Inverter allowed', 'BOOL'),
                   (1286, '    AC Output voltage', 'FLOAT'),
                   (1548, '    AC voltage increase according to battery voltage', 'BOOL'),
                   (1560, '    Max AC voltage increase with battery voltage', 'FLOAT'),
                   (1112, '    Inverter frequency', 'FLOAT'),
                   (1536, '    Inverter frequency increase when battery full', 'BOOL'),
                   (1549, '    Inverter frequency increase according to battery voltage', 'BOOL'),
                   (1546, '    Max frequency increase', 'FLOAT'),
                   (1534, '    Speed of voltage or frequency change in function of battery', 'FLOAT'),
                   (1420, '    Standby and turn on', 'ONLY LEVEL'),
                   (1187, '        Standby level', 'FLOAT'),
                   (1189, '        Time delay between standby pulses', 'FLOAT'),
                   (1188, '        Standby number of pulses', 'FLOAT'),
                   (1599, '        Softstart duration', 'FLOAT'),
                   (1438, '    Solsafe presence Energy source  at AC-Out side', 'BOOL'),
                   (1572, '    Modulator ru_soll', 'BOOL'),
                   (1197, 'AC-IN AND TRANSFER', 'ONLY LEVEL'),
                   (1128, '    Transfer relay allowed', 'BOOL'),
                   (1580, '    Delay before closing transfer relay', 'FLOAT'),
                   (1126, '    Smart-Boost allowed', 'BOOL'),
                   (1607, '    Limitation of the power Boost', 'FLOAT'),
                   (1107, '    Maximum current of AC source (Input limit)', 'FLOAT'),
                   (1471, '    Max input current modification', 'ONLY LEVEL'),
                   (1566, '        Using a secondary value for the maximum current of the AC source', 'BOOL'),
                   (1567, '        Second maximum current of the AC source (Input limit)', 'FLOAT'),
                   (1527, '        Decrease max input limit current with AC-In voltage', 'BOOL'),
                   (1554, '        Decrease of the max. current of the source with input voltage activated by command entry', 'BOOL'),
                   (1309, '        AC input low limit voltage to allow charger function', 'FLOAT'),
                   (1433, '        Adaptation range of the input current according to the input voltage', 'FLOAT'),
                   (1553, '        Speed of input limit increase', 'FLOAT'),
                   (1295, '        Charge current decrease coef. at voltage limit to turn back in inverter mode', 'FLOAT'),
                   (1436, '    Overrun AC source current limit without opening the transfer relay (Input limit)', 'BOOL'),
                   (1552, '    Type of detection of the grid loss (AC-In)', 'LONG ENUM'),
                   (1510, '    Tolerance on detection of AC-input loss (tolerant UPS mode)', 'FLOAT'),
                   (1199, '    Input voltage giving an opening of the transfer relay with delay', 'FLOAT'),
                   (1198, '    Time delay before opening of transfer relay', 'FLOAT'),
                   (1200, '    Input voltage giving an immediate opening of the transfer relay (UPS)', 'FLOAT'),
                   (1432, '    Absolute max limit for input voltage', 'FLOAT'),
                   (1500, '    Standby of the charger allowed', 'BOOL'),
                   (1505, '    Delta frequency allowed above the standard input frequency', 'FLOAT'),
                   (1506, '    Delta frequency allowed under the standard input frequency', 'FLOAT'),
                   (1507, '    Duration with frequency error before opening the transfer', 'FLOAT'),
                   (1575, '    AC-IN current active filtering', 'BOOL'),
                   (1557, '    Use an energy quota on AC-input', 'BOOL'),
                   (1559, '    AC-in energy quota', 'FLOAT'),
                   (1201, 'AUXILIARY CONTACT 1', 'ONLY LEVEL'),
                   (1202, '    Operating mode (AUX 1)', 'LONG ENUM'),
                   (1497, '    Combination of the events for the auxiliary contact (AUX 1)', 'LONG ENUM'),
                   (1203, '    Temporal restrictions (AUX 1)', 'ONLY LEVEL'),
                   (1204, '        Program 1 (AUX 1)', 'ONLY LEVEL'),
                   (1205, '            Day of the week (AUX 1)', 'LONG ENUM'),
                   (1206, '            Start hour (AUX 1)', 'INT32'),
                   (1207, '            End hour (AUX 1)', 'INT32'),
                   (1208, '        Program 2 (AUX 1)', 'ONLY LEVEL'),
                   (1209, '            Day of the week (AUX 1)', 'LONG ENUM'),
                   (1210, '            Start hour (AUX 1)', 'INT32'),
                   (1211, '            End hour (AUX 1)', 'INT32'),
                   (1212, '        Program 3 (AUX 1)', 'ONLY LEVEL'),
                   (1213, '            Day of the week (AUX 1)', 'LONG ENUM'),
                   (1214, '            Start hour (AUX 1)', 'INT32'),
                   (1215, '            End hour (AUX 1)', 'INT32'),
                   (1216, '        Program 4 (AUX 1)', 'ONLY LEVEL'),
                   (1217, '            Day of the week (AUX 1)', 'LONG ENUM'),
                   (1218, '            Start hour (AUX 1)', 'INT32'),
                   (1219, '            End hour (AUX 1)', 'INT32'),
                   (1220, '        Program 5 (AUX 1)', 'ONLY LEVEL'),
                   (1221, '            Day of the week (AUX 1)', 'LONG ENUM'),
                   (1222, '            Start hour (AUX 1)', 'INT32'),
                   (1223, '            End hour (AUX 1)', 'INT32'),
                   (1269, '    Contact active with a fixed time schedule (AUX 1)', 'ONLY LEVEL'),
                   (1270, '        Program 1 (AUX 1)', 'ONLY LEVEL'),
                   (1271, '            Day of the week (AUX 1)', 'LONG ENUM'),
                   (1272, '            Start hour (AUX 1)', 'INT32'),
                   (1273, '            End hour (AUX 1)', 'INT32'),
                   (1274, '        Program 2 (AUX 1)', 'ONLY LEVEL'),
                   (1275, '            Day of the week (AUX 1)', 'LONG ENUM'),
                   (1276, '            Start hour (AUX 1)', 'INT32'),
                   (1277, '            End hour (AUX 1)', 'INT32'),
                   (1278, '        Program 3 (AUX 1)', 'ONLY LEVEL'),
                   (1279, '            Day of the week (AUX 1)', 'LONG ENUM'),
                   (1280, '            Start hour (AUX 1)', 'INT32'),
                   (1281, '            End hour (AUX 1)', 'INT32'),
                   (1455, '    Contact active on event (AUX 1)', 'ONLY LEVEL'),
                   (1225, '        Xtender is OFF (AUX 1)', 'BOOL'),
                   (1518, '        Xtender ON (AUX 1)', 'BOOL'),
                   (1543, '        Remote entry (AUX 1)', 'BOOL'),
                   (1226, '        Battery undervoltage alarm (AUX 1)', 'BOOL'),
                   (1227, '        Battery overvoltage (AUX 1)', 'BOOL'),
                   (1228, '        Inverter or Smart- Boost overload (AUX 1)', 'BOOL'),
                   (1229, '        Overtemperature (AUX 1)', 'BOOL'),
                   (1520, '        No overtemperature (AUX 1)', 'BOOL'),
                   (1231, '        Active charger (AUX 1)', 'BOOL'),
                   (1232, '        Active inverter (AUX 1)', 'BOOL'),
                   (1233, '        Active Smart-Boost (AUX 1)', 'BOOL'),
                   (1234, '        AC input presence but with fault (AUX 1)', 'BOOL'),
                   (1235, '        AC input presence (AUX 1)', 'BOOL'),
                   (1236, '        Transfer relay ON (AUX 1)', 'BOOL'),
                   (1237, '        AC out presence (AUX 1)', 'BOOL'),
                   (1238, '        Bulk charge phase (AUX 1)', 'BOOL'),
                   (1239, '        Absorption phase (AUX 1)', 'BOOL'),
                   (1240, '        Equalization phase (AUX 1)', 'BOOL'),
                   (1242, '        Foating (AUX 1)', 'BOOL'),
                   (1243, '        Reduced Foating (AUX 1)', 'BOOL'),
                   (1244, '        Periodic absorption (AUX 1)', 'BOOL'),
                   (1601, '        AC-in energy quota (AUX1)', 'BOOL'),
                   (1245, '    Contact active according to battery voltage (AUX 1)', 'ONLY LEVEL'),
                   (1288, '        Use dynamic compensation of battery level (AUX 1)', 'BOOL'),
                   (1246, '        Battery voltage 1 activate (AUX 1)', 'BOOL'),
                   (1247, '        Battery voltage 1 (AUX 1)', 'FLOAT'),
                   (1248, '        Delay 1 (AUX 1)', 'FLOAT'),
                   (1249, '        Battery voltage 2 activate (AUX 1)', 'BOOL'),
                   (1250, '        Battery voltage 2 (AUX 1)', 'FLOAT'),
                   (1251, '        Delay 2 (AUX 1)', 'FLOAT'),
                   (1252, '        Battery voltage 3 activate (AUX 1)', 'BOOL'),
                   (1253, '        Battery voltage 3 (AUX 1)', 'FLOAT'),
                   (1254, '        Delay 3 (AUX 1)', 'FLOAT'),
                   (1255, '        Battery voltage to deactivate (AUX 1)', 'FLOAT'),
                   (1256, '        Delay to deactivate (AUX 1)', 'FLOAT'),
                   (1516, '        Deactivate if battery in Floating phase (AUX 1)', 'BOOL'),
                   (1257, '    Contact active with inverter power or Smart-Boost (AUX 1)', 'ONLY LEVEL'),
                   (1258, '        Inverter power level 1 activate (AUX 1)', 'BOOL'),
                   (1259, '        Power level 1 (AUX 1)', 'FLOAT'),
                   (1260, '        Time delay 1 (AUX 1)', 'FLOAT'),
                   (1644, '        Activated by AUX2 event partial overload', 'BOOL'),
                   (1261, '        Inverter power level 2 activate (AUX 1)', 'BOOL'),
                   (1262, '        Power level 2 (AUX 1)', 'FLOAT'),
                   (1263, '        Time delay 2 (AUX 1)', 'FLOAT'),
                   (1264, '        Inverter power level 3 activate (AUX 1)', 'BOOL'),
                   (1265, '        Power level 3 (AUX 1)', 'FLOAT'),
                   (1266, '        Time delay 3 (AUX 1)', 'FLOAT'),
                   (1267, '        Inverter power level to deactivate (AUX 1)', 'FLOAT'),
                   (1268, '        Time delay to deactivate (AUX 1)', 'FLOAT'),
                   (1503, '    Contact active according to battery temperature (AUX 1) With BSP or BTS', 'ONLY LEVEL'),
                   (1446, '        Contact activated with the temperature of battery (AUX 1)', 'BOOL'),
                   (1447, '        Contact activated over (AUX 1)', 'FLOAT'),
                   (1448, '        Contact deactivated below (AUX 1)', 'FLOAT'),
                   (1501, '    Contact active according to SOC (AUX 1) Only with BSP', 'ONLY LEVEL'),
                   (1439, '        Contact activated with the SOC 1 of battery (AUX 1)', 'BOOL'),
                   (1440, '        Contact activated below SOC 1 (AUX 1)', 'FLOAT'),
                   (1581, '        Delay 1 (AUX 1)', 'FLOAT'),
                   (1582, '        Contact activated with the SOC 2 of battery (AUX 1)', 'BOOL'),
                   (1583, '        Contact activated below SOC 2 (AUX 1)', 'FLOAT'),
                   (1584, '        Delay 2 (AUX 1)', 'FLOAT'),
                   (1585, '        Contact activated with the SOC 3 of battery (AUX 1)', 'BOOL'),
                   (1586, '        Contact activated below SOC 3 (AUX 1)', 'FLOAT'),
                   (1587, '        Delay 3 (AUX 1)', 'FLOAT'),
                   (1441, '        Contact deactivated over SOC (AUX 1)', 'FLOAT'),
                   (1588, '        Delay to deactivate (AUX 1)', 'FLOAT'),
                   (1589, '        Deactivate if battery in Floating phase (AUX 1)', 'BOOL'),
                   (1512, '    Security, maximum time of contact (AUX 1)', 'BOOL'),
                   (1514, '    Maximum time of operation of contact (AUX 1)', 'FLOAT'),
                   (1569, '    Reset all settings (AUX 1)', 'INT32'),
                   (1310, 'AUXILIARY CONTACT 2', 'ONLY LEVEL'),
                   (1311, '    Operating mode (AUX 2)', 'LONG ENUM'),
                   (1498, '    Combination of the events for the auxiliary contact (AUX 2)', 'LONG ENUM'),
                   (1312, '    Temporal restrictions (AUX 2)', 'ONLY LEVEL'),
                   (1313, '        Program 1 (AUX 2)', 'ONLY LEVEL'),
                   (1314, '            Day of the week (AUX 2)', 'LONG ENUM'),
                   (1315, '            Start hour (AUX 2)', 'INT32'),
                   (1316, '            End hour (AUX 2)', 'INT32'),
                   (1317, '        Program 2 (AUX 2)', 'ONLY LEVEL'),
                   (1318, '            Day of the week (AUX 2)', 'LONG ENUM'),
                   (1319, '            Start hour (AUX 2)', 'INT32'),
                   (1320, '            End hour (AUX 2)', 'INT32'),
                   (1321, '        Program 3 (AUX 2)', 'ONLY LEVEL'),
                   (1322, '            Day of the week (AUX 2)', 'LONG ENUM'),
                   (1323, '            Start hour (AUX 2)', 'INT32'),
                   (1324, '            End hour (AUX 2)', 'INT32'),
                   (1325, '        Program 4 (AUX 2)', 'ONLY LEVEL'),
                   (1326, '            Day of the week (AUX 2)', 'LONG ENUM'),
                   (1327, '            Start hour (AUX 2)', 'INT32'),
                   (1328, '            End hour (AUX 2)', 'INT32'),
                   (1329, '        Program 5 (AUX 2)', 'ONLY LEVEL'),
                   (1330, '            Day of the week (AUX 2)', 'LONG ENUM'),
                   (1331, '            Start hour (AUX 2)', 'INT32'),
                   (1332, '            End hour (AUX 2)', 'INT32'),
                   (1378, '    Contact active with a fixed time schedule (AUX 2)', 'ONLY LEVEL'),
                   (1379, '        Program 1 (AUX 2)', 'ONLY LEVEL'),
                   (1380, '            Day of the week (AUX 2)', 'LONG ENUM'),
                   (1381, '            Start hour (AUX 2)', 'INT32'),
                   (1382, '            End hour (AUX 2)', 'INT32'),
                   (1383, '        Program 2 (AUX 2)', 'ONLY LEVEL'),
                   (1384, '            Day of the week (AUX 2)', 'LONG ENUM'),
                   (1385, '            Start hour (AUX 2)', 'INT32'),
                   (1386, '            End hour (AUX 2)', 'INT32'),
                   (1387, '        Program 3 (AUX 2)', 'ONLY LEVEL'),
                   (1388, '            Day of the week (AUX 2)', 'LONG ENUM'),
                   (1389, '            Start hour (AUX 2)', 'INT32'),
                   (1390, '            End hour (AUX 2)', 'INT32'),
                   (1456, '    Contact active on event (AUX 2)', 'ONLY LEVEL'),
                   (1333, '        Xtender is OFF (AUX 2)', 'BOOL'),
                   (1519, '        Xtender ON (AUX 2)', 'BOOL'),
                   (1544, '        Remote entry (AUX 2)', 'BOOL'),
                   (1334, '        Battery undervoltage alarm (AUX 2)', 'BOOL'),
                   (1335, '        Battery overvoltage (AUX 2)', 'BOOL'),
                   (1336, '        Inverter or Smart-Boost overload (AUX 2)', 'BOOL'),
                   (1337, '        Overtemperature (AUX 2)', 'BOOL'),
                   (1521, '        No overtemperature (AUX 2)', 'BOOL'),
                   (1339, '        Active charger (AUX 2)', 'BOOL'),
                   (1340, '        Active inverter (AUX 2)', 'BOOL'),
                   (1341, '        Active Smart-Boost (AUX 2)', 'BOOL'),
                   (1342, '        AC input presence but with fault (AUX 2)', 'BOOL'),
                   (1343, '        AC input presence (AUX 2)', 'BOOL'),
                   (1344, '        Transfer contact ON (AUX 2)', 'BOOL'),
                   (1345, '        AC out presence (AUX 2)', 'BOOL'),
                   (1346, '        Bulk charge phase (AUX 2)', 'BOOL'),
                   (1347, '        Absorption phase (AUX 2)', 'BOOL'),
                   (1348, '        Equalization phase (AUX 2)', 'BOOL'),
                   (1350, '        Floating (AUX 2)', 'BOOL'),
                   (1351, '        Reduced Foating (AUX 2)', 'BOOL'),
                   (1352, '        Periodic absorption (AUX 2)', 'BOOL'),
                   (1602, '        AC-in energy quota (AUX2)', 'BOOL'),
                   (1643, '        Partial overload', 'BOOL'),
                   (1353, '    Contact active according to battery voltage (AUX 2)', 'ONLY LEVEL'),
                   (1354, '        Use dynamic compensation of battery level (AUX 2)', 'BOOL'),
                   (1355, '        Battery voltage 1 activate (AUX 2)', 'BOOL'),
                   (1356, '        Battery voltage 1 (AUX 2)', 'FLOAT'),
                   (1357, '        Delay 1 (AUX 2)', 'FLOAT'),
                   (1358, '        Battery voltage 2 activate (AUX 2)', 'BOOL'),
                   (1359, '        Battery voltage 2 (AUX 2)', 'FLOAT'),
                   (1360, '        Delay 2 (AUX 2)', 'FLOAT'),
                   (1361, '        Battery voltage 3 activate (AUX 2)', 'BOOL'),
                   (1362, '        Battery voltage 3 (AUX 2)', 'FLOAT'),
                   (1363, '        Delay 3 (AUX 2)', 'FLOAT'),
                   (1364, '        Battery voltage to deactivate (AUX 2)', 'FLOAT'),
                   (1365, '        Delay to deactivate (AUX 2)', 'FLOAT'),
                   (1517, '        Deactivate if battery in Floating phase (AUX 2)', 'BOOL'),
                   (1366, '    Contact active with inverter power or Smart-Boost (AUX 2)', 'ONLY LEVEL'),
                   (1367, '        Inverter power level 1 activate (AUX 2)', 'BOOL'),
                   (1368, '        Power level 1 (AUX 2)', 'FLOAT'),
                   (1369, '        Time delay 1 (AUX 2)', 'FLOAT'),
                   (1370, '        Inverter power level 2 activate (AUX 2)', 'BOOL'),
                   (1371, '        Power level 2 (AUX 2)', 'FLOAT'),
                   (1372, '        Time delay 2 (AUX 2)', 'FLOAT'),
                   (1373, '        Inverter power level 3 activate (AUX 2)', 'BOOL'),
                   (1374, '        Power level 3 (AUX 2)', 'FLOAT'),
                   (1375, '        Time delay 3 (AUX 2)', 'FLOAT'),
                   (1376, '        Inverter power level to deactivate (AUX 2)', 'FLOAT'),
                   (1377, '        Time delay to deactivate (AUX 2)', 'FLOAT'),
                   (1504, '    Contact active according to battery temperature (AUX 2) With BSP or BTS', 'ONLY LEVEL'),
                   (1457, '        Contact activated with the temperature of battery (AUX 2)', 'BOOL'),
                   (1458, '        Contact activated over (AUX 2)', 'FLOAT'),
                   (1459, '        Contact deactivated below (AUX 2)', 'FLOAT'),
                   (1502, '    Contact active according to SOC (AUX 2) Only with BSP', 'ONLY LEVEL'),
                   (1442, '        Contact activated with the SOC 1 of battery (AUX 2)', 'BOOL'),
                   (1443, '        Contact activated below SOC 1 (AUX 2)', 'FLOAT'),
                   (1590, '        Delay 1 (AUX 2)', 'FLOAT'),
                   (1591, '        Contact activated with the SOC 2 of battery (AUX 2)', 'BOOL'),
                   (1592, '        Contact activated below SOC 2 (AUX 2)', 'FLOAT'),
                   (1593, '        Delay 2 (AUX 2)', 'FLOAT'),
                   (1594, '        Contact activated with the SOC 3 of battery (AUX 2)', 'BOOL'),
                   (1595, '        Contact activated below SOC 3 (AUX 2)', 'FLOAT'),
                   (1596, '        Delay 3 (AUX 2)', 'FLOAT'),
                   (1444, '        Contact deactivated over SOC (AUX 2)', 'FLOAT'),
                   (1597, '        Delay to deactivate (AUX 2)', 'FLOAT'),
                   (1598, '        Deactivate if battery in Floating phase (AUX 2)', 'BOOL'),
                   (1513, '    Security, maximum time of contact (AUX 2)', 'BOOL'),
                   (1515, '    Maximum time of operation of contact (AUX 2)', 'FLOAT'),
                   (1570, '    Reset all settings (AUX 2)', 'INT32'),
                   (1489, 'AUXILIARY CONTACTS  1 AND 2 EXTENDED FUNCTIONS', 'ONLY LEVEL'),
                   (1491, '    Generator control active', 'BOOL'),
                   (1493, '    Number of starting attempts', 'FLOAT'),
                   (1492, '    Starter pulse duration (with AUX2)', 'FLOAT'),
                   (1494, '    Time before a starter pulse', 'FLOAT'),
                   (1574, '    Main contact hold/interrupt time', 'FLOAT'),
                   (1101, 'SYSTEM', 'ONLY LEVE'),
                   (1537, '    Remote entry (Remote ON/OFF)', 'ONLY LEVEL'),
                   (1545, '        Remote entry active', 'LONG ENUM'),
                   (1538, '        Prohibits transfert relay', 'BOOL'),
                   (1539, '        Prohibits inverter', 'BOOL'),
                   (1540, '        Prohibits charger', 'BOOL'),
                   (1541, '        Prohibits Smart-Boost', 'BOOL'),
                   (1542, '        Prohibits grid feeding', 'BOOL'),
                   (1566, '        Using a secondary value for the maximum current of the AC source', 'BOOL'),
                   (1567, '        Second maximum current of the AC source (Input limit)', 'FLOAT'),
                   (1554, '        Decrease of the max. current of the source with input voltage activated by command entry', 'BOOL'),
                   (1576, '        ON/OFF command', 'BOOL'),
                   (1578, '        Activated by AUX1 state', 'BOOL'),
                   (1579, '        Prohibits battery priority', 'BOOL'),
                   (1600, '        Disable minigrid mode', 'BOOL'),
                   (1640, '        Clear AUX2 event partial overload', 'BOOL'),
                   (1647, '        Prohibits charger using only power from Acout', 'BOOL'),
                   (1296, '    Batteries priority as energy source', 'BOOL'),
                   (1297, '    Battery priority voltage', 'FLOAT'),
                   (1565, '    Buzzer alarm duration', 'FLOAT'),
                   (1129, '    Auto restarts', 'ONLY LEVEL'),
                   (1130, '        After battery undervoltage', 'BOOL'),
                   (1304, '        Number of batteries undervoltage allowed before definitive stop', 'FLOAT'),
                   (1404, '        Time period for batteries undervoltages counting', 'FLOAT'),
                   (1305, '        Number of batteries critical undervoltage allowed before definitive stop', 'FLOAT'),
                   (1405, '        Time period for critical batteries undervoltages counting', 'FLOAT'),
                   (1131, '        After battery overvoltage', 'BOOL'),
                   (1132, '        After inverter or Smart-Boost overload', 'BOOL'),
                   (1533, '        Delay to restart after an overload', 'FLOAT'),
                   (1134, '        After overtemperature', 'BOOL'),
                   (1111, '        Autostart to the battery connection', 'BOOL'),
                   (1484, '    System earthing (Earth - Neutral)', 'ONLY LEVEL'),
                   (1485, '        Prohibited ground relay', 'BOOL'),
                   (1486, '        Continuous neutral', 'BOOL'),
                   (1628, '    Xtender watchdog enabled(SCOM)', 'BOOL'),
                   (1629, '    Xtender watchdog delay(SCOM)', 'FLOAT'),
                   (1616, '    Use of functions limited to a number of days', 'BOOL'),
                   (1391, '    Number of days without functionalitie restrictions', 'FLOAT'),
                   (1617, '    Transfer relay disabled after timeout', 'BOOL'),
                   (1618, '    Inverter disabled after timeout', 'BOOL'),
                   (1619, '    Charger disabled after timeout', 'BOOL'),
                   (1620, '    Smart-Boost disabled after timeout', 'BOOL'),
                   (1621, '    Grid feeding disabled after timeout', 'BOOL'),
                   (1395, '    Restore default setting', 'INT32'),
                   (1287, '    Restore factory setting', 'INT32'),
                   (1550, '    Parameters saved in flash memory', 'BOOL'),
                   (1415, '    Global ON of the system', 'INT32'),
                   (1399, '    Global OFF of the system', 'INT32'),
                   (1468, '    Reset of all the inverters', 'INT32'),
                   (1282, 'MULTI XTENDER SYSTEM', 'ONLY LEVEL'),
                   (1283, '    Integral mode', 'BOOL'),
                   (1461, '    Multi inverters allowed', 'BOOL'),
                   (1462, '    Multi inverters independents. Need reset {1468}', 'BOOL'),
                   (1555, '    Battery cycle synchronized by the master', 'BOOL'),
                   (1547, '    Allow slaves standby in multi-Xtender system', 'BOOL'),
                   (1571, '    Splitphase: L2 with 180 degrees phaseshift', 'BOOL'),
                   (1558, '    Separated Batteries', 'BOOL'),
                   (1437, '    Minigrid compatible', 'BOOL'),
                   (1577, '    Minigrid with shared battery energy', 'BOOL'),
                   (1556, '    is central inverter in distributed minigrid', 'BOOL'),
                   (1522, 'GRID-FEEDING', 'ONLY LEVEL'),
                   (1127, '    Grid feeding allowed', 'BOOL'),
                   (1523, '    Max grid feeding current', 'FLOAT'),
                   (1524, '    Battery voltage target for forced grid feeding', 'FLOAT'),
                   (1525, '    Forced grid feeding start time', 'INT32'),
                   (1526, '    Forced grid feeding stop time', 'INT32'),
                   (1610, '    Use of the defined phase shift curve for injection', 'BOOL'),
                   (1622, '    Cos phi at P = 0%', 'FLOAT'),
                   (1623, '    Cos phi at the power defined by param {1613}', 'FLOAT'),
                   (1613, '    Power of the second cos phi point in % of Pnom', 'FLOAT'),
                   (1624, '    Cos phi at P = 100%', 'FLOAT'),
                   (1627, '    ARN4105 frequency control enabled', 'BOOL'),
                   (1630, '    Delta from user frequency to start derating', 'FLOAT'),
                   (1631, '    Delta from user frequency to reach 100% derating', 'FLOAT'),
                   (1562, '    Correction for XTS saturation', 'FLOAT')]
Xtender_setting = pd.DataFrame(Xtender_setting, columns=labels)
# -------------------------------------------------------------
# Xtender info parameters
Xtender_info = [(3000, 'Battery voltage', 'FLOAT'),
                (3001, 'Battery temperature', 'FLOAT'),
                (3002, 'Temperature compensation of battery voltage', 'FLOAT'),
                (3003, 'Dynamic compensation of battery voltage', 'FLOAT'),
                (3004, 'Wanted battery charge current', 'FLOAT'),
                (3005, 'Battery charge current', 'FLOAT'),
                (3006, 'Battery voltage ripple', 'FLOAT'),
                (3007, 'State of charge', 'FLOAT'),
                (3008, 'Low Voltage Disconect', 'FLOAT'),
                (3010, 'Battery cycle phase', 'SHORT ENUM'),
                (3011, 'Input voltage', 'FLOAT'),
                (3012, 'Input current', 'FLOAT'),
                (3013, 'Input power', 'FLOAT'),
                (3017, 'Input limit value', 'FLOAT'),
                (3018, 'Input limite reached', 'SHORT ENUM'),
                (3019, 'Boost active', 'SHORT ENUM'),
                (3020, 'State of transfer relay', 'SHORT ENUM'),
                (3021, 'Output voltage', 'FLOAT'),
                (3022, 'Output current', 'FLOAT'),
                (3023, 'Output power', 'FLOAT'),
                (3028, 'Operating state', 'SHORT ENUM'),
                (3030, 'State of output relay', 'SHORT ENUM'),
                (3031, 'State of auxiliary relay I', 'SHORT ENUM'),
                (3032, 'State of auxiliary relay II', 'SHORT ENUM'),
                (3045, 'Nbr. of overloads', 'FLOAT'),
                (3046, 'Nbr. overtemperature', 'FLOAT'),
                (3047, 'Nbr. batterie overvoltage', 'FLOAT'),
                (3049, 'State of the inverter', 'SHORT ENUM'),
                (3050, 'Number of battery elements', 'FLOAT'),
                (3051, 'Search mode state', 'SHORT ENUM'),
                (3054, 'Relay aux I mode', 'SHORT ENUM'),
                (3055, 'Relay aux II mode', 'SHORT ENUM'),
                (3056, 'Lockings flag', 'FLOAT'),
                (3074, 'State of the ground relay', 'SHORT ENUM'),
                (3075, 'State of the neutral transfer relay', 'SHORT ENUM'),
                (3076, 'Discharge of battery of the previous day', 'FLOAT'),
                (3078, 'Discharge of battery of the current day', 'FLOAT'),
                (3080, 'Energy AC-In from the previous day', 'FLOAT'),
                (3081, 'Energy AC-In from the current day', 'FLOAT'),
                (3082, 'Consumers energy of the previous day', 'FLOAT'),
                (3083, 'Consumers energy of the current day', 'FLOAT'),
                (3084, 'Input frequency', 'FLOAT'),
                (3085, 'Output frequency', 'FLOAT'),
                (3086, 'Remote entry state', 'SHORT ENUM'),
                (3087, 'Output active power', 'FLOAT'),
                (3088, 'Input active power', 'FLOAT'),
                (3089, 'Defined phase', 'FLOAT'),
                (3090, 'Battery voltage (minute min)', 'FLOAT'),
                (3091, 'Battery voltage (minute max)', 'FLOAT'),
                (3092, 'Battery voltage (minute avg)', 'FLOAT'),
                (3093, 'Battery charge current (minute min)', 'FLOAT'),
                (3094, 'Battery charge current (minute max)', 'FLOAT'),
                (3095, 'Battery charge current (minute avg)', 'FLOAT'),
                (3096, 'Output power min (minute min)', 'FLOAT'),
                (3097, 'Output power (minute max)', 'FLOAT'),
                (3098, 'Output power (minute avg)', 'FLOAT'),
                (3099, 'Output active power (minute min)', 'FLOAT'),
                (3100, 'Output active power (minute max)', 'FLOAT'),
                (3101, 'Output active power (minute avg)', 'FLOAT'),
                (3102, 'Dev 1 (minute min)', 'FLOAT'),
                (3103, 'Dev 1 (minute max)', 'FLOAT'),
                (3104, 'Dev 1 (minute avg)', 'FLOAT'),
                (3105, 'Dev 2 (minute min)', 'FLOAT'),
                (3106, 'Dev 2 (minute max)', 'FLOAT'),
                (3107, 'Dev 2 (minute avg)', 'FLOAT'),
                (3108, 'Output frequency (minute min)', 'FLOAT'),
                (3109, 'Output frequency (minute max)', 'FLOAT'),
                (3110, 'Output frequency (minute avg)', 'FLOAT'),
                (3111, 'Input voltage (minute min)', 'FLOAT'),
                (3112, 'Input voltage (minute max)', 'FLOAT'),
                (3113, 'Input voltage (minute avg)', 'FLOAT'),
                (3114, 'Input current (minute min)', 'FLOAT'),
                (3115, 'Input current (minute max)', 'FLOAT'),
                (3116, 'Input current (minute avg)', 'FLOAT'),
                (3117, 'Input active power (minute min)', 'FLOAT'),
                (3118, 'Input active power (minute max)', 'FLOAT'),
                (3119, 'Input active power (minute avg)', 'FLOAT'),
                (3120, 'Input frequency (minute min)', 'FLOAT'),
                (3121, 'Input frequency (minute max)', 'FLOAT'),
                (3122, 'Input frequency (minute avg)', 'FLOAT'),
                (3124, 'ID type', 'FLOAT'),
                (3125, 'ID Power', 'FLOAT'),
                (3126, 'ID Uout', 'FLOAT'),
                (3127, 'ID batt voltage', 'FLOAT'),
                (3128, 'ID Iout nom', 'FLOAT'),
                (3129, 'ID HW', 'FLOAT'),
                (3130, 'ID SOFT msb', 'FLOAT'),
                (3131, 'ID SOFT lsb', 'FLOAT'),
                (3132, 'ID HW PWR', 'FLOAT'),
                (3133, 'Parameter number (in code)', 'FLOAT'),
                (3134, 'Info user number', 'FLOAT'),
                (3135, 'ID SID', 'FLOAT'),
                (3136, 'Output active power', 'FLOAT'),
                (3137, 'Input active power', 'FLOAT'),
                (3138, 'Input power', 'FLOAT'),
                (3139, 'Output power', 'FLOAT'),
                (3140, 'System debug 1', 'FLOAT'),
                (3141, 'System debug 2', 'FLOAT'),
                (3142, 'System state machine', 'FLOAT'),
                (3154, 'Input frequency', 'FLOAT'),
                (3155, 'Desired AC injection current', 'FLOAT'),
                (3156, 'ID FID msb', 'FLOAT'),
                (3157, 'ID FID lsb', 'FLOAT'),
                (3158, 'AC injection current limited (ARN4105)', 'FLOAT'),
                (3159, 'AC injection current, type of limitation (ARN4105)', 'SHORT ENUM'),
                (3160, 'Source of limitation of the functions charger or injector', 'SHORT ENUM'),
                (3161, 'Battery priority active', 'SHORT ENUM'),
                (3162, 'Forced grid feeding active', 'SHORT ENUM')]
Xtender_info = pd.DataFrame(Xtender_info, columns=labels)

# 2.5 Create Instances for Command Class
# ---------------------------------------
register_list = []
# BSP setting
for i in range(BSP_setting.shape[0]):
  tmp_object_id = BSP_setting.iloc[i].property_id
  tmp_data_format = BSP_setting.iloc[i].format
  if tmp_data_format == 'LONG ENUM':
    tmp_data_format = 'ENUM'
  if tmp_data_format == 'SHORT ENUM':
    tmp_data_format = 'ENUM'
  tmp_description = BSP_setting.iloc[i].description
  tmp_class_name = 'r' + str(tmp_object_id)
  register_list.append(tmp_class_name)
  tmp_cmd = ('{variable_name} = ScomCommand({port_name},{verbose_num},{src_addr},'
             '{dst_addr},{object_type},{object_id},{property_id},\'{data_format}\')'.
             format(variable_name=tmp_class_name, port_name=port_name, verbose_num=verbose_num,
                    src_addr=src_addr, dst_addr=BSP_addr, object_type=parameter_object_object_type,
                    object_id=tmp_object_id, property_id=parameter_object_property_Id_flash, data_format=tmp_data_format))
  exec(tmp_cmd)
  tmp_cmd = ('{variable_name}.description = \'{description}\''.format(
      variable_name=tmp_class_name, description=tmp_description))
  exec(tmp_cmd)
########################################################################################################
# BSP info
for i in range(BSP_info.shape[0]):
  tmp_object_id = BSP_info.iloc[i].property_id
  tmp_data_format = BSP_info.iloc[i].format
  if tmp_data_format == 'LONG ENUM':
    tmp_data_format = 'ENUM'
  if tmp_data_format == 'SHORT ENUM':
    tmp_data_format = 'ENUM'
  tmp_description = BSP_info.iloc[i].description
  tmp_class_name = 'r' + str(tmp_object_id)
  register_list.append(tmp_class_name)
  tmp_cmd = ('{variable_name} = ScomCommand({port_name},{verbose_num},{src_addr},'
             '{dst_addr},{object_type},{object_id},{property_id},\'{data_format}\')'.
             format(variable_name=tmp_class_name, port_name=port_name, verbose_num=verbose_num,
                    src_addr=src_addr, dst_addr=BSP_addr, object_type=user_info_object_object_type,
                    object_id=tmp_object_id, property_id=user_info_object_property_Id, data_format=tmp_data_format))
  exec(tmp_cmd)
  tmp_cmd = ('{variable_name}.description = \'{description}\''.format(
      variable_name=tmp_class_name, description=tmp_description))
  exec(tmp_cmd)
########################################################################################################
# RCC
for i in range(RCC.shape[0]):
  tmp_object_id = RCC.iloc[i].property_id
  tmp_data_format = RCC.iloc[i].format
  if tmp_data_format == 'LONG ENUM':
    tmp_data_format = 'LONG_ENUM'
  if tmp_data_format == 'SHORT ENUM':
    tmp_data_format = 'SHORT_ENUM'
  tmp_description = RCC.iloc[i].description
  tmp_class_name = 'r' + str(tmp_object_id)
  register_list.append(tmp_class_name)
  tmp_cmd = ('{variable_name} = ScomCommand({port_name},{verbose_num},{src_addr},'
             '{dst_addr},{object_type},{object_id},{property_id},\'{data_format}\')'.
             format(variable_name=tmp_class_name, port_name=port_name, verbose_num=verbose_num,
                    src_addr=src_addr, dst_addr=RCC_addr, object_type=parameter_object_object_type,
                    object_id=tmp_object_id, property_id=parameter_object_property_Id_flash, data_format=tmp_data_format))
  exec(tmp_cmd)
  tmp_cmd = ('{variable_name}.description = \'{description}\''.format(
      variable_name=tmp_class_name, description=tmp_description))
  exec(tmp_cmd)
########################################################################################################
# Xtender setting
for i in range(Xtender_setting.shape[0]):
  tmp_object_id = Xtender_setting.iloc[i].property_id
  tmp_data_format = Xtender_setting.iloc[i].format
  if tmp_data_format == 'LONG ENUM':
    tmp_data_format = 'ENUM'
  if tmp_data_format == 'SHORT ENUM':
    tmp_data_format = 'ENUM'
  tmp_description = Xtender_setting.iloc[i].description
  tmp_class_name = 'r' + str(tmp_object_id)
  register_list.append(tmp_class_name)
  tmp_cmd = ('{variable_name} = ScomCommand({port_name},{verbose_num},{src_addr},'
             '{dst_addr},{object_type},{object_id},{property_id},\'{data_format}\')'.
             format(variable_name=tmp_class_name, port_name=port_name, verbose_num=verbose_num,
                    src_addr=src_addr, dst_addr=XTM_addr, object_type=parameter_object_object_type,
                    object_id=tmp_object_id, property_id=parameter_object_property_Id_flash, data_format=tmp_data_format))
  exec(tmp_cmd)
  tmp_cmd = ('{variable_name}.description = \'{description}\''.format(
      variable_name=tmp_class_name, description=tmp_description))
  exec(tmp_cmd)
########################################################################################################
# Xtender info
for i in range(Xtender_info.shape[0]):
  tmp_object_id = Xtender_info.iloc[i].property_id
  tmp_data_format = Xtender_info.iloc[i].format
  if tmp_data_format == 'LONG ENUM':
    tmp_data_format = 'ENUM'
  if tmp_data_format == 'SHORT ENUM':
    tmp_data_format = 'ENUM'
  tmp_description = Xtender_info.iloc[i].description
  tmp_class_name = 'r' + str(tmp_object_id)
  register_list.append(tmp_class_name)
  tmp_cmd = ('{variable_name} = ScomCommand({port_name},{verbose_num},{src_addr},'
             '{dst_addr},{object_type},{object_id},{property_id},\'{data_format}\')'.
             format(variable_name=tmp_class_name, port_name=port_name, verbose_num=verbose_num,
                    src_addr=src_addr, dst_addr=XTM_addr, object_type=user_info_object_object_type,
                    object_id=tmp_object_id, property_id=user_info_object_property_Id, data_format=tmp_data_format))
  exec(tmp_cmd)
  tmp_cmd = ('{variable_name}.description = \'{description}\''.format(
      variable_name=tmp_class_name, description=tmp_description))
  exec(tmp_cmd)

# 2.6 Create Command Function
# ----------------------------
"""
The functions below are for reading information from the system and
perform scom command to read system info and get data
"""


def read_info(cmd):
  py2output = subprocess.Popen(dir_scom + cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  str_output = py2output.stdout.readlines()
  if display_output:
    for line in str_output:
      print line
  if str_output[-7] == 'response:\r\n':
    raw_data = str_output[-1]
    raw_data = raw_data[5:]
    try:
      data = int(raw_data)
    except ValueError:
      data = raw_data
    return data
  else:
    print 'Fetching Info Failure'


def send_command(cmd):
  py2output = subprocess.Popen(dir_scom + cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  str_output = py2output.stdout.readlines()
  if display_output:
    for line in str_output:
      print line
  if str_output[-5] != 'debug: rx bytes:\r\n':
    print 'Sending Command Failure'


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

# 3.2 Set port number and open it
# --------------------------------
# open serial port
if open_port:
  ser = serial.Serial('COM3', baudrate=38400)
  print(ser.name)         # check which port was really used

# 3.3 Test serial port connection and scom
# -----------------------------------------
# test if scom protocol is working with current serial port
if test_comm:
  py2output = subprocess.Popen(dir_scom + 'test', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  for line in py2output.stdout.readlines():
    print line
  retval = py2output.wait()

# 4 System Initialization
# ------------------------


def system_init(port_index):
  # Enable Xtender watchdog and diable saving parameters in flash drive
  # Xtender watchdog
  # 1 for yes; 0 for no
  r1628.write(port_index, 0)
  # Xtender watchdog delay in seconds (without response for this period of time, Xtender will restart)
  # r1629.write(port_index,60)
  # --------------
  # whether to save parameters in flash memory (for Xtender parameters)
  # 1 for yes; 0 for no
  # It is disabled in this system to save the lifetime of flash memory in case of repeated writings
  r1550.write(port_index, 0)

# 4.1. Xtender
# -------------


def xtender_open(port_index, Xtender_open):
  if Xtender_open:
    # Xtender on
    r1415.write_RAM(port_index, 1)


def xtender_close(port_index, Xtender_close):
  if Xtender_close:
    # Xtender off
    r1399.write_RAM(port_index, 0)


# 4.2. RCC
# ---------
"""
Get Xtender Time and Date & Synchronise RCC(System) Time and PC Time
When a PC is connected to Xcom-232i via serial port, the connected PC is recognised
by the Xtender as an RCC. For such reason, changing the RCC time according to current
time on the PC can be achieved.
"""
# -------------------------------------------------------------------------------------
# The time of the real system(RCC) is the value of seconds since 1/1/1970 00:00:00
reference_datetime = datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)
# -------------------------------------------------------------------------------
# Define functions to get and set time


def get_system_time(port_index):
  time_delta_second = r5002.read(port_index)
  system_datetime = reference_datetime + timedelta(seconds=time_delta_second)
  return system_datetime


def synchronise_time(port_index):
  current_datetime = datetime.now()
  system_datetime = get_system_time(port_index)
  target_time_delta_second = round((current_datetime - reference_datetime).total_seconds())
  time_delta_second = r5002.write_RAM(port_index, target_time_delta_second)
  system_datetime = get_system_time(port_index)
  return system_datetime
# -------------------------


def rcc_time_sync(port_index, rcc_init):
  if rcc_init:
    start_time = time.time()
    # Get current date and time from PC
    current_datetime = datetime.now()
    #current_year = current_datetime.year
    #current_month = current_datetime.month
    #current_mday = current_datetime.day
    #current_hour = current_datetime.hour
    #current_min = current_datetime.minute
    #current_sec = current_datetime.second
    print 'Local PC datetime is: ' + str(current_datetime)
    # Get current date and time from system(RCC) in seconds (from reference datetime)
    system_datetime = get_system_time(port_index)
    print 'Current system datetime is: ' + str(system_datetime)
    print 'Datetime synchronisation ...'
    current_system_datetime = synchronise_time(port_index)
    print 'Current system datetime is: ' + str(current_system_datetime)
    elapsed_time = time.time() - start_time
    print 'Rig ' + str(port_index) + ' RCC datetime synchronisation finished, took ' + str(elapsed_time) + ' seconds'
# -----------------------------------------------------------------------------------------


# 4.3. BSP
# ---------
"""
The recommended operation temperature range for lead acid batteries is 10°C and 35°C (best 20°C +/- 5k).
Higher temperature will seriously reduce service life. Lower temperature reduces the available capacity.
The absolute maximum temperature is 55°C and should exceed 45°C in service. Refer to the following link for
further information.
http://docs-europe.electrocomponents.com/webdocs/04a1/0900766b804a179a.pdf
"""
# -------------------------------------------------------------------------


def bsp_init(port_index, bsp_init, battery_setting):
    # Start initialization loop if enabled
  if bsp_init:
    if battery_setting == 1:
      """
      BSP ininitial setting for two Sonnenschein-S12/41 A batteries in series (2s)
      Please refer to the following links for futher infotmation about the battery
      used in the syetm.
      http://uk.rs-online.com/web/p/lead-acid-rechargeable-batteries/6521446/
      http://docs-europe.electrocomponents.com/webdocs/04a1/0900766b804a179a.pdf
      http://www.produktinfo.conrad.com/datenblaetter/250000-274999/251241-da-01-de-AKKU_BLEI_41AH_SOLAR_DRY_S12_41A.pdf
      """
      start_time = time.time()
      # ------------------------
      # 1. Voltage of the DC system (V) --- 6057
      #   Only one bit
      #   1: Automatic
      #   2: 12 V
      #   4: 24 V
      #   8: 48 V
      # Note: In the technical specification of Xtender serial
      # protocol (V1.6.20), 6057 should be of the format 'LONG ENUM',
      # however, it is not working with the scom. So 'ENUM' and 'INT32' was tested.
      # 'ENUM' is used here
      r6057.write_RAM(port_index, 4)
      # ------------------
      # 2. Nomonal capacity (Ah@C20) --- 6001
      r6001.write_RAM(port_index, 38)
      # ------------------
      # 3. Nominal discharge duration (C-rating) --- 6002
      r6002.write_RAM(port_index, 20)
      # ------------------
      # 4. Nominal shunt current (A) --- 6017
      r6017.write_RAM(port_index, 500)
      # ------------------
      # 5. Nominal shunt voltage (mV) --- 6018
      r6018.write_RAM(port_index, 50)
      # ------------------
      # 6. Use C20(aka C/20) as reference value (1 for yes, 0 for no) --- 6049
      r6049.write_RAM(port_index, 1)
      # ------------------
      # 7. Battery current limitation activation --- 6058
      # boolean format: 1 for yes, 0 for no
      r6058.write_RAM(port_index, 1)
      # ------------------
      # 8. Max battery charge current --- 6059
      # For lead acid battery, the charging current should be between 10 and 30 percent of the rated capacity.
      # A 10Ah battery at 30 percent charges at about 3A; the percentage can be lower. An 80Ah starter battery
      # may charge at 8A. (A 10 percent charge rate is equal to 0.1C.)
      # For further information please refer to the link below.
      # http://batteryuniversity.com/learn/article/charging_with_a_power_supply
      # In our system, the capacity at C20 is 38 and 30% of it is 11.4 A. So we
      # set our limitation value to 10A
      r6059.write_RAM(port_index, 10)
      elapsed_time = time.time() - start_time
      print 'Rig ' + str(port_index) + ' BSP(DK) initializaiton finished, took ' + str(elapsed_time) + ' seconds'
    # --------------------------------------------------------------------------------------
    elif battery_setting == 2:
      """
      BSP ininitial setting for two Sonnenschein-S12/130 A batteries in series + two in parallel (2s2p)
      Please refer to the following links for futher infotmation about the battery
      used in the syetm.
      https://www.tayna.co.uk/S12130-A-Sonnenschein-Solar-Series-Battery-P8111.html
      Please refer to the following link for battery connection.
      http://batteryuniversity.com/learn/article/serial_and_parallel_battery_configurations
      """
      start_time = time.time()
      # -----------------------
      # 1. Voltage of the DC system (V) --- 6057
      #   Only one bit
      #   1: Automatic
      #   2: 12 V
      #   4: 24 V
      #   8: 48 V
      # Note: In the technical specification of Xtender serial
      # protocol (V1.6.20), 6057 should be of the format 'LONG ENUM',
      # however, it is not working with the scom. So 'ENUM' and 'INT32' was tested.
      # 'ENUM' is used here
      r6057.write_RAM(port_index, 4)
      # -----------------------
      # 2. Nomonal capacity (Ah@C20) --- 6001
      r6001.write_RAM(port_index, 220)
      # -----------------------
      # 3. Nominal discharge duration (C-rating) --- 6002
      r6002.write_RAM(port_index, 20)
      # -----------------------
      # 4. Nominal shunt current (A) --- 6017
      r6017.write_RAM(port_index, 150)
      # -----------------------
      # 5. Nominal shunt voltage (mV) --- 6018
      r6018.write_RAM(port_index, 75)
      # -----------------------
      # 6. Use C20(aka C/20) as reference value (1 for yes, 0 for no) --- 6049
      r6049.write_RAM(port_index, 1)
      # -----------------------
      # 7. Battery current limitation activation --- 6058
      # boolean format: 1 for yes, 0 for no
      r6058.write_RAM(port_index, 1)
      # -----------------------
      # 8. Max battery charge current --- 6059
      # For lead acid battery, the charging current should be between 10 and 30 percent of the rated capacity.
      # A 10Ah battery at 30 percent charges at about 3A; the percentage can be lower. An 80Ah starter battery
      # may charge at 8A. (A 10 percent charge rate is equal to 0.1C.)
      # For further information please refer to the link below.
      # http://batteryuniversity.com/learn/article/charging_with_a_power_supply
      # In our system, the capacity at C20 is 220 and 30% of it is 66 A. So we
      # set our limitation value to 66A
      r6059.write_RAM(port_index, 66)
      # -----------------------
      elapsed_time = time.time() - start_time
      print 'Rig ' + str(port_index) + ' BSP (Lab) initializaiton finished, took ' + str(elapsed_time) + ' seconds'
    # --------------------------------------------------------------------------------------
  # ------------------------------------------------------------------------------------------


def grid_feeding_enable(port_index, max_current, start_time, end_time):
  # Time used in the protocol is in minutes.
  # Min is 0, i.e., 00:00
  # Max is 1440, i.e., 24:00
  # To read the time more easily, the function takes the hours as input
  # and do the convertion to minutes within the function.
  Vbat_force_feed = 23.6
  start_time_in_min = round(start_time * 60)
  end_time_in_min = round(end_time * 60)
  # transfer relay allowed
  r1128.write_RAM(port_index, 1)
  r1127.write_RAM(port_index, 1)
  r1523.write_RAM(port_index, max_current)
  r1524.write_RAM(port_index, Vbat_force_feed)
  r1525.write_RAM(port_index, start_time_in_min)
  r1526.write_RAM(port_index, end_time_in_min)


def grid_feeding_disable(port_index):
  r1127.write_RAM(port_index, 0)


def battery_charge(port_index, charging_current):
  # transfer relay allowed
  r1128.write_RAM(port_index, 1)
  # disable grid feeding
  grid_feeding_disable(port_index)
  # smart boost disabled
  r1126.write_RAM(port_index, 0)
  # charger allowed
  r1125.write_RAM(port_index, 1)
  # battery charge current
  r1138.write_RAM(port_index, charging_current)
  # floating voltage
  r1140.write_RAM(port_index, 27.6)
  # absorption phase disabled
  r1155.write_RAM(port_index, 0)
  # equalization phase disabled
  r1163.write_RAM(port_index, 0)
  # reduced floating phase disabled
  r1170.write_RAM(port_index, 0)
  # periodic absorption phase disabled
  r1173.write_RAM(port_index, 0)

# Data collection function


def read_data(port_index):
  # start_time = time.time()
  current_datetime = datetime.now()
  battery_SOC = r7002.read(port_index)
  battery_current = r7001.read(port_index)
  battery_voltage = r7000.read(port_index)
  battery_power = r7003.read(port_index)
  AC_out_voltage = r3021.read(port_index)
  AC_out_current = r3022.read(port_index)
  AC_out_power = r3139.read(port_index)
  # elapsed_time = time.time() - start_time
  # print 'Data collection took ' + str(elapsed_time) + ' seconds'
  return current_datetime, battery_SOC, battery_current, battery_voltage, battery_power, AC_out_current, AC_out_voltage, AC_out_power


if __name__ == '__main__':

  # system init
  system_init(1)
  xtender_open(1, Xtender_open)
  rcc_time_sync(1, rcc_init)
  bsp_init(1, bsp_init, battery_setting)
  battery_charge(1, 22)

  conn = sqlite3.connect('StuderOpearion.db')
  c = conn.cursor()
  c.execute("""CREATE TABLE IF NOT EXISTS StuderOperation(
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
  sample_no = 20

  while i < sample_no:
    current_datetime, battery_SOC, battery_current, \
        battery_voltage, battery_power, AC_in_current, \
        AC_in_voltage, AC_in_power = read_data(1)

    with conn:
      c.execute('INSERT INTO StuderOperation Values(?,?,?,?,?,?,?,?)', (current_datetime, battery_SOC,
                                                                        battery_current, battery_voltage, battery_power, AC_in_voltage, AC_in_current, AC_in_power))

    print str(i)
    i += 1
    #time.sleep(1)

  print 'Data collection terminated!'
  conn.close()