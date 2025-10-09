# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from m3.actions.results import PreJsonResult
from objectpack.actions import BaseAction
from objectpack.actions import BasePack
from objectpack.actions import BaseWindowAction

from m3_dev_utils import get_config
from m3_dev_utils.utils.objectpack import get_listeners

from .ui import Window
from .utils import ListenerInfo


class WindowAction(BaseWindowAction):

    """Отображение окна с информацией о слушателях системы."""

    def create_window(self):
        self.win = Window()

    def set_window_params(self):
        super(WindowAction, self).set_window_params()

        self.win_params['data_url'] = (
            self.parent.data_action.get_absolute_url()
        )


class DataAction(BaseAction):

    """Отдает данные о слушателях Системы."""

    def run(self, request, context):
        config = get_config()

        data = tuple(
            ListenerInfo(listener, priority).as_dict()
            for priority, (_, listener) in get_listeners(config.observer)
        )

        return PreJsonResult(data)


class Pack(BasePack):

    """Пак окна просмотра сведений о слушателях ``objectpack``."""

    def __init__(self):
        super(Pack, self).__init__()

        self.window_action = WindowAction()
        self.data_action = DataAction()

        self.actions.extend((
            self.window_action,
            self.data_action,
        ))

    def extend_menu(self, menu):
        return menu.SubMenu(
            'Инструменты разработчика',
            menu.Item(
                'Слушатели objectpack',
                self.window_action,
            )
        )
