# cell/serializers.py
# 细胞管理

from rest_framework import serializers
from sysuser.models import CellInventory,CellOutRecord, CellType, Freezer, Level, Column, Drawer, Box, Cell

# 细胞库存管理


class CellTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CellType
        fields = ['id', 'name', 'category', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class StorageLocationSerializer(serializers.Serializer):
    freezer = serializers.CharField(source='box.drawer.column.level.freezer.name')
    level = serializers.CharField(source='box.drawer.column.level.name')
    column = serializers.CharField(source='box.drawer.column.name')
    drawer = serializers.CharField(source='box.drawer.name')
    box = serializers.CharField(source='box.name')
    cell = serializers.CharField(source='name')


class CellInventorySerializer(serializers.ModelSerializer):
    cell_type = CellTypeSerializer()
    storage_location = serializers.SerializerMethodField()
    entry_person = serializers.CharField(source='entry_person.username')

    class Meta:
        model = CellInventory
        fields = [
            'id', 'cell_id', 'cell_type', 'storage_location',
            'quantity', 'status', 'entry_time', 'entry_person', 'notes'
        ]

    def get_storage_location(self, obj):
        return f"{obj.storage_location.box.drawer.column.level.freezer.name}/" \
               f"{obj.storage_location.box.drawer.column.level.name}/" \
               f"{obj.storage_location.box.drawer.column.name}/" \
               f"{obj.storage_location.box.drawer.name}/" \
               f"{obj.storage_location.box.name}/" \
               f"{obj.storage_location.name}"


class CellInventoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CellInventory
        fields = [
            'cell_id', 'cell_type', 'storage_location',
            'quantity', 'status', 'notes'
        ]
        read_only_fields = ['entry_person']  # 添加这行


class StatisticsSerializer(serializers.Serializer):
    type_distribution = serializers.ListField()
    status_labels = serializers.ListField()
    status_data = serializers.ListField()


# 细胞出库


class CellOutRecordSerializer(serializers.ModelSerializer):
    cell_inventory = serializers.SerializerMethodField()  # 修改字段名
    out_person = serializers.SerializerMethodField()

    class Meta:
        model = CellOutRecord
        fields = [
            'id', 'cell_inventory', 'out_time', 'out_person',  # 修改字段名
            'receiver', 'purpose', 'notes'
        ]

    def get_cell_inventory(self, obj):  # 修改方法名
        return {
            'id': obj.cell_inventory.id,
            'cell_id': obj.cell_inventory.cell_id,
            'cell_type': {
                'id': obj.cell_inventory.cell_type.id,
                'name': obj.cell_inventory.cell_type.name
            },
            'storage_location': str(obj.cell_inventory.storage_location)
        }

    def get_out_person(self, obj):
        return {
            'id': obj.out_person.id,
            'name': obj.out_person.username
        }


class CellOutRecordCreateSerializer(serializers.ModelSerializer):
    # cell_id = serializers.CharField(write_only=True)  # 新增字段，仅用于输入

    class Meta:
        model = CellOutRecord
        fields = ['cell_inventory', 'receiver', 'purpose', 'notes']

    # def create(self, validated_data):
    #     cell_id = validated_data.pop('cell_id')
    #     try:
    #         cell_inventory = CellInventory.objects.get(cell_id=cell_id)
    #     except CellInventory.DoesNotExist:
    #         raise serializers.ValidationError({"cell_id": "未找到对应的细胞库存"})
    #
    #     validated_data['cell_inventory'] = cell_inventory
    #     return super().create(validated_data)


class AvailableCellSerializer(serializers.ModelSerializer):
    cell_type = serializers.SerializerMethodField()
    storage_location = serializers.SerializerMethodField()

    class Meta:
        model = CellInventory
        fields = ['id', 'cell_id', 'cell_type', 'storage_location']

    def get_cell_type(self, obj):
        return {
            'id': obj.cell_type.id,
            'name': obj.cell_type.name
        }

    def get_storage_location(self, obj):
        return str(obj.storage_location)

# 细胞类型
class CellTypeSerializer1(serializers.ModelSerializer):
    class Meta:
        model = CellType
        fields = ['id', 'name', 'category', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CellTypeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CellType
        fields = ['name', 'category', 'description']