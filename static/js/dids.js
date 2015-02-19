var new_count = 0;

var publishDid = function(){
    $('#pub_btn').remove();
    $('#cancel_btn').remove();
    $('#main_container').prepend('<a class="btn" id="new_btn" onclick="newDid();">new did</a>');
    var title = document.getElementById('did_title').value
    var body = document.getElementById('did_body').value
    $.ajax({
        url: 'create_did',
        data: {title: title, body: body},
        success: function(data){
            $('#new'+new_count).html(data);
        }});
}

var cancelNewDid = function(id_num){
    $('#new'+id_num).remove();
    $('#main_container').prepend('<a class="btn" id="new_btn" onclick="newDid();">new did</a>');
}

var newDid = function(){
    ++new_count;
    var did_string = '<div class="did" id="new' + new_count + '">'
                    +'<form class="did_form">'
                    +'<input id="did_title" type="text" style="width: 100%"/>'
                    +'<input id="did_body" type="text" style="width: 100%; margin-bottom: 0px"/>'
                    +'</form>'
                    +'<a class="btn" id="pub_btn" onclick="publishDid();" style="margin-top: 10px">publish</a>'
                    +'<a class="btn" id="cancel_btn" onclick="cancelNewDid('+new_count+');" style="margin-top: 10px">cancel</a>'
                    +'</div>';
    $('#new_btn').remove();
    $('#did_container').prepend(did_string);
}

$('#main_container').prepend('<a class="btn" id="new_btn" onclick="newDid();">new did</a>');