# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from django.apps import apps
from django.db import connections
from django.db import router
from django.db.models.fields.related import ForeignKey
from django.http.response import Http404
from m3_django_compatibility import get_related
from objectpack.actions import ObjectPack
from objectpack.models import VirtualModel

from m3_dev_utils import config

from .ui import PrimaryWindow


class ModelInfo(VirtualModel):

    """Виртуальная модель с информацией о системных моделях."""

    def __init__(self, data):
        self.id = data['id']
        self.app_label = data['app_label']
        self.class_name = data['class_name']
        self.database_alias = data['database_alias']
        self.table_name = data['table_name']
        self.verbose_name = data['verbose_name']
        self.verbose_name_plural = data['verbose_name_plural']

    @staticmethod
    def _get_model_data(model_id, model):
        options = getattr(model, '_meta')

        return dict(
            id=model_id,
            app_label=options.app_label,
            class_name=options.object_name,
            database_alias=router.db_for_read(model),
            table_name=options.db_table,
            verbose_name=options.verbose_name,
            verbose_name_plural=options.verbose_name_plural,
        )

    @classmethod
    def _get_ids(cls):
        models = apps.get_models(include_auto_created=True)
        for model_id, model in enumerate(models):
            if not config.models_view__skip_model(model):
                yield cls._get_model_data(model_id, model)

    class _meta:
        verbose_name = 'Параметры модели'
        verbose_name_plural = 'Параметры моделей'


class Pack(ObjectPack):

    """Пак для окна просмотра моделей."""

    model = ModelInfo

    columns = (
        dict(
            data_index='database_alias',
            header='База данных',
            width=1,
            sortable=True,
            column_renderer='monospaceRenderer',
        ),
        dict(
            data_index='app_label',
            hidden=True,
        ),
        dict(
            data_index='class_name',
            header='Модель',
            width=2,
            sortable=True,
            column_renderer='monospaceRenderer',
        ),
        dict(
            data_index='table_name',
            header='Таблица БД',
            width=2,
            sortable=True,
            column_renderer='monospaceRenderer',
        ),
        dict(
            data_index='verbose_name',
            hidden=True,
        ),
        dict(
            data_index='verbose_name_plural',
            header='Описание',
            width=6,
            sortable=True,
        ),
    )

    list_window = PrimaryWindow
    allow_paging = False
    list_sort_order = ('table_name',)

    def __init__(self):
        super(Pack, self).__init__()

        self.fields_pack = FieldsPack()
        self.subpacks.append(self.fields_pack)

    def extend_menu(self, menu):
        return menu.SubMenu(
            u'Инструменты разработчика',
            menu.SubMenu(
                u'Модели',
                menu.Item(u'Просмотр', self.list_window_action)
            )
        )

    def get_list_window_params(self, params, request, context):
        result = super(Pack, self).get_list_window_params(
            params, request, context
        )

        result['pack'] = self

        return result


class FieldInfo(VirtualModel):

    """Виртуальная модель с информацией о полях модели."""

    def __init__(self, data):
        self.id = data['id']
        self.field_name = data['field_name']
        self.column_name = data['column_name']
        self.data_type = data['type']
        self.verbose_name = data['verbose_name']
        self.null = data['null']
        self.unique = data['unique']
        self.related_model = data.get('related_model')

    @staticmethod
    def _get_field_data(model, field_id, field):
        result = dict(
            id=field_id,
            field_name=field.name,
            column_name=field.attname,
            type=field.db_type(connections[router.db_for_read(model)]),
            verbose_name=field.verbose_name,
            null=field.null,
            unique=field.unique,
        )

        if isinstance(field, ForeignKey):
            parent_model = get_related(field).parent_model
            result['related_model'] = '{}.{}'.format(
                parent_model._meta.app_label, parent_model.__name__
            )

        return result

    @classmethod
    def _get_ids(cls, model):  # pylint: disable=arguments-differ
        options = getattr(model, '_meta')

        for field_id, field in enumerate(options.get_fields()):
            if not config.models_view__skip_field(field):
                yield cls._get_field_data(model, field_id, field)

    class _meta:
        verbose_name = 'Параметры поля модели'
        verbose_name_plural = 'Параметры полей модели'


class FieldsPack(ObjectPack):

    """Пак для грида полей модели."""

    model = FieldInfo

    columns = (
        dict(
            data_index='field_name',
            header='Имя поля в модели',
            width=1,
            sortable=True,
            column_renderer='monospaceRenderer',
        ),
        dict(
            data_index='column_name',
            header='Имя столбца в таблице БД',
            width=1,
            sortable=True,
            column_renderer='monospaceRenderer',
        ),
        dict(
            data_index='verbose_name',
            header='Описание',
            width=2,
            sortable=True,
        ),
        dict(
            data_index='data_type',
            header='Тип данных',
            width=2,
            sortable=True,
            column_renderer='dataTypeRenderer',
        ),
        dict(
            data_index='null',
            header='Пустые значения',
            width=1,
            sortable=True,
            column_renderer='yesNoRenderer',
        ),
        dict(
            data_index='related_model',
            hidden=True,
        ),
    )
    allow_paging = False

    def declare_context(self, action):
        result = super(FieldsPack, self).declare_context(action)

        result['app_label'] = dict(type='str')
        result['model_name'] = dict(type='str')

        return result

    def get_rows_query(self, request, context):
        try:
            model = apps.get_model(context.app_label, context.model_name)
        except LookupError:
            raise Http404

        return self.model.objects.configure(model=model)
