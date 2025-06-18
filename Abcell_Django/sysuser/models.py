# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password


# ✅ 正确：只保留一次定义
class User(AbstractUser):
    # 自定义字段
    avatar = models.ImageField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, verbose_name='电话')
    gender = models.CharField(max_length=20, null=True, verbose_name='性别')

    # 权限级别 (1-3级) → 只保留一次定义
    permission_level = models.IntegerField(
        verbose_name='权限级别',
        choices=((1, '1级权限'), (2, '2级权限'), (3, '3级权限')),
        default=1
    )

    # 使用email作为用户名 → 关键配置
    USERNAME_FIELD = 'email'  # 确保这行存在
    REQUIRED_FIELDS = ['username']  # 必须包含username字段

    # 覆盖AbstractUser的email字段，添加unique约束 → 只定义一次
    email = models.EmailField(unique=True, verbose_name='邮箱')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        db_table = 'sysuser_user'

    # 权限级别 (1-3级)
    # permission_level = models.IntegerField(
    #     verbose_name='权限级别',
    #     choices=(
    #         (1, '1级权限'),
    #         (2, '2级权限'),
    #         (3, '3级权限'),
    #     ),
    #     default=1
    # )

    def save(self, *args, **kwargs):
        # 确保密码被保存（即使明文也保存）
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            # 如果要明文存储，直接保存即可
            # 如果要加密存储，使用下面这行：
            # self.password = make_password(self.password)
            pass
        super().save(*args, **kwargs)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='sysuser_user_set',  # 添加唯一反向关联名
        related_query_name='sysuser_user'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='sysuser_user_set',  # 添加唯一反向关联名
        related_query_name='sysuser_user'
    )

    # 覆盖AbstractUser的email字段，添加unique约束
    email = models.EmailField(unique=True, verbose_name='邮箱')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        db_table = 'sysuser_user'  # 确保表名正确

    # 权限级别 (1-3级)
    # permission_level = models.IntegerField(
    #     verbose_name='权限级别',
    #     choices=(
    #         (1, '1级权限'),
    #         (2, '2级权限'),
    #         (3, '3级权限'),
    #     ),
    #     default=1
    # )

    def save(self, *args, **kwargs):
        # 确保取消注释并启用密码哈希
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)  # 取消这行注释
        super().save(*args, **kwargs)
    
    def get_permission_level_display(self):
        return dict(self._meta.get_field('permission_level').choices).get(self.permission_level, '未知')
    get_permission_level_display.short_description = '权限级别'


# 细胞类型模型
class CellType(models.Model):
    """细胞类型管理"""

    class Meta:
        verbose_name = '细胞类型'
        verbose_name_plural = '细胞类型管理'

    # 细胞类型名称字段
    name = models.CharField(max_length=100, verbose_name='类型名称')
    # 细胞类别字段，有预设选项
    category = models.CharField(
        max_length=50,
        verbose_name='细胞类别',
        choices=(
            ('primary', '原代细胞'),
            ('human', '人'),
            ('rat', '大鼠'),
            ('mouse', '小鼠'),
            ('adherent', '贴壁细胞'),
            ('suspension', '悬浮细胞'),
        )
    )
    # 细胞类型描述字段，可选
    description = models.TextField(verbose_name='描述', blank=True)
    # 创建时间字段，自动记录创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间字段，自动记录更新时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name  # 返回细胞类型名称作为字符串表示


# 冰柜模型
class Freezer(models.Model):
    """冰柜表"""

    class Meta:
        verbose_name = '冰柜'
        verbose_name_plural = '冰柜管理'

    # 冰柜名称字段
    name = models.CharField(max_length=100, verbose_name='冰柜名称')
    # 冰柜编号字段，唯一
    number = models.CharField(max_length=50, verbose_name='冰柜编号', unique=True)
    # 冰柜位置字段，可选
    location = models.CharField(max_length=200, verbose_name='位置', blank=True)
    # 冰柜描述字段，可选
    description = models.TextField(verbose_name='描述', blank=True)
    # 创建时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间字段
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f"{self.name} ({self.number})"  # 返回冰柜名称和编号的组合


