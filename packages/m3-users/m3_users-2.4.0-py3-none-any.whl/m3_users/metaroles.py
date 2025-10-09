# coding:utf-8
u"""
Метароли пользователей
======================

На уровне Платформы объявлены следующие метароли:

 - Супер-администратор -- может создавать других администраторов и назначать им
   права доступа
 - Администратор -- выполняет административные функции
 - Обобщенный пользователь -- любой пользователь системы

.. Created on 17.06.2010

.. @author: akvarats
"""

import logging
import threading

from m3 import (
    property_json_encode,
)
from m3.actions.packs import (
    BaseDictionaryActions,
)
from m3.plugins import (
    get_callables_from_modules,
)


class UserMetarole(object):
    u"""
    Класс, описывающий метароль пользователя
    """

    def __init__(self, metarole_code, metarole_name):
        #: кодовое обозначение метароли пользователя
        self.code = metarole_code
        #: название метароли пользователя
        self.name = metarole_name
        #: список метаролей, дети данной метароли
        self.included_metaroles = []

    @property_json_encode
    def id(self):
        u"""
        геттер необходим для лучшей маскировки объекта Метароли под объект
        обычной модели (критично для некоторых операций Dict_Pack'ов)
        """
        return self.code

    def get_owner_metaroles(self):
        u"""
        Возвращает список метаролей в которые входит наша метароль. Проще
        говоря список родителей, ребенком которых является наша метароль.
        """
        result = []
        # TODO: может сразу исключить self из запроса?
        for role in metarole_manager._metaroles.values():
            if (role != self) and (self in role.included_metaroles):
                result.append(role)
        return result

    def __str__(self):
        """ Более наглядное представление для отладки """
        return u'%s: %s at %s' % (self.code, self.name, id(self))


class MetaroleManager(object):
    u"""
    Менеджер метаролей пользователя
    """

    def __init__(self):
        self._loaded = False
        self._write_lock = threading.RLock()
        self._metaroles = {}

    def register_metarole(self, metarole):
        u"""
        Регистрирует метароль в менеджере ролей
        """
        self._metaroles[metarole.code] = metarole

    def get_metarole(self, code):
        u"""
        Возвращает экземпляр метароли по коду
        """
        self._populate()
        return self._metaroles.get(code)

    def get_registered_metaroles(self):
        u"""
        Возвращает экземпляры всех зарегистроированных в системе метаролей
        """
        self._populate()
        return sorted(
            self._metaroles.values(), key=lambda metarole: metarole.name
        )

    def _populate(self):
        u"""
        Собирает метароли по объявленным приложениям
        """
        if self._loaded:
            return
        self._write_lock.acquire()
        try:
            if self._loaded:
                return

            procs = get_callables_from_modules('app_meta', 'register_metaroles')

            for proc in procs:
                metaroles = proc(self)
                if metaroles:
                    for metarole in metaroles:
                        if isinstance(metarole, UserMetarole):
                            self.register_metarole(metarole)

            self._loaded = True
        except:
            logging.exception(
                u'Не удалось выполнить метод _populate у MetaroleManager'
            )
            raise
        finally:
            self._write_lock.release()


#------------------------------------------------------------------------------ 
# метароль обобщенного пользователя системы
# данная роль включается во все остальные метароли системы
#------------------------------------------------------------------------------ 
#GENERIC_USER_METAROLE = UserMetaRole('generic-user', u'Обобщенный пользователь')
#------------------------------------------------------------------------------
# метароль администратора системы.
# поглощает роль GENERIC_USER_METAROLE
#------------------------------------------------------------------------------ 
#ADMIN_METAROLE = UserMetaRole('admin', u'Администратор системы')
#ADMIN_METAROLE.included_metaroles.append(GENERIC_USER_METAROLE)
#------------------------------------------------------------------------------ 
# метароль супер администора системы.
# поглощает роли GENERIC_USER_METAROLE и ADMIN_METAROLE
#------------------------------------------------------------------------------ 
#SUPER_ADMIN_METAROLE = UserMetaRole('super-admin', u'Супер-администратор системы')
#SUPER_ADMIN_METAROLE.included_metaroles.append(GENERIC_USER_METAROLE)
#SUPER_ADMIN_METAROLE.included_metaroles.append(ADMIN_METAROLE)

metarole_manager = MetaroleManager()
#metarole_manager.register_metarole(SUPER_ADMIN_METAROLE)
#metarole_manager.register_metarole(ADMIN_METAROLE)
#metarole_manager.register_metarole(GENERIC_USER_METAROLE)

get_metarole = metarole_manager.get_metarole
get_metaroles = metarole_manager.get_registered_metaroles


#===============================================================================
# Пакет действий для метаролей
#===============================================================================

class Metaroles_DictPack(BaseDictionaryActions):
    u"""
    Пакет действий с метаролями
    """
    url = '/metarole'
    title = u'Метароли системы'
    list_columns = [('name', u'Наименование метароли')]
    list_readonly = True

    # TODO: многие параметры не используются. тогда зачем они?
    # TODO: вместо find, нельзя ли использовать in?
    def get_rows(self, offset, limit, filter_, user_sort=''):
        data = []
        for role in metarole_manager.get_registered_metaroles():
            if filter_:
                # Регистронезависимое вхождение строки
                if role.name.upper().find(filter_.upper()) != -1:
                    data.append(role)
            else:
                data.append(role)
        return {'rows': data}

    def get_row(self, id):
        u"""
        возвращает метароль по id
        """
        return metarole_manager.get_metarole(id)

    def get_select_window(self, win):
        u"""
        возвращает окно выбора метароли

        .. note:: Доступно 1 событие: выбор с присвоением значения вызвавшему контролу
        """
        win.column_name_on_select = 'name'
        return win
