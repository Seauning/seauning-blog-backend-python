import hashlib
import json
import os
import re
import time
import logging

from blog_server import settings
from django.views import View
from apps.users.models import User
from django.http import JsonResponse
from django.core import signing

logger = logging.getLogger('django')


# Create your views here.
# 都不为空或者空字符串
def allNotEmpty(*params):
    for param in params:
        if not param or str(param).strip() == '':
            return False
    return True


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
        if not allNotEmpty(username):
            return JsonResponse({'code': 400, 'msg': '用户名不能为空'})
        try:
            count = User.objects.filter(username=username).count()
        except Exception:
            return JsonResponse({'code': 500, 'msg': '服务器响应错误，请检测网络'})
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
        if not allNotEmpty(phone):
            return JsonResponse({'code': 400, 'msg': '手机号不能为空'})
        regex = '^1(?:3\\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8\\d|9\\d)\\d{8}$'
        # 需要添加手机号码匹配不正确的情况，让前端知道手机号码格式错误，需要提醒用户进行更改
        if not re.match(regex, phone):
            return JsonResponse({'code': 400, 'msg': '手机号格式错误'})
        try:
            count = User.objects.filter(mobile=phone).count()
        except Exception:
            return JsonResponse({'code': 500, 'msg': '服务器响应错误，请检测网络'})

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
    def pathParseAndMixin(self, data, base):
        mediapath = settings.MEDIA_ROOT
        userpath = mediapath + '\\uploads\\{}'.format(base)
        if not os.path.exists(userpath):
            os.mkdir(userpath)
        # 找到最后一个小数点
        dotIndex = data[0].name.rfind('.')
        # 获取图片类型
        avatarType = data[0].name[dotIndex:]
        md5 = hashlib.md5()
        # 获取图片名字
        avatarName = data[0].name[:dotIndex]
        # 加密
        md5.update(avatarName.encode('utf-8'))
        return userpath + '\\temp\\{}'.format(md5.hexdigest() + avatarType), md5, avatarType

    def post(self, request):
        try:
            avatarFileInfo = request.FILES.getlist('file', None)
            avatarPath, md5, avatarType = self.pathParseAndMixin(avatarFileInfo, 'userAvatar')
            # 写入图像
            with open(avatarPath, 'wb') as f:
                for content in avatarFileInfo[0].chunks():
                    f.write(content)
        except Exception:
            return JsonResponse({'code': 500, 'msg': '上传失败，请尝试重新上传'})

        return JsonResponse({
            'code': 0,
            'msg': '上传成功',
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
            # allNotEmpty中的元素只要是None、False、''、'   '则返回False
            if not allNotEmpty([username, password, phone, verifyCode]):
                return JsonResponse({'code': 400, 'msg': '必填项不能为空'})
            # 合法性校验(用户名)
            if not re.match('^(.){2,10}$', username):
                return JsonResponse({'code': 400, 'msg': '用户名格式错误'})
            # 重复性校验(用户名)
            if User.objects.filter(username=username).count() != 0:
                return JsonResponse({'code': 400, 'msg': '用户名重复注册'})
            # 合法性校验(密码)
            if not re.match('^(.){6,20}$', password):
                return JsonResponse({'code': 400, 'msg': '密码格式错误'})
            # 合法性校验(手机号)
            if not re.match('^1(?:3\\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8\\d|9\\d)\\d{8}$', phone):
                return JsonResponse({'code': 400, 'msg': '手机号格式错误'})
            # 重复性校验(手机号)
            if User.objects.filter(mobile=phone).count() != 0:
                return JsonResponse({'code': 400, 'msg': '手机号重复注册'})
            # 手机验证码校验
            verifyRes = self.checkverifyCode(verifyCode, phone)
            if verifyRes == -1:
                return JsonResponse({'code': 400, 'msg': '验证码失效，请重新发送'})
            elif verifyRes == 0:
                return JsonResponse({'code': 400, 'msg': '验证码错误'})
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
                'msg': '注册失败，请尝试重新注册'
            })

        # 5.状态保持(本项目中不在注册后保持状态，此处仅示例)
        # from django.contrib.auth import login
        # # params:request,user
        # login(request, user)

        return JsonResponse({'code': 0, 'msg': '恭喜您注册成功'})

    '''
    如果需求是注册成功后即表示用户认证通过，那么此时可以在注册成功后实现"状态保持"（注册成功后直接跳转登录）
    如果需求是注册成功后不表示用户认证通过，那么此时不用在注册成功后实现"状态保持"（仅注册成功）
    实现状态保持的两种方式：
        在客户端存储信息使用cookie
        在服务端存储信息使用session
    '''


