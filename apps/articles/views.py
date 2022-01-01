import json

from django.views import View
from apps.articles.models import Article, Type, Tag
from django.http import JsonResponse
from ..users.views import AvatarUploadView
from ..users.views import Token, User


class TypeTagView(View):

    # 这个request参数必须加上，在前端发送axios请求时会带上request
    def get(self, request):
        try:
            tags = [{'name': tag.name, 'value': tag.value} for tag in Tag.objects.all()]
            types = [{'name': type.name, 'value': type.value} for type in Type.objects.all()]
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


def getArticleList(id=None):
    if id:
        user = User.objects.get(id=id)
        articles = user.user_art.all()
    else:
        articles = Article.objects.all()
    articleList = [
        {
            'id': a.id,
            'title': a.title,
            'modifiedDate': a.modifiedDate,
            'text': a.description,
            'views': a.views,
            'state': a.state,
            'type': {'name': a.type.name, 'value': a.type.value},
            'tag': [t for t in a.tag.values()],
            'bgPath': str(a.bgImgPath)
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
            title = bodyDict['title']
            description = bodyDict['text']
            stateMode = {'byself': '原创', 'byother': '转载'}
            state = stateMode[bodyDict['state']]
            tag = bodyDict['tag']
            bgImgPath = bodyDict['url']
            obj = {'title': title, 'description': description, 'state': state, 'bgImgPath': bgImgPath}
            newObj = {}
            for key in obj.keys():
                if obj[key] and obj[key].strip() != '':
                    newObj[key] = obj[key]
            # Django中的外键需要一个实例，但是可能存在用户没有添加分类的情况，这时候我们需要给一个默认的type
            # 注意分类与标签不同（分类必须有值，而标签不必，且用户不能创建分类)
            newObj['type'] = Type.objects.get(name=bodyDict['type']) if \
                bodyDict['type'] != '' and not bodyDict['type'] else Type.objects.get(name='learnlog')
            newObj['user'] = User.objects.get(id=uid)
            # 如果存在Tag就直接赋值，如果不存在则重新创建，可能会出现获取到的Tag为''字符串的现象，这是我们默认允许的多对多关系
            tagObj = Tag.objects.filter(name=tag)
            if tagObj.count() == 0:
                tagObj = Tag.objects.create(name=tag)
            else:
                tagObj = tagObj[0]
            # 通过Django中的反向关联创建的方式创建文章实例
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
