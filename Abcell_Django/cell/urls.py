from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cells', views.CellInventoryViewSet, basename='cell')
router.register(r'cell-types', views.CellTypeViewSet, basename='cell-type')
router.register(r'cell-types1', views.CellTypeViewSet1, basename='cell-type1')
router.register(r'storage-locations', views.StorageLocationViewSet, basename='storage-location')
router.register(r'cell-out-records', views.CellOutRecordViewSet, basename='cell-out-record')

urlpatterns = [
    path('', include(router.urls)),

    # 单独添加可出库细胞查询端点
    path(
        'cell-out-records/available-cells/',
        views.CellOutRecordViewSet.as_view({'get': 'available_cells'}),
        name='available-cells'
    ),
    path('cell-out-records/by-cell-id/',
         views.CellOutRecordViewSet.as_view({'post': 'by_cell_id'}),
         name='cell-out-by-id'),
    path('cell-out-records/available-cells-by-id',
         views.CellOutRecordViewSet.as_view({'get': 'available_cells_by_id'}),
         name='available-cells-by-id'),
] + router.urls
