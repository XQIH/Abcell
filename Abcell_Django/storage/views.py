from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from sysuser.models import Freezer, Level, Column, Drawer, Box, Cell, ActivityLog
from .serializers import FreezerSerializer, FreezerCreateUpdateSerializer, LocationTreeSerializer, LevelSerializer, \
    ColumnSerializer, DrawerSerializer, BoxSerializer, CellSerializer


class FreezerViewSet(viewsets.ModelViewSet):
    queryset = Freezer.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'number']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FreezerCreateUpdateSerializer
        return FreezerSerializer

    def create(self, request, *args, **kwargs):
        # 检查冰柜编号是否已存在
        number = request.data.get('number')
        if Freezer.objects.filter(number=number).exists():
            return Response(
                {'number': '冰柜编号已存在'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # 检查冰柜编号是否已存在（排除自己）
        instance = self.get_object()
        number = request.data.get('number')
        if Freezer.objects.filter(number=number).exclude(id=instance.id).exists():
            return Response(
                {'number': '冰柜编号已存在'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # print(dir(instance.levels.name))
        # 检查冰柜是否包含层级结构
        if instance.levels.exists():
            return Response(
                {'error': '无法删除，冰柜中包含层级结构'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FreezerViewSet1(viewsets.ModelViewSet):
    queryset = Freezer.objects.all()
    serializer_class = FreezerSerializer
    permission_classes = [IsAuthenticated]


class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        freezer_id = request.data.get('freezer', instance.freezer.id)
        number = request.data.get('number')
        if Level.objects.filter(freezer_id=freezer_id, number=number).exclude(id=instance.id).exists():
            return Response(
                {'number': '此冰柜中已存在该层级编号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.columns.exists():
            return Response(
                {'error': '无法删除，此层级包含列结构'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        freezer_id = request.data.get('freezer')
        number = request.data.get('number')
        if Level.objects.filter(freezer_id=freezer_id, number=number).exists():
            return Response(
                {'number': '此冰柜中已存在该层级编号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        level_id = request.data.get('level', instance.level.id)
        number = request.data.get('number')
        if Column.objects.filter(level_id=level_id, number=number).exclude(id=instance.id).exists():
            return Response(
                {'number': '此层级中已存在该列级编号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.drawers.exists():
            return Response(
                {'error': '无法删除，此列级包含抽屉结构'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        level_id = request.data.get('level')
        number = request.data.get('number')
        if Column.objects.filter(level_id=level_id, number=number).exists():
            return Response(
                {'number': '此层级中已存在该列级编号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class DrawerViewSet(viewsets.ModelViewSet):
    queryset = Drawer.objects.all()
    serializer_class = DrawerSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        column_id = request.data.get('column', instance.column.id)
        number = request.data.get('number')
        if Drawer.objects.filter(column_id=column_id, number=number).exclude(id=instance.id).exists():
            return Response(
                {'number': '同一列中已存在该抽屉编号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(dir(instance))
        if instance.boxes.exists():
            return Response(
                {'error': '无法删除，此抽屉包含盒子结构'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        column_id = request.data.get('column')
        number = request.data.get('number')
        if Drawer.objects.filter(column_id=column_id, number=number).exists():
            return Response(
                {'number': '同一列中已存在该抽屉编号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        drawer_id = request.data.get('drawer', instance.drawer.id)
        number = request.data.get('number')
        if Box.objects.filter(drawer_id=drawer_id, number=number).exclude(id=instance.id).exists():
            return Response(
                {'number': '同一抽屉中已存在该盒子编号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.cells.exists():
            return Response(
                {'error': '无法删除，此盒子包含格子结构'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        drawer_id = request.data.get('drawer')
        number = request.data.get('number')
        if Box.objects.filter(drawer_id=drawer_id, number=number).exists():
            return Response(
                {'number': '同一抽屉中已存在该盒子编号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)



class CellViewSet(viewsets.ModelViewSet):
    queryset = Cell.objects.all()
    serializer_class = CellSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        box_id = request.data.get('box', instance.box.id)
        number = request.data.get('number')
        if Cell.objects.filter(box_id=box_id, number=number).exclude(id=instance.id).exists():
            return Response(
                {'number': '同一盒子中已存在该格子编号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        box_id = request.data.get('box')
        number = request.data.get('number')
        if Cell.objects.filter(box_id=box_id, number=number).exists():
            return Response(
                {'number': '同一盒子中已存在该格子编号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance.cellinventory_set.exists())
        if instance.cellinventory_set.exists():
            return Response(
                {'error': '无法删除，此格子包含细胞'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LocationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def tree(self, request):
        # 获取完整的存储位置树形结构
        freezers = Freezer.objects.prefetch_related(
            Prefetch('levels', queryset=Level.objects.prefetch_related(
                Prefetch('columns', queryset=Column.objects.prefetch_related(
                    Prefetch('drawers', queryset=Drawer.objects.prefetch_related(
                        Prefetch('boxes', queryset=Box.objects.prefetch_related(
                            'cells'
                        ))
                    ))
                ))
            )
                     )).all()

        def build_tree(node):
            if isinstance(node, Freezer):
                children = node.levels.all()
                node_type = 'freezer'
            elif isinstance(node, Level):
                children = node.columns.all()
                node_type = 'level'
            elif isinstance(node, Column):
                children = node.drawers.all()
                node_type = 'column'
            elif isinstance(node, Drawer):
                children = node.boxes.all()
                node_type = 'drawer'
            elif isinstance(node, Box):
                children = node.cells.all()
                node_type = 'box'
            elif isinstance(node, Cell):
                return {
                    'id': node.id,
                    'name': node.name,
                    'number': node.number,
                    'type': 'cell',
                    'description': node.description,
                    'row_num':node.row_num,
                    'col_num':node.col_num,
                    'children': []
                }

            return {
                'id': node.id,
                'name': node.name,
                'number': getattr(node, 'number', ''),
                'type': node_type,
                'description': node.description,
                'children': [build_tree(child) for child in children]
            }

        tree_data = [build_tree(freezer) for freezer in freezers]
        serializer = LocationTreeSerializer(data=tree_data, many=True)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        return Response(serializer.data)
