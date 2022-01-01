from django.urls import path

from . import views

# 这里虽然是两条不同的路由规则，但是均可在同一个视图中进行业务编写
urlpatterns = [
    path('tagsAtypes/', views.TypeTagView.as_view()),
    # 背景图上传接口
    path('bgImg/', views.BlogBgImgView.as_view()),
    path('articlesSu/', views.ArticleSuperView.as_view()),  # 这条路由规则分别表示get获取所有数据，以及post添加数据
    path('articles/', views.ArticleView.as_view()),     # 这条路由规则分别表示get获取所有数据，以及post添加数据
    path('articles/<aid>/', views.ArticleView.as_view()),      # 这条路由规则分别表示put修改数据，delete删除数据
]
