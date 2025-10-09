# coding: utf-8
"""Инструментарий разработчика веб-приложений на платформе M3."""
from __future__ import absolute_import
from __future__ import unicode_literals

import abc

from six import with_metaclass


class Config(with_metaclass(abc.ABCMeta, object)):

    """Конфигурация приложения."""

    @abc.abstractproperty
    def controller(self):
        """Контроллер, в котором будут регистрироваться паки приложения.

        :rtype: :class:`m3.actions.ActionController`
        """

    @abc.abstractproperty
    def observer(self):
        """Наблюдатель objectpack.

        :rtype: :class:`objectpack.observer.base.Observer`
        """

    def models_view__skip_model(self, model):  # pylint: disable=no-self-use
        """Возвращает True для сокрытия модели в окне просмотра моделей.

        :param model: Класс модели.
        :type model: django.db.models.base.ModelBase

        :rtype: bool
        """
        return model.__module__.startswith('django')

    def models_view__skip_field(self, field):  # pylint: disable=no-self-use
        """Возвращает True для сокрытия поля в окне просмотра моделей.

        :param field: Поле модели.
        :type field: django.db.models.fields.Field

        :rtype: bool
        """
        return not field.concrete


#: Конфигурация приложения ``m3_dev_utils``.
#:
#: В проекте, который использует данное приложение, в этой переменной должен
#: быть сохранен экземпляр потомка класса :class:`~m3_dev_utils.Config`.
#:
#: Пример создания класса с конфигурацией и настройки приложения:
#:
#: .. code-block:: python
#:    :caption: ``extedu/apps.py``
#:
#:    class AppConfig(AppConfig):
#:
#:        def _init_m3_dev_utils(self):
#:            if 'm3_dev_utils' in settings.INSTALLED_APPS:
#:                import m3_dev_utils
#:
#:                class Config(m3_dev_utils.Config):
#:
#:                    @cached_property
#:                    def controller(self):
#:                        from extedu.controllers import main_controller
#:                        return main_controller
#:
#:                    @cached_property
#:                    def observer(self):
#:                        from extedu.controllers import core_observer
#:                        return core_observer
#:
#:                m3_dev_utils.config = Config()
#:
#:        def ready(self):
#:            self._init_m3_dev_utils()
#:
#:            super(AppConfig, self).ready()
config = None


def get_config():
    """Возвращает конфигурацию приложения.

    :rtype: m3_dev_utils.Config
    """
    # pylint: disable=global-statement
    global config
    assert config
    return config
