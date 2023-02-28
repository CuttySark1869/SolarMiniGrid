"""
 Main function for the real-time control and optimization
"""
import datetime
import time
import sqlite3
# from apscheduler.schedulers.blocking import BlockingScheduler  # Time scheduler

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
                ac_out_power real,
                pv_power_ems real,
                ac_in_power_ems real,
                pv_power_forecasting real
              )""")

for i in range(5):
    # (2) raw data collection
    current_datetime = datetime.datetime.now()
    bat_soc, bat_voltage, bat_power = bsp.data_log()
    ac_in_voltage, ac_in_power, ac_out_voltage, ac_out_power = xtm.data_log()
    pv_voltage, pv_power = vtk.data_log()

    # (3) SCADA information
    scada_data = {"SOC": float(bat_soc) / 100,
                  "PL_AC": float(ac_out_power),
                  "PL_DC": 0,
                #   "PL_DC": float(pv_power) + float(ac_in_power) - float(ac_out_power) - float(bat_power),
                  "PV_OUTPUT": float(pv_power),
                  "pv_voltage": float(pv_voltage),
                  "ac_in_voltage": float(ac_in_voltage),
                  "bat_voltage": float(bat_voltage),
                  }
    # scada_data["PL_AC"] = scada_data["PL_DC"] + scada_data["PL_AC"]
    # scada_data["PL_DC"] = 0

    print(scada_data)
    # (4) Forecasting information
    forecasting_data = {"pv_power": (i+1)*50,
                        "PL_DC": scada_data["PL_DC"],
                        "PL_AC": scada_data["PL_AC"]}
    # (5) Formulate the energy management problem
    prob = energy_management_system.problem_formulation(scada_data, forecasting_data)
    # (6) Solve the energy management problem
    sol = energy_management_system.solution_method(prob)
    print(sol)
    # (7) Dispatch the real-time control demand
    vtk.charge_set_current(sol["pv_power"] / scada_data["bat_voltage"])  # PV group
    xtm.charge_set_current(sol["ac_in_power"] / scada_data["bat_voltage"])  # AC to DC group
    # For test purpose
    with conn:
        c.execute('INSERT INTO data_log Values(?,?,?,?,?,?,?,?,?,?,?,?,?)', (current_datetime, bat_soc,
                                                                           bat_voltage, bat_power,
                                                                           pv_voltage, pv_power, ac_in_voltage,
                                                                           ac_in_power, ac_out_voltage,
                                                                           ac_out_power, sol["pv_power"],
                                                                           sol["ac_in_power"],forecasting_data["pv_power"]))
    time.sleep(10)

# (8) Close the connection
xtm.close()
# (9) Save the results
db2csv(data_log_name)
conn.close()