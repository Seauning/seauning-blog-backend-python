import json
import re

from django.views import View
from apps.users.models import User
from django.http import JsonResponse


# Create your views here.

# 类视图

class UsernameCountView(View):
    """
    判断用户名是否重复注册
    前端:
        输入用户名
        失去焦点
        发送请求
    后端：
        请求：接受用户名
        业务逻辑：
            根据用户名查询数据库，如果数量为0，表明没有该用户
                            ，如果数量为1，表明有用户
        响应；
            JSON格式数据
            {
            code:0,            # 状态码
            errmsg: ok，        # 错误信息
            count:0/1,          # 用户名个数
            }
    """

    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        # 1.接收用户名，进行合法性校验
        #   更改为，在路由匹配中加入自定义转换器，在传入路径参数的时候进行合法性校验
        # if not re.match('[(a-zA-Z0-9-_~)|(\u4e00-\u9fa5)]{2,6}', username):
        #     return JsonResponse({'code': 0, 'errmsg': '用户名不满足需求'})
        # 2. 根据用户名查询数据
        count = User.objects.filter(username=username).count()
        # 3. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})


class PhoneCountView(View):
    """
    判断手机号是否重复注册
    前端:
        输入手机号
        失去焦点
        发送请求
    后端：
        请求：接受手机号
        业务逻辑：
            根据手机号查询数据库，如果数量为0，表明没有该手机号
                            ，如果数量为1，表明有该手机号
        响应；
            JSON格式数据
            {
            code:0/1,           # 状态码,0表示成功，1表示失败
            errmsg: ok，        # 错误信息
            count:0/1,          # 手机号个数
            }
    """

    def get(self, request, phone):
        """
        :param request: 请求对象
        :param phone: 手机号
        :return: JSON
        """
        regex = '1(?:3\\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8\\d|9\\d)\\d{8}'
        # 需要添加手机号码匹配不正确的情况，让前端知道手机号码格式错误，需要提醒用户进行更改
        if not re.match(regex, phone):
            return JsonResponse({'code': 1, 'errmsg': 'phone multiple'})

        count = User.objects.filter(mobile=phone).count()
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})


class RegisterUser(View):
    """
    注册用户
    前端:
        点击确定
        获取用户信息并校验（，是否同意协议:略）
        发送请求
    后端：
        请求：接受信息(POST---JSON格式)
        业务逻辑：   验证数据。数据入库
        路由： POST register/
        响应；
            JSON格式数据
            {
            code:0,            # 状态码
            errmsg: ok，        # 错误信息
            }
    """

    def checkverifyCode(self, verifyCode):
        return True

    def post(self, request):
        # 1.接收请求（JSON数据）
        bodyBytes = request.body
        bodyStr = bodyBytes.decode()
        bodyDict = json.loads(bodyStr)
        # 2.获取数据
        username = bodyDict.get('username')   # 通过.get()的方式如果存在异常会中断操作
        password = bodyDict.get('password')
        phone = bodyDict.get('phone')
        verifyCode = bodyDict.get('verifyCode')
        avatar = bodyDict.get('avatar')

        # 3.验证数据
        # all中的元素只要是None或者False则返回False
        if not all([username, password, phone, verifyCode, avatar]):
            return JsonResponse({'code': 400, 'errmsg': 'params err'})

        if not re.match('.{2,6}', username):
            return JsonResponse({'code': 400, 'errmsg': 'uname format err'})

        if User.objects.filter(username=username).count() != 0:
            return JsonResponse({'code': 400, 'errmsg': 'uname multiple'})

        if not re.match('1(?:3\\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8\\d|9\\d)\\d{8}', phone):
            return JsonResponse({'code': 400, 'errmsg': 'phone format err'})

        if User.objects.filter(mobile=phone).count() != 0:
            return JsonResponse({'code': 400, 'errmsg': 'phone multiple'})

        if not self.checkverifyCode(verifyCode):
            return JsonResponse({'code': 400, 'errmsg': 'valid err'})

        # 4.创建数据插入数据表
        user = User(username=username, password=password, mobile=phone, avatarPath=avatar)
        user.save()
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
