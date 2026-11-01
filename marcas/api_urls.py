from rest_framework.routers import SimpleRouter

from .api_views import MarcaViewSet

router = SimpleRouter()
router.register("", MarcaViewSet, basename="marca")

urlpatterns = router.urls
