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

    def test_create_and_finalize_inspection(self):
        create_response = self.client.post(
            reverse("inspection-list-create"),
            {
                "vehicle_id": self.vehicle.id,
                "odometer_km": 1200,
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.data["status"], 1)
        self.assertEqual(create_response.data["vehicle_id"], self.vehicle.id)

        inspection_id = create_response.data["id"]

        finalize_response = self.client.patch(
            reverse("inspection-finalize", kwargs={"pk": inspection_id}),
            format="json",
        )

        self.assertEqual(finalize_response.status_code, 200)
        self.assertEqual(finalize_response.data["status"], 2)

        inspection = VehicleInspection.objects.get(id=inspection_id)
        self.assertEqual(inspection.status, 2)

    def test_cannot_create_inspection_for_inactive_vehicle(self):
        self.vehicle.active = False
        self.vehicle.save(update_fields=["active"])

        response = self.client.post(
            reverse("inspection-list-create"),
            {
                "vehicle_id": self.vehicle.id,
                "odometer_km": 1200,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(VehicleInspection.objects.count(), 0)
