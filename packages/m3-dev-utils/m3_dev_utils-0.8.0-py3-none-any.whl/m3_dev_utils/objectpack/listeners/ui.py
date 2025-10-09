# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from m3_ext.ui.containers.containers import ExtToolBar
from m3_ext.ui.containers.grids import ExtGrid
from m3_ext.ui.containers.trees import ExtTree
from m3_ext.ui.controls.buttons import ExtButton
from m3_ext.ui.misc.store import ExtDataStore
from objectpack.ui import BaseWindow
from objectpack.ui import ColumnsConstructor

from m3_dev_utils.utils.ui import local_template


class TreeToolBar(ExtToolBar):

    """Верхняя панель ."""

    def __init__(self, *args, **kwargs):
        super(TreeToolBar, self).__init__(*args, **kwargs)

        self.button__expand_all = ExtButton(
            text='Развернуть всё',
            handler='expandAllNodes',
        )
        self.button__expand_selected = ExtButton(
            text='Развернуть выбранный',
            handler='expandSelectedNode',
        )
        self.button__collapse_selected = ExtButton(
            text='Свернуть выбранный',
            handler='collapseSelectedNode',
        )
        self.button__collapse_all = ExtButton(
            text='Свернуть всё',
            handler='collapseAllNodes',
        )

        self.items[:] = (
            self.button__expand_all,
            self.button__expand_selected,
            self.button__collapse_selected,
            self.button__collapse_all,
        )


class ListenersTree(ExtTree):

    """Древовидная панель для отображения информации о слушателях."""

    def __init__(self, *args, **kwargs):
        super(ListenersTree, self).__init__(*args, **kwargs)

        ColumnsConstructor.from_config((
            dict(
                data_index='name',
                header='Слушатель',
            ),
        )).configure_grid(self)

        self.top_bar = TreeToolBar()


class Window(BaseWindow):

    """Окно с информацией о слушателях."""

    def _init_components(self):
        super(Window, self)._init_components()

        self.tree = ListenersTree()

        self.grid__warnings = ExtGrid(
            header=True,
            title='Предупреждения для выбранного элемента',
            cls='word-wrap-grid',
        )
        self.grid__warnings.store = ExtDataStore()
        self.grid__warnings.add_column(
            data_index='text',
        )

        self.button__close = ExtButton(
            text='Закрыть',
            handler='function(){Ext.getCmp("%s").close();}' % self.client_id,
        )

    def _do_layout(self):
        super(Window, self)._do_layout()

        self.title = 'Слушатели objectpack'

        self.template_globals = local_template('window.js')

        self.width, self.height = 800, 600
        self.maximizable = self.minimizable = True

        self.layout = 'vbox'
        self.layout_config = {'align': 'stretch'}
        self.tree.flex = 1
        self.grid__warnings.flex = 0
        self.grid__warnings.height = 100

        self.items[:] = (
            self.tree,
            self.grid__warnings,
        )
        self.buttons[:] = (
            self.button__close,
        )

    def set_params(self, params):
        super(Window, self).set_params(params)

        self.data_url = params['data_url']