class Token:
    HEADER = {'typ': 'JWT', 'alg': 'default'}
    TIME_OUT = 24 * 60 * 60  # 1 day

    def encrypt(self, obj):
        """加密"""
        value = signing.dumps(obj)
        value = signing.b64_encode(value.encode()).decode()
        return value

    def decrypt(self, src):
        """解密"""
        src = signing.b64_decode(src.encode()).decode()
        raw = signing.loads(src)
        return raw

    def create_token(self, uid, username):
        """生成token信息"""
        # 1. 加密头信息
        header = self.encrypt(self.HEADER)
        # 2. 构造Payload
        payload = {"uid": uid, "username": username, "iat": time.time()}
        payload = self.encrypt(payload)
        # 3. 生成签名
        md5 = hashlib.md5()
        md5.update(("%s.%s" % (header, payload)).encode())
        signature = md5.hexdigest()
        token = "%s.%s.%s" % (header, payload, signature)
        # 4.存储到缓存中
        from django_redis import get_redis_connection
        redisCli = get_redis_connection('token')
        redisCli.setex('token_{}'.format(uid), self.TIME_OUT, token)
        return token

    def get_payload(self, token):
        payload = str(token).split('.')[1]
        payload = self.decrypt(payload)
        return payload

    # 通过token获取用户编号
    def get_username(self, token):
        payload = self.get_payload(token)
        return payload['uid']

    # 校验token
    def check_token(self, token):
        uid = self.get_username(token)
        from django_redis import get_redis_connection
        redisCli = get_redis_connection('token')
        last_token = redisCli.get('token_{}'.format(uid)).decode()
        if last_token:
            return last_token == token
        return False


class UserLoginView(View):
    """
    用户登录
    前端:
        填写登录表单
        点击登录
    后端：
        请求：接受信息(POST---JSON格式)
        业务逻辑：   验证登录信息，提示登录成功或失败，状态保持
        路由： POST login/
        响应；
            JSON格式数据
            {
            code:0,            # 状态码
            msg: ok，        # 错误信息
            }
    """

    # 校验用户信息
    def checkUserInfo(self, username, password):
        # try:
        #     user = User.objects.get(username=username)
        # except Exception:
        #     return -1
        # from django.contrib.auth.hashers import check_password
        # if not check_password(password, user.password):
        #     return 0
        # 上面两步校验也可以通过如下方法实现(我们一般不提示用户具体的错误信息，所以采用下面的方式)
        # 1、判断是根据用户名校验还是手机号校验
        if re.match('^1(?:3\\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8\\d|9\\d)\\d{8}$', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'
        from django.contrib.auth import authenticate
        # 2、验证
        return authenticate(username=username, password=password)
        # 如果验证正确则会返回该用户，否则返回None

    # 校验图片验证码
    def checkImgValidCode(self, uuid, validCode):
        from django_redis import get_redis_connection
        redisCli = get_redis_connection('code')
        code = redisCli.get('img_{}'.format(uuid))
        # 验证码不存在的情况
        if code is None:
            return -1
        # 对比验证码
        if code.decode().lower() != validCode.lower():  # 错误
            return 0
        # 验证正确就删除图形验证码，避免恶意测试图形验证码
        try:
            redisCli.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)
        return 1

    def post(self, request):
        try:
            bodyDict = json.loads(request.body)
            username = bodyDict.get('username')
            password = bodyDict.get('password')
            uuid = bodyDict.get('uuid')
            validCode = bodyDict.get('verifyCode')
            if not allNotEmpty([username, password, uuid, validCode]):
                return JsonResponse({
                    'code': 400,
                    'msg': '登录信息不能为空'
                })
            # 进行验证码校验
            codeCheckRes = self.checkImgValidCode(uuid, validCode)
            if codeCheckRes == -1:
                return JsonResponse({
                    'code': 400,
                    'msg': '验证码失效'
                })
            elif codeCheckRes == 0:
                return JsonResponse({
                    'code': 400,
                    'msg': '验证码错误'
                })
            # 进行用户名与密码校验
            user = self.checkUserInfo(username, password)
            if not user:  # 登录名或密码错误
                return JsonResponse({
                    'code': 400,
                    'msg': '登录名或密码错误'
                })
            # 状态保持
            from django.contrib.auth import login
            login(request, user)
            userinfo = {
                'id': user.id,
                'username': user.username,
                'mobile': user.mobile,
                'email': user.email,
                'avatar': str(user.avatarPath),
                'isSuper': user.is_superuser,
                'isStaff': user.is_staff,
            }
            t = Token()
            token = t.create_token(user.id, user.username)
            response = JsonResponse({
                'code': 0,
                'msg': 'ok',
                'data': {
                    'token': token,
                    'userinfo': userinfo
                }
            })
            # 十天内免登陆(后续有该需求可以添加)
            """
                # 前端勾选十天内免登陆，并在登录的时候携带该信息
                # 后端在session中保持该用户名的记录并设置有效期为十天
                if remember:
                    request.session.set_expiry(None)
                else:
                    # 不记住登录，浏览器关闭及过期
                    request.session.set_expiry(0)
            """
        except Exception:
            return JsonResponse({
                'code': 500,
                'msg': '登录失败，请稍后再试',

            })
        return response


