import pandapipes as pp
import json
import pandas as pd
import os
from rhn_app.services.network_services.edit_sinks import edit_sinks_from_df
from rhn_app.services.model_limit.lower_limit import returnLowerLimit
# def optimized_temp(best_mass_flows, net):

def calcPipeFlow(net,T1,T2):
    net.circ_pump_pressure.at[0,'t_flow_k']=T1
    net.circ_pump_pressure.at[1,'t_flow_k']=T2
    for i in range(len(net.junction)):
        if net.junction.at[i,'name'].endswith('_supply'):
            net.junction.at[i,'tfluid_k']=min(T1,T2)-5
    net.junction.loc[net.junction['name']=='Sarfvik_supply','tfluid_k']=T1
    net.junction.loc[net.junction['name']=='Kirkkonummi_supply','tfluid_k']=T2
    
    pp.pipeflow(net,mode='sequential')
    
    for i in range(len(net.res_junction)):
        net.junction.at[i,'tfluid_k']=float(str(net.res_junction.at[i,'t_k']))
        net.junction.at[i,'pn_bar']=float(str(net.res_junction.at[i,'p_bar']))
    net.junction
    pp.pipeflow(net,mode='sequential')
    
    return [net.res_circ_pump_pressure.at[0,'mdot_flow_kg_per_s'],net.res_circ_pump_pressure.at[1,'mdot_flow_kg_per_s']]

def gradDescOptimizer(net,
                     req_mass_flow, 
                     learning_rate=0.3, tolerance=2.0, 
                     max_iters=1000, delta=0.5):
    
    # lower_limit = returnLowerLimit()
    #set demands for current time
    edit_sinks_from_df(net)

    m1_target=req_mass_flow[0]
    m2_target=req_mass_flow[1]
    T1, T2 = 350,350#lower_limit+273, lower_limit+273
    history = []

    for i in range(max_iters):
        print('Temp:\t',T1,T2,end='\t')
        m1, m2 = calcPipeFlow(net,T1, T2)
        print('Mass\t',m1,m2)
        
        # Compute error
        err1 = m1 - m1_target
        err2 = m2 - m2_target
        error = err1**2 + err2**2

        history.append((T1, T2, m1, m2, error))

        if abs(err1) <= tolerance and abs(err2) <= tolerance:
            print(f"Converged in {i+1} iterations.")
            break

        # Numerical gradient w.r.t T1
        if abs(err1)>tolerance:
            m1_T1_plus, m2_T1_plus = calcPipeFlow(net,T1 + delta, T2)
            grad_T1 = ((m1_T1_plus - m1) * err1 + (m2_T1_plus - m2) * err2) / delta
        else:
            grad_T1=1.2
        # Numerical gradient w.r.t T2
        if abs(err2)>tolerance:
            m1_T2_plus, m2_T2_plus = calcPipeFlow(net,T1, T2 + delta)
            grad_T2 = ((m1_T2_plus - m1) * err1 + (m2_T2_plus - m2) * err2) / delta
        else:
            grad_T2=1.2
        # Update temperatures
        T1 -= learning_rate * grad_T1
        T2 -= learning_rate * grad_T2
    
    optimized_temp={'Sarfvik':T1,'Kirkkonummi':T2}
    content = []
    for key, value in optimized_temp.items():
        content.append({key: value})
    
    junctions = {
        net.junction.at[_, 'name']: {
            "type": net.junction.at[_,"type"],
            "x": float(str(net.junction_geodata.at[_, 'x'])),
            "y": float(str(net.junction_geodata.at[_, 'y'])),
            "t": float(str(net.res_junction.at[_, 't_k']))-273.15
        }
        for _, row in net.res_junction.iterrows()
    }

    # Get current file directory → rhn_app/services/network_services
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rhn_app_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
    save_dir = os.path.join(rhn_app_dir, 'saved_networks')
    os.makedirs(save_dir, exist_ok=True)

    # Final JSON file path
    json_path = os.path.join(save_dir, 'junctions.json')

    # Save to JSON
    with open(json_path, 'w') as f:
        json.dump(junctions, f, indent=4)

    print(f"✅ Saved junctions data to {json_path}")
    
    pipes = {
    net.pipe.at[_, 'name']: {
            "from": str(net.junction.at[int(net.pipe.at[_,"from_junction"]), 'name']),
            "to": str(net.junction.at[int(net.pipe.at[_,"to_junction"]), 'name']),
            "massflow": abs(float(str(net.res_pipe.at[_, 'mdot_from_kg_per_s'])))
        }
        for _, row in net.res_pipe.iterrows()
    }

    
    json_path = os.path.join(save_dir, 'pipes.json')

    # Save to JSON
    with open(json_path, 'w') as f:
        json.dump(pipes, f, indent=4)

    print(f"✅ Saved pipes data to {json_path}")
    
    response = json.dumps(content)
    return response