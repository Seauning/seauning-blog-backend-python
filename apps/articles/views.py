# from django.shortcuts import render
# from django.views import View
# from apps.articles.models import Article
# from django.http import JsonResponse
#
#
#
# # Create your views here.
# class ArticleView(View):
#     """
#         获取所有博客文章
#         前端:
#             发送get请求
#         后端：
#             请求：
#             业务逻辑：
#                 从数据库中获取所有的文字
#             响应；
#                 JSON格式数据
#                 {
#                 code:0/400,           # 状态码,0表示成功，400表示数据错误,500表示服务器错误
#                 msg: ok，             # 错误信息
#                 data:{
#
#                 }
#         """
#     def get(self):
#         try:
#             articleList = Article.objects.all()
#         except Exception:
#             return JsonResponse({
#                 'code': 500,
#                 'msg': '文章列表获取失败'
#             })
#
#         return JsonResponse({
#             'code': 0,
#             'msg': 'ok'
#         })
#
#     def post(self):
#
#         return JsonResponse({
#             'code': 0,
#             'msg': 'ok'
#         })