from django.db import models
from .core import VModel, VTree
from django.contrib.auth.hashers import check_password


class Role(VModel):
    duty = models.TextField(null=True, verbose_name='职责描述')

    class Meta:
        verbose_name = '角色'


class Account(VModel):
    """账户核心信息"""
    username = models.CharField(max_length=255, null=True, unique=True, verbose_name='账号')
    password = models.CharField(max_length=255, null=True, verbose_name='密码')
    email = models.CharField(max_length=255, null=True, unique=True, verbose_name='邮箱')
    """权限"""
    is_admin = models.BooleanField(default=False, verbose_name='超级管理员')
    roles = models.ManyToManyField(Role)
    """密码找回"""
    is_active = models.BooleanField(default=False, verbose_name='激活状态')
    token = models.CharField(max_length=255, null=True, verbose_name='Token')

    def is_auth(self, password):
        return password == self.token or check_password(password, self.password)

    class Meta:
        verbose_name = '账户信息'


class Menu(VTree):
    scope = models.CharField(max_length=100, null=True, verbose_name='域')
    path = models.CharField(max_length=255, null=True, verbose_name='地址')
    roles = models.ManyToManyField(Role)
    is_admin = models.BooleanField(null=True, default=False, verbose_name='超管权限')
    is_auth = models.BooleanField(null=True, default=False, verbose_name='需要登录')

    class Meta:
        verbose_name = '菜单'
        unique_together = ('scope', 'path')


class AbstractUser(VModel):
    account = models.OneToOneField(Account, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True
