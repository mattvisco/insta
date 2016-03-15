/**
 * Created by M on 3/11/16.
 */

var socket;
$(function() {
    socket = io.connect('http://' + document.domain + ':' + location.port + '/slides');

    $('#super-upload').ajaxForm(function(data) {
        if(data.error) alert(data.error);
        else {
            alert('Success');
            socket.emit('upload complete', data);
        }
    });
});