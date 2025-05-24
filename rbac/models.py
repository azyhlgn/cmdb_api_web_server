from django.db import models


# Create your models here.
class Permission(models.Model):
    url_pattern = models.CharField(verbose_name='url路径', max_length=100)
    title = models.CharField(verbose_name='url标题', max_length=100, default=None, null=True, blank=True)
    reverse_name = models.CharField(verbose_name='reverse名称', max_length=100, null=True, blank=True)

    menu_name = models.CharField(verbose_name='所属一级菜单', max_length=100, null=True, blank=True)
    is_changelist = models.BooleanField(verbose_name='是否是二级菜单', default=False)
    parent_url_pattern = models.ForeignKey('self', verbose_name='所属二级菜单', on_delete=models.CASCADE, null=True,
                                           blank=True)

    def __str__(self):
        return 'url路径:' + self.url_pattern + '----' + 'url标题:' + str(self.title)


class Role(models.Model):
    name = models.CharField(verbose_name='角色名称', max_length=100)
    permission = models.ManyToManyField(Permission, verbose_name='角色权限')

    def __str__(self):
        return self.name


class UserInfo(models.Model):
    username = models.CharField(verbose_name='用户名称', max_length=100)
    email = models.EmailField(verbose_name='用户邮箱', unique=True)
    password = models.CharField(verbose_name='用户密码', max_length=100)
    role = models.ManyToManyField(Role, verbose_name='用户角色',)

    def __str__(self):
        return self.username
