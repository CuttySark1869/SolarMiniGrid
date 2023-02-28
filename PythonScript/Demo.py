import Control as ctr
import time

vtk = ctr.vtk_target(ctr.port_name, 1)
bsp = ctr.bsp_target(ctr.port_name, 1)
xtm = ctr.xtm_target(ctr.port_name, 1)

# bsp.calibrate() # calibrate the battery current sensor
vtk.charge_set_current(10)

time.sleep(2)

ctr.port_name = 2


pv_voltage, pv_power = vtk.data_log()
bat_soc,bat_voltage,bat_power = bsp.data_log()

print('PV Voltage = ' + pv_voltage + 'V')
print('PV Power = ' + pv_power + 'kW')

print('Battery SoC = ' + str(bat_soc) + '%')
print('Battery Voltage = ' + bat_voltage + 'V')
print('Battery Power = ' + bat_power + 'kW')

xtm.open()
xtm.grid_feeding_enable(0,23.9)
time.sleep(10)

xtm.transfer_relay_disable()
xtm.charge_set_current(0)
xtm.grid_feeding_set_current(0.5)
xtm.ac_set_voltage_out(200)

time.sleep(10)

xtm.grid_feeding_control(0)
vtk.charge_set_current(0)
xtm.charge_set_current(1)

xtm.close()
