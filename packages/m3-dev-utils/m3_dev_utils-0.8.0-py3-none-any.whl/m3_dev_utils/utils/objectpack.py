# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import defaultdict
import re

from six import iteritems


def get_listeners(observer):
    """Возвращает слушатели, зарегистрированные в наблюдателе.

    :rtype: list
    """
    return sorted(
        observer._registered_listeners,
        key=lambda descriptor: descriptor[0]
    )


def get_listener_actions(listen_re, observer):
    """Возвращает действия, соответствующие регулярному выражению слушателя.

    :param str listen_re: Регулярное выражение из параметра ``listen``
        слушателя.

    :param observer: Наблюдатель objectpack.
    :type observer: objectpack.observer.base.Observer

    :rtype: dict
    """
    listen_re = re.compile(listen_re)
    result = defaultdict(list)
    for action_name, action in iteritems(observer._actions):
        if listen_re.match(action_name):
            result[action.parent].append(action)

    return result
