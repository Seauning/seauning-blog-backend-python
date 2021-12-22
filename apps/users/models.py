from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

'''
# 1.自定义模型
# 密码需要我们加密，还要实现登录的时候的密码验证
# class User(models.Model):
#     # 用户名最长20位，且唯一
#     username = models.CharField(max_length=20, unique=True)
#     # 密码最长20位
#     password = models.CharField(max_length=20)
#     # 手机号码最长11位，且唯一
#     mobile = models.CharField(max_length=11, unique=True)
'''

# 2. Django 自带用户模型
# 这个用户模型，有密码加密和验证
# from django.contrib.auth.models import User
'''
    此处需要注意：
        用户组和用户权限只能管理一个用户表，此时有两个用户表(系统定义，自定义)
    解决方法：
        让自定义User替换系统定义的User
'''


# 用户头像的路径函数
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uploads/userAvatar/user_<id>/日期/<filename>
    return 'uploads/userAvatar/user_{0}/%Y/%m/%d/{1}'.format(instance.user.id, filename)


class User(AbstractUser):
    # 手机号码最长11位，且唯一
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    # 头像
    avatarPath = models.ImageField(upload_to=user_directory_path,
                                   max_length=300,
                                   blank=True,
                                   null=True,
                                   default='upload/userAvatar/default.png',
                                   verbose_name='头像')

    class Meta:
        db_table = 'tb_users'  # 创建的数据表名
        verbose_name = '用户管理'  # 后台显示的表名(单数)
        verbose_name_plural = verbose_name  # 后台显示的表名(复数)

    def __str__(self):
        return self.username
