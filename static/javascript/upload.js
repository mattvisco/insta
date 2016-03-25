/**
 * Created by M on 3/11/16.
 */

var socket;
var loading = false;

$(function() {
    socket = io.connect('http://' + document.domain + ':' + location.port + '/slides');
    socket.on('connect', function() {
        console.log('joined')
    });

    $('input[type=submit]').click(function(){
        if($('file-to-send').files.length == 0 || loading) {
            return false;
        } else {
            $('#check').hide();
            $('#fail').hide();
            $('#spin').show();
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
            $('#fail').show();
            alert(data.error);
        } else {
            $('#spin').hide();
            $('#fail').hide();
            $('#check').show();
            socket.emit('upload complete', data);
        }
    });
});