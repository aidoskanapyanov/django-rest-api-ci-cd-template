from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from fuel_tracker.calculator.views import AirplaneViewSet
from fuel_tracker.calculator.views import ConfigurationViewSet
from fuel_tracker.calculator.views import FuelCalculationRecordViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("airplanes", AirplaneViewSet)
router.register("configurations", ConfigurationViewSet)
router.register("results", FuelCalculationRecordViewSet)


app_name = "calculator"
urlpatterns = router.urls
