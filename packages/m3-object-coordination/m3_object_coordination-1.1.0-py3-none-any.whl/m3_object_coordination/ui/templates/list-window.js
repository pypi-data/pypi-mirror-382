var templatesGrid = Ext.getCmp('{{ component.grid__templates.client_id }}');
var templatesStore = templatesGrid.getStore();
var templatesSM = templatesGrid.getSelectionModel();
var templateEditButton = Ext.getCmp('{{ component.grid__templates.top_bar.button_edit.client_id }}');
var templateEditContextMenu = Ext.getCmp('{{ component.grid__templates.context_menu_row.menuitem_edit.client_id }}');
var templatesDeleteButton = Ext.getCmp('{{ component.grid__templates.top_bar.button_delete.client_id }}');
var templatesDeleteContextMenu = Ext.getCmp('{{ component.grid__templates.context_menu_row.menuitem_delete.client_id }}');

var phasesGrid = Ext.getCmp('{{ component.grid__phases.client_id }}');
var phasesStore = phasesGrid.getStore();
var phasesSM = phasesGrid.getSelectionModel();
var phaseEditButton = Ext.getCmp('{{ component.grid__phases.top_bar.button_edit.client_id }}');
var phaseEditContextMenu = Ext.getCmp('{{ component.grid__phases.context_menu_row.menuitem_edit.client_id }}');
var phasesDeleteButton = Ext.getCmp('{{ component.grid__phases.top_bar.button_delete.client_id }}');
var phasesDeleteContextMenu = Ext.getCmp('{{ component.grid__phases.context_menu_row.menuitem_delete.client_id }}');
var movePhaseUpButton = Ext.getCmp('{{ component.grid__phases.top_bar.move_up_button.client_id }}');
var movePhaseDownButton = Ext.getCmp('{{ component.grid__phases.top_bar.move_down_button.client_id }}');

var approoversGrid = Ext.getCmp('{{ component.grid__approovers.client_id }}');
var approoversStore = approoversGrid.getStore();
var approoversSM = approoversGrid.getSelectionModel();
var approoverEditButton = Ext.getCmp('{{ component.grid__approovers.top_bar.button_edit.client_id }}');
var approoverEditContextMenu = Ext.getCmp('{{ component.grid__approovers.context_menu_row.menuitem_edit.client_id }}');
var approoversDeleteButton = Ext.getCmp('{{ component.grid__approovers.top_bar.button_delete.client_id }}');
var approoversDeleteContextMenu = Ext.getCmp('{{ component.grid__approovers.context_menu_row.menuitem_delete.client_id }}');
// ----------------------------------------------------------------------------


function yesOrEmpty(value) {
    return value ? 'Да' : '';
}


win.on('show', function() {
  phasesGrid.disable();
  approoversGrid.disable();
});
// ----------------------------------------------------------------------------


/**
 * Перезагружает грид с этапами согласования при выборе другого шаблона.
 * При выборе нескольких шаблонов грид с этапами деактивируется.
 */
templatesSM.on('selectionchange', function() {
  if (templatesSM.getCount() == 1) {
    var rowIdName = templatesGrid.rowIdName;
    var templateId = templatesSM.getSelected().id;

    if (templateId != templatesSM.lastSelectedId) {
      phasesGrid.actionContextJson[rowIdName] = templateId;
      phasesStore.baseParams[rowIdName] = templateId;

      phasesGrid.enable();
      phasesGrid.refreshStore();

      templatesSM.lastSelectedId = templateId;
    }
  } else {
    delete phasesGrid.actionContextJson[templatesGrid.rowIdName];
    delete phasesStore.baseParams[templatesGrid.rowIdName];
    delete templatesSM.lastSelectedId;

    phasesSM.clearSelections();
    phasesStore.removeAll();
    phasesGrid.disable();
  }
});


/**
 * Переключает доступность кнопок в гриде шаблонов в зависимости от выбора.
 */
function switchTemplatesGridButtons() {
  templateEditButton.setDisabled(templatesSM.getCount() != 1);
  templateEditButton.setTooltip(
    templateEditButton.disabled ? 'Выберите запись для изменения' : ''
  );
  templateEditContextMenu.setDisabled(templatesSM.getCount() != 1);

  templatesDeleteButton.setDisabled(!templatesSM.hasSelection());
  templatesDeleteButton.setTooltip(
    templatesDeleteButton.disabled ? 'Выберите записи для удаления' : ''
  );
  templatesDeleteContextMenu.setDisabled(!templatesSM.hasSelection());
}
templatesStore.on('load', switchTemplatesGridButtons);
templatesSM.on('selectionchange', switchTemplatesGridButtons);
// ----------------------------------------------------------------------------


