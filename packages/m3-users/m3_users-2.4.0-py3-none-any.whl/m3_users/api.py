# coding: utf-8

u"""Внешнее API для подсистемы m3_users."""
from six import string_types

from django.contrib.auth import get_user_model

from m3_django_compatibility import atomic

from .helpers import get_assigned_metaroles_query
from .metaroles import get_metarole
from . import models


SUPER_ADMIN_METAROLE = 'super-admin'


def get_user_metaroles(user):
    u"""
    Возвращает список объектов метаролей, которые есть у пользователя.

    :param user: пользователь системы
    :type user: :py:class:`django.contrib.auth.models.User`
    """
    result = []
    for metarole_code in get_assigned_metaroles_query(user):
        metarole = get_metarole(metarole_code)
        if metarole:
            result.append(metarole)

    return result


def user_has_metarole(user, metarole):
    u"""Возвращает True, если пользователю назначена метароль, иначе False.

    :param user: пользователь, для которого проверяется наличие метароли
    :type user: :py:class:`django.contrib.auth.models.User`
    :param str metarole: метароль
    """
    for metarole_code in get_assigned_metaroles_query(user):
        if metarole_code == metarole:
            return True
    return False


def get_user_roles(user):
    u"""
    Возвращает список ролей пользователя

    :param user: пользователь системы
    :type user: :py:class:`django.contrib.auth.models.User`
    """
    return models.UserRole.objects.filter(
        assigned_users__user=user
    ).order_by('name')


@atomic
def remove_user_role(user, role):
    u"""
    Снимает роль у пользователя.

    :param user: пользователь у которого снимается роль
    :type user: :py:class:`django.contrib.auth.models.User`
    :param role: роль
    :type role: :py:class:`m3_users.models.UserRole`

    .. note::

        если снимаем роль у суперпользователя, и него не осталось ролей,
        наследованных от метароли Супер-Администратора, то сниматся с него
        флаг суперпользователя
    """
    models.AssignedRole.objects.filter(user=user, role=role).delete()

    if isinstance(user, int):
        user = get_user_model().objects.get(id=user)

    # снимаем флаг супер-пользователя, если он стоял, и у пользователя не
    # осталось ролей, наследовынных от метароли Супер-Администратора
    if (
        user.is_superuser and not
        models.UserRole.objects.filter(
            metarole=SUPER_ADMIN_METAROLE,
            assigned_users__user=user
        ).exists()
    ):
        user.is_superuser = False
        user.save()


@atomic
def set_user_role(user, role):
    u"""
    Устанавливает роль для пользователя

    :param user: пользователь у которого снимается роль
    :type user: :py:class:`django.contrib.auth.models.User`
    :param role: роль
    :type role: :py:class:`m3_users.models.UserRole`

    .. note::

        если роль суперпользователя, то пользователю ставится флаг
        суперпользователя
    """
    # TODO: что этим хотел сказать автор? можно как-то красиво это сделать?
    # TODO: например exists()
    if len(models.AssignedRole.objects.filter(user=user, role=role)[0:1]) == 0:

        if isinstance(role, int):
            role = models.UserRole.objects.get(id=role)

        if isinstance(user, int):
            user = get_user_model().objects.get(id=user)

        assigned_role = models.AssignedRole()
        assigned_role.user = user
        assigned_role.role = role
        assigned_role.save()

        if role.metarole == SUPER_ADMIN_METAROLE and not user.is_superuser:
            user.is_superuser = True
            user.save()


@atomic
def clear_user_roles(user):
    u"""
    Убирает все роли у пользователя

    :param user: пользователь у которого снимается роль
    :type user: :py:class:`django.contrib.auth.models.User`

    .. note::

        если пользователь суперпользователь, то снимается флаг
        суперпользователя
    """
    models.AssignedRole.objects.filter(user=user).delete()

    if isinstance(user, int):
        user = get_user_model().objects.get(id=user)

    if user.is_superuser:
        user.is_superuser = False
        user.save()


def get_user_by_id(user_id):
    u"""Возвращает экземпляр пользователя AUTH_USER_MODEL по идентификатору.

    :param int user_id: искомый пользователь

    .. note::

        если вдруг в user_id передан реальный пользователь, то он и
        возвращается.
    """
    result = None
    model = get_user_model()

    if isinstance(user_id, (int, string_types)):
        try:
            result = model.objects.get(pk=user_id)
        except model.DoesNotExist:
            result = None
    elif isinstance(user_id, model):
        result = user_id

    return result
