! function() {
 $(window).scroll(function() {
  var t = $(document).scrollTop();
  $(".splash").css({
   "background-position": "0px -" + (t / 3).toFixed(2) + "px"
  }), t > 50 ? $("#home > .navbar").removeClass("navbar-transparent") : $("#home > .navbar").addClass("navbar-transparent")
 }), $("a[href='#']").click(function(t) {
  t.preventDefault()
 });
 var t = $("<div id='source-button' class='btn btn-primary btn-xs'>&lt; &gt;</div>").click(function() {
  var t = $(this).parent().html();
  t = function(t) {
   var n = (t = t.replace(/×/g, "&times;").replace(/«/g, "&laquo;").replace(/»/g, "&raquo;").replace(/←/g, "&larr;").replace(/→/g, "&rarr;")).split(/\n/);
   n.shift(), n.splice(-1, 1);
   var o = n[0].length - n[0].trim().length,
    a = new RegExp(" {" + o + "}");
   return n = (n = n.map(function(t) {
    return t.match(a) && (t = t.substring(o)), t
   })).join("\n")
  }(t), $("#source-modal pre").text(t), $("#source-modal").modal()
 });
 $('.bs-component [data-toggle="popover"]').popover(), $('.bs-component [data-toggle="tooltip"]').tooltip(), $(".bs-component").hover(function() {
  $(this).append(t), t.show()
 }, function() {
  t.hide()
 })
}();