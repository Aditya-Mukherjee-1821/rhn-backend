from django.apps import AppConfig
import threading
import os

# Global init lock and flag
initialized = False
lock = threading.Lock()

class RhnAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rhn_app'

    def ready(self):
        # optional memory monitoring
        # from rhn_app.utils.memory_monitor import start_monitor
        # start_monitor()

        global initialized
        if initialized:
            return

        with lock:
            if not initialized:
                from rhn_app.services.network_services.create_network import create_network
                from rhn_app.services.model_limit.best_mass_flow import best_mass_flow
                import pandapipes as pp

                # Check if input.json already there or not. Else load excel and save as input json.
                base_dir = os.path.dirname(os.path.abspath(__file__))  # /.../rhn_app/
                save_dir = os.path.join(base_dir, 'saved_networks')
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, 'input_rhn.json')
                
                self.net = pp.create_empty_network(name="Data", fluid="water")
                if os.path.exists(save_path):
                    #Reuse input.json
                    create_network(self.net,1)
                    print("📂 Loaded existing pandapipes network from JSON.")
                else:
                    # Save the input network as input.json 
                    create_network(self.net,0)
                    print("💾 Created and saved new pandapipes network to JSON.")

                self.best_mass_flows = best_mass_flow(self.net)
                 
                # This is for saving the network
                # self.net = pp.create_empty_network(name="Data", fluid="water")  # Create network
                # create_network(self.net)  # Initialize network
                # #save it here
                # base_dir = os.path.dirname(os.path.abspath(__file__))  # rhn_app/
                # save_dir = os.path.join(base_dir, 'saved_networks')
                # os.makedirs(save_dir, exist_ok=True)
                # save_path = os.path.join(save_dir, 'regional_heating_network.json')
                # pp.to_json(self.net, save_path)
                # self.best_mass_flows = best_mass_flow(self.net)

                #resuse it here 
                # base_dir = os.path.dirname(os.path.abspath(__file__))  # /.../rhn_app/
                # network = os.path.join(base_dir, 'saved_networks', 'regional_heating_network.json')

                # if not os.path.exists(network):
                #     raise FileNotFoundError(f"Network file not found at {network}. Please create and save the network first.")

                # self.net = pp.from_json(network)  # Load the existing network
                # self.best_mass_flows = best_mass_flow(self.net)  # Run downstream logic

                initialized = True
                print(f"✅ Pandapipes network initialized ONCE in apps.py, net ID: {id(self.net)}")
