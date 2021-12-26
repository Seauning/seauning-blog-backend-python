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

    def smsCodeOpt(self, phone):
        try:
            # 1.生成短信验证码
            from django_redis import get_redis_connection
            redisCli = get_redis_connection('code')
            isNeverDead = redisCli.get('send_flag_{}'.format(phone))
            # 判断该手机号60秒内是否已经发送过验证码
            if isNeverDead:
                return 0
            from random import randint
            smsCode = randint(100000, 999999)
            # 通过redis的pipeline管道操作减少交互次数
            pipeline = redisCli.pipeline()
            # 2.保存短信验证码(1800秒30分钟)
            pipeline.setex('sms_{}'.format(phone), 1800, smsCode)
            # 该手机号60秒内是否发送过短信的标记
            pipeline.setex('send_flag_{}'.format(phone), 60, 1)
            # 执行
            pipeline.execute()
            # 3.发送短信验证码
            # from ronglian_sms_sdk import SmsSDK
            # sdk = SmsSDK(self.accId, self.accToken, self.appId)
            # sdk.sendMessage("1", phone, (smsCode, 5))
            from celeryTask.sms.tasks import celerySendSmsCode
            celerySendSmsCode.delay(phone, smsCode)
        except Exception:
            return -1
        return 1

    def get(self, request, phone):
        try:
            # 1.获取请求参数(phone)
            # 2.验证参数
            # 2.1 非空校验
            if phone is None:
                return JsonResponse({
                    'code': 400,
                    'msg': '手机号不能为空'
                })
            # 需要添加手机号码匹配不正确的情况，让前端知道手机号码格式错误，需要提醒用户进行更改
            # 2.2 合法性校验(手机号)
            if not re.match('^1(?:3\\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8\\d|9\\d)\\d{8}$', phone):
                return JsonResponse({'code': 400, 'msg': 'phone fmt err'})
            # 3.验证码操作
            res = self.smsCodeOpt(phone)
            if res == 0:
                return JsonResponse({
                    'code': 400,
                    'msg': '操作过于频繁，请稍后再试'
                })
            elif res == -1:
                return JsonResponse({
                    'code': 400,
                    'msg': '短信发送失败，请稍后再试'
                })
        except Exception:
            return JsonResponse({
                'code': 500,
                'msg': '短信发送失败，请检查网络'
            })
        # 6.返回响应
        return JsonResponse({
            'code': 0,
            'msg': '发送成功，请在30分钟内填写验证码'
        })