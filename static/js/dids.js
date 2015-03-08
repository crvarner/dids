var new_count = 0;
var elem_count = 0;
var com_count = 0;

var publishDid = function(){
    $('#did_form').submit();
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
    $('#did_form').append('<textarea id="elem'+ elem_count +'" class="form-text animated" name="elem'+elem_count +'"></textarea>'
                         +'<input id="is_img'+ elem_count +'" name="is_img'+ elem_count +'" type="hidden" value="False" />');
    $('#elem'+ elem_count++).autosize();
}

/* Adds an image upload field to the new did being edited */
var addImage = function(){
    $('#did_form').append('<div id="img_prev'+ elem_count +'" class="image-preview"></div>'
                         +'<input id="elem'+ elem_count +'" name="elem'+ elem_count +'" type="file" />'
                         +'<input name="is_img'+ elem_count++ +'" type="hidden" value="True" />');
}

/* adds a comment field and cancel/submit buttons */
var addComment = function(div_id, did_id, com_btn){
    com_id = "com"+com_count;
    
    // prepend comment form to comment section
    $('#com_'+div_id).prepend('<div id="'+com_id+'" class="clear"><form id="'+com_id+'_form">'
                        +'<textarea name="comment" id="com_text'+div_id+'" class="form-text animated"></textarea>'
                        +'<input name="did_id" type="hidden" value="'+did_id+'" />'
                        +'<a id="submit'+did_id+'" class="btn form-btn" style="float:right">submit</a>'
                        +'<a id="cancel'+did_id+'" class="btn form-btn" style="float:right">cancel</a>'
                        +'</form></div>');
    $('#com_text'+div_id).autosize();
    
    // submit comment when submit button is clicked
    $('#submit'+did_id).click(function(){
        $('#'+com_id+'_form').submit();
    });
    
    // removes text-area when cancel is clicked
    $('#cancel'+did_id).click(function(){
        $('#'+com_id).remove();
        $(com_btn).show();
        com_count--;
    });
    
    // submit comment form
    $('#'+com_id+'_form').submit(function(event){
        event.preventDefault(); 
        var fd = new FormData(this);
    
        $.ajax({
            url: 'add_comment',
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function(data){
                //remove comment form
                $('#'+com_id).remove();
                // show add comment button
                $(com_btn).show();
                //add new comment to top of comments
                $('#com_'+div_id).prepend(data);
            }
        });
    });
    
    // hide comment button
    $(com_btn).hide();
    com_count++;
}

/* Removes the last element from the currently editable did */
var rmElement = function(){
    if (elem_count > 0){
        $('#is_img'+ --elem_count).remove();
        $('#elem'+ elem_count).remove();
        $('#img_prev'+ elem_count).remove();
    }
}

/* Generates a new editable did */
var newDid = function(){
    ++new_count;
    var did_string = '<div class="did clear" id="new' + new_count + '">'
                    +'<form id="did_form" enctype="multipart/form-data" action="create_did" method="post">'
                    +'<input class="form-title" name="did_title" type="text"/>'
                    +'<input name="div_id" type="hidden" value="new' + new_count + '" />'
                    +'</form>'
                    +'<a class="btn form-btn" onclick="addText()">add text</a>'
                    +'<a class="btn form-btn" onclick="addImage()">add image</a>'
                    +'<a class="btn form-btn" onclick="rmElement()">remove element</a>'
                    +'<a style="float: right" class="btn form-btn" onclick="publishDid();">publish</a>'
                    +'<a style="float: right" class="btn form-btn" onclick="cancelNewDid('+new_count+');">cancel</a>'
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
                $('#main_container').prepend('<a class="btn" id="new_btn" onclick="newDid();">new did</a>');
            }
        });
    });
    $('#new_btn').remove();
}