# 冰柜层级模型，表示冰柜内的层级结构
class Level(models.Model):
    """层级表"""

    class Meta:
        verbose_name = '层级'  # 单数显示名称
        verbose_name_plural = '层级管理'  # 复数显示名称
        ordering = ['freezer', 'number']  # 默认排序规则
        unique_together = [['freezer', 'number']]

    # 层级名称字段
    name = models.CharField(max_length=100, verbose_name='层级名称')
    # 层级编号字段
    number = models.CharField(max_length=50, verbose_name='层级编号')
    # 外键关联到冰柜模型，级联删除
    freezer = models.ForeignKey(
        Freezer,
        on_delete=models.CASCADE,  # 冰柜删除时层级也删除
        related_name='levels',  # 反向关联名称
        verbose_name='所属冰柜'
    )
    # 层级描述字段，可选
    description = models.TextField(verbose_name='描述', blank=True)
    # 创建时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间字段
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')


    def __str__(self):
        return f"{self.freezer} - 层级 {self.number} ({self.name})"


# 列模型，表示层级中的列结构
class Column(models.Model):
    """列表"""

    class Meta:
        verbose_name = '列'
        verbose_name_plural = '列管理'
        ordering = ['level', 'number']  # 按层级和编号排序
        unique_together = [['level', 'number']]  # 同一 level 下 number 唯一

    # 列名称字段
    name = models.CharField(max_length=100, verbose_name='列名称')
    # 列编号字段
    number = models.CharField(max_length=50, verbose_name='列编号')
    # 外键关联到层级模型
    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name='columns',
        verbose_name='所属层级'
    )
    # 列描述字段，可选
    description = models.TextField(verbose_name='描述', blank=True)
    # 创建时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间字段
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')


    def __str__(self):
        return f"{self.level} - 列 {self.number} ({self.name})"


# 抽屉模型，表示列中的抽屉结构
class Drawer(models.Model):
    """抽屉表"""

    class Meta:
        verbose_name = '抽屉'
        verbose_name_plural = '抽屉管理'
        ordering = ['column', 'number']  # 按列和编号排序
        unique_together = [['column', 'number']]

        # 抽屉名称字段
    name = models.CharField(max_length=100, verbose_name='抽屉名称')
    # 抽屉编号字段
    number = models.CharField(max_length=50, verbose_name='抽屉编号')
    # 外键关联到列模型
    column = models.ForeignKey(
        Column,
        on_delete=models.CASCADE,
        related_name='drawers',
        verbose_name='所属列'
    )
    # 抽屉描述字段，可选
    description = models.TextField(verbose_name='描述', blank=True)
    # 创建时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间字段
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')


    def __str__(self):
        return f"{self.column} - 抽屉 {self.number} ({self.name})"


# 盒子模型，表示抽屉中的盒子结构
class Box(models.Model):
    """盒子表"""

    class Meta:
        verbose_name = '盒子'
        verbose_name_plural = '盒子管理'
        ordering = ['drawer', 'number']  # 按抽屉和编号排序
        unique_together = [['drawer', 'number']]

        # 盒子名称字段
    name = models.CharField(max_length=100, verbose_name='盒子名称')
    # 盒子编号字段
    number = models.CharField(max_length=50, verbose_name='盒子编号')
    # 外键关联到抽屉模型
    drawer = models.ForeignKey(
        Drawer,
        on_delete=models.CASCADE,
        related_name='boxes',
        verbose_name='所属抽屉'
    )
    # 盒子描述字段，可选
    description = models.TextField(verbose_name='描述', blank=True)
    # 创建时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间字段
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')


    def __str__(self):
        return f"{self.drawer} - 盒子 {self.number} ({self.name})"