/**
 * Перезагружает грид с согласующими при выборе другого этапа. При выборе
 * нескольких этапов грид с согласующими деактивируется.
 */
phasesSM.on('selectionchange', function() {
  if (phasesSM.getCount() == 1) {
    var rowIdName = phasesGrid.rowIdName;
    var phaseId = phasesSM.getSelected().id;

    if (phaseId != phasesSM.lastSelectedId) {
      approoversGrid.actionContextJson[rowIdName] = phaseId;
      approoversStore.baseParams[rowIdName] = phaseId;

      approoversGrid.enable();
      approoversGrid.refreshStore();

      phasesSM.lastSelectedId = phaseId;
    }
  } else {
    delete approoversGrid.actionContextJson[phasesGrid.rowIdName];
    delete approoversStore.baseParams[phasesGrid.rowIdName];
    delete phasesSM.lastSelectedId;

    approoversSM.clearSelections();
    approoversStore.removeAll();
    approoversGrid.disable();
  }
});


/**
 * Переключает доступность кнопок в гриде этапов в зависимости от выбора.
 */
function switchPhasesGridButtons() {
  phaseEditButton.setDisabled(phasesSM.getCount() != 1);
  phaseEditButton.setTooltip(
    phaseEditButton.disabled ? 'Выберите запись для изменения' : ''
  );
  phaseEditContextMenu.setDisabled(phasesSM.getCount() != 1);

  phasesDeleteButton.setDisabled(!phasesSM.hasSelection());
  phasesDeleteButton.setTooltip(
    phasesDeleteButton.disabled ? 'Выберите записи для удаления' : ''
  );
  phasesDeleteContextMenu.setDisabled(!phasesSM.hasSelection());

  movePhaseUpButton.setDisabled(
    !phasesSM.hasSelection() ||
    phasesSM.isSelected(0)
  );
  movePhaseUpButton.setTooltip(
    movePhaseUpButton.disabled ? 'Выберите записи для перемещения' : ''
  );

  movePhaseDownButton.setDisabled(
    !phasesSM.hasSelection() ||
    phasesSM.isSelected(phasesStore.totalLength - 1)
  );
  movePhaseDownButton.setTooltip(
    movePhaseDownButton.disabled ? 'Выберите записи для перемещения' : ''
  );
}
phasesStore.on('load', switchPhasesGridButtons);
phasesSM.on('selectionchange', switchPhasesGridButtons);
// ----------------------------------------------------------------------------


/**
 * Перемещает этапы маршрута согласования в указанном направлении.
 */
function movePhases(phaseIds, direction) {
  var params = {};
  params.direction = direction;
  params[phasesGrid.rowIdName] = phaseIds.join(',');

  Ext.Ajax.request({
    url: '{{ component.reorder_phases_url }}',
    params: params,
    success: function(response){
      var result = Ext.util.JSON.decode(response.responseText);
      if (!result.success) {
        smart_eval(response.responseText);
      } else {
        phasesGrid.refreshStore();
      }
    },
    failure: uiAjaxFailMessage
  });
}


function movePhasesUp() {
  if (phasesSM.hasSelection()) {
    movePhases(
      phasesSM.getSelections().map(function(r) {return r.id}), 'up'
    );
  }
}
function movePhasesDown() {
  if (phasesSM.hasSelection()) {
    movePhases(
      phasesSM.getSelections().map(function(r) {return r.id}), 'down'
    );
  }
}
// ----------------------------------------------------------------------------


/**
 * Переключает доступность кнопок в гриде согласующих в зависимости от выбора.
 */
function switchApprooversGridButtons() {
  approoverEditButton.setDisabled(approoversSM.getCount() != 1);
  approoverEditButton.setTooltip(
    approoverEditButton.disabled ? 'Выберите запись для изменения' : ''
  );
  approoverEditContextMenu.setDisabled(approoversSM.getCount() != 1);

  approoversDeleteButton.setDisabled(!approoversSM.hasSelection());
  approoversDeleteButton.setTooltip(
    approoversDeleteButton.disabled ? 'Выберите записи для удаления' : ''
  );
  approoversDeleteContextMenu.setDisabled(!phasesSM.hasSelection());
}
approoversStore.on('load', switchApprooversGridButtons);
approoversSM.on('selectionchange', switchApprooversGridButtons);
// ----------------------------------------------------------------------------
