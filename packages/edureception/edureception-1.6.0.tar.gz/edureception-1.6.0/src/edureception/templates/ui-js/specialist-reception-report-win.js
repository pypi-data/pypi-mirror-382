var dateBeginFld = Ext.getCmp('{{ component.date_begin_fld.client_id }}'),
    dateEndFld = Ext.getCmp('{{ component.date_end_fld.client_id }}'),
    specialistFld = Ext.getCmp('{{ component.specialist_fld.client_id }}');

dateBeginFld.on('select', onBeginChange);
dateEndFld.on('select', onEndChange);
dateBeginFld.on('change', onBeginChange);
dateEndFld.on('change', onEndChange);

specialistFld.on('beforerequest', specialistFldBeforeSelect)
specialistFld.store.on('beforeload', specialistFldBeforeLoad)

function onEndChange(){
    dateBeginFld.setMaxValue(dateEndFld.getValue());
    dateBeginFld.validate();
    resetSpecialist();
}

function onBeginChange(){
    dateEndFld.setMinValue(dateBeginFld.getValue());
    dateEndFld.validate();
    resetSpecialist();
}


function resetSpecialist(){
    specialistFld.store.lastOptions = null;
    specialistFld.store.removeAll();
    specialistFld.lastQuery = null;
    specialistFld.reset();
    specialistFld.setValue();
    specialistFld.markInvalid();
    specialistFld.setReadOnly(!(dateEndFld.isValid() && dateBeginFld.isValid()));

}

function getDatesParams(){
    var params = {};
    params[dateBeginFld.name] = dateBeginFld.getValue();
    params[dateEndFld.name] = dateEndFld.getValue();
    return params
}

function specialistFldBeforeSelect(){
    Ext.apply(this.actionContextJson, getDatesParams());
}

function specialistFldBeforeLoad(){
    Ext.apply(this.baseParams, getDatesParams());
}
