# Ambient temperature [K] = t[C] + 273.15
temp_ext_c = 20
temp_ext_k = temp_ext_c + 273.15

# Initial network fluid temperature (flow side) [K] = t[C] + 273.15
t_net_flow_init_c = 85
t_net_flow_init_k = t_net_flow_init_c + 273.15

# Initial network fluid temperature (return side) [K] = t[C] + 273.15
t_net_return_init_c = 35
t_net_return_init_k = t_net_return_init_c + 273.15

# Initial junction and network pressure, flow side [bar]
net_flow_p_bar = 10

# Initial junction and network pressure, return side [bar]
net_return_p_bar = 8

# Pressure at flow side of producers [bar]
source_flow_bar = 10

# Pressure lift induced by sources [bar] - Used to model pressure difference
# at pump nodes between input and output
pressure_lift = 3

# Production multiplier - general multiplier for testing effects of increasing/
# reducing heated water production. Multiplier applies to mdot_flow_kg_per_s
prod_multiplier = 1

# Desired return water temperature [K] = t[C] + 273.15
# Use t_return_c = t_net_return_init_c to set to initial network temp
t_return_c = t_net_return_init_c + 5
t_return_k = t_return_c + 273.15

# Output water temperature [K] = t[C] + 273.15
t_out_c = 90
t_out_k = t_out_c + 273.15

total_mdot_kg_per_s=193.022376298

upper_limit_temp = 95

e_flow_conv_ratio = (7 / 0.033 + 40.3 / 0.193) / 2  # = 210.4648


