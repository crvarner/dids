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
    $('#new-btn').show();
}

/* Adds a text element to new did being edited */
var addText = function(){
    $('#did_form').append('<textarea id="elem'+ elem_count +'" class="form-text animated" name="elem'+elem_count +'"></textarea>'
                         +'<input id="is_img'+ elem_count +'" name="is_img'+ elem_count +'" type="hidden" value="False" />');
    $('#elem'+ elem_count++).autosize();
}

/* Image preview modified from example*/
/* http://stackoverflow.com/questions/4459379/preview-an-image-before-it-is-uploaded */
var imgPreview = function(image, div_id){
    if(image.files && image.files[0]){
        var reader = new FileReader();
        reader.onload = function(e){
            console.log(e.target.result);
            $('#'+div_id).html(
                '<img style="width: 100%;" src="'+ e.target.result +'"></img>'
            );
        }
        reader.readAsDataURL(image.files[0]);
    }
};


/* Removes the last element from the currently editable did */
var rmElement = function(){
    if (elem_count > 0){
        $('#is_img'+ --elem_count).remove();
        $('#elem'+ elem_count).remove();
        $('#img_prev'+ elem_count).remove();
    }
}


//########################################################################################
//########### profile functions
//###########
//########################################################################################





//var REGEX = ('/\B#\w*[a-zA-Z]+\w*/');
// from rayfranco stackpverflow url http://stackoverflow.com/questions/8650007/regular-expression-for-twitter-username
var linkify = function(str) {
    console.log('in linkify');
    var regex_user   = /(^|[^@\w])@(\w{1,15})\b/g;
    var regex_hash = /(^|\s)#([^ ]*)/g;
    var replace_user = '$1<a href="../dids/default/profile/$2">@$2</a>';
    var replace_hash = '$1<a href="/dids/default/find/$2">#$2</a>';
    str = str.replace( regex_user, replace_user );
    str = str.replace( regex_hash, replace_hash );
    console.log(str);
    console.log('exit linkify');
    return str;
}



//########################################################################################

/******************
navbar menu behaviour
*******************/

$('html').click(function() {
   $('#dids-menu-right').hide(); 
});

$('#dids-menu-right-container').click(function(event){
     event.stopPropagation();
});

$('#dids-menu-title').click(function(event){
     $('#dids-menu-right').slideToggle(100);
});

/*************************
toggle comments
*************************/

var toggleComments = function(div_id, com_btn){
    var num = ($(com_btn).html()).replace(/^\D+|\D+$/g, "")
    if ($('#'+div_id).css('display') != 'none'){
        $(com_btn).html('show comments ('+num+')');
    } else {
        $(com_btn).html('hide comments ('+num+')');
    }
    $('#'+div_id).slideToggle(100);
}
