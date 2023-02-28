import Control as ctr
import time

vtk = ctr.vtk_target('COM5', 1)
bsp = ctr.bsp_target('COM5', 1)
xtm = ctr.xtm_target('COM5', 1)

vtk.charge_set_current(10)
time.sleep(2)
pv_voltage, pv_power = vtk.data_log()
bat_soc,bat_voltage,bat_power = bsp.data_log()
print('PV Voltage = ' + pv_voltage + 'V')
print('PV Power = ' + pv_power + 'W')
print('Battery SoC = ' + str(bat_soc) + '%')
print('Battery Voltage = ' + bat_voltage + 'V')
print('Battery Power = ' + bat_power + 'W')

xtm.open()
xtm.charge_set_current(10)
time.sleep(10)
ac_in_voltage, ac_in_power, ac_out_voltage, ac_out_power = xtm.data_log()
print('ac_in_power = ' + ac_in_power + 'W')
print('ac_out_power = ' + ac_out_power + 'W')

xtm.charge_set_current(-10)
time.sleep(10)
ac_in_voltage, ac_in_power, ac_out_voltage, ac_out_power = xtm.data_log()
print('ac_in_power = ' + ac_in_power + 'W')
print('ac_out_power = ' + ac_out_power + 'W')
print('ac_in_voltage = ' + ac_in_voltage + 'V')
print('ac_out_voltage = ' + ac_out_voltage + 'V')

# xtm.ac_set_voltage_out(100)
# time.sleep(10)
# ac_in_voltage, ac_in_power, ac_out_voltage, ac_out_power = xtm.data_log()
# print('ac_in_power = ' + ac_in_power + 'W')
# print('ac_out_power = ' + ac_out_power + 'W')


xtm.close()
