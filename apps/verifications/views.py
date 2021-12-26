import re
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View


class ImgCodeView(View):
    """
    获取短信验证码
    前端:
        点击获取图片验证码
        生成uuid
        发送请求(参数uuid)
    后端：
        请求：接受信息
        业务逻辑: 生成图片验证码，保存图片验证码，发送图片验证码
        路由： uuid
        响应；
            JSON格式数据
            {
                code:0,            # 状态码
                msg: ok，        # 错误信息
            }
    """

    def get(self, request, uuid):
        # 1、接收路由中的uuid
        # 2、生成图片验证码和图片二进制
        from libs.captcha.captcha import captcha
        # text是图片验证码内容
        # img是图片二进制
        text, img = captcha.generate_captcha()
        # 3、通过redis保存图片验证码
        # 3.1 链接redis
        from django_redis import get_redis_connection
        redisCli = get_redis_connection('code')
        # 3.2 存入验证码
        # name,time(s),value
        redisCli.setex('img_{}'.format(uuid), 60, text)
        # 4、返回图片二进制
        # 因为图片是二进制，我们不能返回一个Json数据
        # content_type=响应体数据类型
        # content_type  的语法是: 大类/小类
        # 如图片：image/jpeg,image/png
        return HttpResponse(img, content_type='image/jpeg')


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
                msg: ok，        # 错误信息
            }
    """
    accId = '8aaf07087de13e49017de600917800c2'
    accToken = 'fb5fa5fd2b1c4df591499191c37b917a'
    appId = '8aaf07087de13e49017de600928300c9'

    def get(self, request, phone):
        try:
            # 1.获取请求参数(phone)
            # 2.验证参数
            # 2.1 非空校验
            if phone is None:
                return JsonResponse({
                    'code': 400,
                    'msg': 'pars err'
                })
            # 需要添加手机号码匹配不正确的情况，让前端知道手机号码格式错误，需要提醒用户进行更改
            # 2.2 合法性校验(手机号)
            if not re.match('^1(?:3\\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8\\d|9\\d)\\d{8}$', phone):
                return JsonResponse({'code': 400, 'msg': 'phone fmt err'})
            # 3.生成短信验证码
            from django_redis import get_redis_connection
            redisCli = get_redis_connection('code')
            from random import randint
            smsCode = randint(100000, 999999)
            # 4.保存短信验证码(3000秒5分钟)
            redisCli.setex('sms_{}'.format(phone), 3000, smsCode)
            # 5.发送短信验证码
            from ronglian_sms_sdk import SmsSDK
            sdk = SmsSDK(self.accId, self.accToken, self.appId)
            sdk.sendMessage("1", phone, (smsCode, 5))
        except Exception:
            return JsonResponse({
                'code': 500,
                'msg': 'send failed'
            })

        # 6.返回响应
        return JsonResponse({
            'code': 0,
            'msg': 'ok'
        })