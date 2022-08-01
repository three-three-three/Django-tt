from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet

'''
[DEBUG日志]：用不到的import要删掉，之前保留了import TweetSerializer，
单元测试过不了，显示tweets/api/serializers里无法import CommentSerializer
后来删掉import TweetSerializer之后就跑通了
怀疑相互查找serializer形成了死循环
'''


class CommentSerializer(serializers.ModelSerializer):
    # 如果不加这个user = UserSerializer(),fields里的user只有id
    user = UserSerializerForComment()
    # tweet = TweetSerializer()
    '''
    只需要返回tweet_id，因为comment是基于某一个tweet,
    应该把comment加进tweet，而不是tweet加入comment
    '''

    class Meta:
        model = Comment
        fields = ('id',
                  'tweet_id',
                  'user',
                  'content',
                  'created_at',
                  'updated_at',)


class CommentSerializerForCreate(serializers.ModelSerializer):
    # 这两项必须手动添加
    # 因为默认 ModelSerializer 里只会自动包含 user 和 tweet 而不是 user_id 和 tweet_id
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('content', 'tweet_id', 'user_id')

    def validate(self, data):
        tweet_id = data['tweet_id']
        if not Tweet.objects.filter(id=tweet_id).exists():
            raise ValidationError({'message': 'tweet does not exist'})
        # 必须 return validated data
        # 也就是验证过之后，进行过处理的（当然也可以不做处理）输入数据
        return data

    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data['user_id'],
            tweet_id=validated_data['tweet_id'],
            content=validated_data['content'],
        )


class CommentSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content', 'tweet_id', 'user_id')

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        # update 方法要求 return 修改后的 instance 作为返回值
        return instance
