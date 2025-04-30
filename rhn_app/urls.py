from django.urls import path
from .views import NextHourDataView, TimeDelayView

urlpatterns = [

    path("next_hour/", NextHourDataView.as_view(), name="next_one_hour_data_view"),
    path("time_delay/", TimeDelayView.as_view(), name="time_delay_view")
]