from django.contrib.auth.models import User
from rest_framework import serializers, exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserSerializerForTweet(serializers.ModelSerializer):
    # 看tweets时不显示邮箱，也不显示用户id
    class Meta:
        model = User
        fields = ('id', 'username')


class UserSerializerForFriendship(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


# 帮助我们去查看用户有没有输入username和password
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    # 检查用户是否存在
    def validate(self, data):
        if not User.objects.filter(username=data['username']).exists():
            raise exceptions.ValidationError({'username': 'User does not exists'})
        return data


class SignupSerializer(serializers.ModelSerializer):
    # 括号里限制输入长度
    # ModelSerializer要求，前面定义的username、password、email等要在Meta fields里面
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    # 先validate, 再create

    def validate(self, data):

        # 大小写不敏感
        if User.objects.filter(username=data['username'].lower()).exists():
            # 检查有没有重复，有重复就抛出一个异常
            raise exceptions.ValidationError({
                'message': 'This email address has been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This email address has been occupied.'
            })

        return data

    def create(self, validated_data):
        # .lower()表示在存用户输入信息的时候就存小写
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user
