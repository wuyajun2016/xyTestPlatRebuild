from django.db import models
from django.contrib.auth.models import User


# 扩展下django原生的用户表auth_user
class UserExt(models.Model):
    POSITION = (
        (0, 'Android端'),
        (1, 'IOS端'),
        (2, 'Test端'),
        (3, 'Web端'),
        (4, '服务端'),
    )
    nickname = models.CharField(blank=True, max_length=15, verbose_name='昵称')
    sex = models.IntegerField(blank=True, default=1, verbose_name='性别')
    phone = models.CharField(blank=True, max_length=11, verbose_name='手机号')
    new_email = models.EmailField(blank=True, verbose_name='邮箱')
    position = models.CharField(blank=True, choices=POSITION, max_length=1, verbose_name="所属端")
    remarks = models.CharField(blank=True, max_length=150, verbose_name='备注')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pic = models.ImageField(upload_to='img', verbose_name='头像', blank=True)

    class Meta:
        ordering = ['id']
        verbose_name = '用户扩展'
        verbose_name_plural = verbose_name
