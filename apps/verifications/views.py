from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View


class SmsCodeView(View):
    """
    获取短信验证码
    前端:
        点击获取验证码
        发送请求(参数手机号)
    后端：
        请求：接受信息
        业务逻辑: 生成短信验证码，保持短信验证码，发送短信验证码
        路由： phone
        响应；
            JSON格式数据
            {
                code:0,            # 状态码
                errmsg: ok，        # 错误信息
            }
    """
    accId = '8aaf07087de13e49017de600917800c2'
    accToken = 'fb5fa5fd2b1c4df591499191c37b917a'
    appId = '8aaf07087de13e49017de600928300c9'

    def get(self, request, phone):
        # 1.获取请求参数(phone)
        # 2.验证参数
        if phone is None:
            return JsonResponse({
                'code': 0,
                'errmsg': 'params err'
            })
        # 3.生成短信验证码
        from django_redis import get_redis_connection
        redisCli = get_redis_connection('code')
        from random import randint
        smsCode = randint(100000, 999999)
        # 4.保存短信验证码(3000秒5分钟)
        redisCli.setex(phone, 3000, smsCode)
        # 5.发送短信验证码
        from ronglian_sms_sdk import SmsSDK
        sdk = SmsSDK(self.accId, self.accToken, self.appId)
        sdk.sendMessage("1", "19959792983", (smsCode, 5))
        # 6.返回响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })