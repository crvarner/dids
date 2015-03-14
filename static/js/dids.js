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





//var REGEX = ('/\B#\w*[a-zA-Z]+\w*/');
// from rayfranco stackpverflow url http://stackoverflow.com/questions/8650007/regular-expression-for-twitter-username
var linkify = function(str) {
    console.log('in linkify');
    var regex   = /(^|[^@\w])@(\w{1,15})\b/g;
    var replace = '$1<a href="http://127.0.0.1:8000/dids/default/profile/$2">@$2</a>';
    str = str.replace( regex, replace );
    console.log(str);
    console.log('exit linkify');
    return str;
}



/* Image preview modified from example*/
/* http://stackoverflow.com/questions/4459379/preview-an-image-before-it-is-uploaded */
var imgProfilePreview = function(image, div_id){
    if(image.files && image.files[0]){
        var reader = new FileReader();
        console.log("in image preview");
        reader.onload = function(e){
            console.log(e.target.result);
            $('#'+div_id).html(
                '<img class ="profile_image_preview" style="width: 100px; height: 100px; border-radius: 15%; padding: 4px" src="'+ e.target.result +'"></img>'
            );
        }
        reader.readAsDataURL(image.files[0]);
    }
};


var editProfileImage = function() {
    //$('#profile_image').hide();
    //var image = $('#profile_image').val();
    //$('#profile_image').html('');
    $('#upper_profile').prepend('<div id=edit_div type="hidden">'
                         +'<form id="image_form" style="padding:0px; margin:0px;"type="hidden" enctype="multipart/form-data" action="update_profile" method="post">'
                         +'<input id="image" name="image" type="file"/>'
                         +'<input name="is_img" type="hidden" value="True"/>'
                         +'</form>'
                         +'</div>');
    $('#image').hide();
    $('#image').click();
    console.log('image sent\n')
    $('#image').change(function(){
        console.log("in in image change");
        $('#image_form').submit();
        imgProfilePreview(this, 'profile_image');
        console.log('image sent\n')
        $('#edit_div').remove();
    });
    $('#image_form').submit(function(event){
        event.preventDefault(); 
        var up = new FormData(this);
       $.ajax({
            url: 'http://127.0.0.1:8000/dids/default/update_profile',
            data: up,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function(data){
                console.log(data);
            }
        });
    }); 
    return;
}


var editAbout = function() {
    $('#lower_profile').hide();
    var user_about = $('#about').text();
    $('#profile_container').append('<div id="edit_div">'
                        +'<form id="profile_form" enctype="multipart/form-data" action="update_profile" method="post">'
                        +'</form>'
                        +'</div>');
    console.log("in editAbout");
    $('#profile_form').prepend('<textarea maxLength="128" id="editing_about" class="about-text animated" name="about">'+user_about+'</textarea>');
    console.log(user_about);
    $('#editing_about').focus();

    // on.blur() function for text area
    $('#editing_about').on('blur', function(){
        console.log('in blur function');
        $('#about').html(linkify($('#editing_about').val()));
        updateProfile();
        $('#profile_form').remove();
        $('#edit_div').remove();
        $('#lower_profile').show();
    });
    // sumbit instrructions for about textarea form
    $('#profile_form').submit(function(event){
        event.preventDefault(); 
        var up = new FormData(this);
       $.ajax({
            url: 'http://127.0.0.1:8000/dids/default/update_profile',
            data: up,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function(data){
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
