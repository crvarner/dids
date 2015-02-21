var new_count = 0;
var elem_count = 0;

var publishDid = function(){
    var elems = document.getElementsByClassName('form_text');
    var elem_data = [];
    for (var i = 0; i < elems.length; i++ ){
        elem_data.push(elems[i].value);
    }   
    var send_data = {
        title: document.getElementById('did_title').value,
        body: elem_data
    };
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
    $('#new'+id_num).remove();
    $('#main_container').prepend('<a class="btn" id="new_btn" onclick="newDid();">new did</a>');
}

var addText = function(){
    $('#did_form').append('<input class="form_text" id="elem'+ ++elem_count+'" type="text"/>');
}

var addImage = function(){
    $('#did_form').append('<div id="elem'+ ++elem_count+'" class="DZdiv">');
    $('#elem'+elem_count).dropzone({ url: "/upload-target",
                                     maxFiles: 1 });
}

var newDid = function(){
    ++new_count;
    var did_string = '<div class="did" id="new' + new_count + '">'
                    +'<div id="did_form">'
                    +'<input id="did_title" class="form_text form_title" type="text"/>'
                    +'</div>'
                    +'<a class="btn form_btn" onclick="addText()">add text</a>'
                    +'<a class="btn form_btn" onclick="addImage()">add image</a>'
                    +'<a class="btn form_btn" onclick="publishDid();">publish</a>'
                    +'<a class="btn form_btn" onclick="cancelNewDid('+new_count+');">cancel</a>'
                    +'</div>';
    $('#did_container').prepend(did_string);
    $('#new_btn').remove();
}

$('#main_container').prepend('<a class="btn" id="new_btn" onclick="newDid();">new did</a>');