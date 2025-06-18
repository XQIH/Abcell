from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'freezers', views.FreezerViewSet, basename='freezer')
router.register(r'freezers1', views.FreezerViewSet1, basename='freezer1')
router.register(r'levels', views.LevelViewSet, basename='level')
router.register(r'columns', views.ColumnViewSet, basename='column')
router.register(r'drawers', views.DrawerViewSet, basename='drawer')
router.register(r'boxes', views.BoxViewSet, basename='box')
router.register(r'cells', views.CellViewSet, basename='cell')
router.register(r'locations', views.LocationViewSet, basename='location')
urlpatterns = router.urls