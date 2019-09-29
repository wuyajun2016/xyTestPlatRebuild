from django.core.cache import cache
from django.conf import settings
from userapp.models import UserValid  # 不知道部署到uwsgi行不行???
import logging

logger = logging.getLogger(__name__)


def first(key, timeout):
    def second(func):
        def third(*args, **kwargs):
            if key+'_'+str(args[0].id) in cache:
                data = cache.get(key+'_'+str(args[0].id))
                logger.debug('存在缓存%s' % data)
            else:
                logger.debug('不存在缓存...')
                data = func(*args, **kwargs)
                if data.get('validate_code') is not None:
                    cache.set(key+'_'+str(data.pop('user_id')), data, timeout)
                else:
                    data = None
            return data
        return third
    return second


@first('validateCode', settings.VALIDATE_CACHE_TIME)
def get_validate_code(user):
    result = UserValid.objects.filter(user=user.id)
    if result.exists():  # 判断验证码是否生成过了
        res = UserValid.objects.get(user=user.id)
        return {"validate_code": res.valid_code, "validate_time": res.valid_time, "user_id": user.id}
    return {"validate_code": None, "user_id": user.id}


