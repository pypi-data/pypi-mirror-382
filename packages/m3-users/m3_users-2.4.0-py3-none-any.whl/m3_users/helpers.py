# coding:utf-8
u"""
Вспомогательне методы модуля
============================

.. Created on 11.06.2010

.. @author: akvarats
"""
from django.contrib.auth import get_user_model
from django.db.models import Q
from m3_django_compatibility import get_installed_apps

from .models import UserRole, AssignedRole


# TODO: может лучше filter=None?, и переименовать filter, чтобы не перекрыть дуфолтный filter
def get_roles_query(filter=''):
    u"""
    Возвращает запрос на получение списка ролей

    :param str filter: необязательный параметр, название конкретной роли
    """
    if filter:
        query = UserRole.objects.filter(name__icontains=filter)
    else:
        query = UserRole.objects.all()

    return query.order_by('name')


# TODO: может лучше filter=None?, и переименовать filter, чтобы не перекрыть дуфолтный filter
def get_users_query(filter=''):
    u"""
    Возвращает запрос на получение списка пользователей

    :param str filter: необязательный параметр, строка по которому будет произведена фильтрация пользователей
    """
    User = get_user_model()

    if 'django.contrib.auth' in get_installed_apps():
        if filter:
            query = User.objects.filter(
                Q(username__icontains=filter) |
                Q(first_name__icontains=filter) |
                Q(last_name__icontains=filter) |
                Q(email__icontains=filter)
            )
        else:
            query = User.objects.all()
        return query.order_by('first_name', 'last_name', 'username')


# TODO: может лучше filter=None?, и переименовать filter, чтобы не перекрыть дуфолтный filter
def get_assigned_users_query(role, filter=None):
    u"""
    Возвращает запрос, пользователи имеющие указанную роль

    :param role: роль системы
    :type role: :py:class:`m3_users.models.UserRole`
    :param str filter: необязательный параметр, строка по которому будет произведена фильтрация пользователей
    """
    filter_ = Q()
    if filter:
        #поиск по полям логин, имя, фамилия, email
        for field in ['username', 'first_name', 'last_name', 'email']:
            filter_ |= Q(**{'user__' + field + '__icontains': filter})
    query = AssignedRole.objects.filter(Q(role=role) & filter_).select_related('user').select_related('role')
    return query


# TODO: может лучше filter=None?, и переименовать filter, чтобы не перекрыть дуфолтный filter
def get_unassigned_users(role, filter):
    u"""
    Хелпер возвращает список пользователей (возможно, отфильтрованных 
    по наименованию), которые еще не включены в роль
    """

    # TODO: list тут необязателен
    # получаем список всех пользователей
    all_users = list(get_users_query(filter))

    # TODO: list тут необязателен
    # получаем список пользователей, которые назначены на роль
    assigned_users = list(get_assigned_users_query(role))

    # TODO: может использовать генератор словаря?
    # excluded_users_dict = {row.user.id:row.user for row in assigned_users}
    excluded_users_dict = {}
    for assigned_user in assigned_users:
        excluded_users_dict[assigned_user.user.id] = assigned_user.user

        # TODO: может использовать генератор списка?
    # result = [user for user in all_users if not user.id in excluded_users_dict]
    result = []
    for user in all_users:
        # TODO: if not user.id in excluded_users_dict
        if not excluded_users_dict.has_key(user.id):
            result.append(user)

    return result


def get_assigned_metaroles_query(user):
    u"""
    Возвращает список метаролей у пользователя

    :param user: пользователь системы
    :type user: :py:class:`django.contrib.auth.models.User`
    """

    # TODO: может срау в фильтре избавиться от пустых записей? и вернуть запрос с ролями
    # metaroles = AssignedRole.objects.filter(user=user, role__metarole__isnull=False)...
    # return metaroles

    metaroles = AssignedRole.objects.filter(user=user).select_related('role') \
        .values('role__metarole').distinct()
    lst = [metarole['role__metarole'] for metarole in metaroles if metarole['role__metarole']]
    # если небыло списка ролей, то возьмем метароли из профиля
    if not lst:
        prof = user.get_profile()
        if hasattr(prof, 'get_metaroles'):
            lst = prof.get_metaroles()
    return lst