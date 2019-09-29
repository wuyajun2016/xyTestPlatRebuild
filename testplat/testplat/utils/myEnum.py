# @File  : valideCodeEnum.py
# @Author: jintao
# @Date  : 2019/9/29

from enum import Enum, unique


@unique
class VDCodeEnum(Enum):
    # 验证码过期时间
    expire_time = 60*60*24

