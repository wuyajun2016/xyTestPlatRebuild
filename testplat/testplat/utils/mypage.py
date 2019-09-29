from rest_framework.pagination import PageNumberPagination


# 分页配置
class ArticlePagination(PageNumberPagination):
    page_size = 10  # 默认每页显示几条,也可以在接口中传入page_size自定义每页显示的数量
    page_size_query_param = 'limit'  # 前端发送的每页数目关键字名，默认为None
    page_query_param = "page"  # 前端发送的页数关键字名，默认为"page"
    max_page_size = 10000  # 前端最多能设置的每页数量
    # limit_query_param = 1  # 设置传入条数,目前还不知道什么用
