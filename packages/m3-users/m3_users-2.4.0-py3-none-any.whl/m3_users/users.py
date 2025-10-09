# coding:utf-8
u"""
Паки и действия для работы с пользователями
===========================================

.. Created on 11.06.2010

.. @author: akvarats
"""

from m3.actions import Action, ActionPack, ACD
from m3.actions.results import JsonResult

from m3_ext.ui import windows
from m3_ext.ui import panels
from m3_ext.ui import controls
from m3_ext.ui.helpers import paginated_json_data

from .helpers import get_users_query


class UsersActions(ActionPack):
    u"""
    Пакет действий для пользователей системы.
    """

    need_check_permission = True

    def __init__(self):
        super(UsersActions, self).__init__()
        self.actions = [
            UsersDataAction(),
        ]


class UsersDataAction(Action):
    u"""
    Получение списка пользователей
    """
    url = '/users-data'

    def context_declaration(self):
        return [
            ACD(name='filter', type=int, required=True, default=''),
            ACD(name='start', type=int, required=True, default=0),
            ACD(name='limit', type=int, required=True, default=25),
        ]

    def run(self, request, context):
        return JsonResult(paginated_json_data(get_users_query(context.filter), context.start, context.limit))


class SelectUsersListWindow(windows.ExtWindow):
    u"""
    Окно со списком пользователей
    """

    def __init__(self, *args, **kwargs):
        super(SelectUsersListWindow, self).__init__(*args, **kwargs)
        self.title = u'Выберите пользователей'
        self.width = 600
        self.height = 400
        self.layout = 'fit'
        self.modal = True
        self.template_globals = 'm3-users/select-users-window.js'

        self.grid = panels.ExtObjectGrid(sm=panels.ExtGridCheckBoxSelModel())
        self.grid.add_column(header=u'Логин', data_index='username', width=150)
        self.grid.add_column(header=u'Фамилия', data_index='last_name', width=150)
        self.grid.add_column(header=u'Имя', data_index='first_name', width=150)
        self.grid.add_column(header=u'E-mail', data_index='email', width=150)

        self.items.append(self.grid)

        self.buttons.extend([
            controls.ExtButton(text='OK', handler='appendUsers'),
            controls.ExtButton(text='Отмена', handler='closeWindow'),
        ])
