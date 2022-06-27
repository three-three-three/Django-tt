from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet


# 注意要加 '/' 结尾，要不然会产生 301 redirect
TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'


class TweetApiTests(TestCase):

    def setUp(self):
        # APIClient()是测试时执行get post请求的人
        # user2是一个单纯被访问的数据
        # 在testing/testcases里面定义了anonymous_client，
        # 直接在下面调用self.anonymous_client就可以了，不需要再重复声明
        # self.anonymous_client = APIClient()

        self.user1 = self.create_user('user1', 'user1@twitter.com')
        self.tweets1 = [
            self.create_tweet(self.user1)
            for i in range(3)
        ]
        self.user1_client = APIClient()
        # 用user1的信息登录
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@twitter.com')
        self.tweets2 = [
            self.create_tweet(self.user2)
            for i in range(2)
        ]

    def test_list_api(self):
        # 必须带 user_id
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # 正常 request
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 3)
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['tweets']), 2)
        # 检测排序是按照新创建的在前面的顺序来的
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)

    def test_create_api(self):
        # 必须登录
        response = self.anonymous_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 403)

        # 必须带 content
        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400)
        # content 不能太短
        response = self.user1_client.post(TWEET_CREATE_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)
        # content 不能太长
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': '0' * 141
        })
        self.assertEqual(response.status_code, 400)

        # 正常发帖
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is my first tweet!'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], self.user1.username)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

        '''
        Debug日志 [2022/6/19]：
        第71行，一开始是self.assertEqual(response.data['user']['id'], self.user1.id)
        测试时出现Key Error, '[id]' 说明查不到id
        response来自tweets/api/views.py/def create，return Response(TweetSerializer(tweet).data, status=201)
        返回的是TweetSerializer(tweet).data，于是查看tweets/api/serializers.py/TweetSerializer
        TweetSerializer fields = ('id', 'user', 'created_at', 'content') 这些就是response.data
        response.data['user'] 来自 user = UserSerializerForTweet()
        于是查看accounts/api/serializers UserSerializerForTweet
        发现UserSerializerForTweet的field没有id，只有username
        于是加上id,发现测试可以跑通
        但是UserSerializerForTweet 设计上不能让用户看推文时看到user的id
        于是UserSerializerForTweet的fields还是只保留username
        选择username作为用来assertEqual
        
        [2022/6/26] 还是加上了id
        
        serializer是用来接收传入request.data, 以及处理数据
        1. 序列化,序列化器会把模型对象转换成字典,经过response以后变成json字符串
        e.g.  return Response(TweetSerializer(tweet).data, status=201)
        
        2. 反序列化,把客户端发送过来的数据,经过request以后变成字典,序列化器可以把字典转成模型
        e.g. serializers = TweetCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        
        3. 反序列化,完成数据校验功能
        e.g. # 检查用户是否存在
            def validate(self, data):
        e.g. if not serializers.is_valid():

        '''
