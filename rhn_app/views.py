import os
import json
import pandapipes as pp
from django.apps import apps
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from .services.network_services.create_network import create_network
from .services.network_services.temp_to_supply import calc_pipeflow_from_df
from .services.network_services.time_delay import time_delay
from .services.network_services.optimized_temp import gradDescOptimizer
from .services.model_limit.best_mass_flow import best_mass_flow

class NextHourDataView(APIView):
    def get(self, request):
        try:
            # Get the network from the app config
            best_mass_flows = apps.get_app_config('rhn_app').best_mass_flows
            print(f"📌 Accessing net in views.py, net ID: {id(apps.get_app_config('rhn_app').net)}")  # Print ID

            # response = calc_pipeflow_from_df(net)
            response = gradDescOptimizer(apps.get_app_config('rhn_app').net,best_mass_flows)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            print({"error": str(e)})
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TimeDelayView(APIView):
    def get(self, request):
        try:
            # Get the network from the app config
            print(f"📌 Accessing net in views.py, net ID: {id(apps.get_app_config('rhn_app').net)}")  # Print ID

            response = time_delay(apps.get_app_config('rhn_app').net)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GraphView(APIView):
    def get(self, request):
        try:
            # Build correct path to saved_networks inside rhn_app
            json_dir = os.path.join(settings.BASE_DIR, 'rhn_app', 'saved_networks')

            junction_path = os.path.join(json_dir, 'junctions.json')
            pipes_path = os.path.join(json_dir, 'pipes.json')

            # Load the JSON files
            with open(junction_path, 'r') as junc_file:
                junctions = json.load(junc_file)

            with open(pipes_path, 'r') as pipes_file:
                pipes = json.load(pipes_file)

            # Combine them into a list of lists
            response = [junctions, pipes]

            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UploadView(APIView):
    def post(self, request):
        try:
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

            # Get absolute path to rhn_app/services/data/Data.xlsx
            current_dir = os.path.dirname(os.path.abspath(__file__))  # .../rhn_app/views/
            data_dir = os.path.normpath(os.path.join(current_dir, "services", "data"))
            os.makedirs(data_dir, exist_ok=True)
            file_path = os.path.join(data_dir, "Data.xlsx")

            # Save the uploaded file
            with open(file_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            print(f"📥 Excel file successfully saved to: {file_path}")

            print(f"📌 Accessing net in Edit API, net ID: {id(apps.get_app_config('rhn_app').net)}")
            apps.get_app_config('rhn_app').net = pp.create_empty_network(name="Data", fluid="water")
            create_network(apps.get_app_config('rhn_app').net, 0)
            apps.get_app_config('rhn_app').best_mass_flows = best_mass_flow(apps.get_app_config('rhn_app').net)
            print("📂 Loaded existing pandapipes network from JSON after updating.")

            response = {"message": True}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)