from celery.task import task
import time
from django.core.mail import EmailMultiAlternatives   # 发送邮件


@task
def sendmail(email, code):
    """
    发送邮件
    :param email:
    :param code:
    :return:
    """
    subject = u'重置您的密码'
    message = u"""
        <h2>质量中心<h2><br />
        <p>重置密码的验证码(有效期1天)：%s</p>
        <p><br/>(请保管好您的验证码)</p>
        """ % code

    send_to = [email]
    fail_silently = False  # 发送异常报错

    msg = EmailMultiAlternatives(subject=subject, body=message, to=send_to)
    msg.attach_alternative(message, "text/html")
    msg.send(fail_silently)

# 异步测试
# @task
# def test(email):
#     print('start send email to %s' % email)
#     time.sleep(10)  # 休息5秒
#     print('success')
#     return True
