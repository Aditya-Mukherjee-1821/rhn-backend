from django.urls import path
from .views import ProcessDataView, SinkDemandChangeDataView, NextHourDataView

urlpatterns = [
    path("process/", ProcessDataView.as_view(), name="process_data_view"),
    path("sink_demand_change/", SinkDemandChangeDataView.as_view(), name = "sink_demand_change_data_view"),
    path("next_hour/", NextHourDataView.as_view(), name="next_one_hour_data_view")
]