var approoverTypeField = Ext.getCmp('{{ component.field__approover_type_id.client_id }}');
var approoverIdField = Ext.getCmp('{{ component.field__approover_id.client_id }}');


win.on('show', function() {
  approoverIdField.setDisabled(!approoverIdField.getValue());
});


/**
 * Перенастраивает поле выбора согласующего в зависимости от выбранного типа.
 */
approoverTypeField.on('change', function(field, newValue, oldValue) {
  if (newValue != oldValue) {
    var record = approoverTypeField.store.getById(newValue);

    var fields = approoverIdField.getStore().fields;
    fields.removeKey(approoverIdField.displayField);
    approoverIdField.displayField = record.json.column_name_on_select;
    fields.add(new Ext.data.Field({
      name: approoverIdField.displayField
    }));

    var reader = approoverIdField.getStore().reader
    reader.meta.fields[1].name = approoverIdField.displayField;
    delete reader.ef;
    reader.buildExtractors();

    approoverIdField.clearValue();
    approoverIdField.actionContextJson.approover_type_id = newValue;

    if (record.json.select_window_url) {
      approoverIdField.actionSelectUrl = record.json.select_window_url;
      approoverIdField.enable();
      approoverIdField.hideTriggerDictSelect = false;
      approoverIdField.showDictSelectBtn();
      approoverIdField.disableTriggers(false);
    } else {
      approoverIdField.actionSelectUrl = null;
      approoverIdField.disable();
      approoverIdField.hideDictSelectBtn();
      approoverIdField.disableTriggers(true);
    }
  }
});
