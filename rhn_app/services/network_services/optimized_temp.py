import pandapipes as pp
import json
import pandas as pd
from rhn_app.services.network_services.edit_sinks import edit_sinks_from_df

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
                     lower_limit, 
                     learning_rate=0.3, tolerance=1.0, 
                     max_iters=1000, delta=0.5):
    
    #set demands for current time
    edit_sinks_from_df(net)

    m1_target=req_mass_flow[0]
    m2_target=req_mass_flow[1]
    T1, T2 = lower_limit[0], lower_limit[1]
    history = []

    for i in range(max_iters):
        print(T1,T2,end='\t')
        m1, m2 = calcPipeFlow(net,T1, T2)
        print(m1,m2)
        
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
    return optimized_temp

    # response = json.dumps([{'temp' : mid}])

    # return response