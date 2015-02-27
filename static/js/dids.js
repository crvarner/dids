var new_count = 0;
var elem_count = 0;

/*function progressHandlingFunction(e){
    if(e.lengthComputable){
        $('progress').attr({value:e.loaded,max:e.total});
    }
}*/

var publishDid = function(){
    $('#did_form').submit();
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
    $('#did_form').append('<textarea class="form-text animated" id="elem'+ elem_count +'" name="elem'+elem_count +'"></textarea>'
                         +'<input name="is_img'+ elem_count +'" type="hidden" value="False" />');
    $('#elem'+ elem_count++).autosize();
}

/* Adds an image upload field to the new did being edited */
var addImage = function(){
    $('#did_form').append('<div id="img_prev'+ elem_count +'" class="image-preview"></div>'
                         +'<input name="elem'+ elem_count +'" type="file" />'
                         +'<input name="is_img'+ elem_count++ +'" type="hidden" value="True" />');
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
                    +'<form id="did_form" enctype="multipart/form-data" action="create_did" method="post">'
                    +'<input id="did_title" class="form-title" name="did_title" type="text"/>'
                    //+'<input type="submit">'
                    +'</form>'
                    +'<a class="btn form_btn" onclick="addText()">add text</a>'
                    +'<a class="btn form_btn" onclick="addImage()">add image</a>'
                    +'<a class="btn form_btn" onclick="rmElement()">remove element</a>'
                    +'<a style="float: right" class="btn form_btn" onclick="publishDid();">publish</a>'
                    +'<a style="float: right" class="btn form_btn" onclick="cancelNewDid('+new_count+');">cancel</a>'
                    +'</div>';
    $('#did_container').prepend(did_string);
    
    $('#did_form').submit(function(event){
        event.preventDefault(); 
        var fd = new FormData(this);
    
        $.ajax({
            url: 'create_did',
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function(data){
                $('#new'+new_count).html(data);
            }
        });
        $('#main_container').prepend('<a class="btn" id="new_btn" onclick="newDid();">new did</a>');
    });
    $('#new_btn').remove();
}