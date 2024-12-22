"""
URL mappings for the instrument app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from instrument import views


router = DefaultRouter()
router.register('instruments', views.InstrumentViewSet)

app_name = 'instrument'

urlpatterns = [
    path('', include(router.urls)),
]
