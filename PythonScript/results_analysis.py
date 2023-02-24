"""
    Analyze the ems results
"""
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

real_time_information = pd.read_csv('data_log.csv')
n_samples = len(real_time_information.DateTime)

plt.plot(np.arange(0, n_samples), real_time_information.battery_soc)
plt.show()

plt.plot(np.arange(0, n_samples), real_time_information.pv_power)
plt.plot(np.arange(0, n_samples), real_time_information.ac_in_power)
plt.plot(np.arange(0, n_samples), real_time_information.ac_out_power)
plt.show()


plt.plot(np.arange(0, n_samples), real_time_information.ac_out_voltage)
plt.show()