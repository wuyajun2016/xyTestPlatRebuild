from rest_framework import viewsets,mixins
from rest_framework.response import Response
from rest_framework.status import *
from .serializer import *
from rest_framework import permissions
from rest_framework_jwt.settings import api_settings
import logging
from .models import *
from testplat.utils.mypage import ArticlePagination  # 将testplat设置成sourceroot，不知道部署到uwsgi行不行???
from testplat.utils.myCache import get_validate_code
import os, io
from PIL import Image
from django.conf import settings
from .email import send_email

logger = logging.getLogger(__name__)


class UserLoginViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserLoginSerializer
    permission_classes = (permissions.AllowAny,)

    # 把create方法重写下，不去做创建的动作，只是序列化时做下validate以及去掉字段原本带的一些校验
    def create(self, request, *args, **kwargs):
        """
        登录
        :param request:
        :param args:
        :param kwargs:
        :return:
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
            logger.info(user.username+'登录了')
            return Response({'msg': '登录成功', 'data': serializer.data})
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserRegitsterViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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

    def retrieve(self, request, *args, **kwargs):
        """
        用户查询
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'msg': '查询成功', 'data': serializer.data})

    # 重写create，主要就把密码加密下，存入数据库
    def create(self, request, *args, **kwargs):
        """
        用户注册
        :param request:
        :param args:
        :param kwargs:
        :return:
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
            logger.info(username + '注册了账号')
            return Response({"msg": "注册成功", "data": serializer.data}, headers=headers)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


# 用户修改密码（登录后修改）
class UserSetPasswordViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSetPasswordSerializer
    queryset = User.objects.all()

    # 把create方法重写下，不去做创建的动作，只是序列化时做下validate以及去掉字段原本带的一些校验,还有设置下新密码并加密
    def create(self, request, *args, **kwargs):
        """
        登录后，修改用户密码
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.validated_data['user']  # 获取用户实列
            instance.set_password(request.data['newpassword'])
            instance.save()
            serializer = UserSetPasswordSerializer({'username': instance.username, 'id': instance.id})
            return Response({'msg': '密码修改成功', 'data': serializer.data})
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserSetPasswordNotLoginViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSetPasswordNotLoginSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """
         用户修改密码（没有登录时修改-验证校验码/用户名）
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if User.objects.filter(username=serializer.validated_data['username']).exists():  # 1 判断用户是否存在
                user_instance = User.objects.get(username=serializer.validated_data['username'])
                vd_code = get_validate_code(user_instance)
                if vd_code is not None:  # 2 判断验证码是否生成过了
                    if vd_code.get('validate_code') == request.data.get('valid_code'):    # 3 判断前端传递过来的验证码是否和数据库的一致
                        # 两个datetime相减，得到datetime.timedelta类型,可以算出秒数
                        td = datetime.now() - vd_code.get('validate_time')
                        if td.total_seconds() < settings.EXPIRE_TIME:  # 4 没有过期（有效期一天）
                            user_instance.set_password(request.data['password'])
                            user_instance.save()
                            return Response({'msg': '密码修改成功，请重新登录'})
                        else:
                            return Response({'msg': '验证码过期，请重新获取!'})
                    else:
                        return Response({'msg': '验证码错误!'})
                else:
                    return Response({'msg': '验证码错误,请先获取验证码!'})
            else:
                return Response({'msg': '您修改的用户名不存在!'})
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class GetValidCodeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserValidSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        通过发送邮件，获取验证码
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if User.objects.filter(username=serializer.validated_data['username']).exists():  # 1 用户存在
                user_instance = User.objects.get(username=serializer.validated_data['username'])
                if user_instance.email != '':  # 2 该用户的email存在
                    data = send_email(user_instance)
                    return Response({'msg': data.get('message')})
                else:
                    return Response({"msg": "您尚未设置邮箱，请联系管理员"})
            else:
                return Response({"msg": "用户名不存在！"})
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserExtViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                     mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = UserExt.objects.all()
    serializer_class = UserExtSerializer
    pagination_class = ArticlePagination
    lookup_field = 'user'

    def update(self, request, *args, **kwargs):
        """
        用户扩展表的更新
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'msg': 'success', 'data': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """
        用户扩展表的单条查询
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'msg': 'success', 'data': serializer.data})

    def list(self, request, *args, **kwargs):
        """
        用户扩展表的全量查询
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagecount = self.get_paginated_response(serializer.data)
            res = self.get_paginated_response(pagecount.data.get('results'))
            return Response({'msg': 'success', 'data': serializer.data, 'count': res.data.get('count')})

        serializer = self.get_serializer(queryset, many=True)
        return Response({'msg': 'success', 'data': serializer.data})

    def create(self, request, *args, **kwargs):
        """
        用户扩展表的创建
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserExt.objects.filter(user=request.user)
        if user:
            UserExt.objects.filter(user=request.user.pk).update(nickname=request.data.get('nickname'),
                                                                sex=request.data.get('sex'),
                                                                phone=request.data.get('phone'),
                                                                new_email=request.data.get('new_email'),
                                                                remarks=request.data.get('remarks'),
                                                                position=request.data.get('position'),
                                                                user=request.user)
            User.objects.filter(id=request.user.pk).update(email=request.data.get('new_email'))
        else:
            UserExt.objects.create(nickname=request.data.get('nickname'),
                                   sex=request.data.get('sex'),
                                   phone=request.data.get('phone'),
                                   new_email=request.data.get('new_email'),
                                   remarks=request.data.get('remarks'),
                                   position=request.data.get('position'),
                                   user=request.user)
            User.objects.filter(id=request.user.pk).update(email=request.data.get('new_email'))
        return Response({"msg": '修改成功', "data": serializer.data})


class UploadImgViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UploadImgSerializer

    def create(self, request, *args, **kwargs):
        """
        用户扩展中：上传头像
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        files = request.FILES.get('pic')
        req_user = request.user.username
        file_name = req_user + '.' + files.name.split('.')[1]
        dirpath = "{bd}/media/{file_name}".format(bd=settings.BASE_DIR, file_name=file_name)
        # 如果之前上传过头像，就先删除老的头像
        pic_name = os.path.join(settings.BASE_DIR, 'media\\'+req_user)
        for old_img_path in [pic_name + '.png', pic_name + '.jpg', pic_name + '.gif',
                             pic_name + '.jpeg', pic_name + '.bmp']:
            if os.path.exists(old_img_path):
                os.remove(old_img_path)
        # 压缩下图片再存入
        _img = files.read()  # 从内存中读取图片,就是一串二进制
        size = len(_img) / (1024 * 1024)
        image = Image.open(io.BytesIO(_img))  # Image.open无法直接打开_img（这是一串二进制）,需要初始化到io.BytesIO()对象中才能打开
        if size > 1:
            x, y = image.size
            im = image.resize((int(x / 1.73), int(y / 1.73)), Image.ANTIALIAS)  # 等比例压缩 1.73 倍
            im.save(dirpath)
        else:
            image.save(dirpath)
        # 将图片路径更新到当前用户扩展表中
        userext = UserExt.objects.filter(user=request.user)
        if userext:
            userext.update(pic=file_name)  # 直接拿图片名存数据库就够了
            return Response({"msg": "上传成功"})
        else:
            UserExt.objects.create(user=request.user, pic=file_name)
        return Response({"msg": "上传成功"})
