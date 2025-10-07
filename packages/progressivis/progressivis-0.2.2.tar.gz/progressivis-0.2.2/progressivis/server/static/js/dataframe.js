var module_id = null,
    dataframe_slot = null;

function dataframe_get(success, error) {
    progressivis_post('/progressivis/module/df/'+module_id+'/'+dataframe_slot,
                     success, error);
}

function dataframe_update(data) {
    progressivis_update(data);
    dataframe_update_table(data);
}

function dataframe_update_table(data) {
    if ( ! $.fn.DataTable.isDataTable( '#dataframe' ) ) {
        var columns = data['columns'].map(function(c) { return {"sTitle": c.toString()}; });
        data_table = $('#dataframe').DataTable( {
            "columns": columns,
            "processing": true,
            "serverSide": true,
            //"retrieve": true,
            "ajax": {url: $SCRIPT_ROOT+'/progressivis/module/dfslice/'+module_id+'/'+dataframe_slot, type:'POST'}
        });
    } else {
        //$('#dataframe').dataTable({"retrieve": true}).ajax.reload();
        data_table.ajax.reload(null, false);
    }
}

function dataframe_refresh() {
  dataframe_get(dataframe_update, error);
}

function dataframe_ready() {
    if (refresh == null) {
        refresh = dataframe_refresh;
    }
    progressivis_ready("dataframe "+module_id);
}
