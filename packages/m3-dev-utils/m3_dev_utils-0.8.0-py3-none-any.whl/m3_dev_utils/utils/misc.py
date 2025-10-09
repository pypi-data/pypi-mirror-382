# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from inspect import isclass

from django.utils.safestring import mark_safe


class cached_property(property):  # Копия из educommon

    """Кешируемое свойство.

    В отличие от :class:`django.utils.functional.cached_property`, наследуется
    от property и копирует строку документации, что актуально при генерации
    документации средствами Sphinx.
    """

    def __init__(self, method):
        super(cached_property, self).__init__(method)

        self.__doc__ = method.__doc__

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.fget.__name__ not in instance.__dict__:
            instance.__dict__[self.fget.__name__] = self.fget(instance)

        return instance.__dict__[self.fget.__name__]


def get_full_class_name(klass, package_tag=None, class_tag=None):
    """Возвращает полное имя класса.

    :param type klass: Класс.
    :param str package_tag: Тег HTML, в который будет обернуто имя пакета.
    :param str class_tag: Тег HTML, в который будет обернуто имя класса.

    :rtype: str
    """
    package = klass.__module__
    if package_tag:
        package = mark_safe(u'<{tag}>{package}</{tag}>'.format(
            tag=package_tag,
            package=package,
        ))

    class_name = klass.__name__ if isclass(klass) else klass.__class__.__name__
    if class_tag:
        class_name = mark_safe(u'<{tag}>{class_name}</{tag}>'.format(
            tag=class_tag,
            class_name=class_name,
        ))

    return mark_safe('.'.join((package, class_name)))
