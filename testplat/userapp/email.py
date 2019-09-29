import random, string
import django.utils.timezone
from .models import UserValid
import datetime
from testplat.utils.tasks import *
from django.core.cache import cache
from django.conf import settings


def send_email(user):
    data = {}
    data['success'] = False
    data['message'] = ''
    try:
        code = ''.join(random.sample(string.digits + string.ascii_letters, 6))

        # 检查短时间内是否有生成过验证码
        acc = UserValid.objects.filter(user=user.id)
        # 创建验证码时间
        cur_time = datetime.datetime.now()
        # 如果存在验证码就判断是否一分钟内发过验证码，否则就新建一个
        if len(acc) > 0:
            # 两个datetime相减，得到datetime.timedelta类型
            td = django.utils.timezone.now() - acc[len(acc)-1].valid_time
            if td.total_seconds() < 60:
                data['message'] = '1分钟内发送过一次验证码'
                return data
            else:
                # 将验证码写入数据库
                UserValid.objects.filter(user=user.id).update(valid_time=cur_time, valid_code=code)
                cache.set('validateCode_' + str(user.id), {"validate_code": code, "validate_time": cur_time},
                          settings.VALIDATE_CACHE_TIME)
        else:
            # 写入数据库
            UserValid.objects.create(user=user, valid_time=datetime.datetime.now(), valid_code=code)
            cache.set('validateCode_' + str(user.id), {"validate_code": code, "validate_time": cur_time},
                      settings.VALIDATE_CACHE_TIME)

        sendmail.delay(user.email, code)
        # test.delay(user.email)  # 测试一波异步

        data['success'] = True
        data['message'] = '发送成功'
    except Exception as e:
        data['success'] = False
        data['message'] = str(e)
        return data

    return data