class UserLogoutView(View):
    """
    用户登录
    前端:
        填写登录表单
        点击登录
    后端：
        请求：接受信息(POST---JSON格式)
        业务逻辑：   验证登录信息，提示登录成功或失败，状态保持
        路由： POST login/
        响应；
            JSON格式数据
            {
            code:0,            # 状态码
            msg: ok，        # 错误信息
            }
    """

    def delete(self, request):
        try:
            # 1.退出当前用户，清除session
            from django.contrib.auth import logout
            logout(request)
            # 2.清除前端的登录标识
            '''
                后续如果添加了token和cookie需要在此处进行清除
            '''

        except Exception:
            return JsonResponse({
                'code': 500,
                'msg': '退出失败，请稍后再试'
            })
        return JsonResponse({
            'code': 0,
            'msg': 'ok'
        })


class UserInfoView(View):
    # 获取用户信息
    def post(self, request):
        try:
            token = request.headers['Authorization'][7:]
            t = Token()
            uid = t.get_username(token)
            user = User.objects.get(id=uid)
            userinfo = {
                'id': user.id,
                'username': user.username,
                'mobile': user.mobile,
                'email': user.email,
                'avatar': str(user.avatarPath),
                'isSuper': user.is_superuser,
                'isStaff': user.is_staff,
            }
        except Exception:
            return JsonResponse({
                'code': 500,
                'msg': '用户信息获取失败',
            })

        def set_default(obj):
            if isinstance(obj, set):
                print(obj)
                return list(obj)
            raise TypeError

        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'data': userinfo
        })

    # 更新用户信息
    def put(self, request):
        try:
            token = request.headers['Authorization'][7:]
            t = Token()
            uid = t.get_username(token)
            bodyDict = json.loads(request.body)
            username = bodyDict['username']
            mobile = bodyDict['mobile']
            email = bodyDict['email']
            avatar = bodyDict['avatarUrl']
            obj = {'username': username, 'mobile': mobile, 'email': email, 'avatarPath': avatar}
            newObj = {}
            for key in obj.keys():
                if obj[key] and obj[key].strip() != '':
                    newObj[key] = obj[key]
            # 通过update修改多个值(注意：此方法需要结合filter使用，如果采用get最好使用.语法进行修改单个属性)
            User.objects.filter(id=uid).update(**newObj)
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 500,
                'msg': '用户信息更新失败',
            })
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
        })


