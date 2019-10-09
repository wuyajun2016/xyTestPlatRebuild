from django_filters.rest_framework import FilterSet
import django_filters
from userapp.models import UserExt


class UserExtFilter(FilterSet):
    # 第一种方式，用lookup_expr
    sex = django_filters.NumberFilter(lookup_expr='gte')
    # icontains前面的i表示忽视大小写
    nickname = django_filters.CharFilter(lookup_expr='icontains')
    # 第二种方式，model中没有的字段可以这么定义
    position_m = django_filters.NumberFilter(method='position_filter', help_text="职位")

    def position_filter(self, queryset, name, value):
        return queryset

    class Meta:
        model = UserExt
        fields = ['sex', 'nickname']


