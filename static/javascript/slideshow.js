/**
 * Created by M on 2/29/16.
 */

var SLIDESHOW = {
    SLIDESHOWTIMEOUT: 3000,

    slides: [],
    index: 0,
    prevIndex: -1,
    socket: null,
    slideTimeout: null,

    getRoom: function() {
        var locationArr = window.location.pathname.split('/');
        var room = locationArr[locationArr.length - 1];
        return room;
    },

    showSlide: function() {
        if(SLIDESHOW.prevIndex != -1) $(SLIDESHOW.slides[SLIDESHOW.prevIndex]).hide();
        $(SLIDESHOW.slides[SLIDESHOW.index]).show();
        SLIDESHOW.prevIndex = SLIDESHOW.index;
        SLIDESHOW.index++;
        if (SLIDESHOW.index >= SLIDESHOW.slides.length) SLIDESHOW.index = 0;
        SLIDESHOW.slideTimeout = setTimeout(SLIDESHOW.showSlide, SLIDESHOW.SLIDESHOWTIMEOUT);
    },

    startSlideshow: function() {
        this.socket = io.connect('http://' + document.domain + ':' + location.port + '/slides');
        this.socket.on('connect', function() {
            console.log('joined')
            SLIDESHOW.socket.emit('joined', {room: SLIDESHOW.getRoom()});
        });
        this.socket.on('new-slide', SLIDESHOW.newSlide);
        this.slides = $('.slideshow-image');
        this.index = 0;
        this.showSlide();
    },

    newSlide: function(data) {
        console.log('new slide!');
        clearTimeout(SLIDESHOW.slideTimeout);
        var image = new Image();
        $(image).addClass('slideshow-image');
        image.src = Flask.url_for("static", {"filename": data.img_type + '/' + data.filename});
        SLIDESHOW.slides[SLIDESHOW.prevIndex].insertAdjacentElement("afterEnd", image);
        SLIDESHOW.slides = $('.slideshow-image');
        SLIDESHOW.showSlide();
    }
};

$(function() {
    SLIDESHOW.startSlideshow();
});