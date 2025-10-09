var deadlineField = Ext.getCmp('{{ component.field__deadline.client_id }}');

Ext.QuickTips.register({
    target: deadlineField,
    text: 'Количество рабочих дней для согласования объекта'
});

win.on('beforeclose', function() {
    Ext.QuickTips.unregister({{ field }});
});
