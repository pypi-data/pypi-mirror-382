// {# зависимости галочек дней недели и редактируемости контролов времени #}

var dependentChboxItemIds = Ext.util.JSON.decode('{{ component.dependent_chbox_items|safe }}'),
    dependentPeriodTypeItemIds = Ext.util.JSON.decode('{{ component.dependent_field_periodtype_items|safe }}'),
    maxPeriodLength = Ext.util.JSON.decode('{{ component.field__period_length.max_period_length|safe }}'),
    periodTypeFld = Ext.getCmp("{{ component.field__period_type.client_id }}"),
    periodLengthFld = Ext.getCmp("{{ component.field__period_length.client_id }}"),
    periodMonthId = {{ component.field__period_type.period_month_id }},
    // {# список контролов чекбоксов #}
    chboxItems = [],
    // {# список id контролов выбора номеров недели #}
    daySelectItemIds = [],
    daySelectNamePrefix = '{{ component.dayselect_prefix }}';


periodTypeFld.isMonthSelected = function(){
    // {# выбран тип периода - ежемесячно #}
    return periodTypeFld.getValue() == periodMonthId;
}

periodTypeFld.on('select', function(){
    toggleDaySelectFld(!periodTypeFld.isMonthSelected());
    periodLengthFld.setMaxValue(maxPeriodLength[periodTypeFld.getValue()]);
    periodLengthFld.validate();
})


// {# действия по блокировке контрола выбора номеров недели при смене типа периода #}
function toggleDaySelectFld(isWeekTypeSelected){
    // {# проход по элементам выбора номеров недели #}
    chboxItems.map(function(chboxFld){
        var daySelectFld = Ext.getCmp(dependentPeriodTypeItemIds[chboxFld.id]),
            isChecked = chboxFld.getValue();

        if (isChecked){
            daySelectFld.setReadOnly(isWeekTypeSelected);
        }

        if (isWeekTypeSelected){
            daySelectFld.clearValue();
            daySelectFld.allowBlank = true;
            daySelectFld.validate();
        }

        if (!isWeekTypeSelected && isChecked) {
            daySelectFld.allowBlank = false;
            daySelectFld.validate();
        }
    })
}

// {# действия при клике по чекбоксу включения / выключения дня недели #}
function toggleCheckBox() {
    // {# проход по элементам контейнера #}
    var isReadOnly = !this.chboxFld.getValue(),
        isMonthSelected = periodTypeFld.isMonthSelected();
    Ext.iterate(
        Ext.getCmp(this.containerId).items.items,
        function(cnt){
            var elReadOnly = isReadOnly,
                // {# в контейнере лежит по одному контролу #}
                el = cnt.items.items[0];

            if (daySelectItemIds.indexOf(el.id) > -1 && !periodTypeFld.isMonthSelected()){
                elReadOnly = true
            }
            el.setReadOnly(elReadOnly);
            el.allowBlank = elReadOnly;
            el.validate();
        });
}


function daySelectFldBeforeSelect(field){
    // {# номер дня в контекст #}
    var dayIdx = field.name.replace(daySelectNamePrefix, '');
    field.actionContextJson.day_idx = dayIdx;
    field.getStore().baseParams.day_idx = dayIdx;
}

win.on('show', function(){
    // {# определение связей между контролами и подписывание #}
    Ext.iterate(dependentChboxItemIds, function (chboxClientId, containerId) {
        var chboxFld = Ext.getCmp(chboxClientId),
            scope = {chboxFld: chboxFld, containerId: containerId};
        chboxItems.push(chboxFld)
        // {# получение id всех контролов выбора номеров недели #}
        daySelectItemIds.push(dependentPeriodTypeItemIds[chboxClientId]);

        chboxFld.on('check', toggleCheckBox, scope);

        // {# биндинг при вызове окна редактирования #}
        (function(){ toggleCheckBox.call(scope)})();
    });

    // {# биндинг при вызове окна редактирования #}
    toggleDaySelectFld(!periodTypeFld.isMonthSelected());
});