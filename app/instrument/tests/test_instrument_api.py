"""
Tests for instrument APIs.
"""
from decimal import Decimal  # noqa
from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Instrument

from instrument.serializers import InstrumentSerializer


INSTRUMENTS_URL = reverse('instrument:instrument-list')


def create_instrument(user, **params):
    """Create and return a sample instrument."""
    defaults = {
        'tag': "11-FV-01",
        'unit': "1100",
        'description': "GO FLOW",
        'type': "CONTROL VALVE",
        'manufacturer': "EMERSON",
        'serial_no': "123456EU",
        'interval': "100",
        'created_at': datetime(2020, 1, 1),
        'last_checked': datetime(2021, 1, 1),
        'notes': """
        01/01/2020: Created
        01/01/2021: Changed
        """,
        'link': "http://example.com/instrument.pdf",
    }
    defaults.update(params)

    instrument = Instrument.objects.create(user=user, **defaults)
    return instrument


class PublicInstrumentAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(INSTRUMENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateInstrumentApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_instruments(self):
        """Test retrieving a list of instruments."""
        create_instrument(user=self.user)
        create_instrument(user=self.user)

        res = self.client.get(INSTRUMENTS_URL)

        instruments = Instrument.objects.all().order_by('-id')
        serializer = InstrumentSerializer(instruments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_instrument_list_limited_to_user(self):
        """Test list of instruments is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_instrument(user=other_user)
        create_instrument(user=self.user)

        res = self.client.get(INSTRUMENTS_URL)

        instruments = Instrument.objects.filter(user=self.user)
        serializer = InstrumentSerializer(instruments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
