from django.db import models
from django.contrib.auth.models import User

'''
为什么要设一个 related_name='following_friendship_set' ，否则会报错？
因为Django有一个反查机制，比如 user.tweet_set 等价于 Tweet.objects.filter(user=user)
如果不重名，user.friendship_set就对应了两个属性
'''


class Friendship(models.Model):
    # 引用了User，所以是外键
    # from_user to_user  谁关注了谁
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friendship_set',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 在 views.py 里面进行关联查找
        index_together = (
            # 获取我关注的所有人，按照关注时间排序
            ('from_user_id', 'created_at'),
            # 获得关注我的所有人，按照关注时间排序
            ('to_user_id', 'created_at'),
        )
        # 在数据库层面严格保证好友关系不会重复
        unique_together = (('from_user_id', 'to_user_id'),)
        ordering = ('-created_at',)

    def __str__(self):
        return '{} followed {}'.format(self.from_user_id, self.to_user_id)
