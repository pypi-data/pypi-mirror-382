# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import inspect
import os.path

from django.conf import settings


def local_template(file_name):  # Копия функции из educommon
    """Возвращает абсолютный путь к файлу относительно модуля.

    Основное предназначение -- формирование значений полей ``template`` и
    ``template_globals`` окон, вкладок и других компонент пользовательского
    интерфейса в тех случаях, когда файл шаблона размещен в той же папке, что
    и модуль с компонентом.

    :param str file_name: Имя файла.

    :rtype: str
    """
    frame = inspect.currentframe().f_back

    root_package_name = frame.f_globals['__name__'].partition('.')[0]
    module = __import__(root_package_name)

    TEMPLATE_DIRS = set(
        path
        for config in settings.TEMPLATES
        for path in config.get('DIRS', ())
    )

    assert any(
        os.path.dirname(path) in TEMPLATE_DIRS
        for path in module.__path__
    ), (
        '{} package path must be in TEMPLATES config.'.format(module.__path__),
        TEMPLATE_DIRS,
    )

    # Путь к модулю вызывающей функции
    module_path = os.path.abspath(os.path.dirname(frame.f_globals['__file__']))

    for path in TEMPLATE_DIRS:
        if module_path.startswith(path):
            module_path = module_path[len(path) + 1:]
            break

    return os.path.join(module_path, file_name)
