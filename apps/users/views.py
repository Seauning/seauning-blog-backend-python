import hashlib
import json
import os
import re
import time

from blog_server import settings
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
            msg: ok，        # 错误信息
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
        #     return JsonResponse({'code': 0, 'msg': '用户名不满足需求'})
        # 2. 根据用户名查询数据
        if username is None:
            return JsonResponse({'code': 400, 'msg': 'pars err'})
        try:
            count = User.objects.filter(username=username).count()
        except Exception:
            return JsonResponse({'code': 500, 'msg': 'get failed'})

        # 3. 返回响应
        return JsonResponse({'code': 0, 'msg': 'ok', 'data': {
            'count': count
        }})


def getTimePath(uid):
    mediapath = settings.MEDIA_ROOT
    userpath = mediapath + '\\uploads\\userAvatar\\user_{}'.format(uid)
    if not os.path.exists(userpath):
        os.mkdir(userpath)
    timepath = userpath + time.strftime('\\%Y_%m_%d', time.localtime())
    if not os.path.exists(timepath):
        os.mkdir(timepath)
    return timepath


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
            code:0/400,           # 状态码,0表示成功，400表示数据错误
            msg: ok，        # 错误信息
            count:0/1,          # 手机号个数
            }
    """

    def get(self, request, phone):
        """
        :param request: 请求对象
        :param phone: 手机号
        :return: JSON
        """
        if phone is None:
            return JsonResponse({'code': 400, 'msg': 'pars err'})

        regex = '^1(?:3\\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8\\d|9\\d)\\d{8}$'
        # 需要添加手机号码匹配不正确的情况，让前端知道手机号码格式错误，需要提醒用户进行更改
        if not re.match(regex, phone):
            return JsonResponse({'code': 400, 'msg': 'phone fmt err'})

        try:
            count = User.objects.filter(mobile=phone).count()
        except Exception:
            return JsonResponse({'code': 500, 'msg': 'get failed'})

        return JsonResponse({'code': 0, 'msg': 'ok', 'data': {
            'count': count
        }})


class AvatarUploadView(View):
    """
        该接口仅用于upload组件上传图片时的接口
    前端:
        上传
    后端：
        请求：接受信息
        路由： POST upload/avatar/
        响应；
            JSON格式数据
            {
            code:0,                  # 状态码
            msg: ok，                # 错误信息
            data: {
                    url: ''         # 头像的本地链接
                }
            }
    """

    def post(self, request):
        try:
            avatarFileInfo = request.FILES.getlist('file', None)
            mediapath = settings.MEDIA_ROOT
            userpath = mediapath + '\\uploads\\userAvatar'
            if not os.path.exists(userpath):
                os.mkdir(userpath)
            # 找到最后一个小数点
            dotIndex = avatarFileInfo[0].name.rfind('.')
            # 获取图片类型
            avatarType = avatarFileInfo[0].name[dotIndex:]
            md5 = hashlib.md5()
            # 获取图片名字
            avatarName = avatarFileInfo[0].name[:dotIndex]
            # 加密
            md5.update(avatarName.encode('utf-8'))
            avatarPath = userpath + '\\temp\\{}'.format(md5.hexdigest() + avatarType)
            # 写入图像
            with open(avatarPath, 'wb') as f:
                for content in avatarFileInfo[0].chunks():
                    f.write(content)
        except Exception:
            return JsonResponse({'code': 500, 'msg': 'upload failed'})

        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'data': {
                'url': 'http://localhost:8082/media/uploads/userAvatar/temp/' + md5.hexdigest() + avatarType
            }
        })


class RegisterUserView(View):
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
            msg: ok，        # 错误信息
            }
    """

    # 检查验证码
    # 返回值 -1:过期，0:不一致,1正确
    def checkverifyCode(self, verifyCode, phone):
        # 判断短信验证码是否正确：跟图形验证码的验证一样的逻辑
        # 提取服务端存储的短信验证码：以前怎么存储，现在就怎么提取
        from django_redis import get_redis_connection
        redisCli = get_redis_connection('code')
        smsCodeRedis = redisCli.get('sms_{}'.format(phone))
        # 判断短信验证码是否过期
        if not smsCodeRedis:
            return -1
        # 对比用户输入的和服务端存储的短信验证码是否一致
        if verifyCode != smsCodeRedis.decode():
            return 0
        return 1

    def post(self, request):
        try:
            # 1.接收请求（JSON数据）
            bodyBytes = request.body
            bodyStr = bodyBytes.decode()
            bodyDict = json.loads(bodyStr)
            # 2.获取数据
            username = bodyDict.get('username')  # 通过.get()的方式如果存在异常会中断操作
            password = bodyDict.get('password')
            phone = bodyDict.get('phone')
            verifyCode = bodyDict.get('smsVerifyCode')
            # 传递过来的默认值可能为空字符串
            avatarFileInfo = bodyDict.get('avatar')['url'] if bodyDict.get('avatar') != '' else ''
            # 3.验证数据
            # all中的元素只要是None或者False则返回False
            if not all([username, password, phone, verifyCode]):
                return JsonResponse({'code': 400, 'msg': 'pars err'})
            # 合法性校验(用户名)
            if not re.match('^(.){2,6}$', username):
                return JsonResponse({'code': 400, 'msg': 'uname fmt err'})
            # 重复性校验(用户名)
            if User.objects.filter(username=username).count() != 0:
                return JsonResponse({'code': 400, 'msg': 'uname mtpl'})
            # 合法性校验(密码)
            if not re.match('^(.){6,20}$', password):
                return JsonResponse({'code': 400, 'msg': 'passwd fmt err'})
            # 合法性校验(手机号)
            if not re.match('^1(?:3\\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8\\d|9\\d)\\d{8}$', phone):
                return JsonResponse({'code': 400, 'msg': 'phone fmt err'})
            # 重复性校验(手机号)
            if User.objects.filter(mobile=phone).count() != 0:
                return JsonResponse({'code': 400, 'msg': 'phone mtpl'})
            # 手机验证码校验
            verifyRes = self.checkverifyCode(verifyCode, phone)
            if verifyRes == -1:
                return JsonResponse({'code': 400, 'msg': 'valid dead'})
            elif verifyRes == 0:
                return JsonResponse({'code': 400, 'msg': 'valid err'})
            # 4.创建用户插入用户表
            # 此方法密码无加密
            # user = User(username=username, password=password, mobile=phone, avatarPath=avatar)
            # user.save()
            # 此方法会加密密码(在这里对头像进行判断是为了使用数据库中的默认值，若直接复制则不会用默认值)
            if avatarFileInfo == '':
                user = User.objects.create_user(username=username, password=password, mobile=phone)
            else:
                user = User.objects.create_user(username=username, password=password, mobile=phone,
                                                avatarPath=avatarFileInfo)
        except Exception:
            return JsonResponse({
                'code': 500,
                'msg': 'register failed'
            })

        # 5.状态保持(本项目中不在注册后保持状态，此处仅示例)
        # from django.contrib.auth import login
        # # params:request,user
        # login(request, user)

        return JsonResponse({'code': 0, 'msg': 'ok'})

    '''
    如果需求是注册成功后即表示用户认证通过，那么此时可以在注册成功后实现"状态保持"（注册成功后直接跳转登录）
    如果需求是注册成功后不表示用户认证通过，那么此时不用在注册成功后实现"状态保持"（仅注册成功）
    实现状态保持的两种方式：
        在客户端存储信息使用cookie
        在服务端存储信息使用session
    '''
