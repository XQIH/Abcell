from rest_framework import serializers
from sysuser.models import Freezer,Level, Column, Drawer, Box, Cell


class FreezerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freezer
        fields = ['id', 'name', 'number', 'location', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class FreezerCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freezer
        fields = ['name', 'number', 'location', 'description']
        extra_kwargs = {
            'number': {'validators': []}  # 禁用唯一性验证，在视图函数中处理
        }


# class FreezerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Freezer
#         fields = ['id', 'name', 'number', 'description', 'created_at', 'updated_at']
#         read_only_fields = ['created_at', 'updated_at']

class LevelSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        # 创建操作必须提供freezer，更新操作自动保留原值
        if self.instance is None and 'freezer' not in attrs:
            raise serializers.ValidationError({"freezer": "创建层级必须指定所属冰柜"})
        return attrs

    class Meta:
        model = Level
        fields = ['id', 'name', 'number', 'description', 'freezer', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'freezer': {'required': False}  # 设为非必填，通过validate方法控制
        }


class ColumnSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if self.instance is None and 'level' not in attrs:
            raise serializers.ValidationError({"level": "创建列级必须指定所属层"})
        return attrs

    class Meta:
        model = Column
        fields = ['id', 'name', 'number', 'description', 'level', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'level': {'required': False}  # 设为非必填，通过validate方法控制
        }


class DrawerSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if self.instance is None and 'column' not in attrs:
            raise serializers.ValidationError({"column": "创建抽屉级必须指定所属列"})
        return attrs

    class Meta:
        model = Drawer
        fields = ['id', 'name', 'number', 'description', 'column', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'column': {'required': False}  # 设为非必填，通过validate方法控制
        }


class BoxSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if self.instance is None and 'drawer' not in attrs:
            raise serializers.ValidationError({"level": "创建盒子级必须指定所属抽屉"})
        return attrs

    class Meta:
        model = Box
        fields = ['id', 'name', 'number', 'description', 'drawer', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'drawer': {'required': False}  # 设为非必填，通过validate方法控制
        }


class CellSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if self.instance is None and 'box' not in attrs:
            raise serializers.ValidationError({"level": "创建格子级必须指定所属盒子"})
        return attrs

    class Meta:
        model = Cell
        fields = ['id', 'name', 'number', 'description', 'box', 'row_num', 'col_num', 'is_occupied', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'box': {'required': False}  # 设为非必填，通过validate方法控制
        }


class LocationTreeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    number = serializers.CharField(required=False)
    type = serializers.CharField()
    description = serializers.CharField(required=False)
    children = serializers.ListField(child=serializers.DictField())