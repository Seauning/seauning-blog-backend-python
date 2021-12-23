from django.urls import path
from . import views

urlpatterns = [
    # path('')
    path('sms_codes/<phone>/', views.SmsCodeView.as_view())
]
