/**
 * Created by M on 2/29/16.
 */

var INSTAAPI = {
    makeBlob: function(imgSrc, callback) {
        var img = new Image();
        img.setAttribute('crossOrigin', 'anonymous');
        img.src = imgSrc;
        img.onload = function () {
            var canvas = document.createElement("canvas");
            canvas.width = this.width;
            canvas.height = this.height;
            var ctx = canvas.getContext("2d");
            ctx.drawImage(this, 0, 0);
            canvas.toBlob(callback);
        }
    },

    radioClick: function() {
        /* changed the selectors since I added some div's in between */
        var id = $(this).parent().parent().attr('id');
        //var id = $(this).parent().parent().attr('id');
        var value = $(this).val();
        if (value == 'delete') INSTAAPI.delete(id);
        else INSTAAPI.storeImage(id, value, $(this).parent().parent().find('img').attr('src'));
        //else INSTAAPI.storeImage(id, value, $(this).siblings('.insta-image').prop('src'));
        
    },

    delete: function(id) {
        var request = {
            url: '/delete/' + id,
            type: 'DELETE'
        }
        $.ajax(request);
    },

    storeImage: function(id, value, imageSrc) {
        var url = '/store/' + value + '/' + id;
        var sendImage = function(blob) {
            var form = new FormData();

            /* Changed the extension to jpg like the original file don't know if it is of any use */
            form.append('file', blob, id+'.jpg');
            //form.append('file', blob, id+'.png');
            var request = {
                url: url,
                data: form,
                type: 'POST',
                cache: false,
                processData: false,
                contentType: false,
                success: function(response){
                    console.log(response);
                },
                error: function(response) {
                    console.log(response);
                }
            };
            $.ajax(request);
        };
        INSTAAPI.makeBlob(imageSrc, sendImage);
    },

    checkIds: function(holder) {
        var holder = $(holder);
        var id = holder.attr('id');
        var url = '/check_id/' + id;
        var success = function(response) {
            var val = response.idValue;
            holder.find("input[value='"+val+"']").get(0).checked = 'checked';
        };
        var request = {
            url: url,
            type: 'GET',
            success: success,
            error: function(response) {
                console.log(response);
            }
        };
        $.ajax(request);
    }
};

$(function() {
    var i = 0;
    $('.insta-holders').each(function(){
        INSTAAPI.checkIds(this);

        /* increment the inputs name attribute for each holder */
        $(this).find('input').each(function(){
            var new_name = 'store_image_'+i;
            $(this).attr('name', new_name);
        });
        i++;
        /* --------------------------------------------------- */
    });
    $("input[type='radio']").click(INSTAAPI.radioClick);
});