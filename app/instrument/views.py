"""
Views for the instrument APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Instrument
from instrument import serializers

import pandas as pd  # noqa
from rest_framework.views import APIView  # noqa
from rest_framework.response import Response  # noqa
from rest_framework import status  # noqa


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
