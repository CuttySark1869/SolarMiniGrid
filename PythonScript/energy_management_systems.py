"""
  Energy management systems for the mini grid
  1) Forecasting
  2) Energy management problem formulation, for the real-time optimal power flow
  3) Optimization problem solution
"""

import pandas as pd
from numpy import zeros, ones, vstack
from scipy.optimize import linprog

from configuration import data_log_name

from configuration import PG_UG, PL_AC, PL_DC, PAC2DC, PDC2AC, PG_PV, PB_DC, PB_CH, \
    ESS_SOC, SOC_MIN, SOC_MAX, PUG_MAX, PBIC_MAX, ECAP, PPV_MAX, PB_MAX, eff_dc, eff_ch, eff_a2d, eff_d2a

from configuration import LCOE_Battery, GEN_cost, VOLL 
class EnergyManagement():

    def __int__(self, data_log_name):
        """
        Initial the energy management class with parameter
        :param data_log_name:
        :return:
        """
        self.data_scada = data_log_name

    def statue_update(self):
        scada_data = pd.read_csv('{0}.csv'.format(self.data_scada))
        # Currently, we need the following information
        # (1) SOC
        # (2) AC load
        # (3) DC load
        # (4) pv output
        status = {"SOC": scada_data["battery_soc"].values[-1] / 100,
                  "PL_AC": scada_data["ac_out_power"].values[-1],
                  "PL_DC": scada_data["pv_power"].values[-1] +
                           scada_data["ac_in_power"].values[-1] -
                           scada_data["ac_out_power"].values[-1] -
                           scada_data["battery_power"].values[-1],
                  "PV_OUTPUT": scada_data["pv_power"].values[-1],
                  }

        return status

    def problem_formulation(self, scada, forecasting_data):
        """
        Minimize the pv output shedding
        :return:
        """
        nx = ESS_SOC + 1  # number of decision variables
        lb = zeros((nx, 1))
        ub = zeros((nx, 1))
        cobj = zeros((nx, 1))
        # Utility grid part
        lb[PG_UG] = 0
        ub[PG_UG] = PUG_MAX
        cobj[PG_UG] = 10
        # AC load shedding
        lb[PL_AC] = 0
        ub[PL_AC] = forecasting_data["PL_AC"]
        cobj[PL_AC] = 1e4
        # AC to DC conversion part
        lb[PAC2DC] = 0
        ub[PAC2DC] = PBIC_MAX
        cobj[PAC2DC] = 0
        # DC to AC conversion part
        lb[PDC2AC] = 0
        ub[PDC2AC] = PBIC_MAX
        cobj[PDC2AC] = 0
        # DC load shedding
        lb[PL_DC] = 0
        ub[PL_DC] = forecasting_data["PL_DC"]
        cobj[PL_DC] = 1e4
        # PV output part
        lb[PG_PV] = 0
        ub[PG_PV] = forecasting_data["pv_power"]
        cobj[PG_PV] = 0
        # Battery part
        lb[PB_DC] = 0
        ub[PB_DC] = PB_MAX
        cobj[PB_DC] = 1e-1

        lb[PB_CH] = 0
        ub[PB_CH] = PB_MAX
        cobj[PB_CH] = 1e-1

        lb[ESS_SOC] = SOC_MIN
        ub[ESS_SOC] = SOC_MAX
        cobj[ESS_SOC] = 0
        # Formulate the power balance constraint (AC bus)
        Aeq = zeros((1, nx))
        beq = ones((1, 1)) * forecasting_data["PL_AC"]
        Aeq[0, PG_UG] = 1
        Aeq[0, PL_AC] = 1
        Aeq[0, PAC2DC] = -1
        Aeq[0, PDC2AC] = eff_d2a
        # Formulate the power balance constraint (DC bus)
        Aeq_temp = zeros((1, nx))
        beq_temp = ones((1, 1)) * forecasting_data["PL_DC"]
        Aeq_temp[0, PAC2DC] = eff_a2d
        Aeq_temp[0, PDC2AC] = -1
        Aeq_temp[0, PB_CH] = -1
        Aeq_temp[0, PB_DC] = 1
        Aeq_temp[0, PG_PV] = 1
        Aeq_temp[0, PL_DC] = 1
        Aeq = vstack([Aeq, Aeq_temp])
        beq = vstack([beq, beq_temp])
        # Limit the energy status
        Aeq_temp = zeros((1, nx))
        if scada["SOC"] > SOC_MAX:
            beq_temp = SOC_MAX
        elif scada["SOC"] < SOC_MIN:
            beq_temp = SOC_MIN
        else:
            beq_temp = scada["SOC"]

        Aeq_temp[0, ESS_SOC] = 1
        Aeq_temp[0, PB_DC] = 1 / eff_dc / ECAP
        Aeq_temp[0, PB_CH] = -eff_ch / ECAP
        Aeq = vstack([Aeq, Aeq_temp])
        beq = vstack([beq, beq_temp])

        prob = {"c": cobj,
                "Aeq": Aeq,
                "beq": beq,
                "lb": lb,
                "ub": ub}
        return prob

    def solution_method(self, prob):
        nx = ESS_SOC + 1  # number of decision variables
        bounds = [(0, 0)] * nx
        for i in range(nx):
            bounds[i] = (prob["lb"][i].tolist()[0], prob["ub"][i].tolist()[0])
        res = linprog(prob["c"], A_eq=prob["Aeq"], b_eq=prob["beq"], bounds=bounds)
        x = res.x
        obj = res.fun
        sol = {"PG_UG": x[PG_UG],
               "PL_AC": x[PL_AC],
               "PL_DC": x[PL_DC],
               "ac_in_power": x[PDC2AC] - x[PAC2DC],
               "PDC2AC": x[PDC2AC],
               "pv_power": x[PG_PV],
               "PB_DC": x[PB_DC],
               "PB_CH": x[PB_CH],
               "ESS_SOC": x[ESS_SOC],
               "cost": obj,
               }
        return sol


if __name__ == '__main__':
    energy_management_system = EnergyManagement()
    energy_management_system.__int__(data_log_name)
    data = energy_management_system.statue_update()
    forecasting_data = {"PL_AC": 0,
                        "PL_DC": 300,
                        "PG_PV": 200, }
    prob = energy_management_system.problem_formulation(data, forecasting_data)
    sol = energy_management_system.solution_method(prob)
    print(sol)
