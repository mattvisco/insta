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
    /* added height properties */
    height: null,
    diffHeight: 0,

    getRoom: function() {
        var locationArr = window.location.pathname.split('/');
        var room = locationArr[locationArr.length - 1];
        return room;
    },

    showSlide: function() {
        if(SLIDESHOW.prevIndex != -1) $(SLIDESHOW.slides[SLIDESHOW.prevIndex]).hide();
        $(SLIDESHOW.slides[SLIDESHOW.index]).show();

        /* Get shown slide's height */
        SLIDESHOW.height = $(SLIDESHOW.slides[SLIDESHOW.index]).height();

        SLIDESHOW.prevIndex = SLIDESHOW.index;
        SLIDESHOW.index++;
        if (SLIDESHOW.index >= SLIDESHOW.slides.length) SLIDESHOW.index = 0;
        SLIDESHOW.slideTimeout = setTimeout(SLIDESHOW.showSlide, SLIDESHOW.SLIDESHOWTIMEOUT); 

        /* compare slide/window heights and center image */      
        if(SLIDESHOW.height > $(window).height()) SLIDESHOW.diffHeight = 1;
        if(SLIDESHOW.height < $(window).height()) SLIDESHOW.diffHeight = 0;
        SLIDESHOW.centerSlide(SLIDESHOW.diffHeight); 
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
    },
    /* center image */
    centerSlide: function(diff) {
        var d = Math.abs(SLIDESHOW.height - $(window).height())/2;       
        if (diff==1) {
            d = d * -1;
        }else{
            d = d;
        };
        SLIDESHOW.slides.css('margin-top', d);
    }
};

$(function() {
    $('body').css('background-color', '#000');
    SLIDESHOW.startSlideshow();
});