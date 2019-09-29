from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class Middle1(MiddlewareMixin):
    """中间件：打印日志"""
    def process_request(self, request):
        logger.info('{who}发起了请求{url}'.format(who=request.user.username,url=request.path_info))

    def process_response(self, request, response):
        logger.info('服务器响应{who}的请求{url},响应体为{result}'.format(who=request.user.username,
                                                             url=request.path_info, result=response))
        return response
