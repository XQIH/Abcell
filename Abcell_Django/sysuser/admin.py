from django.contrib import admin
from .models import User
from django.core.exceptions import PermissionDenied

class PermissionLevelFilter(admin.SimpleListFilter):
    title = '权限级别'
    parameter_name = 'permission_level'

    def lookups(self, request, model_admin):
        return User.PERMISSION_LEVEL_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(permission_level=self.value())
        return queryset

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = (PermissionLevelFilter,)
    list_display = ('username', 'email', 'get_permission_level_display', 'is_active')
    list_filter = ('permission_level', 'is_active')
    search_fields = ('username', 'email')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'email', 'password')
        }),
        ('权限设置', {
            'fields': ('permission_level', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('其他信息', {
            'fields': ('phone', 'gender', 'last_login', 'date_joined')
        }),
    )
    
    actions = ['make_level1', 'make_level2', 'make_level3']
    
    def make_level1(self, request, queryset):
        queryset.update(permission_level=1)
    make_level1.short_description = "设为1级权限(超级管理员)"
    
    def make_level2(self, request, queryset):
        queryset.update(permission_level=2)
    make_level2.short_description = "设为2级权限(管理员)"
    
    def make_level3(self, request, queryset):
        queryset.update(permission_level=3)
    make_level3.short_description = "设为3级权限(普通用户)"
    
    def has_change_permission(self, request, obj=None):
        if obj and request.user.permission_level > obj.permission_level:
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        if obj and request.user.permission_level > obj.permission_level:
            return False
        return super().has_delete_permission(request, obj)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(permission_level__gte=request.user.permission_level)
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            # 非超级管理员不能修改权限级别
            fieldsets[1][1]['fields'] = tuple(
                f for f in fieldsets[1][1]['fields'] 
                if f != 'permission_level'
            )
        return fieldsets
