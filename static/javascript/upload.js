/**
 * Created by M on 3/11/16.
 */

var socket;
var loading = false;
var images = [];

function removeElFromArr(array, el) {
    var index = array.indexOf(el);
    if (index > -1) {
        array.splice(index, 1);
    }
    //return array;
}



$(function() {
    socket = io.connect('http://' + document.domain + ':' + location.port + '/slides');
    socket.on('connect', function() {
        console.log('joined');
        images.forEach(function (image) {
           socket.emit('send-image', image);
        });
    });

    $('input[type=submit]').click(function(){
	if($('#file-to-send').get(0).files.length == 0 || loading) {
            return false;
        } else {
            $('#check').hide();
            $('#fail').hide();
            $('#spin').css({display: 'inline-block'});
            loading = true;
            $(this).css({backgroundColor: 'grey', cursor: 'not-allowed'});
        }
    });

    $('#super-upload').ajaxForm(function(data) {
        loading = false;
        $('input[type=submit]').css({backgroundColor: '', cursor: ''});
        if(data.error) {
            $('#spin').hide();
            $('#check').hide();
            $('#fail').css({display: 'inline-block'});
            alert(data.error);
        } else {
            $('#spin').hide();
            $('#fail').hide();
            $('#check').css({display: 'inline-block'});
            images.push(data);
            socket.emit('send-image', data);
        }
    });

    // Remove received image from cache
    socket.on('image-received', function(data) {
        images.forEach(function (image_data) {
           if (image_data.image.filename == data.image.filename) removeElFromArr(images, image_data);
        });
    });
});
