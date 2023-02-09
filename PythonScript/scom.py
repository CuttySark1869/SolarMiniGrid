# -*- coding: utf-8 -*-
import subprocess
import serial



class ScomTarget:
 
  def __init__(self, port, verbose, display, src_addr, dst_addr, object_type, property_id):
    self.port = port
    self.verbose = verbose
    self.src_addr = src_addr
    self.dst_addr = dst_addr
    self.object_type = object_type
    self.property_id = property_id
    self.display = display
    self.dir_scom = 'scom.exe '

  @property
  def description(self):
    return self.description

  @description.setter
  def description(self, description):
    self.description = description

  def write_cmd(self, object_id, value, data_format):
    write_cmd = ('--port={} --verbose={} write_property src_addr={} dst_addr={} object_type={} '
                 'object_id={} property_id={} format={} value={}'.
                 format(self.port, self.verbose, self.src_addr, self.dst_addr, self.object_type, object_id, self.property_id, data_format, value))
    return write_cmd

  def write(self, object_id, value, data_format):
    write_cmd = self.write_cmd(object_id, value, data_format)
    scom_output = subprocess.Popen(self.dir_scom + write_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if self.display:
      str_output = scom_output.stdout.readlines()
      for line in str_output:
        print(line)

  def read_cmd(self, object_id, data_format):
    read_cmd = ('--port={} --verbose={} read_property src_addr={} dst_addr={} object_type={} '
                'object_id={} property_id={} format={}'.
                format(self.port, self.verbose, self.src_addr, self.dst_addr, self.object_type, object_id, self.property_id, data_format))
    return read_cmd

  def read(self, object_id, data_format):
    read_cmd = self.read_cmd(object_id, data_format)
    scom_output = subprocess.Popen(self.dir_scom + read_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if self.display:
      str_output = scom_output.stdout.readlines()
      for line in str_output:
        print(line)

  @classmethod
  def test_scom():
    py2output = subprocess.Popen(ScomTarget.dir_scom + 'test', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in py2output.stdout.readlines():
      print(line)
    retval = py2output.wait()
    return(retval)

  def check_port():
    py2output = subprocess.Popen(['mode'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in py2output.stdout.readlines():
      print(line)
    retval = py2output.wait()
    return(retval)

  def open_port(port_name):
    ser = serial.Serial(port_name, baudrate=38400)
    print(ser.name)         