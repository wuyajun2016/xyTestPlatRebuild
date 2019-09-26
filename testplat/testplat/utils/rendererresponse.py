# 导入控制返回的JSON格式的类
from rest_framework.renderers import JSONRenderer
import re


class CustomRenderer(JSONRenderer):
    # 重构render方法
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context:
            msg = '' if renderer_context.get('response').status_code == 200 else (re.findall('[\u4e00-\u9fa5]+',str(data)))[0]
            code = renderer_context.get('response').status_code
            count = data.pop('count', 0)
            new_data = data if renderer_context.get('response').status_code == 200 else ''
            # 重新构建返回的JSON字典
            ret = {
                'msg': msg,
                'code': code,
                'count': count,
                'data': new_data,
            }
            # 返回JSON数据
            return super().render(ret, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)
