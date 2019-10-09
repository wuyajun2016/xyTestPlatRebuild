# 导入控制返回的JSON格式的类
from rest_framework.renderers import JSONRenderer
import re
import logging
from datetime import datetime
from .myEnum import ResponseEnum

logger = logging.getLogger(__name__)
collect_logger = logging.getLogger("collect")


def statusJudge(data, code):
    """不同状态不同的获取msg方式"""
    if 'ErrorDetail' in str(data):
        # token过期|未登录
        if code == ResponseEnum.un_auth.value:
            return '未授权'
        # 校验错误
        if code == ResponseEnum.params_error.value or code == ResponseEnum.page_not_found.value \
                or code == ResponseEnum.throttle_limit.value:
            msg_result = []
            for result in (re.findall('[\u4e00-\u9fa5]+', str(data))):
                msg_result.append(result)
            return ','.join(msg_result)
        # 服务器内部代码有错误
        if code == ResponseEnum.server_error.value or code == ResponseEnum.insufficient_storage.value:
            return '服务器内部错误'
        collect_logger.info('[{}]未处理的获取msg方式，数据为：{},code为：{}'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data, code))
        return '服务器内部错误，请联系管理员'
    return 'success'


class CustomRenderer(JSONRenderer):
    """重构render方法"""
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context:
            ret = {}
            code = renderer_context.get('response').status_code
            ret['code'] = code
            if 'msg' in data.keys():
                ret['msg'] = data.pop('msg')
            else:
                ret['msg'] = statusJudge(data, code)
            if 'data' in data.keys() and code == 200:
                ret['data'] = data.pop('data')
            if 'count' in data.keys():
                ret['count'] = data.pop('count')

            # 返回JSON数据
            return super().render(ret, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)
