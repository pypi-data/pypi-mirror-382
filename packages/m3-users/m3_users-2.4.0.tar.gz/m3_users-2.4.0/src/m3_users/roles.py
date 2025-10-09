# coding: utf-8

"""
Created on 11.06.2010

@author: akvarats
"""

import inspect
import logging

from m3.actions import ACD
from m3.actions import Action
from m3.actions import ActionContext
from m3.actions import ActionPack
from m3.actions import ControllerCache
from m3.actions import urls
from m3.actions.packs import BaseDictionaryModelActions
from m3.actions.results import JsonResult
from m3.actions.results import OperationResult
from m3.actions.results import PreJsonResult
from m3.db import queryset_limiter
from m3.db import safe_delete
from m3_ext.ui import controls
from m3_ext.ui import fields
from m3_ext.ui import helpers as ui_helpers
from m3_ext.ui import panels
from m3_ext.ui import windows
from m3_ext.ui.containers import ExtTree
from m3_ext.ui.containers import ExtTreeNode
from m3_ext.ui.fields.complex import ExtSearchField
from m3_ext.ui.results import ExtGridDataQueryResult
from m3_ext.ui.results import ExtUIScriptResult

from . import api
from . import helpers
from . import models
from .ui import RolesEditWindow
from .ui import RolesListWindow
from .users import SelectUsersListWindow


try:
    from m3_audit.manager import AuditManager
    from m3_audit.models import RolesAuditModel

    _M3_AUDIT_INSTALLED = True
except ImportError:
    _M3_AUDIT_INSTALLED = False


class RolesActions(ActionPack):
    """
    Пакет действий для подсистемы прав пользователей.
    """

    url = '/roles'

    list_win = RolesListWindow
    edit_win = RolesEditWindow
    select_win = SelectUsersListWindow

    need_check_permission = True

    def __init__(self):
        super(RolesActions, self).__init__()

        self.roles_window_action = RolesWindowAction()
        self.edit_role_window_action = EditRoleWindowAction()
        self.save_role_action = SaveRoleAction()
        self.delete_role_action = DeleteRoleAction()
        # показ окна со списком пользователей, ассоциированных с ролью
        self.show_assigned_users_action = ShowAssignedUsersAction()
        # получение списка пользователей, ассоциированных с ролью
        self.role_assigned_users_data_action = RoleAssignedUsersDataAction()
        # получение окна со списком пользователей,
        # которые можно добавить в роль
        self.select_users_to_assign_window = SelectUsersToAssignWindowAction()
        # получение списка пользователей,
        # которых можно включить в заданную роль
        self.users_for_role_assignment_data = UsersForRoleAssignmentData()
        self.roles_data_action = RolesDataAction()
        # действие на добавление пользователей в роль
        self.assign_users = AssignUsers()
        # удаление связанного с ролью пользователя
        self.delete_assigned_user = DeleteAssignedUser()
        # получение списка прав доступа роли
        self.get_role_permission_action = GetRolePermissionAction()
        # выбор прав доступа для добавления в роль
        self.add_role_permission = AddRolePermission()
        self.actions.extend([
            self.roles_window_action,
            self.edit_role_window_action,
            self.save_role_action,
            self.delete_role_action,
            self.show_assigned_users_action,
            self.role_assigned_users_data_action,
            self.select_users_to_assign_window,
            self.users_for_role_assignment_data,
            self.roles_data_action,
            self.assign_users,
            self.delete_assigned_user,
            self.get_role_permission_action,
            self.add_role_permission
        ])

    def _get_list_win_grid_urls(self):
        return {
            'url_data': self.roles_data_action.get_absolute_url(),
            'url_new': self.edit_role_window_action.get_absolute_url(),
            'url_edit': self.edit_role_window_action.get_absolute_url(),
            'url_delete': self.delete_role_action.get_absolute_url(),
            'url_show_assigned_users': (
                self.show_assigned_users_action.get_absolute_url()),
            'show_assigned_users': self.show_assigned_users_action
        }

    def create_list_win(self):
        win = self.list_win()

        params = self._get_list_win_grid_urls()
        win.configure_grid(**params)

        return win

    def _get_edit_win_params(self):
        return {
            'url_data': self.get_role_permission_action.get_absolute_url(),
            'url_new': self.add_role_permission.get_absolute_url(),
            'form_url': self.save_role_action.get_absolute_url()
        }

    def create_edit_win(self, new_role, user_role):
        win = self.edit_win(new_role=new_role)

        params = self._get_edit_win_params()
        win.configure_window(user_role, **params)

        return win

    def create_select_win(self, role):
        win = self.select_win()
        win.grid.url_data = (
            self.users_for_role_assignment_data.get_absolute_url())
        win.grid.title = u"Выберите пользователей для роли '%s'" % role.name
        win.action_submit = self.assign_users

        return win


