# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from importlib import import_module

from six.moves import map

from m3_dev_utils import get_config


def _get_pack(package):
    return import_module(package).Pack()


def register_actions():
    get_config().controller.extend_packs(map(_get_pack, (
        'm3_dev_utils.objectpack.listeners.actions',
        'm3_dev_utils.django.models.export.visual_paradigm.actions',
        'm3_dev_utils.django.models.view.actions',
    )))
