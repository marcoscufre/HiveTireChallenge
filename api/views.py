from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Vehicle, VehicleInspection
from api.serializers import (
    CreateInspectionSerializer,
    InspectionListSerializer,
    VehicleDetailSerializer,
    VehicleListSerializer,
)
from api.services import create_inspection, finalize_inspection, ServiceError


class StandardResultsSetPagination(PageNumberPagination):
    """paginacion estandar para todas las vistas"""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class VehicleListView(generics.ListAPIView):
    serializer_class = VehicleListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Vehicle.objects.all()

        active = self.request.query_params.get("active")
        brand = self.request.query_params.get("brand")
        vehicle_type = self.request.query_params.get("type")
        fleet = self.request.query_params.get("fleet")
        search = self.request.query_params.get("search")
        ordering = self.request.query_params.get("ordering", "id")

        if active is not None:
            queryset = queryset.filter(active=active.lower() == "true")
        
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        if vehicle_type:
            queryset = queryset.filter(type__icontains=vehicle_type)

        if fleet:
            queryset = queryset.filter(fleet__icontains=fleet)

        if search:
            queryset = queryset.filter(plate__icontains=search)

        allowed_ordering = {
            "id", "-id",
            "plate", "-plate",
            "brand", "-brand",
            "type", "-type",
            "fleet", "-fleet",
        }

        if ordering not in allowed_ordering:
            ordering = "id"

        return queryset.order_by(ordering)


class VehicleDetailView(generics.RetrieveAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleDetailSerializer


class InspectionListCreateView(APIView):
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        queryset = VehicleInspection.objects.select_related("vehicle").all()

        status_param = request.query_params.get("status")
        vehicle_id = request.query_params.get("vehicle_id")
        plate = request.query_params.get("vehicle_plate")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        ordering = request.query_params.get("ordering", "-date")

        if status_param:
            queryset = queryset.filter(status=status_param)

        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)

        if plate:
            queryset = queryset.filter(vehicle__plate__icontains=plate)

        if date_from:
            queryset = queryset.filter(date__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(date__date__lte=date_to)

        allowed_ordering = {
            "id", "-id",
            "date", "-date",
            "odometer", "-odometer",
            "status", "-status",
            "vehicle__plate", "-vehicle__plate",
        }

        if ordering not in allowed_ordering:
            ordering = "-date"

        queryset = queryset.order_by(ordering)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = InspectionListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CreateInspectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            inspection = create_inspection(
                vehicle_id=serializer.validated_data["vehicle_id"],
                odometer_km=serializer.validated_data["odometer_km"],
            )
        except ServiceError as error:
            return Response(
                {"detail": error.message},
                status=error.status_code,
            )

        output_serializer = InspectionListSerializer(inspection)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class InspectionFinalizeView(APIView):
    def patch(self, request, pk):
        try:
            inspection = finalize_inspection(pk)
        except ServiceError as error:
            return Response(
                {"detail": error.message},
                status=error.status_code,
            )

        serializer = InspectionListSerializer(inspection)

        return Response(serializer.data, status=status.HTTP_200_OK)