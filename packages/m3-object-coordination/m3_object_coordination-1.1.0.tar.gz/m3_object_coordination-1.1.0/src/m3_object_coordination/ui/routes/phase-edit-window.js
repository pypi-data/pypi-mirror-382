var deadlineField = Ext.getCmp('{{ component.field__deadline.client_id }}');

// Корректировка ширины подписи поля "Нормативный срок исполнения".
var labelWidth = 190;
var delta = labelWidth - deadlineField.label.getWidth();
deadlineField.label.setWidth(labelWidth);
deadlineField.setWidth(deadlineField.getWidth() - delta);
