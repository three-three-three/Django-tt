from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from tweets.models import Tweet

'''
防止重名，把Django的TestCase改名成DjangoTestCase
继承了DjangoTestCase，自己写了一个TestCase
'''


class TestCase(DjangoTestCase):

    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client

    # 把password和email设置成了非必填
    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'
        # 不能写成 User.objects.create()
        # 因为 password 需要被加密, username 和 email 需要进行一些 normalize 处理
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user, content=content)


'''
在进行单元测试时，不同的app有相同的步骤，比如测试accounts和tweets都需要创建用户
所以把这些方法单独放出来
'''
