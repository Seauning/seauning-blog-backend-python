from django.urls import path
from . import views

urlpatterns = [
    # 判断用户名是否重复，以及用户名合法性
    path('usernames/<username:username>/count/', views.UsernameCountView.as_view()),
    # 判断手机号是否重复，以及手机号合法性
    path('phones/<phone>/count/', views.PhoneCountView.as_view()),
]
