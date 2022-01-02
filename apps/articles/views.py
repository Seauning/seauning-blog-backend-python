import json
import time

from django.db.models import Q
from django.views import View
from apps.articles.models import Article, Type, Tag, ArticleTag
from django.http import JsonResponse
from ..users.views import AvatarUploadView
from ..users.views import Token, User


class TypeTagView(View):
    # 这个request参数必须加上，在前端发送axios请求时会带上request
    def get(self, request):
        try:
            tags = [{'name': tag.name, 'value': tag.value, 'count': tag.tag_art.all().count()} for tag in Tag.objects.all()]
            types = [{'name': type.name, 'value': type.value, 'count': type.type_art.all().count() } for type in Type.objects.all()]
            data = {'tags': tags, 'types': types}
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'msg': '标签、类型列表获取失败',
            })
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'data': data
        })


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
            fileInfo = request.FILES.getlist('file', None)
            path, md5, type = self.pathParseAndMixin(fileInfo, 'blogBgImg')
            # 写入图像
            with open(path, 'wb') as f:
                for content in fileInfo[0].chunks():
                    f.write(content)
            url = 'http://localhost:8082/media/uploads/blogBgImg/temp/' + md5.hexdigest() + type
        except Exception:
            return JsonResponse({'code': 500, 'msg': '图片上传失败，请尝试重新上传'})
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'data': {
                'url': url
            }
        })


