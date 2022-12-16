# -*- encoding: utf-8 -*-
"""
@File Name      :   base.py    
@Create Time    :   2022/4/4 15:50
@Description    :   
@Version        :   
@License        :   MIT
@Author         :   diklios
@Contact Email  :   diklios5768@gmail.com
@Github         :   https://github.com/diklios5768
@Blog           :   
@Motto          :   All our science, measured against reality, is primitive and childlike - and yet it is the most precious thing we have.
"""
__auth__ = 'diklios'

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist


def handle_object_does_not_exist(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ObjectDoesNotExist:
            return False

    return wrapper


class StatusChoices(models.IntegerChoices):
    # 如果没有提供元组，或者最后一项不是（惰性）字符串，label是从成员名自动生成。
    STATUS_NORMAL = 1, _('正常')
    STATUS_DELETE = 0, _('删除')
    STATUS_TRASH = -1, _('回收站中删除')


class BaseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=1)

    def get(self, *args, **kwargs):
        try:
            return super().get(*args, **kwargs)
        except ObjectDoesNotExist:
            return None
        # except MultipleObjectsReturned:
        #     return False


class Base(models.Model):
    objects = BaseManager()
    # 默认设置了主键id，所以基本除了外键不需要进行配置primary key
    # 所有字段默认不允许为空
    # 配置了unique的字段不需要再配置db_index索引
    # 可以通过db_column字段指定列名

    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_TRASH = -1
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
        (STATUS_TRASH, '回收站中删除')
    )
    # 注意：auto_now、auto_now_add和default三个会互相排斥
    # auto_now_add，默认值为false，设置为true时，会在model对象第一次被创建时，将字段的值设置为创建时的时间，以后修改对象时，字段的值不会再更新。
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # auto_now，默认值为false，设置为true时，每次执行save操作时，将其值设置为当前时间，并且每次修改model，都会自动更新。
    modified_time = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    # choice要显示完整的内容，需要调用Model.get_FOO_display()
    # 参考https://docs.djangoproject.com/zh-hans/3.2/ref/models/instances/#django.db.models.Model.get_FOO_display
    # 即使不在choices中也是可以成功的，只是get_FOO_display()显示的还是自身值
    status = models.IntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name='状态')
    remarks = models.CharField(max_length=1000, null=True, blank=True, default=None, verbose_name='备注')
    # todo:重写一个JSONEncoder，能够处理时间相关或者其他常用对象
    remarks_json = models.JSONField(null=True, blank=True, default=dict, verbose_name='json类型的额外信息')

    # Meta用于配置Model的一些属性
    # 更多模型可选参数详见：https://docs.djangoproject.com/zh-hans/3.2/ref/models/options/
    class Meta:
        """
        db_table:数据库表名
        ordering：这是一个字符串和／或查询表达式的元组或列表。每一个字符串都是一个字段名，前面有一个可选的“-”字头，表示降序。没有前缀“-”的字段将按升序排列。使用字符串“?”来随机排序。
        verbose_name和verbose_name_plural：阅读友好的单复数名，此属性不会被继承
        abstract：是否是抽象类，设置为抽象类在数据库中不会构建，这个属性不会被继承
        Django在安装Meta属性前，对抽象基类的Meta做了一个调整——设置abstract = False。这意味着抽象基类的子类不会自动地变成抽象类
        为了继承一个抽象基类创建另一个抽象基类，你需要在子类上显式地设置abstract = True。
        """
        abstract = True
        # 必须要指定表的 app_label，如果不指定则会创建到 default 中配置的数据库名下
        # 注意app_label是app_name，不是database_name，虽然大部分情况下是一样的

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    def to_dict(self, fields=None, exclude=None):
        data = {}
        for field in self._meta.concrete_fields + self._meta.many_to_many:
            value = field.value_from_object(self)
            if fields and field.name not in fields:
                continue
            if exclude and field.name in exclude:
                continue
            if isinstance(field, models.ManyToManyField):
                value = [i.id for i in value] if self.pk else None
            if isinstance(field, models.DateTimeField):
                value = value.strftime('%Y-%m-%d %H:%M:%S') if value else None
            data[field.name] = value
        return data
