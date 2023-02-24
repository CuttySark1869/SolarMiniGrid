"""
  Read control signals from CSV file

  We have three columns as time series:
  (0) date-time (seconds)
  (1) pv charging current (A) 0~5
  (2) diesel charging current (A) 0~5
  (3) ac output voltage (V) 180~240
"""

import pandas as pd
import random

control_log = "ems_log"
time_slots = 60

class secondary_control_signal:
    def __init__(self, control_log):
        self.control_log = control_log

    def create_control_log(self, control_signals):
        """

        :param control_signals: in numpy array data format
        :return: a saved file
        """
        df = pd.DataFrame(control_signals)
        df.to_csv('{0}.csv'.format(self.control_log), index=False)
        # control_signals.tofile('{0}.csv'.format(self.control_log), format='%10.5f')

    def read_control_log(self):
        control_signal = pd.read_csv('{0}.csv'.format(self.control_log))
        # control_signal = np.loadtxt('{0}.csv'.format(self.control_log))

        return control_signal


if __name__ == "__main__":
    singals = {"time_slots": [0] * time_slots,
               "pv_current": [0] * time_slots,
               "ac_in_current": [0] * time_slots,
               "ac_out_voltage": [0] * time_slots,
               }
    for t in range(time_slots):
        singals["time_slots"][t] = t
        singals["pv_current"][t] = random.random() * 5
        singals["ac_in_current"][t] = random.random() * 10 - 5
        singals["ac_out_voltage"][t] = 180 + random.random() * 60

    tester = secondary_control_signal(control_log)
    tester.create_control_log(singals)
    singals = tester.read_control_log()

    print(singals)
