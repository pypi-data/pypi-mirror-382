# coding: utf-8

from django.db import models
from m3_django_compatibility import AUTH_USER_MODEL

from .metaroles import get_metarole


class UserRole(models.Model):
    u"""
    Модель хранения роли пользователя в прикладной подсистеме
    """
    #: строка, наименование роли пользователя
    name = models.CharField(max_length=200, db_index=True,
                            verbose_name=u'Наименование роли пользователя')

    #: строка, ассоциированная с ролью метароль
    #: (определяет интерфейс пользователя).
    metarole = models.CharField(max_length=100, null=True, blank=True,
                                verbose_name=u'Метароль')

    def metarole_name(self):
        u"""
        возвращает название метароли
        """
        mr = get_metarole(self.metarole)
        return mr.name if mr else ''

    metarole_name.json_encode = True

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'm3_users'
        db_table = 'm3_users_role'
        verbose_name = u'Роль пользователя'
        verbose_name_plural = u'Роли пользователя'


class RolePermission(models.Model):
    u"""
    Разрешение, сопоставленное пользовательской роли.
    """

    #: роль, связь с :py:class:`m3_users.models.UserRole`
    role = models.ForeignKey(
        UserRole, verbose_name=u'Роль', on_delete=models.CASCADE
    )

    #: строка, код права доступа
    permission_code = models.CharField(max_length=200, db_index=True,
                                       verbose_name=u'Код права доступа')

    #: текстовое поле, человеческое наименование разрешения
    #: с наименованиями модулей, разделенных через запятые.
    verbose_permission_name = models.TextField(
        verbose_name=u'Описание права доступа')

    #: булево, активность роли
    disabled = models.BooleanField(default=False, verbose_name=u'Активно')

    def __unicode__(self):
        return self.permission_code

    def __str__(self):
        return self.permission_code

    class Meta:
        app_label = 'm3_users'
        db_table = 'm3_users_rolepermissions'
        verbose_name = u'Право доступа у роли'
        verbose_name_plural = u'Права доступа у ролей'


class AssignedRole(models.Model):
    u"""
    Роль, назначенная на пользователя
    """
    #: пользователь, ссылка :py:class:`django.contrib.auth.models.User`
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name='assigned_roles',
        verbose_name=u'Пользователь',
        on_delete=models.CASCADE,
    )

    #: роль, ссылка :py:class:`m3_users.models.UserRole`
    role = models.ForeignKey(
        UserRole,
        related_name='assigned_users',
        verbose_name=u'Роль',
        on_delete=models.CASCADE,
    )

    # TODO: Удалить, за очевидной ненужностью
    def user_login(self):
        return self.user.username if self.user else ''

    # TODO: смысл этого метода?
    def user_first_name(self):
        return self.user.first_name if self.user else ''

    # TODO: смысл этого метода?
    def user_last_name(self):
        return self.user.last_name if self.user else ''

    # TODO: смысл этого метода?
    def user_email(self):
        return self.user.email if self.user else ''

    user_login.json_encode = True
    user_first_name.json_encode = True
    user_last_name.json_encode = True
    user_email.json_encode = True

    def __unicode__(self):
        return u'Роль "%s" у %s' % (self.role.name,
                                    self.user.username)

    def __str__(self):
        return 'Роль "{0}" у {1}'.format(self.role.name, self.user.username)

    class Meta:
        app_label = 'm3_users'
        db_table = 'm3_users_assignedrole'
        verbose_name = u'Связка роли с пользователем'
        verbose_name_plural = u'Связки ролей с пользователями'
