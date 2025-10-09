Ext.namespace('Ext.m3.ObjectCoordination');
// ============================================================================

/**
 * Направления перемещения этапов в маршруте согласования.
 */
Ext.m3.ObjectCoordination.MoveDirection = {

    /**
     * Вверх.
     */
    UP: 0,

    /**
     * Вниз.
     */
    DOWN: 1
}


/**
 * Результаты рассмотрения объекта согласования.
 */
Ext.m3.ObjectCoordination.ReviewResult = {

    /**
     * Согласовано.
     */
    AGREED: 0,

    /**
     * На доработку.
     *
     * Данный результат рассмотрения позволяет возобновить маршрут
     * согласования.
     */
    NEED_CHANGES: 1,

    /**
     * Отклонено.
     *
     * Данный результат рассмотрения делает невозможным возобновление
     * согласования.
     */
    REJECTED: 2
}


/**
 * Состояния маршрута.
 */
Ext.m3.ObjectCoordination.RouteState = {

  /**
  * Подготовка.
  *
  * В этом состоянии находятся маршруты, у которых еще нет этапов, либо
  * содержащие этапы без согласующих.
  */
  PREPARATION: 1,

  /** В ожидании.
   *
   * Данное состояние соответствует маршрутам с созданными этапами и
   * согласующими в каждом их них, при этом ни в одном из этапов маршрута не
   * заполнена плановая дата исполнения.
   */
  WAITING: 2,

  /**
   * Исполняется.
   * 
   * Данное состояние соответствует маршрутам с созданными этапами и
   * согласующими в каждом их них, при этом хотя бы в одном из этапов
   * маршрута должна быть заполнена плановая дата исполнения и хотя бы у одного
   * этапа не заполнена фактическая дата исполнения.
   */
  EXECUTING: 3,

  /**
   * Согласован.
   *
   * Состояние соответствует маршруту, у которого все этапы согласованы.
   */
  APPROOVED: 4,

  /**
   * Отправлен на доработку.
   *
   * Состояние соответствует маршруту, на одном из этапов которого есть
   * результат рассмотрения "На доработку" и нет результатов "Отклонено".
   */
  NEED_CHANGES: 5,

  /**
   * Отклонен.
   *
   * Состояние соответствует маршруту, в котором есть результат рассмотрения
   * "Отклонено".
   */
  REJECTED: 6
}


/**
 * Состояния этапов согласования.
 */
Ext.m3.ObjectCoordination.PhaseState = {

  /**
   * В ожидании.
   *
   * Состояние соответствует этапу, согласование которого еще не начато, при
   * этом предыдущие этапы не были отклонены или отправлены на доработку.
   */
 WAITING: 1,

  /**
   * Исполняется.
   *
   * Состояние соответствует этапу, который находится в процессе рассмотрения
   * согласующими.
   */
  EXECUTING: 2,

  /**
   * Исполненный.
   *
   * Состояние соответствует этапу, в котором все согласующие рассмотрели
   * предмет согласования с результатом "Согласовано".
   */
  EXECUTED: 3,

  /**
   * Остановлен.
   *
   * Состояние соответствует этапу, который был отклонен, либо отправлен на
   * доработку.
   */
  STOPPED: 4,

  /**
   * Заблокированный.
   *
   * Состояние соответствует этапу, согласование которого не было начато, при
   * этом один из предыдущих этапов был отклонен, либо отправлен на
   * доработку.
   */
  BLOCKED: 5
}
// ============================================================================

/**
 * Верхняя панель грида маршрута согласования.
 */
Ext.m3.ObjectCoordination.RouteGridTopBar = Ext.extend(Ext.Toolbar, {

  initComponent: function() {
    Ext.m3.ObjectCoordination.RouteGridTopBar.superclass.initComponent.call(
      this
    );

    this.add(this.addMenu);
    this.add(this.editButton);
    this.add(this.deleteButton);
    this.add(this.upButton);
    this.add(this.downButton);
    this.add(this.changeTemplateButton);
    this.add(this.refreshButton);
    this.add(this.setReviewResultButton);
    this.add(this.historyButton);

    this.addMenu = Ext.getCmp(this.addMenu.id);
    this.addPhaseMenuItem = Ext.getCmp(this.addMenu.menu.get(0).id);
    this.addApprooverMenuItem = Ext.getCmp(this.addMenu.menu.get(1).id);
  }

});
// ============================================================================


