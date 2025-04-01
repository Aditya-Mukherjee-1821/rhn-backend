from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.apps import apps
from .services.network_services.calc_pipeflow import calc_pipeflow_from_df_old
from .services.network_services.temp_to_supply import calc_pipeflow_from_df
from .services.network_services.read_data import read_data

class NextHourDataView(APIView):
    def get(self, request):
        try:
            # Get the network from the app config
            net = apps.get_app_config('rhn_app').net
            print(f"📌 Accessing net in views.py, net ID: {id(net)}")  # Print ID

            response = calc_pipeflow_from_df(net)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
