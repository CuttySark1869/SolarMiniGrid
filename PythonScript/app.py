"""
 Main function for the real-time control and optimization
"""
import time

from apscheduler.schedulers.blocking import BlockingScheduler  # Time scheduler

import Control as ctr

from energy_management_systems import EnergyManagement

from configuration import port_name, PPV_MAX, data_log_name
from db2csv import db2csv

from random import random

energy_management_system = EnergyManagement()

# For each time step.
# (1) update the scada information
vtk = ctr.vtk_target(port_name, 1)  # PV group
bsp = ctr.bsp_target(port_name, 1)  # Battery group
xtm = ctr.xtm_target(port_name, 1)  # BIC group
xtm.open()  # The automatic control of BIC control

for i in range(10):
    # (2) raw data collection
    bat_soc, bat_voltage, bat_power = bsp.data_log()
    ac_in_voltage, ac_in_power, ac_out_voltage, ac_out_power = xtm.data_log()
    pv_voltage, pv_power = vtk.data_log()

    # (3) SCADA information
    scada_data = {"battery_soc": bat_soc,
                  "PL_AC": ac_out_power,
                  "PL_DC": pv_power + ac_in_power - ac_out_power - bat_power,
                  "PV_OUTPUT": pv_power,
                  "pv_voltage": pv_voltage,
                  "ac_in_voltage": ac_in_voltage,
                  }
    # (4) Forecasting information
    forecasting_data = {"pv_power": PPV_MAX * random()}
    # (5) Formulate the energy management problem
    prob = energy_management_system.problem_formulation(scada_data, forecasting_data)
    # (6) Solve the energy management problem
    sol = energy_management_system.solution_method(prob)
    # (7) Dispatch the real-time control demand
    vtk.charge_set_current(sol["pv_power"] / scada_data["pv_voltage"])  # PV group
    xtm.charge_set_current(sol["ac_in_power"] / scada_data["ac_in_voltage"])  # AC to DC group
    # For test purpose
    time.sleep(10)

# (8) Close the connection
xtm.close()
# (9) Save the results
db2csv(data_log_name)
