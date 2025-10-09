// Добавление класса для моноширинного шрифта.
const MONOSPACE_SELECTOR = '.m3-dev-utils-monospace'

win.on("beforeshow", function() {
    var cssStyleSheet = document.styleSheets[0];
    var cssRules = cssStyleSheet.cssRules;

    for (var i = 0; i < cssRules.length; i++) {
        if (cssRules[i].selectorText == MONOSPACE_SELECTOR) {
            return;
        }
    }

    cssStyleSheet.insertRule(
        MONOSPACE_SELECTOR + ' {' +
        'font-family: monospace !important;' +
        'font-weight: bold;' +
        '}',
        cssRules.length
    );
});

win.on('close', function() {
    var cssStyleSheet = document.styleSheets[0];
    var cssRules = cssStyleSheet.cssRules;

    for (var i = cssRules.length - 1; i >= 0; i--) {
        if (cssRules[i].selectorText == MONOSPACE_SELECTOR) {
            cssStyleSheet.deleteRule(i);
        }
    }
});
// {# ---------------------------------------------------------------------- #}
var modelsGrid = Ext.getCmp('{{ component.grid.client_id }}');
var modelsSM = modelsGrid.getSelectionModel();
var modelsStore = modelsGrid.getStore();
var modelsView= modelsGrid.getView();

var fieldsGrid = Ext.getCmp('{{ component.grid__fields.client_id }}');
var fieldsSM = fieldsGrid.getSelectionModel();
var fieldsStore = fieldsGrid.getStore();


function monospaceRenderer(value, metaData, record, rowIndex, colIndex, store) {
    metaData.css = 'm3-dev-utils-monospace';
    return value;
}


function yesNoRenderer(value, metaData, record, rowIndex, colIndex, store) {
    return value ? 'Да' : 'Нет';
}


modelsGrid.activateModel = function(modelName) {
    var appLabel = modelName.split('.')[0];
    var className = modelName.split('.')[1];

    var rowIndex = modelsStore.findBy(function(record) {
        return (
            record.data.app_label == appLabel &&
            record.data.class_name == className
        );
    });
    if (rowIndex != -1) {
        modelsSM.selectRow(rowIndex);
        modelsView.focusRow(rowIndex);
    }
}


function dataTypeRenderer(value, metaData, record, rowIndex, colIndex, store) {
    if (record.data.related_model) {
        var template = new Ext.Template(
            '{0} (ссылка на <a ',
                'href="#" ',
                'onclick="Ext.getCmp(\'{1}\').activateModel(\'{2}\')"',
            '>{2}</a>)'
        );
        value = template.apply([
            value,
            '{{ component.grid.client_id }}',
            record.data.related_model,
        ]);
    }
    return value;
}


function reloadFieldsGrid(){
    if (modelsSM.hasSelection()) {
        fieldsGrid.setDisabled(false);
        fieldsGrid.store.lastOptions = null;

        var param = {};
        var selectedRecordData = modelsSM.getSelected().data;
        param.app_label = selectedRecordData.app_label;
        param.model_name = selectedRecordData.class_name;
        Ext.apply(fieldsGrid.store.baseParams, param);
        Ext.apply(fieldsGrid.actionContextJson, param);

        fieldsGrid.store.reload();
    } else {
        fieldsGrid.setDisabled(true);
    }
}

modelsSM.on('selectionchange', reloadFieldsGrid);
modelsStore.on('load', reloadFieldsGrid);
