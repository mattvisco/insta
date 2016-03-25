/**
 * Created by M on 3/11/16.
 */

var socket;
var loading = false;

$(function() {
    socket = io.connect('http://' + document.domain + ':' + location.port + '/slides');
    socket.on('connect', function() {
        socket.emit('upload complete', data);
        console.log('joined')
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
            socket.emit('upload complete', data);
        }
    });
});
