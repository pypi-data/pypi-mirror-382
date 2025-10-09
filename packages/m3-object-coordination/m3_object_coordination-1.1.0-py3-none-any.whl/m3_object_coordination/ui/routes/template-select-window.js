/**
 * Окно выбора нового маршрута согласования.
 */

var grid = Ext.getCmp('{{ component.grid.client_id }}');
var gridStore = grid.getStore();
var gridSM = grid.getSelectionModel();
var selectButton = Ext.getCmp('{{ component.button__select.client_id }}');

gridStore.setBaseParam('object_type_id', '{{ component.object_type_id }}');
gridStore.setBaseParam('current_route_id', '{{ component.current_route_id }}');

function yesNoRenderer(value, metaData, record, rowIndex, colIndex, store) {
    return value ? 'Да' : 'Нет';
}

/**
 * Обработчик нажатия кнопки "Выбрать".
 */
function selectRouteTemplate() {
  if (!gridSM.hasSelection())
    return;

  win.fireEvent('closed_ok', gridSM.getSelected().id)
  win.close();

}
selectButton.handler = selectRouteTemplate;
grid.on('dblclick', selectRouteTemplate);

/**
 * Переключает доступность кнопки "Выбрать".
 */
function switchSelectButton() {
  selectButton.setDisabled(!gridSM.hasSelection());
}
gridSM.on('selectionchange', switchSelectButton);
switchSelectButton();
