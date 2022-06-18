from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now


class Tweet(models.Model):
    # help_text可以在admin界面显示
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who posts this tweet',
    )
    content = models.CharField(max_length=255)
    # auto_now_add 当我add的时候，自动计算当前时间是什么
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now 每次更新时都会更新时间
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def hours_to_now(self):
        # datetime.now 不带时区信息，需要增加上 utc 的时区信息
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        # 这里是你执行 print(tweet instance) 的时候会显示的内容
        return f'{self.created_at} {self.user}: {self.content}'

# 定义完model之后要修改数据库--migrate
# 1. python manage.py makemigartions 前提条件是tweets里面已经有一个migrations文件夹
# 如果没有migrations文件夹，python manage.py makemigartions tweets （在后面加上app的名字）
