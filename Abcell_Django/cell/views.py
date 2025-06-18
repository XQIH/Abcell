from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.

# cell/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from sysuser.models import CellInventory, CellType, Cell, CellOutRecord
from django.db.models import Q

from .filters import CellOutRecordFilterSet
from .serializers import (
    CellInventorySerializer,
    CellInventoryCreateUpdateSerializer,
    CellTypeSerializer,
    StatisticsSerializer,
    CellOutRecordSerializer,
    CellOutRecordCreateSerializer,
    AvailableCellSerializer,
    CellTypeCreateUpdateSerializer
)


class CellInventoryViewSet(viewsets.ModelViewSet):
    queryset = CellInventory.objects.select_related(
        'cell_type', 'entry_person', 'storage_location__box__drawer__column__level__freezer'
    ).all()
    serializer_class = CellInventorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cell_id', 'cell_type__name', 'status']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CellInventoryCreateUpdateSerializer
        return super().get_serializer_class()
        
    def perform_create(self, serializer):
        # 自动设置录入人为当前用户
        serializer.save(entry_person=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        # 细胞类型分布统计
        type_distribution = []
        for cell_type in CellType.objects.all():
            count = CellInventory.objects.filter(cell_type=cell_type).count()
            type_distribution.append({
                'value': count,
                'name': cell_type.name
            })

        # 细胞状态统计
        status_labels = ['在库', '出库', '已销毁']
        status_data = [
            CellInventory.objects.filter(status='in_stock').count(),
            CellInventory.objects.filter(status='out_stock').count(),
            CellInventory.objects.filter(status='destroyed').count()
        ]

        data = {
            'type_distribution': type_distribution,
            'status_labels': status_labels,
            'status_data': status_data
        }

        serializer = StatisticsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class CellTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CellType.objects.all()
    serializer_class = CellTypeSerializer
    permission_classes = [IsAuthenticated]


class StorageLocationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # 这里简化为返回所有格子，实际可以根据需要筛选
        cells = Cell.objects.select_related(
            'box__drawer__column__level__freezer'
        ).all()[:100]  # 限制返回数量

        # 构建级联选择器需要的数据结构
        freezers = {}
        for cell in cells:
            freezer = cell.box.drawer.column.level.freezer
            level = cell.box.drawer.column.level
            column = cell.box.drawer.column
            drawer = cell.box.drawer
            box = cell.box

            if freezer.id not in freezers:
                freezers[freezer.id] = {
                    'value': freezer.name,
                    'label': freezer.name,
                    'children': {}
                }

            if level.id not in freezers[freezer.id]['children']:
                freezers[freezer.id]['children'][level.id] = {
                    'value': level.name,
                    'label': level.name,
                    'children': {}
                }

            if column.id not in freezers[freezer.id]['children'][level.id]['children']:
                freezers[freezer.id]['children'][level.id]['children'][column.id] = {
                    'value': column.name,
                    'label': column.name,
                    'children': {}
                }

            if drawer.id not in freezers[freezer.id]['children'][level.id]['children'][column.id]['children']:
                freezers[freezer.id]['children'][level.id]['children'][column.id]['children'][drawer.id] = {
                    'value': drawer.name,
                    'label': drawer.name,
                    'children': {}
                }

            if box.id not in freezers[freezer.id]['children'][level.id]['children'][column.id]['children'][drawer.id][
                'children']:
                freezers[freezer.id]['children'][level.id]['children'][column.id]['children'][drawer.id]['children'][
                    box.id] = {
                    'value': box.name,
                    'label': box.name,
                    'children': [
                        {'value': cell.name, 'label': cell.name}
                    ]
                }

        # 转换为前端需要的格式
        def convert_to_list(tree):
            result = []
            for item in tree.values():
                new_item = {
                    'value': item['value'],
                    'label': item['label']
                }
                if 'children' in item and item['children']:
                    new_item['children'] = convert_to_list(item['children'])
                result.append(new_item)
            return result

        options = convert_to_list(freezers)
        return Response(options)


# 细胞出库
class CellOutRecordViewSet(viewsets.ModelViewSet):
    queryset = CellOutRecord.objects.select_related(
        'cell_inventory__cell_type', 'out_person'  # 修改关联字段
    ).all()
    serializer_class = CellOutRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    
    # 使用自定义的FilterSet类
    filterset_class = CellOutRecordFilterSet
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return CellOutRecordCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        # 自动设置出库人为当前用户
        serializer.save(out_person=self.request.user)
    
        # 更新细胞库存状态
        cell_inventory = serializer.validated_data['cell_inventory']  # 修改为访问cell_inventory
        cell_inventory.status = 'out_stock'
        cell_inventory.save()

        # cell = serializer.validated_data['cell','']
        # cell.status = 'out_stock'
        # cell.save()

    @action(detail=False, methods=['post'])
    def by_cell_id(self, request):
        """根据cell_id创建出库记录"""
        cell_id = request.data.get('cell_id')
        if not cell_id:
            return Response({'error': 'cell_id不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cell_inventory = CellInventory.objects.get(cell_id=cell_id)
            # 复制请求数据并替换cell_id为cell_inventory.id
            data = request.data.copy()
            data['cell_inventory'] = cell_inventory.id
            serializer = CellOutRecordCreateSerializer(data=data)  # 直接指定 Serializer
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except CellInventory.DoesNotExist:
            return Response({'error': '未找到对应的细胞库存'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def available_cells_by_id(self, request):
        """根据cell_id获取可出库细胞"""
        search_query = request.query_params.get('search', '')
        
        queryset = CellInventory.objects.filter(
            status='in_stock'
        ).select_related('cell_type', 'storage_location')

        if search_query:
            queryset = queryset.filter(cell_id__icontains=search_query)  # 改为匹配cell_id

        serializer = AvailableCellSerializer(queryset[:20], many=True)
        return Response(serializer.data)


# 细胞类型

class CellTypeViewSet1(viewsets.ModelViewSet):
    queryset = CellType.objects.all()

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'category']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CellTypeCreateUpdateSerializer
        return CellTypeSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # 检查是否有细胞使用此类型
        if instance.cell_inventories.exists():
            return Response(
                {'error': '无法删除，有细胞使用此类型'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


@login_required
def add_cell(request):
    if request.method == 'POST':
        # 获取当前登录用户ID
        user_id = request.user.id
        
        return JsonResponse({'status': 'success'})
