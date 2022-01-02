from django.urls import path

from . import views

# 这里虽然是两条不同的路由规则，但是均可在同一个视图中进行业务编写
urlpatterns = [
    path('tagsAtypes/', views.TypeTagView.as_view()),
    # 背景图上传接口
    path('bgImg/', views.BlogBgImgView.as_view()),
    # 文章图上传接口
    path('articleImg/', views.BlogArticleImgView.as_view()),
    path('articlesSu/', views.ArticleSuperView.as_view()),  # 这条路由规则分别表示get获取所有数据，以及post添加数据
    path('article/<aid>/', views.SigArticleView.as_view()),  # 这条路由规则表示获取单篇文章
    path('article/', views.SigArticleView.as_view()),  # 这条路由规则表示修改观看人数
    path('articles/', views.ArticleView.as_view()),     # 这条路由规则分别表示get获取所有数据，以及post添加数据
    path('articles/<aid>/', views.ArticleView.as_view()),      # 这条路由规则分别表示put修改数据，delete删除数据
]
