/* 章節導覽列 .chnav — 捲到哪一段就高亮哪一顆。三頁共用。
   不需要設定:它讀每個 <a data-sec="…"> 去對應同名的 section id,
   所以之後增減章節按鈕不用動這個檔。 */
(function () {
  var links = document.querySelectorAll('.chnav a[data-sec]');
  if (!links.length || !('IntersectionObserver' in window)) return;

  var byId = {};
  links.forEach(function (a) { byId[a.dataset.sec] = a; });

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var a = byId[e.target.id];
      if (!a) return;
      if (e.isIntersecting) {
        links.forEach(function (l) { l.classList.toggle('on', l === a); });
      }
    });
  }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });

  Object.keys(byId).forEach(function (id) {
    var sec = document.getElementById(id);
    if (sec) io.observe(sec);
  });
})();