# =============================================================================
# UI actions
# - RolesWindowAction -- получение окна со списком ролей
# - EditRoleWindowAction -- получение окна редактирования роли
# =============================================================================
class RolesWindowAction(Action):
    """
    Действие на получение окна показа списка пользовательских ролей
    """
    url = '/roles-window'

    def run(self, request, context):
        win = self.parent.create_list_win()

        return ExtUIScriptResult(data=win)


class EditRoleWindowAction(Action):
    """
    Получение окна редактирования роли пользователя
    """

    url = '/edit-role-window'
    need_check_permission = True
    verbose_name = u'Добавление и редактирование роли'

    def context_declaration(self):
        return [ACD(name=u'userrole_id', type=int, required=True, default=0)]

    def run(self, request, context):

        new_role = True
        if context.userrole_id:
            new_role = False
            try:
                user_role = models.UserRole.objects.get(pk=context.userrole_id)
            except models.UserRole.DoesNotExist:
                return OperationResult(
                    success=False,
                    message=u'Роль с указанным идентификатором не найдена')
        else:
            user_role = models.UserRole()

        win = self.parent.create_edit_win(new_role, user_role)

        return ExtUIScriptResult(data=win)


class ShowAssignedUsersAction(Action):
    """
    Получение окна со списком связанных пользователей.
    """

    url = '/role-assigned-users-window'

    def context_declaration(self):
        return [
            ACD(name='userrole_id', type=int, required=True),
        ]

    def run(self, request, context):
        window = AssignedUsersWindow()
        role = models.UserRole.objects.get(id=context.userrole_id)
        window.field_role_name.value = role.name

        return ExtUIScriptResult(window)


class SelectUsersToAssignWindowAction(Action):
    """
    Показ окна с выбором сотрудников,
    которые не были выбраны ранее для указанной роли.

    """

    url = '/role-assigned-users-append-window'
    need_check_permission = True
    verbose_name = u'Добавление пользователя роли'

    def context_declaration(self):
        return [
            ACD(name='userrole_id', type=int, required=True)
        ]

    def run(self, request, context):
        role = models.UserRole.objects.get(id=context.userrole_id)

        win = self.parent.create_select_win(role)

        return ExtUIScriptResult(win)


class AddRolePermission(Action):
    """
    Выбор прав доступа для добавления в роль
    """
    url = '/role-add-permission-window'
    need_check_permission = True
    verbose_name = u'Добавление прав'

    def context_declaration(self):
        return {
            'perms': {
                'type': 'str_list',
                'default': [],
            },
        }

    def run(self, request, context):
        window = SelectPermissionWindow(action_context=context,)
        return ExtUIScriptResult(window)


# =============================================================================
# DATA actions
# =============================================================================
class RolesDataAction(Action):
    url = '/roles-data'

    def context_declaration(self):
        return [
            ACD(name='filter', type=str, required=True, default=''),
            ACD(name='start', type=int, required=True, default=0),
            ACD(name='limit', type=int, required=True, default=25),
        ]

    def run(self, request, context):
        return JsonResult(
            ui_helpers.paginated_json_data(
                helpers.get_roles_query(context.filter),
                context.start, context.limit)
        )


class RoleAssignedUsersDataAction(Action):
    """
    Получение данных (списка) пользователей,
    которые прикреплены к указанной роли.

    """

    url = '/role-users'

    def context_declaration(self):
        return [
            ACD(name='userrole_id', type=int, required=True),
            ACD(name='filter', type=str, requeired=False),
            ACD(name='start', type=int, required=True),
            ACD(name='limit', type=int, required=True)
        ]

    def run(self, request, context):
        filter = getattr(context, 'filter', None)
        return ExtGridDataQueryResult(
            helpers.get_assigned_users_query(context.userrole_id, filter),
            context.start, context.limit
        )


