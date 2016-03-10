/**
 * Created by M on 2/29/16.
 */

var SLIDESHOW = {
    SLIDESHOWTIMEOUT: 1000,

    slides: [],
    index: 0,
    prevIndex: -1,
    jug: new Juggernaut(),

    showSlide: function() {
        if(SLIDESHOW.prevIndex != -1) $(SLIDESHOW.slides[SLIDESHOW.prevIndex]).hide();
        $(SLIDESHOW.slides[SLIDESHOW.index]).show();
        SLIDESHOW.prevIndex = SLIDESHOW.index;
        SLIDESHOW.index++;
        if (SLIDESHOW.index >= SLIDESHOW.slides.length) SLIDESHOW.index = 0;
        setTimeout(SLIDESHOW.showSlide, SLIDESHOW.SLIDESHOWTIMEOUT);
    },

    startSlideshow: function() {
        this.slides = $('.slideshow-image');
        this.index = 0;
        this.showSlide();
    }
  //  ,
  //
  //jug.subscribe('channel', function(data) {
  //  alert('Got message: ' + data);
  //});
};

$(function() {
    SLIDESHOW.startSlideshow();
});