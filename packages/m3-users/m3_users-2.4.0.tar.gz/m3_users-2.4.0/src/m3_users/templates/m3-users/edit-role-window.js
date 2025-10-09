function getJsonOfStore(store){
    var datar = new Array(),
        records = store.getRange();
    for (var i = 0; i < records.length; i++) {
        datar.push(records[i].data);
    }
    return Ext.util.JSON.encode(datar);
}

function getPermissionCodes(store){
    {# Получение выбранных кодов прав доступа из store #}
    var permissionCodes = [],
        records = store.getRange();

    for (var i = 0; i < records.length; i++) {
        permissionCodes.push(records[i].data.permission_code);
    }

    return Ext.util.JSON.encode(permissionCodes);
}

function addPermissionCodesInParams(grid, req){
    {# Добавление в контекст выбранных кодов прав доступа #}
    req.params.perms = getPermissionCodes(grid.getStore());
}

function beforeSubmit(submit){
    {# сохранение роли #}
    var store = Ext.getCmp('{{ component.grid.client_id }}').getStore(),
        res = getJsonOfStore(store);
    submit.params.perms = res;
    return true;
}

function addPermission(grid, res, opt) {
    {# добалвяет запись о роли в грид #}
    var win = smart_eval(res.responseText);
    win.on('closed_ok', function (sels) {
        var store = this.getStore(),
            count = store.getCount();
        store.removeAll();
        for(var i = 0, len = sels.length; i < len; i++){
            var record = sels[i];
            var rec = new store.recordType(
                {
                    id: null,
                    "permission_code":record.attributes.url,
                    "verbose_name": record.attributes.fullname,
                    "disabled": false
                },
                record.attributes.url);
            store.add(rec);
        }
    }, scope = grid);
    win.show();
    return false;
}

var form = Ext.getCmp('{{ component.client_id }}'),
    grid = Ext.getCmp('{{ component.grid.client_id }}');
form.on('beforesubmit', beforeSubmit);
grid.on('afternewrequest', addPermission);
grid.on('beforenewrequest', addPermissionCodesInParams);

function deletePermission() {
    {# обработчик удаления роли #}
    if (grid.getSelectionModel().hasSelection()) {
        Ext.Msg.show({
            title: 'Удаление записи',
            msg: 'Вы действительно хотите удалить выбранные записи?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            fn: function(btn, text, opt){ 
                if (btn == 'yes') {
                    var store = grid.getStore();
                    store.remove(grid.getSelectionModel().getSelections());
                }
            }
        });
    } else {
        Ext.Msg.show({
            title: 'Удаление',
            msg: 'Элемент не выбран!',
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.INFO
        });
    }
}

{% block content %}
{% endblock %}