# 格子模型，表示盒子中的格子结构
class Cell(models.Model):
    """格子表"""

    class Meta:
        verbose_name = '格子'
        verbose_name_plural = '格子管理'
        ordering = ['box', 'row_num', 'col_num']  # 按盒子、行号和列号排序
        unique_together = [['box', 'number']]

        # 格子名称字段
    name = models.CharField(max_length=100, verbose_name='格子名称')
    # 格子编号字段
    number = models.CharField(max_length=50, verbose_name='格子编号')
    # 外键关联到盒子模型
    box = models.ForeignKey(
        Box,
        on_delete=models.CASCADE,
        related_name='cells',
        verbose_name='所属盒子'
    )
    # 行号字段
    row_num = models.IntegerField(verbose_name='行号')
    # 列号字段
    col_num = models.IntegerField(verbose_name='列号')
    # 是否占用字段，默认未占用
    is_occupied = models.BooleanField(default=False, verbose_name='是否占用')
    # 格子描述字段，可选
    description = models.TextField(verbose_name='描述', blank=True)
    # 创建时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间字段
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')


    def __str__(self):
        return f"{self.box} - 格子 {self.row_num}-{self.col_num} ({self.name})"


# 细胞库存模型，记录细胞存储信息
class CellInventory(models.Model):
    """细胞出入库管理"""

    class Meta:
        verbose_name = '细胞库存'
        verbose_name_plural = '细胞出入库管理'
        ordering = ['-entry_time']  # 按入库时间倒序排列

    # 细胞唯一ID字段
    cell_id = models.CharField(max_length=100, unique=True, verbose_name='细胞ID')
    # 外键关联到细胞类型模型
    cell_type = models.ForeignKey(
        CellType,
        on_delete=models.PROTECT,  # 保护模式，防止误删
        verbose_name='细胞类型'
    )
    # 外键关联到格子模型，表示存储位置
    storage_location = models.ForeignKey(
        Cell,
        on_delete=models.PROTECT,
        verbose_name='存放位置'
    )
    # 外键关联到用户模型，表示录入人
    entry_person = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name='cell_entries',
        verbose_name='录入人'
    )
    # 入库时间字段，自动记录
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name='录入时间')
    # 修改时间字段，自动更新
    modify_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    # 细胞数量字段，默认为1
    quantity = models.IntegerField(verbose_name='数量', default=1)
    # 细胞状态字段，有预设选项
    status = models.CharField(
        max_length=20,
        verbose_name='状态',
        choices=(
            ('in_stock', '在库'),
            ('out_stock', '出库'),
            ('destroyed', '已销毁'),
        ),
        default='in_stock'  # 默认状态为在库
    )
    # 备注字段，可选
    notes = models.TextField(verbose_name='备注', blank=True)

    def __str__(self):
        return f"{self.cell_id} - {self.cell_type.name}"


# 细胞出库记录模型
class CellOutRecord(models.Model):
    """细胞出库记录"""

    class Meta:
        verbose_name = '细胞出库记录'
        verbose_name_plural = '细胞出库记录'
        ordering = ['-out_time']  # 按出库时间倒序排列

    # 外键关联到细胞库存模型
    cell_inventory = models.ForeignKey(
        CellInventory,
        on_delete=models.PROTECT,
        verbose_name='细胞库存'
    )
    # 外键关联到用户模型，表示出库人
    out_person = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cell_outs',
        verbose_name='出库人'
    )
    # 出库时间字段，自动记录
    out_time = models.DateTimeField(auto_now_add=True, verbose_name='出库时间')
    # 用途字段
    purpose = models.TextField(verbose_name='用途')
    # 接收人字段
    receiver = models.CharField(max_length=100, verbose_name='接收人')
    # 备注字段，可选
    notes = models.TextField(verbose_name='备注', blank=True)

    def __str__(self):
        return f"{self.cell_inventory.cell_id} 出库记录"


User = get_user_model()

class ActivityLog(models.Model):
    ACTIVITY_TYPES = (
        ('primary', '主要'),
        ('success', '成功'),
        ('warning', '警告'),
        ('danger', '危险'),
        ('info', '信息')
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPES, default='info')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