class UsersForRoleAssignmentData(Action):
    """
    Получение списка пользователей, которые могут быть назначены на роль.

    """

    url = '/role-assign-users-unassigned'

    def context_declaration(self):
        return [
            ACD(name='userrole_id', type=int, required=True),
            ACD(name='filter', type=str, required=True, default=u''),
            ACD(name='start', type=int, required=True),
            ACD(name='limit', type=int, required=True)
        ]

    def run(self, request, context):
        users = helpers.get_unassigned_users(
            context.userrole_id, context.filter)
        rows, total = queryset_limiter(users, context.start, context.limit)
        return PreJsonResult({'rows': rows, 'total': total})


class GetRolePermissionAction(Action):
    """
    Получение списка прав доступа для указанной роли

    """

    url = '/role-permission-rows'

    def context_declaration(self):
        return [
            ACD(name='userrole_id', type=int, required=True),
        ]

    def run(self, request, context):
        perms = models.RolePermission.objects.filter(
            role=int(context.userrole_id))
        res = []
        for perm in perms:
            codes = str(perm.permission_code).split('#')
            act_code = codes[0]
            sub_code = codes[1] if len(codes) > 1 else ''
            act = ControllerCache.find_node_by_perm(act_code)
            if not act:
                # попробуем найти набор экшенов, если есть суб-код
                pack = urls.get_pack_by_url(act_code)
                if (sub_code
                        and pack and sub_code in pack.sub_permissions.keys()):
                    pack_name = pack.get_verbose_name()
                    perm.verbose_name = "%s - %s" % (
                        pack_name, pack.sub_permissions[sub_code])
                else:
                    # Объект права не найден - не показываем
                    continue
            else:
                if act.parent:
                    pack_name = act.parent.get_verbose_name()
                else:
                    pack_name = act.get_verbose_name()
                perm.verbose_name = '%s - %s' % (
                    pack_name,
                    act.verbose_name
                    if act.verbose_name else act.__class__.__name__)
                if sub_code:
                    if sub_code in act.sub_permissions:
                        perm.verbose_name = '%s - %s' % (
                            pack_name, act.sub_permissions[sub_code])
                    else:
                        # Не показываем, если наименование прав
                        # этого RolePermisson'a отсутствует
                        # в возможных правах objectpack'а
                        continue
            res.append(perm)
        res.sort(key=lambda o: o.verbose_name)
        return ExtGridDataQueryResult(res)


