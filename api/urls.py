from django.conf.urls import url, include

from rest_framework import routers
from rest_framework.authtoken import views as drf_views

from api import views

router = routers.DefaultRouter()
router.register(r'flavors', views.FlavorViewSet, 'Flavor')
router.register(r'ingredients', views.IngredientViewSet, 'Ingredient')
router.register(r'leafweights', views.LeafWeightViewSet, 'LeafWeight')
router.register(r'users', views.UserViewSet)
router.register(r'tags', views.TagViewSet)

urlpatterns = (
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^auth$', drf_views.obtain_auth_token, name='auth'),
)

