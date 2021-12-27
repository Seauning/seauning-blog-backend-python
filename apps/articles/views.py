from django.shortcuts import render
from django.views import View
from apps.articles.models import Article
from django.http import JsonResponse


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

    def post(self):

        return JsonResponse({
            'code': 0,
            'msg': 'ok'
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