def get_all_permission_tree(permission_codes):
    """Общий подход к формированию дерева прав доступа (алгоритм):
    собирается список прав доступа исходя из наборов действий, действий,
    субправ наборов действий, субправ действий
    у каждого элемента списка прав должен быть путь в дереве (пока строкой),
    наименование права доступа, полное наименование права (для грида прав)
    путь в дереве строится из значения path элемента, а если он отсутствует,
    то по иерархии этого элемента в фактической структуре действий
    и набора действий.

    Args:
        permission_codes: Список активных кодов прав доступа (для активации чекбокса).
    Returns:
        Список прав доступа.
    """

    class PermProxy(ExtTreeNode):
        def __init__(self, id, parent=None, name='', url='', can_select=True,
                     fullname=None, path='', checked=False,):
            super(PermProxy, self).__init__()
            self.parent = parent
            if parent:
                parent.add_children(self)
            self.name = name
            self.path = path
            self.expanded = True
            self.items['name'] = name
            self.items['url'] = url
            self.items['fullname'] = fullname if fullname else name
            self.checked = checked
            self.can_check = can_select

    def find_node(node_name, parent_node, res):
        for item in res:
            if (item.parent == parent_node
                    and item.name.upper() == node_name.upper()):
                return item
        return None

    def add_path(path, res):
        """Добавление пути набора действий в дерево."""

        parent_node = None
        if path:
            items = path.strip().split("\\")
            for name in items:
                node = find_node(name, parent_node, res)
                if not node:
                    node = PermProxy(
                        len(res) + 1, parent_node, name, '', False)
                    res.append(node)
                parent_node = node
        return parent_node

    def get_action_sub_perm_path(action, sub_perm_code):
        result = ''
        if action:
            if sub_perm_code in action.sub_permissions.keys():
                path = action.sub_permissions[sub_perm_code]
                items = path.strip().split("\\")
                # если длина пути больше 1,
                # значит указали путь - выделим путь и имя
                if len(items) > 1:
                    name = items[-1]
                    items.remove(name)
                    result = '\\'.join(items)
                else:
                    # если нет пути, то построим путь по экшену
                    result = get_action_perm_path(action)
                    result = (
                            result
                            + ('\\' if result != '' else '')
                            + action.get_verbose_name()
                    )
        return result

    def get_action_perm_path(action):
        result = ''
        if action:
            # если указан путь,
            # то строится по этому пути, иначе по иерархии паков
            if action.path:
                result = action.path
            else:
                result = get_actionpack_perm_path(action.parent)
                result = (
                        result
                        + ('\\' if result != '' else '')
                        + action.parent.get_verbose_name()
                )
        return result

    def get_actionpack_sub_perm_path(actionpack, sub_perm_code):
        result = ''
        if actionpack:
            if sub_perm_code in actionpack.sub_permissions.keys():
                path = actionpack.sub_permissions[sub_perm_code]
                items = path.strip().split("\\")
                # если длина пути больше 1,
                # значит указали путь - выделим путь и имя
                if len(items) > 1:
                    name = items[-1]
                    items.remove(name)
                    result = '\\'.join(items)
                else:
                    # если нет пути, то построим путь по набору экшенов
                    result = get_actionpack_perm_path(actionpack)
                    result = (
                            result
                            + ('\\' if result != '' else '')
                            + actionpack.get_verbose_name()
                    )
        return result

    def get_actionpack_perm_path(actionpack):
        result = ''
        if actionpack:
            # если указан путь,
            # то строится по этому пути, иначе по иерархии паков
            if actionpack.path:
                result = actionpack.path
            else:
                if actionpack.parent:
                    result = get_actionpack_perm_path(actionpack.parent)
                    result = (
                            result
                            + ('\\' if result != '' else '')
                            + actionpack.parent.get_verbose_name()
                    )
        return result

    def add_nodes(parent_node, action_set, res, ctrl):
        # если передали Набор действий,
        # то у него надо взять Действия и подчиненные Наборы
        if isinstance(action_set, ActionPack):
            # обработаем действия
            if action_set.need_check_permission:
                for act in action_set.actions:
                    # добавляем если надо проверять права
                    # или есть подчиненные права
                    add_nodes(None, act, res, ctrl)
            # обработаем подчиненные права
            # добавляем если надо проверять права или есть подчиненные права
            if action_set.need_check_permission and action_set.sub_permissions:
                pack_name = action_set.get_verbose_name()
                for key, value in action_set.sub_permissions.items():
                    fullname = '%s - %s' % (pack_name, value)
                    path = get_actionpack_sub_perm_path(action_set, key)
                    url = action_set.get_sub_permission_code(key)
                    checked = url in permission_codes
                    if url not in res_urls.keys():
                        child4 = PermProxy(
                            len(res) + 1, None, value, url, True,
                            fullname, path, checked,)
                        res.append(child4)
                        res_urls[url] = child4
            # обработаем подчиненные Наборы
            for pack in action_set.subpacks:
                add_nodes(None, pack, res, ctrl)

        # если передали Действие
        elif isinstance(action_set, Action):
            if action_set.need_check_permission or action_set.sub_permissions:
                if inspect.isclass(action_set):
                    action_set = action_set()
                if action_set.parent:
                    pack = action_set.parent
                    pack_name = pack.get_verbose_name()
                else:
                    pack_name = ''

                name = action_set.get_verbose_name()
                fullname = '%s - %s' % (pack_name, name)
                if action_set.need_check_permission:
                    path = get_action_perm_path(action_set)
                    url = action_set.get_permission_code()
                    checked = url in permission_codes
                    if url not in res_urls.keys():
                        item = PermProxy(
                            len(res) + 1, None, name, url, True,
                            fullname, path, checked,)
                        res.append(item)
                        res_urls[url] = item
                # у действия берем подчиненные права
                for key, value in action_set.sub_permissions.items():
                    items = value.strip().split("\\")
                    # если длина пути больше 1,
                    # значит указали путь - выделим путь и имя
                    if len(items) > 1:
                        name = items[-1]
                        pack_name = items[-2]
                    else:
                        name = value
                    fullname = '%s - %s' % (pack_name, name)
                    path = get_action_sub_perm_path(action_set, key)
                    url = action_set.get_sub_permission_code(key)
                    checked = url in permission_codes
                    if not url in res_urls.keys():
                        child3 = PermProxy(
                            len(res) + 1, None, name, url,
                            True, fullname, path, checked,)
                        res.append(child3)
                        res_urls[url] = item

    res = []
    res_urls = {}
    # пройдемся по контроллерам
    for ctrl in ControllerCache.get_controllers():
        # пройдемся по верхним наборам действий
        for pack in ctrl.get_top_actions():
            add_nodes(None, pack, res, ctrl)

    # выстроим иерархию
    for item in res:
        if not item.parent:
            parent_node = add_path(item.path, res)
            if parent_node:
                parent_node.add_children(item)
                item.parent = parent_node
    # преобразуем список в дерево (оставим только корневые элементы)
    nodes = []
    for item in res:
        if not item.parent:
            nodes.append(item)
    return nodes


