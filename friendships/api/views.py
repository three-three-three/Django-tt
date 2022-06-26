from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    # 我们希望 POST /api/friendship/1/follow 是去 follow user_id=1 的用户
    # 因此这里 queryset 需要是 User.objects.all()
    # 如果是 Friendship.objects.all 的话就会出现 404 Not Found
    # 因为 detail=True 的 actions 会默认先去调用 get_object() 也就是
    # queryset.filter(pk=1) 查询一下这个 object 在不在
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()
    '''
    detail: 声明该action的路径是否与单一资源对应，及是否是xxx/<pk>/action方法名/
    True 表示路径格式是xxx/<pk>/action方法名/
    False 表示路径格式是xxx/action方法名/
    detail=True 说明是在某一个具体的user上操作
    '''

    # api/friendships/ 页面的显示
    def list(self, request):
        return Response({'message': 'this is friendships home page'})

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # Friendship Model 里面设定了to_user为外键，就会有一个to_user_id,
        # 和直接设定user（User），然后就会有一个user_id 同理
        # to_uer 和 user 是同一种东西
        # GET /api/friendships/1/followers 去查看用户1的followers
        # 在Friendship Model中定义了ordering，order_by可以删掉
        friendships = Friendship.objects.filter(to_user_id=pk)  # .order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response(
            {'followers': serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk)  # .order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response(
            {'followings': serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # POST /api/friendships/<pk>/follow follow<pk>用户

        # follow_user = self.get_object() 以pk为id去取user，取得到就会返回
        # 取不到就会返回404，和serializer validate里面的一个逻辑功能相同
        follow_user = self.get_object()

        # 特殊判断重复follow的情况（比如前端猛点好多少次follow)
        # 静默处理，不报错，因为这类重复操作因为网络延迟的原因会比较多，没必要当做错误处理
        # 也可以在serializer的raise exception里报错，写了注释可以看一看
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)
        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': follow_user.id,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            FollowingSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # pk不存在时会返回错误
        self.get_object()
        # 注意 pk 的类型是 str，所以要做类型转换
        # 或者把unfollow_user取出来
        # unfollow_user = self.get_object()
        # if request.user.id == unfollowed_user.id:
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#delete
        # Queryset 的 delete 操作返回两个值，一个是删了多少数据，一个是具体每种类型删了多少
        # 为什么会出现多种类型数据的删除？因为可能因为 foreign key 设置了 cascade 出现级联
        # 删除，也就是比如 A model 的某个属性是 B model 的 foreign key，并且设置了
        # on_delete=models.CASCADE, 那么当 B 的某个数据被删除的时候，A 中的关联也会被删除。
        # 所以 CASCADE 是很危险的，我们一般最好不要用，而是用 on_delete=models.SET_NULL (Model里的设置)
        # 取而代之，这样至少可以避免误删除操作带来的多米诺效应。
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        return Response({'success': True, 'deleted': deleted})
