function appendUsers(){
    {# обработчик, вызывается при нажатии кнопки ОК, в окне добаления пользователей к роли #}
    var selection = Ext.getCmp('{{window.grid.client_id}}').getSelectionModel().getSelections();
    if(selection.length == 0){
        Ext.Msg.show({
            title: 'Добавление пользователей',
            msg: 'Отметьте пользователей, которых Вы хотите добавить в роль.',
            buttons:Ext.Msg.OK,
            icon: Ext.Msg.WARNING});
    }
    else{
        Ext.Msg.show({
            title: 'Добавление пользователей',
            msg: 'Вы действительно хотите добавить отмеченных пользователей в роль (кол-во: ' + selection.length.toString() + ')?',
            buttons:Ext.Msg.YESNO,
            icon: Ext.Msg.QUESTION,
            fn : processResult});
    }
}

function processResult(btn){
    {# обработчик добавления пользователей к роли #}
    if(btn == 'yes'){
        {# получаем выбранных пользователей #}
        var selection = Ext.getCmp('{{window.grid.client_id}}').getSelectionModel().getSelections(),
            ids = '';
        for(var i = 0; i < selection.length; i++){
            ids += (selection[i].data['id'].toString() + ' ');
        }
        {# отправляем субмит на сервер #}
        Ext.Ajax.request({
            url: '{{ window.action_submit.absolute_url }}',
            params: Ext.applyIf({ ids: ids},{% if component.action_context %}{{component.action_context.json|safe}}{% else %}{}{% endif %}),
            success: function(response, opts){ 
                smart_eval(response.responseText);
                Ext.getCmp('{{window.client_id}}').fireEvent('closed_ok');
                Ext.getCmp('{{window.client_id}}').close();
            },
            failure: function(){
                Ext.Msg.show({
                    title:'',
                    msg: 'Не удалось добавить пользователей в роль.<br>Причина: сервер временно недоступен.',
                    buttons:Ext.Msg.OK, icon: Ext.Msg.WARNING});}
        });
    }
}