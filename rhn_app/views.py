from django.apps import apps
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .services.network_services.read_data import read_data
from .services.network_services.temp_to_supply import calc_pipeflow_from_df
from .services.network_services.time_delay import time_delay
from .services.network_services.optimized_temp import gradDescOptimizer

class NextHourDataView(APIView):
    def get(self, request):
        try:
            # Get the network from the app config
            net = apps.get_app_config('rhn_app').net
            best_mass_flows = apps.get_app_config('rhn_app').best_mass_flows
            print(f"📌 Accessing net in views.py, net ID: {id(net)}")  # Print ID

            # response = calc_pipeflow_from_df(net)
            response = gradDescOptimizer(net,best_mass_flows)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TimeDelayView(APIView):
    def get(self, request):
        try:
            # Get the network from the app config
            net = apps.get_app_config('rhn_app').net
            print(f"📌 Accessing net in views.py, net ID: {id(net)}")  # Print ID

            response = time_delay(net)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)