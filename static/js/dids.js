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

var cancelNewDid = function(id_num){
    elem_count = 0;
    $('#new'+id_num).remove();
    $('#main_container').prepend('<a class="btn" id="new_btn" onclick="newDid();">new did</a>');
}

var addText = function(){
    $('#did_form').append('<textarea class="form-text animated" id="elem'+ elem_count +'"></textarea>');
    $('#elem'+ elem_count++).autosize();
}

var addImage = function(){
    $('#did_form').append('<div class="image-preview"></div>'
                         +'<input id="elem'+ elem_count++ +'" type="file" />' );
}

var newDid = function(){
    ++new_count;
    var did_string = '<div class="did" id="new' + new_count + '">'
                    +'<div id="did_form">'
                    +'<input id="did_title" class="form-title" type="text"/>'
                    +'</div>'
                    +'<a class="btn form_btn" onclick="addText()">add text</a>'
                    +'<a class="btn form_btn" onclick="addImage()">add image</a>'
                    +'<a class="btn form_btn" onclick="publishDid();">publish</a>'
                    +'<a class="btn form_btn" onclick="cancelNewDid('+new_count+');">cancel</a>'
                    +'</div>';
    $('#did_container').prepend(did_string);
    $('#new_btn').remove();
}

$(document).ready(function(){
    $('textarea').autosize();    
});
$('#main_container').prepend('<a class="btn" id="new_btn" onclick="newDid();">new did</a>');