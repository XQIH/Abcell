from django_filters import rest_framework as filters
from sysuser.models import CellOutRecord


class CellOutRecordFilterSet(filters.FilterSet):
    cell_id = filters.CharFilter(field_name='cell_inventory__cell_id', lookup_expr='icontains')  # 修改关联字段
    receiver = filters.CharFilter(field_name='receiver', lookup_expr='icontains')
    
    class Meta:
        model = CellOutRecord
        fields = ['cell_id', 'receiver']