/**
 * UI для для узлов дерева без контрола для сворачивания узлов.
 *
 * Также поддерживаает следующие параметры
 *
 * - singleCell: сли этот параметр равен true, то объединяет все
 *   ячейки строки, соответствующей узлу дерева;
 * - bold: истинное значение параметра узла указывает на необходимость
 *   отображения узла полужирным шрифтом.
 */
Ext.m3.ObjectCoordination.TreeNodeUI = Ext.extend(
  Ext.ux.tree.TreeGridNodeUI,
  {
    renderElements: function(n, a, targetNode, bulkRender) {
      Ext.m3.ObjectCoordination.TreeNodeUI.superclass.renderElements.call(
        this, n, a, targetNode, bulkRender
      );

      // Настройка параметров отображения узла.
      this.ecNode.style.display = 'none';
      Ext.apply(this.iconNode.style, {
        marginLeft: '2px',
        marginRight: '2px'
      });

      // Объединение ячеек узла.
      if (n.singleCell) {
        var rowCells = this.elNode.children;
        var colSpan = rowCells.length;
        for (var j = 1; j < rowCells.length; j++) {
          rowCells.item(j).remove()
        }
        rowCells.item(0).colSpan = colSpan;
      }

      if (n.bold) {
        this.getTextEl().style.fontWeight = 'bold';
      }
    }
  }
);


/**
 * UI для корневого узла дерева.
 */
Ext.m3.ObjectCoordination.RouteNodeUI = Ext.extend(
  Ext.m3.ObjectCoordination.TreeNodeUI,
  {
    renderElements: function(n, a, targetNode, bulkRender) {
      n.singleCell = true;
      n.bold = true;
      a.iconCls = 'icon-application-view-list';

      Ext.m3.ObjectCoordination.RouteNodeUI.superclass.renderElements.call(
        this, n, a, targetNode, bulkRender
      );
    }
  }
);


/**
 * UI для узлов дерева без возможности их сворачивания.
 */
Ext.m3.ObjectCoordination.PhaseNodeUI = Ext.extend(
  Ext.m3.ObjectCoordination.TreeNodeUI,
  {
    renderElements: function(n, a, targetNode, bulkRender) {
      n.singleCell = true;
      n.bold = true;
      a.iconCls = 'icon-comments';

      Ext.m3.ObjectCoordination.PhaseNodeUI.superclass.renderElements.call(
        this, n, a, targetNode, bulkRender
      );
    }
  }
);


/**
 * UI для узлов дерева без возможности их сворачивания.
 */
Ext.m3.ObjectCoordination.ApprooverNodeUI = Ext.extend(
  Ext.m3.ObjectCoordination.TreeNodeUI,
  {
    renderElements: function(n, a, targetNode, bulkRender) {
      a.iconCls = 'icon-comment';

      Ext.m3.ObjectCoordination.ApprooverNodeUI.superclass.renderElements.call(
        this, n, a, targetNode, bulkRender
      );

      // включение переноса слов
      var rowCells = this.elNode.children;
      for (var i = 1; i < rowCells.length; i++) {
        rowCells[i].style['white-space'] = 'normal';
      }
    }
  }
);


/**
 * Узел дерева в гриде маршрута согласования.
 *
 * Не имеет возможности сворачивания.
 */
Ext.m3.ObjectCoordination.TreeNode = Ext.extend(
  Ext.tree.TreeNode,
  {
    singleCell: false,
    collapse: Ext.emptyFn,
  }
);
// ============================================================================

/**
 * Панель для работы с маршрутом согласования.
 *
 * Предоставляет средства для отображения информации о маршруте согласования и
 * его модификации.
 */
