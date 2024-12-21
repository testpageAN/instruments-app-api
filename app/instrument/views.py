"""
Views for the instrument APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Instrument
from instrument import serializers

import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from .serializers import BulkUploadSerializer


class InstrumentViewSet(viewsets.ModelViewSet):
    """View for manage instrument APIs."""
    # serializer_class = serializers.InstrumentSerializer
    serializer_class = serializers.InstrumentDetailSerializer
    queryset = Instrument.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve instruments for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.InstrumentSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new instrument."""
        serializer.save(user=self.request.user)


class BulkUploadView(APIView):
    """View for bulk upload"""

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = pd.read_csv(file)
        except Exception as e:
            return Response({"error": f"Error reading CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        records = data.to_dict(orient='records')
        serializer = BulkUploadSerializer(data=records, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Bulk upload successful", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
