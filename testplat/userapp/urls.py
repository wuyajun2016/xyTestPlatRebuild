from django.conf.urls import url, include
from . import views
from django.urls import re_path
from rest_framework.routers import DefaultRouter
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


router = DefaultRouter()
router.register(r'userLogin', views.UserLoginViewSet, base_name="userLogin")  # 如果是继承ModelViewSet，用这种路由方式
router.register(r'userRegister', views.UserRegitsterViewSet, base_name="userRegister")
urlpatterns = [
    # url(r'^', include(router.urls)),
    url(r'^(?P<version>[v1|v2]+)/', include(router.urls)),  # 可以像这样添加版本
    # re_path('test/', views.UserLoginViewSet.as_view()),  # 如果是继承apiview，用这种路由方式
]
urlpatterns += staticfiles_urlpatterns()

