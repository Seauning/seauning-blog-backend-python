from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.ArticleView.as_view()),
    path('upload/article/', views.ArticleView.as_view())
]