# =============================================================================
# OPERATIONS
# =============================================================================
class SaveRoleAction(Action):
    """Сохранение роли пользователя."""

    url = '/save-role'

    def context_declaration(self):
        return [
            ACD(name=u'userrole_id', type=int, required=True, default=0),
            ACD(name=u'perms', type=object, required=True, default=[])
        ]

    def run(self, request, context):
        try:
            if context.userrole_id > 0:
                try:
                    user_role = models.UserRole.objects.get(
                        id=context.userrole_id)
                except models.UserRole.DoesNotExist:
                    return OperationResult(
                        success=False,
                        message=u'Роль с указанным идентификатором не найдена')
            else:
                user_role = models.UserRole()
            context.user_role = user_role

            # аудит
            existing_permissions = self._get_existing_permissions(
                request, context)
            supplied_permissions = self._get_supplied_permissions(
                request, context)
            # end

            window = RolesEditWindow()
            window.form.bind_to_request(request)
            window.form.to_object(user_role)

            user_role.save()

            # сохраним также права доступа
            ids = []
            for perm in context.perms:
                code = perm['permission_code']
                q = models.RolePermission.objects.filter(
                    role=user_role, permission_code=code).all()
                if len(q) > 0:
                    perm_obj = q[0]
                else:
                    perm_obj = models.RolePermission(
                        role=user_role,
                        permission_code=perm['permission_code'])
                perm_obj.disabled = perm['disabled']
                perm_obj.save()

                ids.append(perm_obj.id)
            # удалим те, которые не обновились
            models.RolePermission.objects.filter(
                role=user_role).exclude(id__in=ids).delete()

            # аудит
            if _M3_AUDIT_INSTALLED:
                for i in self._added_permissions(
                        existing_permissions, supplied_permissions):
                    AuditManager().write(
                        'roles', user=request.user,
                        role=user_role,
                        permission_or_code=i.permission_code,
                        type=RolesAuditModel.PERMISSION_ADDITION)
                for i in self._deleted_permissions(
                        existing_permissions, supplied_permissions):
                    AuditManager().write(
                        'roles', user=request.user,
                        role=user_role,
                        permission_or_code=i.permission_code,
                        type=RolesAuditModel.PERMISSION_REMOVAL)
                    # end
        except:
            msg = u'Не удалось сохранить роль пользователя'
            logging.exception(msg)
            return OperationResult(success=False, message=msg)

        return OperationResult(success=True)

    def _get_role(self, request, context):
        if context.userrole_id > 0:
            try:
                user_role = models.UserRole.objects.get(id=context.userrole_id)
            except models.UserRole.DoesNotExist:
                return OperationResult(
                    success=False,
                    message=u'Роль с указанным идентификатором не найдена')
        else:
            user_role = models.UserRole()
        # только два скоупа в питоне ))
        return user_role

    def _get_existing_permissions(self, request=None, context=None):
        return models.RolePermission.objects.filter(role=context.user_role)

    # Есть копипаста
    def _get_supplied_permissions(self, request, context):
        result = []
        for perm in context.perms:
            code = perm['permission_code']
            q = models.RolePermission.objects.filter(
                role=context.user_role, permission_code=code).all()
            if len(q) > 0:
                perm_obj = q[0]
            else:
                perm_obj = models.RolePermission(
                    role=context.user_role,
                    permission_code=perm['permission_code'])
            perm_obj.disabled = perm['disabled']

            result.append(perm_obj)
        return result

    def _added_permissions(self, existing, supplied):
        result = list(supplied)
        for e in existing:
            for s in supplied:
                if e.id == s.id:
                    result.remove(s)
        return result

    def _deleted_permissions(self, existing, supplied):
        result = list(existing)
        for e in existing:
            for s in supplied:
                if e.id == s.id:
                    result.remove(e)
        return result


