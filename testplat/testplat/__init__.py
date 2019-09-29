from __future__ import absolute_import, unicode_literals
import pymysql
from .celeryJob import app as celery_app  # 引入celery实例对象


pymysql.install_as_MySQLdb()  # 这种写法貌似不行了

