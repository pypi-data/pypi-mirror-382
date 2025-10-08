from ..models.core import VTree, VModel
from django.db import models


class IndicatorSet(VTree):
    name = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = '指标集'


class Indicator(VModel):
    set = models.ForeignKey(IndicatorSet, null=True, on_delete=models.CASCADE, verbose_name='指标集')
    domain = models.CharField(max_length=100, verbose_name='domain', null=True)
    category = models.CharField(max_length=100, verbose_name='category', null=True)
    name = models.CharField(max_length=100, verbose_name='名称', null=True)
    frequency = models.CharField(max_length=100, verbose_name='频度', null=True)
    scope = models.CharField(max_length=100, verbose_name='尺度', null=True)
    unit = models.CharField(max_length=100, verbose_name='单位', null=True)
    object_id = models.CharField(max_length=100, verbose_name='ObjectId', null=True)
    file = models.FileField(null=True, verbose_name='数据文件')

    class Meta:
        verbose_name = '指标项'


class Location(VModel):
    scope = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100, null=True)
    name_cn = models.CharField(max_length=100, null=True)
    name_en = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = '指标集'
