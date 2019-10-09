# @File  : valideCodeEnum.py
# @Author: jintao
# @Date  : 2019/9/29

from enum import Enum, unique


@unique
class ResponseEnum(Enum):
    # 正常登陆
    success = 200
    # 参数错误
    params_error = 400
    # 权限错误
    un_auth = 401
    # 页面无效
    page_not_found = 404
    # 方法错误
    method_error = 405
    # 超过访问频率
    throttle_limit = 429
    # 服务器内部错误
    server_error = 500
    insufficient_storage = 507

