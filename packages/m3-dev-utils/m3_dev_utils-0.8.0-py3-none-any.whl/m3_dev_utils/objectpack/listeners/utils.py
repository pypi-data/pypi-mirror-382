# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from inspect import isclass

from django.utils.safestring import mark_safe
from six import iteritems

from m3_dev_utils import get_config
from m3_dev_utils.utils.misc import cached_property
from m3_dev_utils.utils.misc import get_full_class_name
from m3_dev_utils.utils.objectpack import get_listener_actions


class ActionInfo(object):

    """Класс для хранения информации о действиях M3."""

    def __init__(self, action):
        """Инициализация экземпляра класса.

        :param actions: Прослушиваемое действия M3.
        :type: tuple of m3.actions.Action
        """
        self.action = action

    @cached_property
    def name(self):
        return mark_safe(
            get_full_class_name(self.action, class_tag='b')
        )

    def as_dict(self):
        """Возвращает данные о действии M3 в виде словаря.

        :rtype: dict
        """
        return dict(
            name=self.name,
        )


class PackInfo(object):

    """Класс для хранения информации о наборах прослушиваемых действий M3."""

    def __init__(self, pack, actions):
        """Инициализация экземпляра класса.

        :param pack: Набор действий M3.
        :type pack: m3.actions.ActionPack

        :param actions: Прослушиваемые действия M3 в указанном наборе действий.
        :type: tuple of m3.actions.Action
        """
        assert all(action.parent is pack for action in actions), actions

        self.pack = pack
        self._actions = actions

    @cached_property
    def full_name(self):
        """Полное имя класса набора действий..

        :rtype: str
        """
        return mark_safe(
            get_full_class_name(self.pack, class_tag='b')
        )

    @cached_property
    def actions(self):
        """Информация о действиях M3 в наборе действий.

        :rtype: tuple of ActionInfo
        """
        return tuple(
            ActionInfo(action)
            for action in self._actions
        )

    def as_dict(self):
        """Возвращает данные о наборе действий M3 в виде словаря.

        :rtype: dict
        """
        return dict(
            name=self.full_name,
            actions=tuple(
                action_info.as_dict()
                for action_info in self.actions
            ),
        )


class ListenInfo(object):

    """Класс для хранения информации о прослушиваемых действиях M3."""

    def __init__(self, listen_re):
        self.listen_re = listen_re

    @cached_property
    def packs(self):
        """Информация о наборах (packs) прослушиваемых действий M3."""
        listener_actions = get_listener_actions(
            self.listen_re, get_config().observer
        )

        return tuple(
            PackInfo(pack, actions)
            for pack, actions in iteritems(listener_actions)
        )

    def _has_no_actions(self):
        """Возвращает True, если не прослушивается ни одного действия M3.

        :rtype: bool
        """
        for pack_info in self.packs:
            if pack_info.actions:
                return False

        return True

    @cached_property
    def warnings(self):
        """Возвращает сообщения с предупреждениями об ошибках в слушателе.

        Перечень проверок:

            1. Наличие хотя бы одного действия M3, которое соответствует
               регулярному выражению.
        """
        check_list = (
            (self._has_no_actions,
             'Регулярному выражению не соответствует ни одного действия в '
             'системе.'),
        )

        return tuple(
            message
            for check, message in check_list
            if check()
        )

    def as_dict(self):
        """Возвращает данные о прослушиваемых действиях M3 в виде словаря.

        :rtype: dict
        """
        return dict(
            name=self.listen_re,
            warnings=self.warnings,
            packs=tuple(
                pack_info.as_dict()
                for pack_info in self.packs
            )
        )


class ListenerInfo(object):

    """Класс для хранения информации о слушателе и её проверке."""

    def __init__(self, listener_class, priority):
        """Инициализация экземпляра класса.

        :param type listener_class: Класс слушателя.
        :param int priority: Приоритет слушателя.
        """
        assert isclass(listener_class), listener_class

        self.listener_class = listener_class
        self.priority = priority

    @cached_property
    def full_name(self):
        """Полное имя класса слушателя.

        :rtype: str
        """
        return mark_safe(
            get_full_class_name(self.listener_class, class_tag='b')
        )

    @cached_property
    def listen(self):
        """Информация о прослушиваемых действиях M3.

        :rtype: tuple of ListenInfo
        """
        result = None
        if (
            hasattr(self.listener_class, 'listen') and
            self.listener_class.listen
        ):
            result = tuple(
                ListenInfo(listen)
                for listen in self.listener_class.listen
            )
        return result

    def _has_no_actions(self):
        """Возвращает True, если не прослушивается ни одного действия M3.

        :rtype: bool
        """
        if not self.listen:
            return False  # Прослушиваются все действия

        for listen_info in self.listen:
            for pack_info in listen_info.packs:
                if pack_info.actions:
                    return False

        return True

    @cached_property
    def warnings(self):
        """Возвращает сообщения с предупреждениями об ошибках в слушателе.

        Перечень проверок:

            1. Наличие хотя бы одного прослушиваемого действия M3.

        :rtype: tuple of unicode
        """
        check_list = (
            (self._has_no_actions,
             'Слушатель не прослушивает ни одного действия в системе.'),
        )

        return tuple(
            message
            for check, message in check_list
            if check()
        )

    def as_dict(self):
        """Возвращает данные о слушателе в виде словаря.

        :rtype: dict
        """
        result = dict(
            name=self.full_name,
            priority=self.priority,
            warnings=self.warnings,
        )

        if self.listen:
            result['listen'] = tuple(
                listen.as_dict()
                for listen in self.listen
            )
        else:
            result['listen'] = dict(
                name='Слушает все действия M3',
                packs=(),
            )

        return result
