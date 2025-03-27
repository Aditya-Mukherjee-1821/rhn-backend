from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.network_services.data_processor import extract_and_modify_data
from .services.network_services.data_processor_sink_demand_change import process_sink_demand_change
from .services.network_services.calc_pipeflow import calc_pipeflow_from_df
from .services.network_services.data_processor_next_hour import next_hour_prediction

class ProcessDataView(APIView):
    def post(self, request):
        """
        API Endpoint:
        - Accepts an Excel file and modification parameters.
        - Extracts and modifies data.
        - Runs simulation and returns output.
        """
        modifications = request.data  # Read modifications from request body

        try:
            df_heater, df_sink, df_connection, df_nodetype = extract_and_modify_data(modifications)
            response = calc_pipeflow_from_df(df_heater, df_sink, df_connection, df_nodetype)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SinkDemandChangeDataView(APIView):
    def post(self, request):
        modifications = request.data  # Read modifications from request body
        try:
            df_heater, df_sink, df_connection, df_nodetype = process_sink_demand_change(modifications)
            response = calc_pipeflow_from_df(df_heater, df_sink, df_connection, df_nodetype)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class NextHourDataView(APIView):
    def get(self, request):
        try:
            df_heater, df_sink, df_connection, df_nodetype = next_hour_prediction()
            response = calc_pipeflow_from_df(df_heater, df_sink, df_connection, df_nodetype)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
