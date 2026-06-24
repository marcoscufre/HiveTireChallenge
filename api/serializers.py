from rest_framework import serializers
from core.models import Vehicle, VehicleInspection


class VehicleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["id", "plate", "active", "brand", "type", "fleet"]

class VehicleDetailSerializer(serializers.ModelSerializer):
    last_inspection = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = ["id", "plate", "active", "brand", "type", "fleet", "last_inspection"]
    
    def get_last_inspection(self, vehicle):
        inspection = (
            VehicleInspection.objects
            .filter(vehicle=vehicle)
            .order_by("-date", "-id")
            .first()
        )
        if inspection is None:
            return None
        return LastInspectionSerializer(inspection).data

class InspectionListSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.IntegerField(source="vehicle.id", read_only=True)
    vehicle_plate = serializers.CharField(source="vehicle.plate",
    read_only=True)

    class Meta:
        model = VehicleInspection
        fields = ["id", "status", "date", "odometer", "vehicle_id", "vehicle_plate"]

class LastInspectionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    odometer_km = serializers.FloatField(source="odometer")

    class Meta:
        model = VehicleInspection
        fields = ["status", "date", "odometer_km"]

class CreateInspectionSerializer(serializers.Serializer):
    """No usa ModelSerializer porque la creacion tiene logica aparte"""

    vehicle_id = serializers.IntegerField()
    odometer_km = serializers.FloatField(min_value=0)