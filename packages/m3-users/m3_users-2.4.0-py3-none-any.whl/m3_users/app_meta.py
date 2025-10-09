# coding: utf-8

from django.urls import (
    re_path,
)
from m3 import (
    authenticated_user_required,
)
from m3.actions import (
    ActionController,
)

from .constants import (
    ADMIN,
    GENERIC_USER,
    SUPER_ADMIN,
)
from .metaroles import (
    Metaroles_DictPack,
    UserMetarole,
)
from .roles import (
    Roles_DictPack,
    RolesActions,
)
from .users import (
    UsersActions,
)


# контроллер
users_controller = ActionController(url='/m3-users', name='Пользователи М3')


def register_actions():
    users_controller.packs.extend(
        [
            RolesActions(),
            UsersActions(),
            Roles_DictPack(),
            Metaroles_DictPack(),  # метароли пользователей
        ]
    )


@authenticated_user_required
def users_view(request):
    return users_controller.process_request(request)


def register_urlpatterns():
    return [
        re_path(r'^m3-users', users_view),
    ]


def register_metaroles(manager):
    """
    Функция возвращает список метаролей, которые регистрируются
    по умолчанию на уровне Платформы М3.

    :param manager: менеджер, отвечающий за управление метаролями.
    :type manager: :py:class:`m3_users.metaroles.MetaroleManager`
    """

    # метароль обычного пользователя системы
    manager.GENERIC_USER_METAROLE = UserMetarole(GENERIC_USER, 'Обобщенный пользователь')

    # метароль администратора системы
    manager.ADMIN_METAROLE = UserMetarole(ADMIN, 'Администратор')
    manager.ADMIN_METAROLE.included_metaroles.extend([manager.GENERIC_USER_METAROLE])

    # метароль супер-администратора системы
    manager.SUPER_ADMIN_METAROLE = UserMetarole(SUPER_ADMIN, 'Супер-администратор')
    manager.SUPER_ADMIN_METAROLE.included_metaroles.extend([manager.GENERIC_USER_METAROLE, manager.ADMIN_METAROLE])

    return [manager.GENERIC_USER_METAROLE, manager.ADMIN_METAROLE, manager.SUPER_ADMIN_METAROLE]
