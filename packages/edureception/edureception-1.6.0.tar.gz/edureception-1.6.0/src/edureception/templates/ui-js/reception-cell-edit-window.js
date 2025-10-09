var fieldApplicantId = Ext.getCmp("{{ component.field_applicant_id.client_id }}");

var gridApplicant = Ext.getCmp("{{ component.grid_applicant.client_id }}");
var topBarButtonAdd = Ext.getCmp("{{ component.grid_applicant.top_bar.button_new.client_id }}");
var contextMenuGrid = Ext.getCmp("{{ component.grid_applicant.context_menu_grid.client_id }}");
var contextMenuRow = Ext.getCmp("{{ component.grid_applicant.context_menu_row.client_id }}");

function applicantExist() {
    return gridApplicant.getStore().getCount() > 0;
}

contextMenuGrid.on("show", function () {
    this.items.get(0).setDisabled(applicantExist());
});

contextMenuRow.on("show", function () {
    this.items.get(0).setDisabled(applicantExist());
});

if (fieldApplicantId.getValue()) {
    topBarButtonAdd.setDisabled(true);
}

gridApplicant.on("rowadded", function (scope, data) {
    topBarButtonAdd.setDisabled(true);
});

gridApplicant.on("rowedited", function (scope, data) {
    topBarButtonAdd.setDisabled(true);
});

gridApplicant.on("beforedeleterequest", function (scope, req) {
    var store = this.getStore();
    var sm = this.getSelectionModel();
    if (sm.hasSelection()) {
        // только для режима выделения строк
        if (sm instanceof Ext.grid.RowSelectionModel) {
            var rec = sm.getSelections();
            store.remove(rec);
            topBarButtonAdd.setDisabled(false);
        }
    }
    return false;
});

win.on("beforesubmit", function (submit) {
    var applicant = gridApplicant.getStore().getAt(0);
    if (!applicant) {
        Ext.Msg.show({
            title: 'Проверка формы',
            msg: 'Не выбран заявитель.',
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.WARNING
        });
        return false;
    }
    fieldApplicantId.setValue(applicant.data.id);
});
