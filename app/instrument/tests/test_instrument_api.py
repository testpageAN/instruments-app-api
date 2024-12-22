"""
Tests for instrument APIs.
"""
from decimal import Decimal  # noqa
from datetime import datetime
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Instrument

from instrument.serializers import (
    InstrumentSerializer,
    InstrumentDetailSerializer,
)

from rest_framework.test import APITestCase  # noqa
from django.core.files.uploadedfile import SimpleUploadedFile  # noqa
import io  # noqa

INSTRUMENTS_URL = reverse('instrument:instrument-list')
# BULK_UPLOAD_URL = reverse('instrument:bulk-upload')


def detail_url(instrument_id):
    """Create and return a instrument detail URL."""
    return reverse('instrument:instrument-detail', args=[instrument_id])


def create_instrument(user, **params):
    """Create and return a sample instrument."""
    defaults = {
        'tag': "11-FV-01",
        'unit': "1100",
        'description': "GO FLOW",
        'type': "CONTROL VALVE",
        'manufacturer': "EMERSON",
        'serial_no': "123456EU",
        'interval': 100,
        'created_at': timezone.make_aware(datetime(2020, 1, 1)),
        'last_checked': timezone.make_aware(datetime(2021, 1, 1)),
        'notes': "01/01/2020: Created" + "\n" + "01/01/2021: Changed" + "\n",
        'link': "http://example.com/instrument.pdf",
    }
    defaults.update(params)

    instrument = Instrument.objects.create(user=user, **defaults)
    return instrument


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


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
        # self.user = get_user_model().objects.create_user(
        #     'user@example.com',
        #     'testpass123',
        # )
        self.user = create_user(email='user@example.com', password='test123')
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
        # other_user = get_user_model().objects.create_user(
        #     'other@example.com',
        #     'password123',
        # )
        other_user = create_user(email='other@example.com', password='test123')
        create_instrument(user=other_user)
        create_instrument(user=self.user)

        res = self.client.get(INSTRUMENTS_URL)

        instruments = Instrument.objects.filter(user=self.user)
        serializer = InstrumentSerializer(instruments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_instrument_detail(self):
        """Test get instrument detail."""
        instrument = create_instrument(user=self.user)

        url = detail_url(instrument.id)
        res = self.client.get(url)

        serializer = InstrumentDetailSerializer(instrument)
        self.assertEqual(res.data, serializer.data)

    def test_create_instrument(self):
        """Test creating an instrument."""
        payload = {
            'tag': "11-FV-01",
            'unit': "1100",
            'description': "GO FLOW",
            'type': "CONTROL VALVE",
            'manufacturer': "EMERSON",
            'serial_no': "123456EU",
            'interval': 100,
            # 'created_at': datetime.now().replace(microsecond=0),
            'created_at': timezone.now(),
            'last_checked': timezone.make_aware(datetime(2021, 1, 1)),
            'notes': "01/01/2020: Created" + "\n" + "01/01/2021: Changed",
            'link': "http://example.com/instrument.pdf",
        }
        res = self.client.post(INSTRUMENTS_URL, payload)
        print(res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        instrument = Instrument.objects.get(id=res.data['id'])
        # for k, v in payload.items():
        #     self.assertEqual(getattr(instrument, k), v)
        # self.assertEqual(instrument.user, self.user)
        for k, v in payload.items():
            if isinstance(v, datetime):
                self.assertEqual(
                    getattr(instrument, k).replace(microsecond=0),
                    v.replace(microsecond=0)
                )
            else:
                self.assertEqual(getattr(instrument, k), v)

    def test_partial_update(self):
        """Test partial update of a instrument."""
        original_link = 'https://example.com/instrument.pdf'
        instrument = create_instrument(
            user=self.user,
            link=original_link,
            tag="11-FV-01",
            unit="1100",
            description="GO FLOW",
            type="CONTROL VALVE",
            manufacturer="EMERSON",
            serial_no="123456EU",
            interval=100,
            created_at=timezone.make_aware(datetime(2020, 1, 1)),
            last_checked=timezone.make_aware(datetime(2021, 1, 1)),
            notes="01/01/2020: Created" + "\n" + "01/01/2021: Changed" + "\n",
        )

        payload = {'tag': 'NEW_11-FV-01_NEW'}
        url = detail_url(instrument.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        instrument.refresh_from_db()
        self.assertEqual(instrument.tag, payload['tag'])
        self.assertEqual(instrument.link, original_link)
        self.assertEqual(instrument.user, self.user)

    def test_full_update(self):
        """Test full update of instrument."""
        instrument = create_instrument(
            user=self.user,
            link="http://example.com/instrument.pdf",
            tag="11-FV-01",
            unit="1100",
            description="GO FLOW",
            type="CONTROL VALVE",
            manufacturer="EMERSON",
            serial_no="123456EU",
            interval=100,
            created_at=timezone.make_aware(datetime(2020, 1, 1)),
            last_checked=timezone.make_aware(datetime(2021, 1, 1)),
            notes="01/01/2020: Created" + "\n" + "01/01/2021: Changed" + "\n",
        )

        payload = {
            'tag': "11-FV-01_NEW",
            'unit': "1100_NEW",
            'description': "GO FLOW_NEW",
            'type': "CONTROL VALVE_NEW",
            'manufacturer': "EMERSON_NEW",
            'serial_no': "123456EU_NEW",
            'interval': 111,
            # 'created_at': datetime.now().replace(microsecond=0),
            'created_at': timezone.now(),
            'last_checked': timezone.make_aware(datetime(2021, 1, 1)),
            'notes': "01/01/2020: Created_NEW" + "\n" +
                     "01/01/2021: Changed_NEW",
            'link': "http://example.com/instrument_NEW.pdf",
        }
        url = detail_url(instrument.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        instrument.refresh_from_db()
        # for k, v in payload.items():
        #     self.assertEqual(getattr(instrument, k), v)
        # self.assertEqual(instrument.user, self.user)
        for k, v in payload.items():
            if isinstance(v, datetime):
                self.assertEqual(
                    getattr(instrument, k).replace(microsecond=0),
                    v.replace(microsecond=0)
                )
            else:
                self.assertEqual(getattr(instrument, k), v)

    def test_update_user_returns_error(self):
        """Test changing the instrument user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        instrument = create_instrument(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(instrument.id)
        self.client.patch(url, payload)

        instrument.refresh_from_db()
        self.assertEqual(instrument.user, self.user)

    def test_delete_instrument(self):
        """Test deleting a instrument successful."""
        instrument = create_instrument(user=self.user)

        url = detail_url(instrument.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Instrument.objects.filter(id=instrument.id).exists())

    def test_instrument_other_users_instrument_error(self):
        """Test trying to delete another users instrument gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        instrument = create_instrument(user=new_user)

        url = detail_url(instrument.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Instrument.objects.filter(id=instrument.id).exists())
