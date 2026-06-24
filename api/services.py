from django.utils import timezone
from rest_framework import status
from core.models import Vehicle, VehicleInspection

class ServiceError(Exception):
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def create_inspection(vehicle_id, odometer_km):
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)   
    except Vehicle.DoesNotExist:
        raise ServiceError("Vehiculo no encontrado", status.HTTP_404_NOT_FOUND)  
    if not vehicle.active:
        raise ServiceError("Vehiculo inactivo", status.HTTP_400_BAD_REQUEST)
    
    already_inspecting = VehicleInspection.objects.filter(
        vehicle=vehicle,
        status=1,
    ).exists()

    if already_inspecting:
        raise ServiceError(
            "El vehiculo ya tiene una inspeccion en curso", status.HTTP_409_CONFLICT
        )
    return VehicleInspection.objects.create(
        vehicle=vehicle,
        date=timezone.now(),
        odometer=odometer_km,
        status=1
    )

def finalize_inspection(inspection_id):
    try:
        inspection = VehicleInspection.objects.get(id=inspection_id)
    except VehicleInspection.DoesNotExist:
        raise ServiceError("Inspeccion no encontrada", status.HTTP_404_NOT_FOUND)
    
    if inspection.status != 1:
        raise ServiceError(
            "La inspeccion ya fue finalizada", status.HTTP_400_BAD_REQUEST
        )
    inspection.status = 2
    inspection.save(update_fields=["status"])

    return inspection