from django.apps import AppConfig
import threading

# Define a global flag to ensure ready() runs only once
initialized = False
lock = threading.Lock()

class RhnAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rhn_app'

    def ready(self):
        global initialized
        if initialized:
            return  # Exit if already initialized

        with lock:  # Thread-safe execution
            if not initialized:  # Double-check inside lock
                from rhn_app.services.network_services.create_network import create_network
                from rhn_app.services.model_limit.best_mass_flow import best_mass_flow
                import pandapipes as pp
                
                self.net = pp.create_empty_network(name="Data", fluid="water")  # Create network
                create_network(self.net)  # Initialize network
                # self.best_mass_flows = best_mass_flow(self.net)

                initialized = True  # Mark as initialized
                print(f"✅ Pandapipes network initialized ONCE in apps.py, net ID: {id(self.net)}")
