{% include "m3-dev-utils/css.js" %}

var treePanel = Ext.getCmp('{{ component.tree.client_id }}');
var treeSM = treePanel.getSelectionModel();

var warningsGrid = Ext.getCmp('{{ component.grid__warnings.client_id }}');
var warningsGridStore = warningsGrid.getStore();
// ----------------------------------------------------------------------------
// {# Загрузка данных и формирование узлов дерева. #}


function createActionNode(actionInfo) {
    return new Ext.tree.TreeNode({
        name: actionInfo.name,
        warnings: actionInfo.warnings,
        leaf: true,
        cls: 'm3-dev-utils-monospace'
    });
}


function createPackNode(packInfo) {
    var packNode = new Ext.tree.TreeNode({
        name: packInfo.name,
        warnings: packInfo.warnings,
        leaf: !packInfo.actions || packInfo.actions.length == 0,
        cls: 'm3-dev-utils-monospace'
    });

    if (packInfo.actions && packInfo.actions.length > 0) {
        for (var i = 0; i < packInfo.actions.length; i++) {
            var actionInfo = packInfo.actions[i];
            packNode.appendChild(
                createActionNode(actionInfo)
            );
        }
    }

    return packNode;
}


function createListenNode(listenInfo) {
    var listenNode = new Ext.tree.TreeNode({
        name: listenInfo.name,
        warnings: listenInfo.warnings,
        leaf: !listenInfo.packs || listenInfo.packs.length == 0,
        cls: 'm3-dev-utils-monospace'
    });

    if (listenInfo.packs && listenInfo.packs.length > 0) {
        for (var i = 0; i < listenInfo.packs.length; i++) {
            var packInfo = listenInfo.packs[i];
            listenNode.appendChild(
                createPackNode(packInfo)
            );
        }
    }

    return listenNode;
}


function createListenerNode(listenerInfo) {
    var listenerNode = new Ext.tree.TreeNode({
        name: listenerInfo.name,
        warnings: listenerInfo.warnings,
        leaf: !listenerInfo.listen || listenerInfo.listen.length == 0,
        cls: 'm3-dev-utils-monospace'
    });

    if (listenerInfo.listen && listenerInfo.listen.length > 0) {
        for (var i = 0; i < listenerInfo.listen.length; i++) {
            var listenInfo = listenerInfo.listen[i];
            listenerNode.appendChild(
                createListenNode(listenInfo)
            )
        }
    }

    return listenerNode;
}


function onExpandNode(node) {
    var childNode, warnings;

    for (var i = 0; i < node.childNodes.length; i++) {
        childNode = node.childNodes[i];
        warnings = childNode.attributes.warnings;

        if (warnings && warnings.length > 0) {
            childNode.ui.addClass('m3-dev-utils-red');
        }
    }
}


function loadData() {
    Ext.Ajax.request({
        url: '{{ component.data_url }}',
        success: function(response, options) {
            var data = Ext.util.JSON.decode(response.responseText);

            for (var i = 0; i < data.length; i++) {
                var listenerInfo = data[i];
                treePanel.root.appendChild(
                    createListenerNode(listenerInfo)
                )
            }

            // Окрашивание красным узлов с предупреждениями.
            treePanel.root.cascade(function(node) {
                node.on('expand', onExpandNode);
            });
            onExpandNode(treePanel.root);
        },
        failure: function(response, options) {
            uiAjaxFailMessage.apply(this, arguments);
        }
    });
}


win.on('show', loadData);
// ----------------------------------------------------------------------------
// {# Обработчики кнопок верхней панели. #}


function expandAllNodes() {
    treePanel.getRootNode().expandChildNodes(true, false);
}


function expandSelectedNode() {
    var node = treeSM.getSelectedNode();
    if (node) {
        node.expand(true, false);
    }
}


function collapseSelectedNode() {
    var node = treeSM.getSelectedNode();
    if (node) {
        node.collapse(true, false);
    }
}


function collapseAllNodes() {
    treePanel.getRootNode().collapseChildNodes(true, false);
}
// ----------------------------------------------------------------------------
// Работа с предупреждениями.


treeSM.on('selectionchange', function(sm, node) {
    warningsGridStore.removeAll();

    if (node && node.attributes.warnings) {
        node.attributes.warnings.forEach(function(warningText) {
            warningsGridStore.add(new warningsGridStore.recordType({
                text: warningText
            }));
        });
    }
});
// ----------------------------------------------------------------------------
