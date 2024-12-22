"""
Serializers for instruments APIs
"""
from rest_framework import serializers

from core.models import Instrument


class InstrumentSerializer(serializers.ModelSerializer):
    """Serializer for instruments."""
    # last_checked = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z",
    # input_formats=["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"])

    class Meta:
        model = Instrument
        fields = ['id',
                  'tag',
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


class InstrumentDetailSerializer(InstrumentSerializer):
    """Serializer for Instrument detail view."""

    class Meta(InstrumentSerializer.Meta):
        # fields = InstrumentSerializer.Meta.fields + ['description_2']
        pass
