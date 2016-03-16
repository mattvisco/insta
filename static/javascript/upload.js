/**
 * Created by M on 3/11/16.
 */

var socket;
$(function() {
    socket = io.connect('http://' + document.domain + ':' + location.port + '/slides');

    $('#super-upload').ajaxForm(function(data) {
        socket.emit('upload complete', data);
    });

    socket.on('new_slide', function(){console.log('got eeeem')});
});