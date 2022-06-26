from django.contrib.auth.models import User

from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    # from_user_id to_user_id 都必须是整数
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        # attrs和data一样，都是字典格式的传入数据，可以换成data
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'You cannot follow yourself.'
            })
        # 这是一个不能重复关注的逻辑，但实际没啥用，因为validate自带的会进行重复操作判断
        # 所以view里面我们还是选择静默处理
        '''if Friendship.objects.filter(
                from_user_id=attrs['from_user_id'],
                to_user_id=attrs['to_user_id'],
        ).exists():
            raise ValidationError({
                'message': 'You have already followed this user.'
            })'''

        # 要关注的人不存在，返回400
        # 写在了view里面的 follow_user = self.get_object()
        '''if not User.objects.filter(id=attrs['to_user_id']).exists():
            raise ValidationError({
                'message': 'You cannot follow a non-exist user.'
            })'''
        return attrs

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return Friendship.objects.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
        )


# 可以通过 source=xxx 指定去访问每个 model instance 的 xxx 方法
# 即 model_instance.xxx 来获得数据
# https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')
    # created_at = serializers.DateTimeField()
    # 可以注释掉，因为Friendship这个model里面本身也定义了created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')
    # created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')
