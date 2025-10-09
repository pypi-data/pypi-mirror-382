var resultField = Ext.getCmp('{{ component.field__result.client_id }}');
var commentField = Ext.getCmp('{{ component.field__comment.client_id }}');
var saveButton = Ext.getCmp('{{ component.save_btn.client_id }}');
var REVIEW_RESULT__AGREED = parseInt('{{ component.REVIEW_RESULT__AGREED }}');


function switchSaveButton() {
  saveButton.setDisabled(
    resultField.getValue() != REVIEW_RESULT__AGREED &&
    !commentField.getValue()
  );
}
resultField.on('change', switchSaveButton);
resultField.on('select', switchSaveButton);
commentField.on('change', switchSaveButton);
win.on('show', switchSaveButton);


function validateCommentField() {
  commentField.allowBlank = resultField.getValue() == REVIEW_RESULT__AGREED;
  commentField.validate();
}
resultField.on('change', validateCommentField);
resultField.on('select', validateCommentField);
