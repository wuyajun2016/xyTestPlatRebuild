"""testplat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include, url
from rest_framework_swagger.views import get_swagger_view
from rest_framework_jwt.views import obtain_jwt_token

schema_view = get_swagger_view(title="TestPlat")
urlpatterns = [
    path('admin/', admin.site.urls),  # 这是后台的url,django自带
    url(r'^api-auth/', include('rest_framework.urls')),  # drf登录:swagger借助了drf的登录，所以这里要配置下
    re_path('^docs/$', schema_view),  # swagger路由:ip/docs
    url(r'', include('userapp.urls')),  # 让diango能够找到应用的url
    url(r'^api-token-auth/', obtain_jwt_token),  # jwt（settings配置后token可带过期时间,token不是存在数据库的）
]
