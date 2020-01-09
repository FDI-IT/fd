jQuery(document).ready(function(){  

    setInterval(function() {
    //In order to refresh the images, we change the image source on a set interval.
    //The browser will think it's a different image, when in reality the 'rand' argument
    // after the '?' is ignored.
        
        var images = $('.padtest');
        
        for (var i=0; i<images.length; i++) {
          var image_source = images[i].src;
          // if image_source already contains '?rand=', replace it.  if not, append it.
          if (image_source.match(/rand/)) {
            images[i].src = image_source.replace(/\brand=[^&]*/, 'rand=' + Math.random());
          }
          else {                                         
              images[i].src = image_source + '?rand=' + Math.random();
          }
        }
    }, 5000);
    
});