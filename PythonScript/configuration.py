"""
  Configuration file for solar minigrid
"""

# 1: generator connected mode; 2: islanded mode
ctrl_mode = 1
port_name = 'COM5'  # the port name can be find in device manager
ems_signal_name = 'ems_log'
data_log_name = 'data_log'
verbose = 3
src_addr = 1
rcc_addr = 500  # Xcom-232i = RCC
bsp_addr = 600
xtm_addr = 100
vtk_addr = 300
sampling_time = 5  # in seconds
total_steps = 5  # total time = total_steps * sampling_time

# info object type and property id (read-only)
user_info_object_object_type = 1
user_info_object_property_id = 1
# parameter object type and property id (read-write)
parameter_object_object_type = 2
parameter_object_flash_property_id = 5  # stored in flash
parameter_object_ram_property_id = 13  # stored in ram

# energy management related parameter
PG_UG = 0  # Utility grid output
PL_AC = 1  # AC load shedding
PAC2DC = 2  # AC to DC conversion
PDC2AC = 3  # DC to AC conversion
PL_DC = 4  # DC load shedding
PG_PV = 5  # PV output
PB_DC = 6  # Battery discharging rate
PB_CH = 7  # Battery discharging rate
ESS_SOC = 8  # Energy status of the battery


## Technical limitations
ECAP = 38 * 24
SOC_MAX = 0.8
SOC_MIN = 0.2
PUG_MAX = 1000
PBIC_MAX = 1000
PDCDC_MAX = 1000
PPV_MAX = 1000
PB_MAX = 500

## Efficiency group
eff_dc = 0.95
eff_ch = 0.95
eff_a2d = 0.95
eff_d2a = 0.95

## Cost group
VOLL = 1e4 # The load shedding cost
GEN_cost = 1e1
LCOE_Battery = 1e-1