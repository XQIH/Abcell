from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'gender', 'permission_level', 'avatar']


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""
    permission_level_display = serializers.CharField(
        source='get_permission_level_display',
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'gender',
            'permission_level', 'permission_level_display'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(
        write_only=True,  # 确保密码不返回
        required=True,
        min_length=6,
        style={'input_type': 'password'}
    )

    def create(self, validated_data):
        print(validated_data.keys())
        if 'permission_level' not in validated_data.keys():
            validated_data['permission_level'] = 1
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            gender=validated_data['gender'],
            phone=validated_data['phone'],
            permission_level=validated_data['permission_level']
        )
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone', 'gender', 'permission_level']


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""

    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone', 'gender',
            'permission_level'
        ]

    def validate(self, data):
        # 获取实例
        instance = self.instance

        # 验证邮箱唯一性（排除自己）
        if 'email' in data and User.objects.filter(email=data['email']).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({'email': '邮箱已被注册'})

        # 验证用户名唯一性（排除自己）
        if 'username' in data and User.objects.filter(username=data['username']).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({'username': '用户名已存在'})

        # 验证电话唯一性（排除自己）
        if 'phone' in data and data['phone'] and User.objects.filter(phone=data['phone']).exclude(
                pk=instance.pk).exists():
            raise serializers.ValidationError({'phone': '电话已被使用'})

        return data


class PasswordResetSerializer(serializers.Serializer):
    """密码重置序列化器"""
    user_id = serializers.IntegerField(required=True)
    new_password = serializers.CharField(
        required=True,
        min_length=6,
        write_only=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '两次密码输入不一致'})
        return data


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        # 添加额外的验证逻辑
        if not attrs.get('email') or not attrs.get('password'):
            raise serializers.ValidationError("邮箱和密码不能为空")
        return attrs