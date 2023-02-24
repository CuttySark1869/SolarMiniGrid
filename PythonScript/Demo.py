import Control as ctr
import time

vtk = ctr.vtk_target(ctr.port_name, 1)

vtk.charge_set_current(4)

time.sleep(2)

pv_voltage, pv_power = vtk.data_log()

print('PV Voltage = ' + pv_voltage + 'V')
print('PV Power = ' + pv_power + 'kW')
