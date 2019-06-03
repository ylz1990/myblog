from django.db import models

class ModelBase(models.Model):
    """"""
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    is_delete = models.BooleanField(default=False,verbose_name='逻辑删除')
    # 只用于继承用的
    class Meta:
        abstract = True