class DeleteRoleAction(Action):
    url = '/delete-role'
    need_check_permission = True
    verbose_name = u'Удаление роли'

    def context_declaration(self):
        return [
            ACD(name=u'userrole_id', type=int, required=True)
        ]

    def run(self, request, context):
        try:
            user_role = models.UserRole.objects.get(id=context.userrole_id)
        except models.UserRole.DoesNotExist:
            return OperationResult(
                success=False,
                message=u'Роль с указанным идентификатором не найдена')

        if len(helpers.get_assigned_users_query(user_role)) > 0:
            return OperationResult(
                success=False,
                message=u'К данной роли привязаны пользователи. '
                        u'Удалять такую роль нельзя')

        try:
            if not safe_delete(user_role):
                # FIXME: return в try - это зло
                return OperationResult(
                    success=False,
                    message=u'Не удалось удалить роль пользователя.'
                            u'<br>На эту запись есть ссылки в базе данных.')
        except:
            msg = (
                u'Не удалось удалить роль пользователя. '
                u'Подробности в логах системы.')
            logging.exception(msg)
            return OperationResult(success=False,
                                   message=msg)

        return OperationResult(success=True)


class AssignUsers(Action):
    """Сопоставление пользователей роли."""

    url = '/assign-users-to-role'

    def context_declaration(self):
        return [
            ACD(name='userrole_id', type=int, required=True),
            ACD(name='ids', type=str, required=True),
        ]

    def run(self, request, context):
        # получаем список пользователей,
        # которые уже были ассоциированы с ролью

        try:

            user_ids = context.ids.strip().split(' ')
            for strid in user_ids:
                if not strid:
                    continue
                try:
                    user_id = int(strid)
                    api.set_user_role(user_id, context.userrole_id)
                except ValueError:
                    logging.warning(u'Не верный user id %s' % strid)
                    continue

        except:
            msg = u'Не удалось добавить список пользователей в роль'
            logging.exception(msg)
            return OperationResult(success=False, message=msg)
        return OperationResult(success=True, )


class DeleteAssignedUser(Action):
    """Удаление связанного с ролью пользователя."""

    url = '/delete-assigned-user'
    need_check_permission = True
    verbose_name = u'Удаление пользователя роли'

    def context_declaration(self):
        return [
            ACD(name='assigneduser_id',
                type=ActionContext.ValuesList(), required=True)
        ]

    def run(self, request, context):
        for assigneduser_id in context.assigneduser_id:
            try:
                assigned_user = models.AssignedRole.objects.get(
                    id=assigneduser_id)
            except models.AssignedRole.DoesNotExist:
                return OperationResult(
                    success=False,
                    message=u'Не удалось удалить запись. '
                            u'Указанный пользователь не найден.')

            try:
                api.remove_user_role(assigned_user.user, assigned_user.role)
            except Exception:
                msg = (
                    u'Не удалось удалить запись. Подробности в логах системы.')
                logging.exception(msg)
                return OperationResult.by_message(msg)

        return OperationResult()


