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
            code:0,            # 状态码
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
        count = User.objects.filter(mobile=phone).count()
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})
