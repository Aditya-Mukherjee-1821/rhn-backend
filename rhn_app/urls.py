from django.urls import path
from .views import NextHourDataView

urlpatterns = [

    path("next_hour/", NextHourDataView.as_view(), name="next_one_hour_data_view")
]