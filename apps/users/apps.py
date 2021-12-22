from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'users'
    # 在后台中显示的名字(如果未开启后台可以不配置)
    verbose_name = '用户管理'
