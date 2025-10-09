# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractmethod
from uuid import uuid4

from lxml.etree import Element
from lxml.etree import ElementTree
from lxml.etree import SubElement
from m3_django_compatibility import get_related
from six import text_type
from six import with_metaclass
import django

from m3_dev_utils.utils.misc import cached_property


class ObjectIdRegistry(object):

    """Реестр идентификаторов объектов."""

    def __init__(self):
        self._model_ids = {}
        self._field_ids = {}
        self._field_type_ids = {}
        self._foreign_key_ids = {}

    @staticmethod
    def _get(obj, ids):
        if obj not in ids:
            ids[obj] = text_type(uuid4())

        return ids[obj]

    def get_model_id(self, model):
        return ObjectIdRegistry._get(model, self._model_ids)

    def get_field_id(self, field):
        return ObjectIdRegistry._get(field, self._field_ids)

    def get_field_type_id(self, field_type):
        return ObjectIdRegistry._get(field_type, self._field_type_ids)

    def get_foreign_key_id(self, field):
        return ObjectIdRegistry._get(field, self._foreign_key_ids)


class Base(with_metaclass(ABCMeta, object)):

    def __init__(self, ids_registry):
        self._ids_registry = ids_registry

    @abstractmethod
    def as_node(self):
        pass


class DBColumn(Base):

    def __init__(self, ids_registry, field):
        super(DBColumn, self).__init__(ids_registry)

        self._field = field

    def as_node(self):
        params = {
            'Name': self._field.name,
            'Id': self._ids_registry.get_field_id(self._field),
            'Nullable': 'true' if self._field.null else 'false',
            'PrimaryKey': 'true' if self._field.primary_key else 'false',
            'Index': 'true' if self._field.db_index else 'false',
            'Unique': 'true' if self._field.unique else 'false',
        }
        if self._field.verbose_name:
            params['Documentation_plain'] = text_type(self._field.verbose_name)

        result = Element('DBColumn', params)
        user_types = SubElement(result, 'UserTypes')
        SubElement(user_types, 'DBColumnUserType', {
            'Type': self._field.get_internal_type(),
            'Id': self._ids_registry.get_field_type_id(self._field),
        })

        if (
            not self._field.auto_created and self._field.concrete and
            (self._field.one_to_one or self._field.many_to_one)
        ):
            # Внешний ключ.
            SubElement(
                SubElement(result, 'ForeignKeyConstraints'),
                'DBForeignKeyConstraint',
                {
                    'ForeignKey': self._ids_registry.get_foreign_key_id(
                        self._field
                    ),
                    'RefColumn': self._ids_registry.get_field_id(
                        self._field.related_model._meta.get_field('id')
                    )
                }
            )

        return result


class ModelChildren(Base):

    def __init__(self, ids_registry, model):
        super(ModelChildren, self).__init__(ids_registry)

        self._model = model

    def as_node(self):
        result = Element('ModelChildren')

        for field in self._model._meta.get_fields():
            if field.concrete and not field.many_to_many:
                result.append(
                    DBColumn(self._ids_registry, field).as_node()
                )

        return result


class DBTable(Base):

    def __init__(self, ids_registry, model):
        super(DBTable, self).__init__(ids_registry)

        self._model = model

    def as_node(self):
        params = {
            'Name': self._model._meta.object_name,
            'Id': self._ids_registry.get_model_id(self._model),
            'DataModel': 'Physical',
        }
        if self._model._meta.verbose_name:
            params['Documentation_plain'] = text_type(
                self._model._meta.verbose_name
            )

        result = Element('DBTable', params)

        result.append(
            ModelChildren(self._ids_registry, self._model).as_node()
        )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        to_simple_relationships = Element('ToSimpleRelationships')
        from_simple_relationships = Element('FromSimpleRelationships')
        for field in self._model._meta.get_fields():
            if field.one_to_one or field.one_to_many:
                if field.concrete and not field.auto_created:
                    tag = to_simple_relationships  # Прямая связь
                elif not field.concrete and field.auto_created:
                    tag = from_simple_relationships  # Обратная связь
                else:
                    tag = None

                if tag is not None:
                    if not field.concrete:
                        if django.VERSION < (1, 9):
                            field = field.field
                        else:
                            field = field.remote_field
                    SubElement(tag, 'DBForeignKey', {
                        'Idref': self._ids_registry.get_foreign_key_id(field),
                    })

        # pylint: disable=len-as-condition
        if len(to_simple_relationships):
            result.append(to_simple_relationships)
        if len(from_simple_relationships):
            result.append(from_simple_relationships)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        return result


class DBForeignKey(Base):

    def __init__(self, ids_registry, field):
        super(DBForeignKey, self).__init__(ids_registry)

        self._field = field

    def as_node(self):
        from_model = self._field.model
        to_model = get_related(self._field).parent_model
        params = {
            'DataModel': 'Physical',
            'From': self._ids_registry.get_model_id(from_model),
            'To': self._ids_registry.get_model_id(to_model),
            'Id': self._ids_registry.get_foreign_key_id(self._field),
        }
        if self._field.many_to_many:
            params['FromMultiplicity'] = '0..*'
            params['ToMultiplicity'] = '0..*'
        elif self._field.one_to_one:
            min_number = 1 if self._field.null else 0
            params['FromMultiplicity'] = '{}..1'.format(min_number)
            params['ToMultiplicity'] = '{}..1'.format(min_number)
        else:
            min_number = 1 if self._field.null else 0
            params['FromMultiplicity'] = '{}..*'.format(min_number)
            params['ToMultiplicity'] = '{}..1'.format(min_number)

        result = Element('DBForeignKey', params)
        master_view = SubElement(result, 'MasterView')
        SubElement(master_view, 'DBForeignKey', {
            'Idref': text_type(uuid4()),
        })

        return result


class Models(Base):

    def __init__(self, ids_registry, apps):
        super(Models, self).__init__(ids_registry)

        self._apps = apps

    def as_node(self):
        result = Element('Models')

        for model in self._apps.get_models():
            if model._meta.proxy:
                continue

            result.append(
                DBTable(self._ids_registry, model).as_node()
            )

            for field in model._meta.get_fields():
                if (
                    not field.auto_created and field.concrete and
                    (field.one_to_one or field.many_to_one)
                ):
                    result.append(
                        DBForeignKey(self._ids_registry, field).as_node()
                    )

        return result


class Project(object):

    """Построитель XML-документа с данными моделей Системы."""

    def __init__(self, apps=None):
        if apps is None:
            from django.apps import apps
            self._apps = apps

        self._apps = apps

        self._ids_registry = ObjectIdRegistry()

    @cached_property
    def models_node(self):
        """Корень формируемого XML-документа.

        :rtype: lxml.etree.Element
        """
        result = Element(
            'Project',
            {
                'Xml_structure': 'simple',
                'UmlVersion': '2.x',
            }
        )

        return result

    def as_node(self):
        """Возвращает данные о моделях Системы.

        :rtype: lxml.etree.Element
        """
        result = Element(
            'Project',
            {
                'UmlVersion': '2.x',
                'Xml_structure': 'simple',
            }
        )

        result.append(Models(self._ids_registry, self._apps).as_node())

        return result


def get_xml_document():
    """Возвращает XML-документ с данными о моделях Системы.

    :rtype: lxml.etree.ElementTree
    """
    root_node = Project().as_node()
    result = ElementTree(root_node)

    return result
