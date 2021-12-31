import json

from django.shortcuts import render
from django.views import View
from apps.articles.models import Article, Type, Tag
from django.http import JsonResponse
from ..users.views import AvatarUploadView
from ..users.views import Token, User


class BlogBgImgView(AvatarUploadView, View):
    """
        该接口仅用于upload组件上传背景图时的接口
        前端:
            上传
        后端：
            请求：接受信息
            路由： POST upload/bgImg/
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
            id = json.load(request.body)['id']
            fileInfo = request.FILES.getlist('file', None)
            path, md5, type = self.pathParseAndMixin(fileInfo, 'blogBgImg')
            # 写入图像
            with open(path, 'wb') as f:
                for content in fileInfo[0].chunks():
                    f.write(content)
            url = 'http://localhost:8082/media/uploads/userAvatar/temp/' + md5.hexdigest() + type

        except Exception:
            return JsonResponse({'code': 500, 'msg': '上传失败，请尝试重新上传'})

        return JsonResponse({
            'code': 0,
            'msg': '上传成功',
            'data': {
                'url': url
            }
        })


# Create your views here.
class ArticleView(View):
    """
        获取所有博客文章
        前端:
            发送get请求
        后端：
            请求：
            业务逻辑：
                从数据库中获取所有的文章
                返回响应
            响应；
                JSON格式数据
                {
                code:0/400,           # 状态码,0表示成功，400表示数据错误,500表示服务器错误
                msg: ok，             # 错误信息
                data:{
                    articles: []
                }
        """
    def get(self):
        try:
            articleList = Article.objects.all()
        except Exception:
            return JsonResponse({
                'code': 500,
                'msg': '文章列表获取失败'
            })

        return JsonResponse({
            'code': 0,
            'msg': 'ok'
        })

    """
        添加文章
        前端:
            编写文章
            发送post请求
        后端：
            请求：
            业务逻辑：
                获取文章数据
                添加到数据库中
                返回响应
            响应；
                JSON格式数据
                {
                code:0/400,           # 状态码,0表示成功，400表示数据错误,500表示服务器错误
                msg: ok，             # 错误信息
        """

    def post(self, requests):
        try:
            token = requests.headers['Authorization'][7:]
            t = Token()
            bodyDict = json.loads(requests.body)
            uid = t.get_username(token)
            title = bodyDict['title']
            description = bodyDict['text']
            state = bodyDict['state']
            tag = bodyDict['tag']
            obj = {'title': title, 'description': description, 'state': state}
            newObj = {}
            for key in obj.keys():
                if obj[key] and obj[key].strip() != '':
                    newObj[key] = obj[key]
            # 给一个默认的type
            newObj['type'] = Type.objects.get(name=bodyDict['type']) if bodyDict['type'] != '' and\
                                                                        not bodyDict['type'] else Type.objects.get(name='learnlog')
            newObj['user'] = User.objects.get(id=uid)
            if not Tag.objects.get(name=tag):
                tagObj = Tag.objects.create(name=tag)
            else:
                tagObj = Tag.objects.get(name=tag)
            article = tagObj.tag_art.create(**newObj)
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 500,
                'msg': '文章发布失败',
            })
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'data': {
                'id': article.id
            }
        })

    """
        修改文章
        前端:
            修改文章
            点击确认修改
            发送put请求
        后端：
            请求：
            业务逻辑：
                获取文章编号等信息
                修改文章
                返回响应
            响应；
                JSON格式数据
                {
                code:0/400,           # 状态码,0表示成功，400表示数据错误,500表示服务器错误
                msg: ok，             # 错误信息
        """

    def put(self, aid):
        try:
            # 1.获取该文章
            article = Article.objects.get(id=aid)
            print(article)
            # 2.修改该文章

        except Exception:
            return JsonResponse({
                'code': 500,
                'msg': '文章修改失败，请稍后再试'
            })

        return JsonResponse({
            'code': 0,
            'msg': 'ok'
        })

    """
        删除文章
        前端:
            点击确认删除
            发送delete请求
        后端：
            请求：
            业务逻辑：
                获取文章编号
                删除文章
                返回响应
            响应；
                JSON格式数据
                {
                code:0/400,           # 状态码,0表示成功，400表示数据错误,500表示服务器错误
                msg: ok，             # 错误信息
        """

    def delete(self, aid):
        try:
            # 删除该文章
            Article.objects.delete(id=aid)
        except Exception:
            return JsonResponse({
                'code': 500,
                'msg': '删除失败，请稍后再试'
            })

        return JsonResponse({
            'code': 0,
            'msg': 'ok'
        })