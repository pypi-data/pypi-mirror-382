function isGridSelected(grid, title, message) {
    var res = true;
    if (!grid.getSelectionModel().hasSelection()) {
        Ext.Msg.show({
            title: title,
            msg: message,
            buttons: Ext.Msg.OK,
            icon: Ext.MessageBox.INFO
        });
        res = false;
    }
    return res;
}

function selectValue() {
    var id, displayText;

    var grid = Ext.getCmp('{{ component.grid.client_id}}');
    if (!isGridSelected(grid, 'Выбор элемента', 'Выберите элемент из списка')) {
        return;
    }
    id = grid.getSelectionModel().getSelected().id;
    displayText = grid.getSelectionModel().getSelected().get("{{ component.column_name_on_select }}");
    if (displayText == undefined){
        displayText = grid.getSelectionModel().getSelected().json["{{ component.column_name_on_select }}"];
    }
    var win = Ext.getCmp('{{ component.client_id }}');
    {% if component.callback_url %}
    Ext.Ajax.request({
        url: "{{ component.callback_url }}"
        ,
        success: function (res, opt) {
            var result = Ext.util.JSON.decode(res.responseText);
            if (!result.success) {
                Ext.Msg.alert('Ошибка', result.message)
            }
            else {
                win.fireEvent('closed_ok');
                win.close();
            }
        }
        ,
        params: Ext.applyIf({id: id}, {% if component.action_context %}{{component.action_context.json|safe}}{% else %}{}{% endif %})
        ,
        failure: function (response, opts) {
            uiAjaxFailMessage();
        }
    });
    {% else %}
    if (id != undefined && displayText != undefined) {
        win.fireEvent('select_value', id, displayText); // deprecated
        win.fireEvent('closed_ok', Ext.util.JSON.encode({data: grid.getSelectionModel().getSelected().data}));
    }
    win.close();
    {% endif %}
}
