/**
 * Created by M on 2/29/16.
 */

var INSTAAPI = {
    makeBlob: function(imgSrc, callback) {
        var img = new Image();
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
        var id = $(this).parent().attr('id');
        var value = $(this).val();
        if (value == 'delete') INSTAAPI.delete(id);
        else INSTAAPI.storeImage(id, value, $(this).siblings('.insta-image').prop('src'));
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
            form.append('file', blob, id+'.png');
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
            if (val == 'edited_super') val = 'super'; // TODO: set another thing to mark it as edited
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
    $('.insta-holders').each(function(){
        INSTAAPI.checkIds(this);
    });
    $("input[type='radio']").click(INSTAAPI.radioClick);
});