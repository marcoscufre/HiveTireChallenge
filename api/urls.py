from django.urls import path

from api.views import (
    InspectionFinalizeView,
    InspectionListCreateView,
    VehicleDetailView,
    VehicleListView,
)

urlpatterns = [
    path("vehicles/", VehicleListView.as_view(), name="vehicle-list"),
    path("vehicles/<int:pk>/", VehicleDetailView.as_view(), name="vehicle-detail"),
    path("inspections/", InspectionListCreateView.as_view(), name="inspection-list-create"),
    path("inspections/<int:pk>/finalize/", InspectionFinalizeView.as_view(), name="inspection-finalize"),
]