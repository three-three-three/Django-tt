from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from accounts.api.serializers import UserSerializer, LoginSerializer, SignupSerializer
from django.contrib.auth import (
    logout as django_logout,
    login as django_login,
    authenticate as django_authenticate,
)


class UserViewSet(viewsets.ModelViewSet):
    # 这里直接继承了ModelViewSet，Django 默认了 增删查改 都可以做
    # 但是不是所有的接口都要做这些操作，因为不是所有人都是admin权限，所以一般不用ModelViewSet
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)


'''没有这个permission就打不开这个localhost/api/user'''


class AccountViewSet(viewsets.ViewSet):
    '''界面出现用户输入用户名和密码'''
    serializer_class = SignupSerializer
    permission_classes = (AllowAny,)

    """我只能用get去请求"""

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        """
        查看用户当前的登录状态和具体信息
        """
        data = {
            'has_logged_in': request.user.is_authenticated,
            'ip': request.META['REMOTE_ADDR']}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def login(self, request):
        """
        默认的 username 是 admin, password 也是 admin，

        """
        # 把用户的输入传给LoginSerializer检查
        # request.data就是用户请求[POST]的数据
        '''在开发中，凡是要检测用户输入，都是把request.data传到serializer中
        ，然后调用is_valid()，错误会放在.errors中'''
        # serializers 相当于经过处理后的data
        serializer = LoginSerializer(data=request.data)
        '''输入不合法，返回400 Bad Request'''
        '''errors也是django serializer自带的，带有错误信息'''
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)

        '''validation is ok, login'''
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        '''User不存在就无法登录，抛出异常'''
        # 这一段移到serializer里的validate了，
        '''if not User.objects.filter(username=username).exists():
            return Response({
                "success": False,
                "message": "User does not exit",
            }, status=400)'''

        # authenticate 是 django 自带的一个函数，会在验证用户名和密码后返回一个user对象
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "username and password does not match",
            }, status=400)

        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        """
        登出当前用户
        """
        django_logout(request)
        return Response({"success": True})

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        """
        使用 username, email, password 进行注册
        """
        '''对应 serializers 里面的 class meta限制了用户的输入信息'''
        # 不太优雅的写法
        # username = request.data.get('username')
        # if not username:
        #     return Response("username required", status=400)
        # password = request.data.get('password')
        # if not password:
        #     return Response("password required", status=400)
        # if User.objects.filter(username=username).exists():
        #     return Response("password required", status=400)
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)

        # save() 保存到数据库
        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status=201)
