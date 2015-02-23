var new_count = 0;
var elem_count = 0;

var publishDid = function(){
    //extract element data
    var elem_data = [];  
    for( var i = 0; i < elem_count; i++ ){
        var e = document.getElementById('elem'+i);
        elem_data.push({
            value: e.value,
            image: (e.type == "file")
        });
        if(e.type == "file") console.log(e.value);
    }
    
    //creata data Obj and attach title
    var send_data = {
        title: document.getElementById('did_title').value,
        body: elem_data
    };

    //ajax call sending did data to default/create_did
    $.ajax({
        type: 'POST',
        url: 'create_did',
        data: {data: JSON.stringify(send_data)},
        success: function(data){
            $('#new'+new_count).html(data);
        }});
    $('#main_container').prepend('<a class="btn" id="new_btn" onclick="newDid();">new did</a>');
    elem_count = 0;
}

/* Cancels the creation of the current 'new#' did */
var cancelNewDid = function(id_num){
    elem_count = 0;
    new_count--;
    $('#new'+id_num).remove();
    $('#main_container').prepend('<a class="btn" id="new_btn" onclick="newDid();">new did</a>');
}

/* Adds a text element to new did being edited */
var addText = function(){
    $('#did_form').append('<textarea class="form-text animated" id="elem'+ elem_count +'"></textarea>');
    $('#elem'+ elem_count++).autosize();
}

/* Adds an image upload field to the new did being edited */
var addImage = function(){
    $('#did_form').append('<div id="img_prev'+elem_count+'"class="image-preview"></div>'
                         +'<input id="elem'+ elem_count++ +'" type="file" />' );
}

/* Removes the last element from the currently editable did */
var rmElement = function(){
    if (elem_count > 0){
        $('#elem'+ --elem_count).remove();
        $('#img_prev'+ elem_count).remove();
    }
}

/* Generates a new editable did */
var newDid = function(){
    ++new_count;
    var did_string = '<div class="did" id="new' + new_count + '">'
                    +'<div id="did_form">'
                    +'<input id="did_title" class="form-title" type="text"/>'
                    +'</div>'
                    +'<a class="btn form_btn" onclick="addText()">add text</a>'
                    +'<a class="btn form_btn" onclick="addImage()">add image</a>'
                    +'<a class="btn form_btn" onclick="rmElement()">remove element</a>'
                    +'<a style="float: right" class="btn form_btn" onclick="publishDid();">publish</a>'
                    +'<a style="float: right" class="btn form_btn" onclick="cancelNewDid('+new_count+');">cancel</a>'
                    +'</div>';
    $('#did_container').prepend(did_string);
    $('#new_btn').remove();
}