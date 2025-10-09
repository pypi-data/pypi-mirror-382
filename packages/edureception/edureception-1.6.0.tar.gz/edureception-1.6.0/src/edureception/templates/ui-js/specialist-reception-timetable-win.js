var mask = new Ext.LoadMask(win.getEl()),
    grid_panel = Ext.getCmp('{{ component.grid_panel.client_id }}'),
    filter_panel = Ext.getCmp('{{ component.filter_cnt.client_id }}'),
    dateFld = Ext.getCmp('{{ component.date_fld.client_id }}'),
    specialistFld = Ext.getCmp('{{ component.specialist_fld.client_id }}'),
    columnParamName = '{{ component.column_name }}';


function reloadGrid() {
    if (dateFld.isValid()) {
        grid_panel.fireEvent('reloadgrid', filter_panel.params);
    } else {
        Ext.Msg.alert('Ошибка', 'Некорректно указана дата!')
    }
}

win.on('show', reloadGrid);

grid_panel.on({
    scope: grid_panel,
    'afterreload': function (grid) {

        // {# случай read_only, не будет урла на редактирование #}
        if (grid.actionEditUrl != undefined) {
            grid.un('celldblclick', grid.events['celldblclick'].listeners[0].fn);
            grid.un('dblclick', grid.events['dblclick'].listeners[0].fn);
            grid.on({
                'beforenewrequest': beforeNewRequest,
                'beforeeditrequest': beforeEditRequest,
                'beforedeleterequest': beforeDeleteRequest,
                'celldblclick': onCellDblClick,
                scope: grid
            });
        }
        grid.getSelectedRecord = function () {
            // {# рекорд строки строа грида #}
            return grid.store.getAt(this.selModel.getSelectedCell()[0])
        };
        grid.getTimeTableCellData = function () {
            var record = grid.getSelectedRecord(),
                dayIdx = grid.getSelectionContext()[columnParamName];

            return record.data[dayIdx];
        };
    }
});

function onCellDblClick() {
    // {# исходя из данных в ячейке: либо редактирование, либо добавление #}
    var cellData = getAndValidateCellData(this);

    if (!cellData) {
        return false;
    }
    var params = {
        'record_id': cellData.record_id,
        'is_editing': cellData.fullname != undefined && cellData.fullname != ""
    };
    sendCellRequest(params, this.actionEditUrl);
    return false;
}


function beforeEditRequest() {
    var cellData = getAndValidateCellData(this);

    if (!cellData) {
        return false;
    }
    // {# изменять еще нечего #}
    if (cellData.fullname == undefined || cellData.fullname == "") {
        Ext.Msg.alert('Внимание', 'Это время еще не назначено!');
        return false;
    }
    var params = {
        'record_id': cellData.record_id,
        'is_editing': true
    };
    sendCellRequest(params, this.actionEditUrl);
    return false;
}

function beforeNewRequest() {
    if (!this.getSelectionModel().hasSelection()) {
        Ext.Msg.alert('Внимание', 'Необходимо выбрать ячейку!');
    } else {
        var cellData = getAndValidateCellData(this);

        if (!cellData) {
            return false;
        }
        if (cellData.fullname != "") {
            Ext.Msg.alert('Внимание', 'Это время уже занято!');
            return false;
        }
        var params = {
            'record_id': cellData.record_id,
            'is_editing': false
        };
        sendCellRequest(params, this.actionNewUrl);

    }

    return false;
}


function beforeDeleteRequest() {
    var cellData = getAndValidateCellData(this);

    if (!cellData) {
        return false;
    }
    // {# удалять нечего #}
    if (cellData.fullname == "") {
        Ext.Msg.alert('Внимание', 'Это время еще не назначено!');
        return false;
    }
    var params = {
        'record_id': cellData.record_id,
    };
    sendCellRequest(params, this.actionDeleteUrl);
    return false;
}


function getAndValidateCellData(grid) {
    /**
     * Получение данных выделенной ячейки и валидация поля record_id.
     *
     * @param {Object} grid
     * @return {Object} rv данные ячейки.
     */
    var rv, cellData = grid.getTimeTableCellData();
    // {# Валидация поля record_id у всех одинаковая, но fullname - разная #}
    if (cellData.record_id === undefined) {
        Ext.Msg.alert('Внимание', 'Это время не является приёмным!');
        rv = null;
    } else {
        rv = cellData
    }

    return rv
}


function sendCellRequest(params, url) {
    mask.show();
    Ext.Ajax.request({
        url: url,
        params: params,
        success: function (response) {
            mask.hide();
            var cellWin = smart_eval(response.responseText);
            if (cellWin != undefined) {
                cellWin.on('closed_ok', function (responseText) {
                    reloadGrid();
                });
            } else {
                reloadGrid();
            }
        },
        failure: function (response, request) {
            uiAjaxFailMessage.apply(this, arguments);
            mask.hide();
        }
    });

}

function dateSpecialKeyChange(field, e) {
    if (e.getKey() == e.ENTER) {
        filter_panel.params[field.name] = field.getValue();
        reloadGrid()
    }
}

function printSchedule() {
    mask.show();
    var params = {},
        specialistId = specialistFld.getValue(),
        date = dateFld.getValue();
    if (specialistId != undefined && date != undefined) {
        params[specialistFld.name] = specialistId;
        params[dateFld.name] = date;
    }
    Ext.Ajax.request({
        url: '{{ component.print_url }}',
        params: params,
        method: 'POST',
        success: function (response) {
            smart_eval(response.responseText);
            mask.hide();
        },
        failure: function (response, request) {
            uiAjaxFailMessage.apply(this, arguments);
            mask.hide();
        }
    });
}
