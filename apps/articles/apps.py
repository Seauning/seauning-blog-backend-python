from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    name = 'articles'
    # 在后台中显示的名字(如果未开启后台可以不配置)
    verbose_name = '文章管理'
