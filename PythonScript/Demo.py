import Control as ctr
import time

vtk = ctr.vtk_target(ctr.port_name, 1)
bsp = ctr.bsp_target(ctr.port_name, 1)
xtm = ctr.xtm_target(ctr.port_name, 1)

vtk.charge_set_current(1)

time.sleep(2)

pv_voltage, pv_power = vtk.data_log()
bat_soc,bat_voltage,bat_power = bsp.data_log()

print('PV Voltage = ' + pv_voltage + 'V')
print('PV Power = ' + pv_power + 'kW')

print('Battery SoC = ' + bat_soc + '%')
print('Battery Voltage = ' + bat_voltage + 'V')
print('Battery Power = ' + bat_power + 'kW')