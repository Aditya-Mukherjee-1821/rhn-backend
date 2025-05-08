import pandapipes as pp
import json
import pandas as pd
import os
import numpy as np
from rhn_app.services.network_services.edit_sinks import edit_sinks_from_df
from rhn_app.services.model_limit.lower_limit import returnLowerLimit


def calcPipeFlow(net, *T):
    n = len(T)

    # Set pump flow temperatures
    for i in range(n):
        net.circ_pump_pressure.at[i, 't_flow_k'] = T[i]

    # Set default temperature for all supply junctions
    min_temp = min(T) - 5
    net.junction.loc[net.junction['name'].str.endswith('_supply'), 'tfluid_k'] = min_temp

    # Assign each pump's temperature to its respective junction
    supply_junctions = net.junction[net.junction['name'].str.endswith('_supply')].reset_index()
    for i in range(min(n, len(supply_junctions))):
        idx = supply_junctions.at[i, 'index']
        net.junction.at[idx, 'tfluid_k'] = T[i]

    # First simulation
    pp.pipeflow(net, mode='sequential')

    # Update junction temps and pressures from results
    for i in range(len(net.res_junction)):
        net.junction.at[i, 'tfluid_k'] = float(net.res_junction.at[i, 't_k'])
        net.junction.at[i, 'pn_bar'] = float(net.res_junction.at[i, 'p_bar'])

    # Second simulation
    pp.pipeflow(net, mode='sequential')

    # Return mass flows for each pump
    return [net.res_circ_pump_pressure.at[i, 'mdot_flow_kg_per_s'] for i in range(n)]


def gradDescOptimizer(net,
                      req_mass_flow,
                      learning_rate=0.3, tolerance=2.0,
                      max_iters=1000, delta=0.5):

    edit_sinks_from_df(net)

    n = len(req_mass_flow)
    T = np.full(n, 350.0)
    history = []

    for i in range(max_iters):
        print(f"Iteration {i+1}")
        print("Temps:\t", T)

        m = np.array(calcPipeFlow(net, *T))
        print("Mass:\t", m)

        err = m - req_mass_flow
        error = np.sum(err ** 2)
        history.append((T.copy(), m.copy(), error))

        if np.all(np.abs(err) <= tolerance):
            print(f"✅ Converged in {i+1} iterations.")
            break

        grads = np.zeros(n)
        for j in range(n):
            T_perturbed = T.copy()
            T_perturbed[j] += delta
            m_perturbed = np.array(calcPipeFlow(net, *T_perturbed))
            grads[j] = np.sum((m_perturbed - m) * err) / delta

        T -= learning_rate * grads

    # Map temperatures to supply junction names
    supply_junctions = net.junction[net.junction['name'].str.endswith('_supply')].reset_index()
    optimized_temp = {
        supply_junctions.at[i, 'name']: float(T[i]) for i in range(min(n, len(supply_junctions)))
    }

    content = [{key: val} for key, val in optimized_temp.items()]

    # Save junctions data
    junctions = {
        net.junction.at[i, 'name']: {
            "type": net.junction.at[i, "type"],
            "x": float(net.junction_geodata.at[i, 'x']),
            "y": float(net.junction_geodata.at[i, 'y']),
            "t": float(net.res_junction.at[i, 't_k']) - 273.15
        }
        for i in range(len(net.res_junction))
    }

    current_dir = os.path.dirname(os.path.abspath(__file__))
    rhn_app_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
    save_dir = os.path.join(rhn_app_dir, 'saved_networks')
    os.makedirs(save_dir, exist_ok=True)

    with open(os.path.join(save_dir, 'junctions.json'), 'w') as f:
        json.dump(junctions, f, indent=4)
    print("✅ Saved junctions data")

    # Save pipes data
    pipes = {
        net.pipe.at[i, 'name']: {
            "from": str(net.junction.at[int(net.pipe.at[i, "from_junction"]), 'name']),
            "to": str(net.junction.at[int(net.pipe.at[i, "to_junction"]), 'name']),
            "massflow": abs(float(net.res_pipe.at[i, 'mdot_from_kg_per_s']))
        }
        for i in range(len(net.res_pipe))
    }

    with open(os.path.join(save_dir, 'pipes.json'), 'w') as f:
        json.dump(pipes, f, indent=4)
    print("✅ Saved pipes data")

    return json.dumps(content)