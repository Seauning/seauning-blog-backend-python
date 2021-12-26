from django.urls import path
from . import views

urlpatterns = [
    path('img_codes/<uuid>/', views.ImgCodeView.as_view()),
    path('sms_codes/<phone>/', views.SmsCodeView.as_view())
]
