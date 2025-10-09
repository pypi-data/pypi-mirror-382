# -*- coding: utf-8 -*-
from __future__ import absolute_import
import warnings

from m3_ext.ui import windows, panels, controls, fields

from . import metaroles


class RolesListWindow(windows.ExtWindow):
    def __init__(self, *args, **kwargs):
        super(RolesListWindow, self).__init__(*args, **kwargs)

        self.title = u'Роли пользователей'
        self.layout = 'fit'
        self.width = 540
        self.height = 500
        self.template_globals = 'm3-users/roles-list-window.js'

        # Настройка грида со списком ролей
        self.grid = panels.ExtObjectGrid()

        self.init_component(*args, **kwargs)

    def configure_grid(self, **params):
        self.grid.add_column(
            header=u'Наименование роли', data_index='name', width=300)
        self.grid.add_column(
            header=u'Метароль', data_index='metarole_name', width=240)
        self.items.append(self.grid)

        self.grid.url_data = params.get('url_data', None)
        self.grid.url_new = params.get('url_new', None)
        self.grid.url_edit = params.get('url_edit', None)
        self.grid.url_delete = params.get('url_delete', None)
        self.grid.top_bar.button_new.text = u'Добавить новую роль'
        self.grid.top_bar.items.append(
            controls.ExtButton(
                text=u'Показать пользователей',
                icon_cls='search',
                handler='contextMenu_ShowAssignedUsers'))
        self.grid.row_id_name = 'userrole_id'

        warnings.warn(
            "Attribute 'action_show_assigned_users' is deprecated. "
            "Use 'show_assigned_users_url'", FutureWarning)
        self.grid.action_show_assigned_users = params.get(
            'show_assigned_users', None)
        # дополнительные действия формы
        self.grid.show_assigned_users_url = params.get(
            'url_show_assigned_users', None)

        self.grid.context_menu_row.add_item(
            text=u'Показать пользователей',
            icon_cls='user-icon-16',
            handler='contextMenu_ShowAssignedUsers')
        self.grid.context_menu_row.add_separator()


class RolesEditWindow(windows.ExtEditWindow):
    """
    Окно редактирования роли
    """

    def __init__(self, new_role=False, *args, **kwargs):
        super(RolesEditWindow, self).__init__(*args, **kwargs)

        from . import app_meta

        self.width = 500
        self.height = 400
        self.modal = True

        self.new_role = new_role

        self.template_globals = 'm3-users/edit-role-window.js'

        self.title = u'Роль пользователя'
        self.layout = 'border'
        self.form = panels.ExtForm(
            layout='form', region='north',
            height=60, style={'padding': '5px'})
        self.form.label_width = 100

        field_name = fields.ExtStringField(
            name='name', label=u'Наименование',
            allow_blank=False, anchor='100%')
        field_metarole = fields.ExtDictSelectField(
            name='metarole', label=u'Метароль',
            anchor='100%', hide_trigger=False)
        field_metarole.configure_by_dictpack(
            metaroles.Metaroles_DictPack, app_meta.users_controller)
        field_metarole.editable = False
        field_metarole.hide_dict_select_trigger = True

        self.form.items.extend([field_name, field_metarole])

        self.grid = panels.ExtObjectGrid(
            title=u"Права доступа", region="center")

        self.items.append(self.grid)

        self.buttons.extend([
            controls.ExtButton(text=u'Сохранить', handler='submitForm'),
            controls.ExtButton(text=u'Отмена', handler='cancelForm')
        ])

    def configure_window(self, user_role, **params):
        self.form.url = params.get('form_url')
        self.form.from_object(user_role)
        self._configure_grid(**params)

    def _configure_grid(self, **params):
        self.grid.url_data = params.get('url_data', None)
        self.grid.url_new = params.get('url_new', None)
        self.grid.top_bar.items.append(controls.ExtButton(
            text=u'Удалить',
            icon_cls='delete_item', handler='deletePermission'))
        self.grid.top_bar.button_refresh.hidden = True
        self.grid.force_fit = True
        self.grid.allow_paging = False
        self.grid.row_id_name = 'permission_code'
        self.grid.store.id_property = 'permission_code'
        self.grid.store.auto_save = False
        self.grid.add_column(header=u'Разрешенные права',
                             data_index='verbose_name', width=100)
        self.grid.add_bool_column(header=u'Запрет', data_index='disabled',
                                  width=50, text_false=u'Нет',
                                  text_true=u'Да', hidden=True)
