from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from core.models import Vehicle, VehicleInspection

class InspectionCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.vehicle = Vehicle.objects.create(
            active=True,
            plate="ABC-123",
            brand="Toyota",
            type="Camion",
            fleet="Norte",
        )

    def test_cannot_create_inspection_when_vehicle_has_open_inspection(self):
        VehicleInspection.objects.create(
            vehicle=self.vehicle,
            date="2024-06-01T10:30:00Z",
            odometer=1000,
            status=1,
        )

        response = self.client.post(
            reverse("inspection-list-create"),
            {
                "vehicle_id": self.vehicle.id,
                "odometer_km": 1200,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(VehicleInspection.objects.count(), 1)