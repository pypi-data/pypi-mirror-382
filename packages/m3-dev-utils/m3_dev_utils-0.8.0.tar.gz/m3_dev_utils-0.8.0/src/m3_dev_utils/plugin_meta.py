# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from os.path import dirname


def connect_plugin(settings, plugin_settings):  # @UnusedVariable
    settings['INSTALLED_APPS'].append(__package__)

    # Добавление пути к папке с шаблонами для local_template
    path = dirname(dirname(__file__))
    if path not in settings['TEMPLATES'][0]['DIRS']:
        settings['TEMPLATES'][0]['DIRS'].append(path)
