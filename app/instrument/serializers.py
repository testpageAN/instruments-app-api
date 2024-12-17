"""
Serializers for instruments APIs
"""
from rest_framework import serializers

from core.models import Instrument


class InstrumentSerializer(serializers.ModelSerializer):
    """Serializer for instruments."""

    class Meta:
        model = Instrument
        fields = ['tag',
                  'unit',
                  'description',
                  'type',
                  'manufacturer',
                  'serial_no',
                  'interval',
                  'created_at',
                  'last_checked',
                  'notes',
                  'link']
        read_only_fields = ['id']
