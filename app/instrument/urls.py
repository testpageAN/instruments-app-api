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
    # path('instruments/bulk-upload/', views.BulkUploadView.as_view(), name='bulk-upload'),
    path('', include(router.urls)),
]
