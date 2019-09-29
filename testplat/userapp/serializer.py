from rest_framework import serializers
from django.contrib.auth import authenticate
from datetime import datetime
from django.contrib.auth.models import User
from .models import UserExt
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator


# 用户登录
class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, max_length=100)  # 这里定义下，不然User会去做一些自带的校验
    password = serializers.CharField(required=True, max_length=100, write_only=True)  # 这里定义下，不然User会去做一些自带的校验
    code = serializers.SerializerMethodField()
    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段
    is_super = serializers.IntegerField(read_only=True)  # 增加is_super字段，view序列化时候会传入这个值
    login_time = serializers.SerializerMethodField()
    user_position = serializers.SerializerMethodField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                raise serializers.ValidationError('用户名或密码错误', code='authorization')
        else:
            raise serializers.ValidationError('必须同时输入账号和密码', code='authorization')
        attrs['user'] = user
        return attrs

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'code', 'token', 'is_super', 'login_time', 'user_position')

    def get_code(self, obj):
        return 0

    def get_login_time(self, obj):
        now_time = datetime.now()
        login_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
        return login_time

    def get_user_position(self, obj):
        userid = obj.get("id")
        res = ''
        if UserExt.objects.filter(user=userid).exists():
            res = UserExt.objects.get(user=userid).position
            # print(res.get_position_display())  # get_position_display()方法可以返回choice里面键对应的值
        return res


# 用户详情
class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('password',)


# 用户注册
class UserRegisterSerializer(serializers.ModelSerializer):
    # 这里定义下，改变下用户已经存在时候的提示以及用户名为空/用户名长度提示
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户名已存在")],
                                     error_messages={'blank': '用户名不能为空', 'max_length': '用户名最大长度为20'}, max_length=20)
    # 这里定义下，不让密码响应给用户
    password = serializers.CharField(style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password',)


# 用户修改密码(登录后修改密码)
class UserSetPasswordSerializer(serializers.ModelSerializer):
    # 这里定义下，不然User会去做一些自带的校验
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False)
    # 这里定义下，不然User会去做一些自带的校验
    password = serializers.CharField(style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True)
    # 这里定义下，因为需要一个newpassword入参
    # 因为在view中不会将序列后的值存入数据库，所以这里随便定义一个新字段，尽管数据库中不存在该字段(view中只是做下校验)
    newpassword = serializers.CharField(style={'input_type': 'password'}, help_text="新密码", label="新密码", write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # del attrs["newpassword"]

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                raise serializers.ValidationError('原密码错误,请重试', code='authorization')
        else:
            raise serializers.ValidationError('必须同时输入用户名和密码', code='authorization')

        attrs['user'] = user
        return attrs

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'newpassword',)


# 用户修改密码（未登录时候，发送邮件修改密码）
class UserSetPasswordNotLoginSerializer(serializers.ModelSerializer):
    # 这里定义下，不然User会去做一些自带的校验
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     error_messages={'blank': '用户名不能为空', 'max_length': '用户名最大长度为20'}, max_length=20)
    # 这里定义下，不然User会去做一些自带的校验
    password = serializers.CharField(style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True)
    valid_code = serializers.CharField(max_length=24, help_text="验证码", label="验证码", write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password", "valid_code")


# 验证码
class UserValidSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     error_messages={'blank': '用户名不能为空', 'max_length': '用户名最大长度为20'}, max_length=20)
    valid_code = serializers.CharField(max_length=24, help_text="验证码", label="验证码", read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "valid_code")


# 用户扩展
class UserExtSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserExt
        exclude = ("user", "pic",)


# 用户扩展:上传图片
class UploadImgSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserExt
        fields = ("id", "pic")