# =============================================================================
# UI
# =============================================================================
class AssignedUsersWindow(windows.ExtWindow):
    """
    Окно просмотра пользователей, которые включены в данную роль.

    """

    def __init__(self, *args, **kwargs):
        super(AssignedUsersWindow, self).__init__(*args, **kwargs)
        self.title = u'Пользователи, с указанной ролью'
        self.width = 700
        self.height = 400
        self.modal = True

        self.layout = 'border'
        self.panel_north = panels.ExtForm(
            layout='form', region='north', height=40, label_width=50,
            style={'padding': '5px'})
        self.panel_center = panels.ExtPanel(
            layout='fit', region='center', body_cls='x-window-mc',
            title=u'Пользователи с данной ролью', style={'padding': '5px'})

        self.items.extend([
            self.panel_north,
            self.panel_center,
        ])

        # настройка северной панели
        self.field_role_name = fields.ExtStringField(
            name='role-name', label=u'Роль', anchor='100%', read_only=True)
        self.panel_north.items.append(self.field_role_name)

        # настройка центральной панели
        self.grid_users = panels.ExtObjectGrid()
        self.grid_users.allow_paging = False
        self.grid_users.add_column(
            header=u'Логин', data_index='user_login', width=100)
        self.grid_users.add_column(
            header=u'Фамилия', data_index='user_last_name', width=200)
        self.grid_users.add_column(
            header=u'Имя', data_index='user_first_name', width=200)
        self.grid_users.add_column(
            header=u'E-mail', data_index='user_email', width=200)
        self.grid_users.action_data = RoleAssignedUsersDataAction

        search_text_grid = ExtSearchField(
            empty_text=u'Поиск',
            component_for_search=self.grid_users)
        self.grid_users.top_bar.add_fill()
        self.grid_users.top_bar.items.append(search_text_grid)

        self.grid_users.allow_paging = True

        self.grid_users.action_new = SelectUsersToAssignWindowAction

        self.grid_users.action_delete = DeleteAssignedUser
        self.grid_users.top_bar.button_new.text = u'Добавить пользователей'
        self.grid_users.context_menu_grid.menuitem_new.text = (
            u'Добавить пользователей')
        self.grid_users.context_menu_row.menuitem_new.text = (
            u'Добавить пользователей')
        self.grid_users.context_menu_row.menuitem_delete.text = (
            u'Удалить пользователя из роли')
        self.grid_users.row_id_name = 'assigneduser_id'
        self.panel_center.items.append(self.grid_users)

        self.buttons.append(
            controls.ExtButton(text=u'Закрыть', handler='closeWindow'))


class SelectPermissionWindow(windows.ExtEditWindow):
    """
    Окно выбора прав доступа для добавления в роль.

    """

    def __init__(self, *args, **kwargs):
        super(SelectPermissionWindow, self).__init__(*args, **kwargs)
        self.title = u'Выберите права доступа для роли'
        self.width = 600
        self.height = 500
        self.maximizable = True
        self.layout = 'fit'
        self.tree = ExtTree()
        self.tree.add_column(header=u'Имя', data_index='name', width=140)
        self.tree.master_column_id = 'name'
        self.tree.nodes = get_all_permission_tree(self.action_context.perms)
        self.items.append(self.tree)
        self.buttons.append(controls.ExtButton(
            text=u'Выбрать', handler='''function select(btn, e, baseParams) {
            var tree = Ext.getCmp('%s');
            var records = tree.getChecked();
            win.fireEvent('closed_ok', records);
            win.close(true);
        }''' % self.tree.client_id))
        self.buttons.append(
            controls.ExtButton(text=u'Отмена', handler='cancelForm'))


# =============================================================================
# Справочник "Роли пользователей"
# =============================================================================
class Roles_DictPack(BaseDictionaryModelActions):
    """
    Справочник "Роли пользователей".

    Используется для выбора значений.
    """

    need_check_permission = True

    url = '/roles-dict'
    shortname = 'user-roles-dictpack'
    model = models.UserRole
    title = u'Роли пользователей системы'
    list_columns = [('name', u'Наименование'), ]
    edit_window = RolesEditWindow
    filter_fields = ['name']
    list_readonly = True  # справочник - только для выбора из него
