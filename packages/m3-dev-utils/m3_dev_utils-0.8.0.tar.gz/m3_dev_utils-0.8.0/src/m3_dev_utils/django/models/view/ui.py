# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from m3_ext.ui.panels.grids import ExtObjectGrid
from objectpack.ui import BaseListWindow

from m3_dev_utils.utils.ui import local_template


class PrimaryWindow(BaseListWindow):

    """Основное окно просмотра моделей Системы."""

    def _init_components(self):
        super(PrimaryWindow, self)._init_components()

        self.grid__fields = ExtObjectGrid(
            header=True,
            title='Поля модели',
            cls='word-wrap-grid',
        )

    def _do_layout(self):
        super(PrimaryWindow, self)._do_layout()

        self.items.append(self.grid__fields)

        self.layout = 'hbox'
        self.layout_config = {'align': 'stretch'}
        self.grid.flex = 1
        self.grid__fields.flex = 1

    def set_params(self, params, *args, **kwargs):
        super(PrimaryWindow, self).set_params(params, *args, **kwargs)

        self.template_globals = local_template('list-window.js')

        self.maximized = self.maximizable = True

        params['pack'].fields_pack.configure_grid(self.grid__fields)
        self.grid__fields.store.auto_load = False
