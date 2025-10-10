from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, UserViewSet

router = DefaultRouter()
router.register(r'api/organizations', OrganizationViewSet, basename='organization')
router.register(r'auth/user', UserViewSet, basename='user')

urlpatterns = router.urls
