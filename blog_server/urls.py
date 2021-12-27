"""blog_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import register_converter

from utils.converters import UsernameConverter, PhoneConverter

# 注册用户名规则，规则名为(username)
register_converter(UsernameConverter, 'username')
# 注册手机号规则，规则名为(phone)
register_converter(PhoneConverter, 'phone')

urlpatterns = [
    path('admin/', admin.site.urls),
    # 因为在每个子应用都放在apps中，因此此处需要用apps来获取子应用
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.verifications.urls')),
    path('api/', include('apps.articles.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
