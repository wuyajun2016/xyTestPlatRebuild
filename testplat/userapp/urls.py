from django.conf.urls import url, include
from . import views
from django.urls import re_path
from rest_framework.routers import DefaultRouter
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings


router = DefaultRouter()
router.register(r'userLogin', views.UserLoginViewSet, base_name="userLogin")  # 如果是继承ModelViewSet，用这种路由方式
router.register(r'userRegister', views.UserRegitsterViewSet, base_name="userRegister")
router.register(r'userSetPassword', views.UserSetPasswordViewSet, base_name="userSetPassword")
router.register(r'userExt', views.UserExtViewSet, base_name="userExt")
router.register(r'uploadHeadImg', views.UploadImgViewSet, base_name="uploadHeadImg")
router.register(r'getValidCode', views.GetValidCodeViewSet, base_name="getValidCode")
router.register(r'userSetPasswordNotLogin', views.UserSetPasswordNotLoginViewSet, base_name="userSetPasswordNotLogin")
urlpatterns = [
    url(r'^(?P<version>[v1|v2]+)/', include(router.urls)),  # 可以像这样添加版本控制
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # django展示图片的方式，还需要在settings.py中配置下

