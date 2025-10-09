# coding:utf-8
u"""
Права ролей
===========
"""
from django.contrib.auth import get_backends
from django.contrib.auth import get_user_model

from m3_django_compatibility import is_authenticated

# TODO: можно обойтись from models import RolePermission
from m3_users.models import RolePermission


class ActionsBackend(object):
    u"""
    Бэкенд для работы с пользователями
    """
    # Поддержка прав доступа на уровне объекта (пока отключена, потом можно будет включить)
    supports_object_permissions = False
    # Поддержка прав доступа анонимного пользователя
    supports_anonymous_user = True

    #TODO: смысл данного метода?
    def authenticate(self, username=None, password=None):
        u"""
        Авторизация, возвращает всегда None
        Мы не будем проверять пользователя - на это есть другие бэкенды
        """
        return None

    def get_group_permissions(self, user_obj):
        u"""
        Возвращается набор строк с правами по всем группам, в которые входит пользователь
        В нашем случае это роли и права в ролях

        :param user_obj: пользователь
        :type user_obj: :py:class:`django.contrib.auth.models.User`
        """
        if not hasattr(user_obj, '_role_perm_cache'):
            perms = RolePermission.objects \
                .filter(role__assigned_users__user=user_obj) \
                .values_list('permission_code') \
                .order_by('permission_code')
            user_obj._role_perm_cache = set()
            for code in perms:
                user_obj._role_perm_cache.update(code)
        return user_obj._role_perm_cache

    def get_all_permissions(self, user_obj):
        u"""
        Возвращается набор строк с правами по всем группам, в которые входит пользователь и права непосредственно пользователя
        В нашем случае это все роли, т.к. у пользователя нет прав :)

        :param user_obj: пользователь
        :type user_obj: :py:class:`django.contrib.auth.models.User`
        """
        if not is_authenticated(user_obj):
            return set()
        return self.get_group_permissions(user_obj)

    def has_perm(self, user_obj, perm, obj=None):
        u"""
        Проверка наличия права у пользователя

        :param user_obj: пользователь
        :type user_obj: :py:class:`django.contrib.auth.models.User`
        :param perm: право
        :type perm: :py:class:`m3_users.models.RolePermission`
        """
        return perm in self.get_all_permissions(user_obj)

    def has_module_perms(self, user_obj, app_label):
        u"""
        Проверка наличия каких-либо права в указанном приложении/модуле

        :param user_obj: пользователь
        :type user_obj: :py:class:`django.contrib.auth.models.User`
        :param str app_label: название приложения
        """
        for perm in self.get_all_permissions(user_obj):
            if perm[:perm.index('.')] == app_label:
                return True
        return False

    #TODO: смысл данного метода?
    def get_user(self, user_id):
        u"""
        Возвращает пользователя системы по id

        :param int user_id: идентификатор пользователя
        """
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    #TODO: смысл данного метода?
    def get_perm_details(self, user_obj, perm):
        u"""
        Возвращает детали прав доступа по коду, возвращает всегда None
        """
        return None


def get_permission_details(user_obj, perm):
    u"""
    Возвращает параметры права

    :param user_obj: пользователь
    :type user_obj: :py:class:`django.contrib.auth.models.User`
    :param perm: право
    :type perm: :py:class:`m3_users.models.RolePermission`
    """
    for backend in get_backends():
        if hasattr(backend, 'get_perm_details'):
            details = backend.get_perm_details(user_obj, perm)
            return details
    return None