class BlogArticleImgView(AvatarUploadView, View):
    """
        该接口仅用于upload组件上传文章图片时的接口
        前端:
            上传
        后端：
            请求：接受信息
            路由： POST upload/articleImg/
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
            fileInfo = request.FILES.getlist('file', None)
            path, md5, type = self.pathParseAndMixin(fileInfo, 'blogArticleImg')
            # 写入图像
            with open(path, 'wb') as f:
                for content in fileInfo[0].chunks():
                    f.write(content)
            url = 'http://localhost:8082/media/uploads/blogArticleImg/temp/' + md5.hexdigest() + type
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '图片上传失败，请尝试重新上传'})
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'data': {
                'url': url
            }
        })


def getArticleList(id=None):
    if id:  # 表明当前是查询该作者的所有文章
        user = User.objects.get(id=id)
        articles = user.user_art.all()
    else:    # 表明当前是查询所有文章
        articles = Article.objects.all().order_by('-views')
    articleList = [
        {
            'id': a.id,
            'title': a.title,
            'createdTime': a.createdDate,
            'modifiedDate': a.modifiedDate,
            'digest': a.digest,
            'text': a.description,
            'views': a.views,
            'state': a.state,
            'type': {'name': a.type.name, 'value': a.type.value},
            'tag': [{'name': t.name, 'value': t.value} for t in a.tag.all() if t.name != ''],
            'bgPath': str(a.bgImgPath),
            'user': {'name': a.user.username, 'avatar': str(a.user.avatarPath)}
        }
        for a in articles
    ]

    return articleList


class ArticleSuperView(View):
    """
        获取当前用户的所有文章
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
                data:
                    articles: []

        """

    def get(self, request):
        try:
            uid = Token().get_username(request.headers['Authorization'][7:])
            articleList = getArticleList(uid)
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'msg': '用户文章列表获取失败'
            })
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'data': articleList
        })


class SigArticleView(View):
    def get(self, request, aid):
        try:
            q = Article.objects.get(id=aid)
            article = {
                'id': aid,
                'title': q.title,
                'createdTime': q.createdDate,
                'modifiedDate': q.modifiedDate,
                'digest': q.digest,
                'text': q.description,
                'views': q.views,
                'state': q.state,
                'type': {'name': q.type.name, 'value': q.type.value},
                'tag': [{'name': t.name, 'value': t.value} for t in q.tag.all() if t.name != ''],
                'bgPath': str(q.bgImgPath),
                'user': {'name': q.user.username, 'avatar': str(q.user.avatarPath)}
            }
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'msg': '文章获取失败'
            })
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'data': article
        })

    def post(self, request):
        bodyDict = json.loads(request.body)
        aid = bodyDict['id']
        views = bodyDict['views']
        article = Article.objects.get(id=aid)
        article.views = views
        article.save()
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
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
                data:
                    articles: []

        """

    def parseArticleData(self, bodyDict):
        title = bodyDict['title']
        digest = bodyDict['digest']
        description = bodyDict['text']
        state = bodyDict['state']
        bgImgPath = bodyDict['url']
        obj = {'title': title, 'digest': digest, 'description': description, 'state': state, 'bgImgPath': bgImgPath}
        newObj = {}
        for key in obj.keys():
            if obj[key] and obj[key].strip() != '':
                newObj[key] = obj[key]
        # Django中的外键需要一个实例，但是可能存在用户没有添加分类的情况，这时候我们需要给一个默认的type
        # 注意分类与标签不同（分类必须有值，而标签不必，且用户不能创建分类)
        newObj['type'] = Type.objects.get(name=bodyDict['type']) if \
            bodyDict['type'] != '' and not bodyDict['type'] else Type.objects.get(name='learnlog')
        # !!!!(在这里我们不能直接将tag加入到newObj里来，因为这是多对多关系，article和tag之间是靠表关联的，两者的模型中并无相应字段，我们只需要将tagObj返回)
        # 如果存在Tag就直接赋值，如果不存在则重新创建，可能会出现获取到的Tag为''字符串的现象，这是我们默认允许的多对多关系
        tag = bodyDict['tag']
        tagObj = Tag.objects.filter(name=tag)
        if tagObj.count() == 0:
            tagObj = Tag.objects.create(name=tag)
        else:
            tagObj = tagObj[0]
        return newObj, tagObj

    def get(self, request):
        try:
            articleList = getArticleList()
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'msg': '文章列表获取失败'
            })
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'data': articleList
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
            newObj, tagObj = self.parseArticleData(bodyDict)
            newObj['user'] = User.objects.get(id=uid)
            # 通过Django中的反向关联创建的方式创建文章实例
            article = tagObj.tag_art.create(**newObj)
        except Exception as e:
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

    def put(self, request, aid):
        try:
            # 0.校验token
            token = request.headers['Authorization'][7:]
            t = Token()
            uid = t.get_username(token)
            # 1.获取该文章
            bodyDict = json.loads(request.body)
            article = Article.objects.get(id=aid)
            if article.user_id != uid:  # 防止恶意攻击
                return JsonResponse({
                    'code': 400,
                    'msg': '不允许修改他人的文章'
                })
            newObj, tagObj = self.parseArticleData(bodyDict)
            tagList = [tagObj]
            # 2.修改该文章
            article.tag.clear()  # 清空该文章已经有的标签
            article.tag.add(*tagList)     # 给该篇文章添加新的标签
            # 因为文章和标签时多对多关系，通过这两个模型的关联表进行修改
            articleTags = ArticleTag.objects.filter(article_id=aid)   # 先找出所有需要修改的记录
            # 2.重新添加多对多联系
            # 这里多对多的数据更改有点迷糊了（?????)
            for articleTag in articleTags:
                # 此处的意思是，将多对多表中该文章的所有记录对应的文字实例全部更新
                for (key, v) in newObj.items():
                    setattr(articleTag.article, key, v)     # setattr是python中内置的一个修改实例属性值(不一定存在)的方法
                # articleTag.article.modifiedDate =             # 将修改时间变为当前
                articleTag.article.save()   # 记得在修改每各字段的同时，在其末尾保存修改(这里修改的是文章)
        except Exception as e:
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

    def delete(self, request, aid):
        try:
            # 删除该文章
            ArticleTag.objects.get(article_id=aid).delete()
            Article.objects.get(id=aid).delete()
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'msg': '删除失败，请稍后再试'
            })
        return JsonResponse({
            'code': 0,
            'msg': 'ok'
        })
