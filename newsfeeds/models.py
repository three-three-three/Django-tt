from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet


class NewsFeed(models.Model):
    # 注意这个 user 不是存储谁发了这条 tweet，而是谁可以看到这条 tweet
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    # 虽然tweet里面已经有created_at，但是不能依靠Foreign Key里面的时间去排序
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        unique_together = (('user', 'tweet'),)
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'
