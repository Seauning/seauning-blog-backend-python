from django.urls import path
from . import views

urlpatterns = [
    path('sms_codes/<phone:phone>/', views.SmsCodeView.as_view())
]
