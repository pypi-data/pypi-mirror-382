# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from django.http.response import HttpResponse
from django.template.loader import render_to_string
from lxml.etree import tostring
from m3.actions.results import OperationResult
from objectpack.actions import BaseAction
from objectpack.actions import BasePack

from m3_dev_utils.utils.ui import local_template

from .utils import get_xml_document


class ExportAction(BaseAction):

    """Экспорт данных о моделях Системы в XML."""

    def run(self, request, context):
        xml_document = get_xml_document()
        content = tostring(
            xml_document,
            encoding='UTF-8',
            xml_declaration=True,
        )

        result = HttpResponse(
            content,
            content_type='application/xml',
        )
        result['Content-Disposition'] = 'attachment; filename=models.xml'
        result['Expires'] = '0'

        return result


class DownloadAction(BaseAction):

    """Скачивание XML-файла с данными о моделях Системы."""

    def run(self, request, context):
        url = self.parent.export_action.get_absolute_url()
        js_code = render_to_string(
            local_template('download.js'),
            dict(
                url=url,
            ),
        )

        return OperationResult(
            success=True,
            code=js_code,
        )


class Pack(BasePack):

    """Набор действий для экспорта данных о моделях Системы в XML.

    Полученный XML-файл пригоден для импорта в Visual Paradigm и последующего
    просомтра моделей Системы на ER-диаграмме.
    """

    def __init__(self):
        super(Pack, self).__init__()

        self.download_action = DownloadAction()
        self.export_action = ExportAction()
        self.actions.extend((
            self.download_action,
            self.export_action,
        ))

    def extend_menu(self, menu):
        return menu.SubMenu(
            'Инструменты разработчика',
            menu.SubMenu(
                'Модели',
                menu.Item(
                    'Экспорт: Visual Paradigm',
                    self.download_action,
                )
            )
        )
