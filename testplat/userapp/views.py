from rest_framework import viewsets,mixins
from rest_framework.response import Response
from rest_framework.status import *
from .serializer import *
from rest_framework import permissions
from rest_framework_jwt.settings import api_settings
import logging
from .models import User

logger = logging.getLogger(__name__)


class UserLoginViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserLoginSerializer
    permission_classes = (permissions.AllowAny,)

    # 把create方法重写下，不去做创建的动作，只是序列化时做下validate以及去掉字段原本带的一些校验
    def create(self, request, *args, **kwargs):
        """
         功能：登录
         """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            # jwt手动签发token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            user.token = token
            serializer = UserLoginSerializer(
                {'username': user.username, 'id': user.id, 'token': user.token, 'is_super': user.is_superuser})
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors)


class UserRegitsterViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """功能：用户查询"""
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return []
        return [permissions.IsAuthenticated()]

    # 重写下get_serializer_class，让get/x/请求返回用户详情信息，create返回用户部分信息
    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegisterSerializer
        return UserDetailSerializer

    # 重写create，主要就把密码加密下，存入数据库
    def create(self, request, *args, **kwargs):
        """
        功能：用户注册
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data['password']
            username = request.data['username']
            self.perform_create(serializer)  # 入库
            # 加密
            user = User.objects.get(username=username)  # 获取用户对象
            user.set_password(password)
            user.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=HTTP_200_OK, headers=headers)
        return Response(serializer.errors)
