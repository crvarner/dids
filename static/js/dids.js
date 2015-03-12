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

/* Image preview modified from example*/
/* http://stackoverflow.com/questions/4459379/preview-an-image-before-it-is-uploaded */
var imgPreview = function(image, div_id){
    if(image.files && image.files[0]){
        var reader = new FileReader();
        reader.onload = function(e){
            console.log(e.target.result);
            $('#'+div_id).html(
                '<img style="width: 100%; height: 100%; border-radius: 5px;" src="'+ e.target.result +'"></img>'
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

var editAbout = function() {
    $('#lower_profile').hide();
    user_about = $('#about').text();
    $('#profile_container').append('<div id="edit_div">'
                        +'<form id="profile_form" enctype="multipart/form-data" action="update_profile" method="post">'
                        +'</form>'
                        +'</div>');
    console.log("in editAbout");
    $('#profile_form').prepend('<textarea maxLength="256" id="editing_about" class="about-text animated" name="about">'+user_about+'</textarea>');
    console.log(user_about);
    $('#editing_about').focus();

    // on.blur() function for text area
    $('#editing_about').on('blur', function(){
        console.log('in blur function');
        $('#about').html($('#editing_about').val());
        updateProfile();
        $('#edit_div').remove();
        $('#lower_profile').show();
    });
    // sumbit instrructions for about textarea form
    $('#profile_form').submit(function(event){
        event.preventDefault(); 
        var up = new FormData(this);
       $.ajax({
            url: 'update_profile',
            data: up,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function(data){
                $('#profile_form').remove();
                $(edit_btn).show();
            }
        });
    }); 
    return;
}

var updateProfile = function(){
    console.log('in updateProfile');
    $('#profile_form').submit();
}

//########################################################################################
