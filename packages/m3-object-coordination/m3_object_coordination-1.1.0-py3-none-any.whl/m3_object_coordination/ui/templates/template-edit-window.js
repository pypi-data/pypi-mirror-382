var startDateField = Ext.getCmp('{{ component.field__start_date.client_id }}');
var endDateField = Ext.getCmp('{{ component.field__end_date.client_id }}');


function setEndDateMinValue(field, newValue) {
  endDateField.setMinValue(newValue);
  endDateField.validate();
};
startDateField.on('select', setEndDateMinValue);
startDateField.on('change', setEndDateMinValue);
