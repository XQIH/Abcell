from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.hashers import check_password, make_password
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
import os
from django.conf import settings


from rest_framework.permissions import AllowAny
from .models import User
from .serializers import (
    UserListSerializer, UserDetailSerializer,
    UserCreateSerializer, UserUpdateSerializer,
    PasswordResetSerializer, UserLoginSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, authenticate
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ActivityLog

@api_view(['GET'])
def get_recent_activities(request):
    activities = ActivityLog.objects.all().order_by('-created_at')[:10]
    data = [{
        'time': activity.created_at.strftime('%Y-%m-%d %H:%M'),
        'content': activity.content,
        'type': activity.activity_type
    } for activity in activities]
    return Response(data)

User = get_user_model()

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 验证必填字段
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'error': f'{field}是必填字段'}, status=400)
            
            # 检查用户是否已存在
            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({'error': '邮箱已被注册'}, status=400)
                
            # 创建用户
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            
            # 修改为不返回密码
            return JsonResponse({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'status': '注册成功'
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '只支持POST请求'}, status=405)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # 需要添加这行
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['permission_level']
    search_fields = ['username', 'email']

    def get_queryset(self):
        queryset = super().get_queryset()

        # 获取查询参数
        username = self.request.query_params.get('username', None)
        email = self.request.query_params.get('email', None)
        permission_level = self.request.query_params.get('permission_level', None)

        # 应用过滤条件
        if username:
            queryset = queryset.filter(username__icontains=username)
        if email:
            queryset = queryset.filter(email__icontains=email)
        if permission_level:
            queryset = queryset.filter(permission_level=permission_level)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserListSerializer  # 默认返回UserListSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(
            request,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if not user:
            raise AuthenticationFailed('邮箱或密码错误')
        
        refresh = RefreshToken.for_user(user)
        print(refresh)
        print(user.user_permissions)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'permission_level': user.permission_level
        })

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordResetSerializer(data=request.data)
    
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        # 自动处理密码哈希
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'status': '密码重置成功'})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        """删除用户（禁止删除自己）"""
        instance = self.get_object()

        if instance.id == request.user.id:
            return Response(
                {'error': '不能删除当前登录用户'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from .models import User

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data['email'])
            # 添加以下字段到响应数据
            response.data.update({
                'user_id': user.id,
                'permission_level': user.permission_level,  # 确保User模型有这个字段
                'email': user.email,
                'username': user.username
            })
            print(response.data)
        return response

# def abcd(request):
#     if request.method == 'GET':
#         return JsonResponse({'code': '200', 'message': 'abcd'})
#     if request.method == 'POST':
#         return JsonResponse({'code': '200', 'message': 'efg'})