Ext.m3.ObjectCoordination.RoutePanel = Ext.extend(Ext.ux.tree.TreeGrid, {

  initComponent: function() {
    this.addEvents(
      /**
      * @event loaddata
      * Срабатывает после загрузки данных маршрута согласования.
      */
     'loaddata'
    );

    if (this.autoLoad) {
      this.on('afterrender', this.loadRouteData, this);

      this.autoLoad = false;
    }

    Ext.m3.ObjectCoordination.RoutePanel.superclass.initComponent.call(this);

    this.topBar = this.toolbars[0];
    this.configureTopBar();

    this.on('dblclick', this.onEditButtonClick, this);
  },

  /**
   * Возвращает true, если узел дерева соответствует маршруту согласования.
   */
  isRouteNode: function(node) {
    return node === this.root;
  },

  /**
   * Возвращает true, если узел дерева соответствует этапу согласования.
   */
  isPhaseNode: function(node) {
    return node && node.parentNode === this.getRootNode();
  },

  /**
   * Возвращает true, если узел дерева соответствует согласующему на этапе.
   */
  isApprooverNode: function(node) {
    return node && node.parentNode !== this.getRootNode();
  },

  /**
   * Возвращает true, если действие доступно для узла грида.
   */
  isActionPermitted: function(action, node) {
    return node.attributes.permittedActions.indexOf(action) !== -1;
  },

  /**
   * Настраивает верхнюю панель.
   */
  configureTopBar: function() {
    // Обработчики для кнопок и пунктов меню.
    var buttonHandlers = {
      refreshButton: this.loadRouteData,
      addPhaseMenuItem: this.onAddPhaseButtonClick,
      editButton: this.onEditButtonClick,
      deleteButton: this.onDeleteButtonClick,
      addApprooverMenuItem: this.onAddApprooverButtonClick,
      upButton: this.onMoveButtonClick.bind(this, 'up'),
      downButton: this.onMoveButtonClick.bind(this, 'down'),
      changeTemplateButton: this.onChangeTemplateButtonClick,
      setReviewResultButton: this.onSetReviewResultButtonClick,
      historyButton: this.onHistoryButtonClick
    };
    for (var button in buttonHandlers) {
      this.topBar[button].setHandler(buttonHandlers[button], this);
    }

    // Переключатели доступности кнопок.
    var controls = [
      this.switchAddPhase,
      this.switchAddApproover,
      this.switchEditButton,
      this.switchDeleteButton,
      this.switchUpButton,
      this.switchDownButton,
      this.switchSetReviewResultButton,
      this.switchHistoryButton
    ];
    controls.forEach(function(handler) {
      this.getSelectionModel().on('selectionchange', handler, this);
    }, this);
  },

  /**
   * Переключает доступность добавления этапа в маршрут.
   */
  switchAddPhase: function(sm, node) {
    this.topBar.addPhaseMenuItem.setDisabled(
      !this.isActionPermitted('add-phase', node)
    );
    this.switchAddMenu();
  },

  /**
   * Переключает доступность добавления согласующего в маршрут.
   */
  switchAddApproover: function(sm, node) {
    this.topBar.addApprooverMenuItem.setDisabled(
      !this.isActionPermitted('add-approover', node)
    );
    this.switchAddMenu();
  },

  /**
   * Переключает доступность добавления согласующего в маршрут.
   */
  switchAddMenu: function(sm, node) {
    this.topBar.addMenu.setDisabled(
      this.topBar.addPhaseMenuItem.disabled &&
      this.topBar.addApprooverMenuItem.disabled
    );
  },

  /**
   * Переключает доступность кнопки "Изменить".
   */
  switchEditButton: function(sm, node) {
    this.topBar.editButton.setDisabled(
        !this.isActionPermitted('edit-phase', node)
    );
  },

  /**
   * Переключает доступность кнопки "Удалить".
   */
  switchDeleteButton: function(sm, node) {
    this.topBar.deleteButton.setDisabled(
        !this.isActionPermitted('delete-phase', node) &&
        !this.isActionPermitted('delete-approover', node)
    );
  },

  /**
   * Переключает доступность кнопки "Переместить вверх".
   */
  switchUpButton: function(sm, node) {
    this.topBar.upButton.setDisabled(
      !this.isActionPermitted('move-phase-up', node)
    );
  },

  /**
   * Переключает доступность кнопки "Переместить вниз".
   */
  switchDownButton: function(sm, node) {
    this.topBar.downButton.setDisabled(
      !this.isActionPermitted('move-phase-down', node)
    );
  },

  /**
   * Переключает доступность кнопки "Выбрать другой маршрут согласования".
   */
  switchChangeTemplateButton: function() {
    this.topBar.changeTemplateButton.setDisabled(
      !this.isActionPermitted('change-template', this.root)
    );
  },

  /**
   * Переключает доступность кнопки "Указать результат согласования".
   */
  switchSetReviewResultButton: function(sm, node) {
    this.topBar.setReviewResultButton.setDisabled(
      !this.isActionPermitted('set-review-result', node)
    );
  },

  /**
   * Переключает доступность кнопки "История".
   */
  switchHistoryButton: function(sm, node) {
    this.topBar.historyButton.setDisabled(
      !this.isActionPermitted('view-approover-history', node)
    );
  },

  /**
   * Возвращает id объекта в указанном узле дерева элементов грида.
   *
   * Если узел не указан, используется текущий.
   */
  getNodeObjectId: function(node) {
    if (!node) {
      node = this.getSelectionModel().getSelectedNode();
    }

    var objectId = node.attributes.id;
    if (typeof objectId === 'string' || objectId instanceof String) {
      objectId = objectId.match(/^(route|phase|approover)-(\d+)$/);
      if (objectId)
        objectId = Number(objectId[2]);
    }

    return objectId;
  },

  /**
   * Обработчик для меню добавления этапа согласования.
   */
  onAddPhaseButtonClick: function() {
    if (!this.isActionPermitted('add-phase', this.root)) return;

    Ext.Ajax.request({
      url: this.phaseAddWindowUrl,
      method: 'POST',
      params: {
        route_id: this.getNodeObjectId(this.root)
      },
      scope: this,
      success: function(response) {
        var win = smart_eval(response.responseText);
        if (!win)
          return;

        win.on('closed_ok', this.loadRouteData, this);
      },
      failure: uiAjaxFailMessage
    });
  },

  /**
   * Обработчик для меню добавления согласующего в этап.
   */
  onAddApprooverButtonClick: function() {
    var currentNode = this.getSelectionModel().getSelectedNode();
    if (
      !currentNode || !this.isPhaseNode(currentNode) ||
      !this.isActionPermitted('add-approover', currentNode)
    ) return;

    Ext.Ajax.request({
      url: this.approoverAddWindowUrl,
      method: 'POST',
      params: {
        phase_id: this.getNodeObjectId(currentNode)
      },
      scope: this,
      success: function(response) {
        var win = smart_eval(response.responseText);
        if (!win)
          return;

        win.on('closed_ok', this.loadRouteData, this);
      },
      failure: uiAjaxFailMessage
    });
  },

  /**
   * Обработчик нажатия кнопки Изменить.
   *
   * Кнопка позволяет редактировать этапы и согласующих.
   */
  onEditButtonClick: function() {
    var currentNode = this.getSelectionModel().getSelectedNode();
    if (
      !currentNode ||
      !this.isPhaseNode(currentNode) ||
      !this.isActionPermitted('edit-phase', currentNode)
    ) return;

    Ext.Ajax.request({
      url: this.phaseEditWindowUrl,
      method: 'POST',
      scope: this,
      params: {
        phase_id: this.getNodeObjectId(currentNode)
      },
      success: function(response) {
        var win = smart_eval(response.responseText);
        if (!win)
          return;

        win.on('closed_ok', this.loadRouteData, this);
      },
      failure: uiAjaxFailMessage
    });
  },

  /**
   * Обработчик нажатия кнопки Удалить.
   */
  onDeleteButtonClick: function() {
    var currentNode = this.getSelectionModel().getSelectedNode();
    if (
      !currentNode ||
      this.isRouteNode(currentNode) ||
      (
        this.isPhaseNode(currentNode) &&
        !this.isActionPermitted('delete-phase', currentNode)
      ) ||
      (
        this.isApprooverNode(currentNode) &&
        !this.isActionPermitted('delete-approover', currentNode)
      )
    ) return;

    var requestParams = {
      method: 'POST',
      scope: this,
      params: {},
    }

    var messageBoxParams = {
      icon: Ext.Msg.QUESTION,
      buttons: Ext.Msg.YESNO,
      scope: this,
      fn: function(btn, text, opt) {
        if (btn == 'yes') {
          var mask = this.getEl().mask();
          mask.show();

          requestParams.success = function() {
            mask.hide();
            this.loadRouteData();
          }
          requestParams.failure = function() {
            mask.hide();
            uiAjaxFailMessage(this, arguments);
          }

          Ext.Ajax.request(requestParams);
        }
      }
    };

    if (this.isPhaseNode(currentNode)) {
      requestParams.url = this.phaseDeleteUrl;
      requestParams.params.phase_id = this.getNodeObjectId(currentNode);

      if (currentNode.hasChildNodes()) {
        messageBoxParams.msg = (
          'Удалить выбранный этап из маршрута согласования (все согласующие ' +
          'также будут удалены )?'
        );
      } else {
        messageBoxParams.msg = (
          'Удалить выбранный этап из маршрута согласования?'
        );
      }
    } else if (this.isApprooverNode(currentNode)) {
      requestParams.url = this.approoverDeleteUrl;
      requestParams.params.approover_id = this.getNodeObjectId(currentNode);

      messageBoxParams.msg = 'Удалить выбранного согласующего из этапа?'
    }

    Ext.Msg.show(messageBoxParams);
  },

  /**
   * Обработчик нажатия кнопок "Переместить вверх" и "Переместить вниз".
   *
   * @param direction направление перемещения ('up' или 'down').
   */
  onMoveButtonClick: function(direction) {
    var currentNode = this.getSelectionModel().getSelectedNode();
    if (
      !currentNode ||
      !this.isPhaseNode(currentNode) ||
      (
        direction == 'up' &&
        !this.isActionPermitted('move-phase-up', currentNode)
      ) ||
      (
        direction == 'down' &&
        !this.isActionPermitted('move-phase-down', currentNode)
      )
    ) return;

    Ext.Ajax.request({
      url: this.reorderUrl,
      method: 'POST',
      params: {
        phase_id: this.getNodeObjectId(currentNode),
        direction: direction
      },
      scope: this,
      success: function(response) {
        var data = Ext.decode(response.responseText);
        if (data.success) {
          this.loadRouteData()
        } else {
          smart_eval(response.responseText);
        }
      },
      failure: uiAjaxFailMessage
    });
  },

  /**
   * Обработчик нажатия кнопки "Выбрать другой шаблон".
   */
  onChangeTemplateButtonClick: function() {
    if (!this.isActionPermitted('change-template', this.root)) return;

    Ext.Ajax.request({
      url: this.templateSelectUrl,
      method: 'POST',
      scope: this,
      params: Ext.applyIf({
        object_type_id: this.objectTypeId,
        current_route_id: this.routeId,
      }, this.actionContextJson),
      success: function(response) {
        var win = smart_eval(response.responseText);
        if (!win)
          return;

        win.on('closed_ok', this.recreateRoute, this);
      },
      failure: uiAjaxFailMessage
    });
  },

  /**
   * Отображает окно проставления результата рассмотрения объекта согласования.
   */
  onSetReviewResultButtonClick: function() {
    var currentNode = this.getSelectionModel().getSelectedNode();
    if (
      !currentNode ||
      !this.isApprooverNode(currentNode) ||
      !this.isActionPermitted('set-review-result', currentNode)
    ) return;

    Ext.Ajax.request({
      url: this.reviewWindowUrl,
      method: 'POST',
      scope: this,
      params: Ext.applyIf({
        route_approover_id: this.getNodeObjectId(currentNode),
      }, this.actionContextJson),
      success: function(response) {
        var win = smart_eval(response.responseText);
        if (!win)
          return;

        win.on('closed_ok', this.loadRouteData, this);
      },
      failure: uiAjaxFailMessage
    });
  },

  /**
   * Отправляет HTTP-запрос на пересоздание маршрута согласования.
   * @param {*} templateId  идентификатор шаблона маршрута.
   */
  recreateRoute: function(templateId) {
    Ext.Ajax.request({
      url: this.recreateRouteUrl,
      method: 'POST',
      scope: this,
      params: Ext.applyIf({
        object_type_id: this.objectTypeId,
        object_id: this.objectId,
        template_id: templateId,
      }, this.actionContextJson),
      success: function(response) {
        var data = Ext.decode(response.responseText);
        if (data.route_id) {
          this.routeId = parseInt(data.route_id);
          this.loadRouteData()
        } else {
          smart_eval(response.responseText);
        }
      },
      failure: uiAjaxFailMessage
    });
  },

  /**
   * Обработчик нажатия кнопки "История".
   */
  onHistoryButtonClick: function() {
    var currentNode = this.getSelectionModel().getSelectedNode();
    if (
      !currentNode ||
      !this.isApprooverNode(currentNode) ||
      !this.isActionPermitted('view-approover-history', currentNode)
    ) return;

    Ext.Ajax.request({
      url: this.historyWindowUrl,
      method: 'POST',
      scope: this,
      params: {
        approover_id: this.getNodeObjectId(currentNode),
      },
      success: function(response) {
        smart_eval(response.responseText);
      },
      failure: uiAjaxFailMessage
    });
  },

  /**
   * Возвращает состояние маршрута согласования.
   */
  getRouteState: function() {
    return this.root.attributes.stateId;
  },

  /**
   * Возвращает текстовое описание маршрута согласования.
   */
  getRouteTitle: function(routeData) {
    var result = 'Состояние маршрута: ' + routeData.state_name;
    if (routeData.template_name) {
      result |= ', создан на основе шаблона "' + routeData.template_name + '"';
    }
    return result;
  },

  /**
   * Загружает данные маршрута согласования.
   */
  loadRouteData: function() {
    if (!this.routeId) return;

    var mask = this.getEl().mask();
    mask.show();

    Ext.Ajax.request({
      url: this.dataUrl,
      method: 'POST',
      params: {
        route_id: this.routeId,
      },
      scope: this,
      success: function(response, options) {
        mask.hide();
        var data = Ext.util.JSON.decode(response.responseText);
        if ('success' in data) {
          smart_eval(response.responseText);
          return;
        }
        // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        // Пересоздание корневого узла (узла маршрута согласования).

        this.rootVisible = true;
        this.setRootNode(new Ext.m3.ObjectCoordination.TreeNode({
          id: 'route-' + data.route.id,
          title: this.getRouteTitle(data.route),
          stateId: data.route.state_id,
          stateName: data.route.state_name,
          permittedActions: data.route.permitted_actions,
          expanded: true,
          uiProvider: Ext.m3.ObjectCoordination.RouteNodeUI
        }));
        // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        // Доступные в гриде действия.

        this.permittedActions = data.route.permitted_actions;
        // - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        // Данные грида.

        for (var i = 0; i < data.route.phases.length; i++) {
          var phaseData = data.route.phases[i];
          var phaseNode = new Ext.m3.ObjectCoordination.TreeNode({
            id: 'phase-' + phaseData.id,
            title: phaseData.title,
            permittedActions: Ext.util.JSON.decode(
              phaseData.permitted_actions
            ),
            uiProvider: Ext.m3.ObjectCoordination.PhaseNodeUI,
            expanded: true
          });
          this.root.appendChild(phaseNode);

          for (var j = 0; j < phaseData.approovers.length; j++) {
            var approoverData = phaseData.approovers[j];
            var approoverNode = new Ext.m3.ObjectCoordination.TreeNode({
              id: 'approover-' + approoverData.id,
              title: approoverData.title,
              result: approoverData.result,
              comment: approoverData.comment || '',
              user: approoverData.user,
              time: approoverData.time,
              permittedActions: Ext.util.JSON.decode(
                approoverData.permitted_actions
              ),
              uiProvider: Ext.m3.ObjectCoordination.ApprooverNodeUI
            });
            phaseNode.appendChild(approoverNode);
          }
        }

        this.switchChangeTemplateButton();
        this.root.select();

        this.fireEvent('loaddata');
      },
      failure: function(response, options) {
        mask.hide();
        uiAjaxFailMessage(response, options);
      }
    });
  }
});
// ============================================================================
