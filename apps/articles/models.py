from django.db import models
from apps.users.models import User
import django.utils.timezone as timezone


# Create your models here.


# 文章的类型类
from blog_server import settings


class Type(models.Model):
    """
       django 要求模型必须继承 models.Model 类。
       Type 只需要一个简单的分类名 name 就可以了。
       CharField 指定了分类名 name 的数据类型，CharField 是字符型，
       CharField 的 max_length 参数指定其最大长度，超过这个长度的分类名就不能被存入数据库。
       当然 django 还为我们提供了多种其它的数据类型，django 内置的全部类型可查看文档：
       https://docs.djangoproject.com/en/2.2/ref/models/fields/#field-types
   """
    name = models.CharField(verbose_name='分类', max_length=20, default='学习日志', primary_key=True)

    class Meta:
        db_table = 'blog_types'  # 创建的数据表名
        verbose_name = '文章类型管理'  # 后台显示的表名(单数)
        verbose_name_plural = verbose_name  # 后台显示的表名(复数)

    def __str__(self):
        return self.name


# 文章的标签类
class Tag(models.Model):
    """
       标签 Tag 也比较简单，和 Category 一样。
       再次强调一定要继承 models.Model 类！
   """
    name = models.CharField(verbose_name='标签', max_length=20, primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'blog_tags'  # 创建的数据表名
        verbose_name = '文章标签管理'  # 后台显示的表名(单数)
        verbose_name_plural = verbose_name  # 后台显示的表名(复数)


class Article(models.Model):
    id = models.AutoField(verbose_name='文章编号', primary_key=True)
    """
        默认情况下 CharField 要求我们必须存入数据，否则就会报错。
        指定 CharField 的 blank=True 参数值后就可以允许空值
    """
    title = models.CharField(verbose_name='标题', max_length=100, blank=True)
    createdDate = models.DateTimeField(verbose_name='创建时间',
                                       max_length=20,
                                       default=timezone.now)
    modifiedDate = models.DateTimeField(verbose_name='最近修改时间',
                                        max_length=20,
                                        blank=True,
                                        null=True)
    description = models.TextField(verbose_name='内容', blank=True)
    views = models.PositiveIntegerField('浏览量', default=0)  # 正整数
    # 规定一个作者多篇文章，删除用户时保留它的文章，若通过该文章访问作者，提示该作者已注销
    # 此处绑定的外键需要使用settings.AUTH_USER_MODEL更新为我们扩展AbstractUser类的User模型，而不是原本Django的模型
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作者', on_delete=models.DO_NOTHING,
                             null=True,
                             related_name='user_art')
    # 文章分类(多篇文章一个类型)，删除类型时，将该分类的文章更改为默认值
    type = models.ForeignKey(Type, to_field='name', verbose_name='分类', on_delete=models.SET_DEFAULT,
                             default='学习日志', related_name='type_art')
    # 文章标签(多篇文章多个标签)，删除标签时，将该标签的文章的该标签置空
    # 指明多对多关系的关联模型，以及具体的外键
    tag = models.ManyToManyField(Tag, verbose_name='标签', blank=True,
                                 through='ArticleTag',
                                 through_fields=('article', 'tag'))

    class Meta:
        db_table = 'blog_articles'  # 创建的数据表名
        verbose_name = '文章管理'  # 后台显示的表名(单数)
        verbose_name_plural = verbose_name  # 后台显示的表名(复数)

    # 重构文章模型的save方法
    def save(self, *args, **kwargs):
        self.modifiedDate = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# 文章和标签的关联模型
class ArticleTag(models.Model):
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='article_relate')
    tag = models.ForeignKey(Tag, to_field='name', on_delete=models.SET_NULL,
                            null=True, blank=True, related_name='tag_relate')

    class Meta:
        db_table = 'blog_articles_tag_relations'  # 创建的数据表名
        verbose_name = '文章标签关系管理'  # 后台显示的表名(单数)
        verbose_name_plural = verbose_name  # 后台显示的表名(复数)
