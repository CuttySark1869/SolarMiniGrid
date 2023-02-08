# -*- coding: utf-8 -*-
"""
Description: the following script is for creating Scom Control class command
Developing Operating System: Windows 7 Enterprise SP1
Developing Environment: Anaconda Python 2.7.13
First created: 04/06/2018
Last modified: 04/06/2018
Author: Minghao Xu
Scom Version: 1.6.26
Xtender Version: 1.6.22
BSP Version: 1.6.14
"""
import subprocess
from datetime import datetime, timedelta
import time
from ScomDF import Register_DF


class ScomCommand():
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

    dir_scom = 'H:\\Profiles_Do_Not_Delete\\campus\\Desktop\\SoLa Kit\\scom.exe '
    parameter_object_property_Id_RAM = 13
    register_df = Register_DF
    display_output = False
    port = ['COM0', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',
            'COM9', 'COM10', 'COM11', 'COM12', 'COM13', 'COM14', 'COM15', 'COM16', 'COM17',
            'COM18', 'COM19', 'COM20']

    @classmethod
    def description(self, register_id):
        register_df = self.register_df[self.register_df.object_id == register_id]
        return register_df.description.item()

    @classmethod
    def write_cmd(self, register_id, port_index, value):
        register_df = self.register_df[self.register_df.object_id == register_id]
        write_cmd = ('--port={} --verbose={} write_property src_addr={} dst_addr={} object_type={} '
                     'object_id={} property_id={} format={} value={}'.
                     format(self.port[port_index], register_df.verbose.item(), register_df.src_addr.item(),
                            register_df.dst_addr.item(), register_df.object_type.item(), register_df.object_id.item(),
                            register_df.property_id.item(), register_df.data_format.item(), value))
        return write_cmd

    @classmethod
    def write_cmd_RAM(self, register_id, port_index, value):
        register_df = self.register_df[self.register_df.object_id == register_id]
        write_cmd_RAM = ('--port={} --verbose={} write_property src_addr={} dst_addr={} object_type={} '
                         'object_id={} property_id={} format={} value={}'.
                         format(self.port[port_index], register_df.verbose.item(), register_df.src_addr.item(),
                                register_df.dst_addr.item(), register_df.object_type.item(), register_df.object_id.item(),
                                self.parameter_object_property_Id_RAM, register_df.data_format.item(), value))
        return write_cmd_RAM

    @classmethod
    def read_cmd(self, register_id, port_index):
        register_df = self.register_df[self.register_df.object_id == register_id]
        read_cmd = ('--port={} --verbose={} read_property src_addr={} dst_addr={} object_type={} '
                    'object_id={} property_id={} format={}'.
                    format(self.port[port_index], register_df.verbose.item(), register_df.src_addr.item(),
                           register_df.dst_addr.item(), register_df.object_type.item(), register_df.object_id.item(),
                           register_df.property_id.item(), register_df.data_format.item()))
        return read_cmd

    @classmethod
    def read(self, register_id, port_index):
        read_cmd = self.read_cmd(register_id, port_index)
        scom_output = subprocess.Popen(self.dir_scom + read_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

    @classmethod
    def write(self, register_id, port_index, value):
        write_cmd = self.write_cmd(register_id, port_index, value)
        scom_output = subprocess.Popen(self.dir_scom + write_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        str_output = scom_output.stdout.readlines()
        if ScomCommand.display_output:
            for line in str_output:
                print line
        if str_output[-5] != 'debug: rx bytes:\r\n':
            print 'Sending Command Failure'

    @classmethod
    def write_RAM(self, register_id, port_index, value):
        write_cmd = self.write_cmd_RAM(register_id, port_index, value)
        scom_output = subprocess.Popen(self.dir_scom + write_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        str_output = scom_output.stdout.readlines()
        if ScomCommand.display_output:
            for line in str_output:
                print line
        if str_output[-5] != 'debug: rx bytes:\r\n':
            print 'Sending Command Failure'

    @classmethod
    def test_comm(self):
        py2output = subprocess.Popen(self.dir_scom + 'test', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in py2output.stdout.readlines():
            print line
        retval = py2output.wait()


# -----------------------------------------------------------------------------------------------------------------------
# Define some functions
sc = ScomCommand


def system_init(port_index):
    # Enable Xtender watchdog and diable saving parameters in flash drive
    # Xtender watchdog
    # 1 for yes; 0 for no
    sc.write(1628, port_index, 0)
    # Xtender watchdog delay in seconds (without response for this period of time, Xtender will restart)
    # r1629.write(port_index,60)
    # --------------
    # whether to save parameters in flash memory (for Xtender parameters)
    # 1 for yes; 0 for no
    # It is disabled in this system to save the lifetime of flash memory in case of repeated writings
    sc.write(1550, port_index, 0)

# Xtender
# -------------


def xtender_open(port_index, Xtender_open):
    if Xtender_open:
        # Xtender on
        sc.write_RAM(1415, port_index, 1)


def xtender_close(port_index, Xtender_close):
    if Xtender_close:
        # Xtender off
        sc.write_RAM(1399, port_index, 0)


# RCC
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
    time_delta_second = sc.read(5002, port_index)
    system_datetime = reference_datetime + timedelta(seconds=time_delta_second)
    return system_datetime


def synchronise_time(port_index):
    current_datetime = datetime.now()
    system_datetime = get_system_time(port_index)
    target_time_delta_second = round((current_datetime - reference_datetime).total_seconds())
    time_delta_second = sc.write_RAM(5002, port_index, target_time_delta_second)
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


# BSP
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
            sc.write_RAM(6057, port_index, 4)
            # ------------------
            # 2. Nomonal capacity (Ah@C20) --- 6001
            sc.write_RAM(6001, port_index, 38)
            # ------------------
            # 3. Nominal discharge duration (C-rating) --- 6002
            sc.write_RAM(6002, port_index, 20)
            # ------------------
            # 4. Nominal shunt current (A) --- 6017
            sc.write_RAM(6017, port_index, 500)
            # ------------------
            # 5. Nominal shunt voltage (mV) --- 6018
            sc.write_RAM(6018, port_index, 50)
            # ------------------
            # 6. Use C20(aka C/20) as reference value (1 for yes, 0 for no) --- 6049
            sc.write_RAM(6049, port_index, 1)
            # ------------------
            # 7. Battery current limitation activation --- 6058
            # boolean format: 1 for yes, 0 for no
            sc.write_RAM(6058, port_index, 1)
            # ------------------
            # 8. Max battery charge current --- 6059
            # For lead acid battery, the charging current should be between 10 and 30 percent of the rated capacity.
            # A 10Ah battery at 30 percent charges at about 3A; the percentage can be lower. An 80Ah starter battery
            # may charge at 8A. (A 10 percent charge rate is equal to 0.1C.)
            # For further information please refer to the link below.
            # http://batteryuniversity.com/learn/article/charging_with_a_power_supply
            # In our system, the capacity at C20 is 38 and 30% of it is 11.4 A. So we
            # set our limitation value to 10A
            sc.write_RAM(6059, port_index, 10)
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
            sc.write_RAM(6057, port_index, 4)
            # -----------------------
            # 2. Nomonal capacity (Ah@C20) --- 6001
            sc.write_RAM(6001, port_index, 220)
            # -----------------------
            # 3. Nominal discharge duration (C-rating) --- 6002
            sc.write_RAM(6002, port_index, 20)
            # -----------------------
            # 4. Nominal shunt current (A) --- 6017
            sc.write_RAM(6017, port_index, 150)
            # -----------------------
            # 5. Nominal shunt voltage (mV) --- 6018
            sc.write_RAM(6018, port_index, 75)
            # -----------------------
            # 6. Use C20(aka C/20) as reference value (1 for yes, 0 for no) --- 6049
            sc.write_RAM(6049, port_index, 1)
            # -----------------------
            # 7. Battery current limitation activation --- 6058
            # boolean format: 1 for yes, 0 for no
            sc.write_RAM(6058, port_index, 1)
            # -----------------------
            # 8. Max battery charge current --- 6059
            # For lead acid battery, the charging current should be between 10 and 30 percent of the rated capacity.
            # A 10Ah battery at 30 percent charges at about 3A; the percentage can be lower. An 80Ah starter battery
            # may charge at 8A. (A 10 percent charge rate is equal to 0.1C.)
            # For further information please refer to the link below.
            # http://batteryuniversity.com/learn/article/charging_with_a_power_supply
            # In our system, the capacity at C20 is 220 and 30% of it is 66 A. So we
            # set our limitation value to 66A
            sc.write_RAM(6059, port_index, 66)
            # -----------------------
            elapsed_time = time.time() - start_time
            print 'Rig ' + str(port_index) + ' BSP (Lab) initializaiton finished, took ' + str(elapsed_time) + ' seconds'
        # --------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------

# Charge and Discharge


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
    sc.write_RAM(1128, port_index, 1)
    sc.write_RAM(1127, port_index, 1)
    sc.write_RAM(1523, port_index, max_current)
    sc.write_RAM(1524, port_index, Vbat_force_feed)
    sc.write_RAM(1525, port_index, start_time_in_min)
    sc.write_RAM(1526, port_index, end_time_in_min)


def grid_feeding_disable(port_index):
    sc.write_RAM(1127, port_index, 0)


def battery_charge(port_index, charging_current):
    # transfer relay allowed
    sc.write_RAM(1128, port_index, 1)
    # disable grid feeding
    grid_feeding_disable(port_index)
    # smart boost disabled
    sc.write_RAM(1126, port_index, 0)
    # charger allowed
    sc.write_RAM(1125, port_index, 1)
    # battery charge current
    sc.write_RAM(1138, port_index, charging_current)
    # floating voltage
    sc.write_RAM(1140, port_index, 27.6)
    # absorption phase disabled
    sc.write_RAM(1155, port_index, 0)
    # equalization phase disabled
    sc.write_RAM(1163, port_index, 0)
    # reduced floating phase disabled
    sc.write_RAM(1170, port_index, 0)
    # periodic absorption phase disabled
    sc.write_RAM(1173, port_index, 0)


def force_equalization(port_index):
    # transfer relay allowed
    sc.write_RAM(1128, port_index, 1)
    # disable grid feeding
    grid_feeding_disable(port_index)
    # charger allowed
    sc.write_RAM(1125, port_index, 1)
    # equalization phase enabled
    sc.write_RAM(1163, port_index, 1)
    # force equalization
    sc.write_RAM(1162, port_index, 1)


def get_fid(port_index):
    try:
            # ID FID MSB
        ID_FID_MSB = hex(sc.read(3156, port_index))[2:]
        # ID FID LSB
        ID_FID_LSB = hex(sc.read(3157, port_index))[2:]
        FID = ID_FID_MSB + ID_FID_LSB
    except:
        FID = 'Port out of range'
    return FID


def unit_port_test(fid_dict):
    port_unit_dict = {}
    for port in range(8):
        if fid_list[0] == get_fid(port):
            port_unit_dict[fid_dict[get_fid(port)]] = port
            print 'Unit 1 is using port ' + str(port)
        if fid_list[1] == get_fid(port):
            port_unit_dict[fid_dict[get_fid(port)]] = port
            print 'Unit 2 is using port ' + str(port)
        if fid_list[2] == get_fid(port):
            port_unit_dict[fid_dict[get_fid(port)]] = port
            print 'Unit 3 is using port ' + str(port)
        if fid_list[3] == get_fid(port):
            port_unit_dict[fid_dict[get_fid(port)]] = port
            # port_unit_dict['port' + str(port)] = fid_dict[get_fid(port)]
            print 'Unit 4 is using port ' + str(port)
    return port_unit_dict


# Data collection function
def read_data(port_index):
    # start_time = time.time()
    current_datetime = datetime.now()
    battery_SOC = sc.read(7002, port_index)
    battery_current = sc.read(7001, port_index)
    battery_voltage = sc.read(7000, port_index)
    battery_power = sc.read(7003, port_index)
    AC_in_current = sc.read(3012, port_index)
    AC_in_voltage = sc.read(3011, port_index)
    AC_in_power = sc.read(3137, port_index)
    # elapsed_time = time.time() - start_time
    # print 'Data collection took ' + str(elapsed_time) + ' seconds'
    return current_datetime, battery_SOC, battery_current, battery_voltage, battery_power, AC_in_current, AC_in_voltage, AC_in_power
