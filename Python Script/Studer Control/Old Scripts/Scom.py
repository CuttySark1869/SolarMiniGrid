# -*- coding: utf-8 -*-
"""
Description: the following script is for creating Scom Control class
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
dir_scom = 'H:\\Profiles_Do_Not_Delete\\campus\\Desktop\\SoLa Kit\\scom.exe '


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
