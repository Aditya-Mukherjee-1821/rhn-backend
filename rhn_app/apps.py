from django.apps import AppConfig
import threading

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

                self.net = pp.create_empty_network(name="Data", fluid="water")
                create_network(self.net)
                self.best_mass_flows = best_mass_flow(self.net)

                initialized = True
                print(f"✅ Pandapipes network initialized ONCE in apps.py, net ID: {id(self.net)}")
