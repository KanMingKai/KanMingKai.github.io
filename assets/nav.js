/* 章節導覽列 .chnav — 捲到哪一段就高亮哪一顆。六頁共用。
   不需要設定:它讀每個 <a data-sec="…"> 去對應同名的 section id,
   所以之後增減章節按鈕不用動這個檔。

   ★ 同時負責「回履歷」那顆按鈕的目的地:
       .chnav-back[data-resume-default]  該頁的預設落點(章節沒有對應項目時用)
       .chnav a[data-sec][data-resume]   該章節在履歷上的對應項目 id
     捲到哪一節,就把回履歷的 href 換成那一節的 data-resume;
     沒有 data-resume 的章節則退回 data-resume-default。
     ★ href 在 HTML 裡已經寫死成預設值 —— 這裡只是「跟著捲動變得更精準」。
       所以 JS 沒載入時按鈕仍然可用,只是不會隨章節變化。

   ★★ 為什麼要自己記 visible 狀態,而不是直接在 callback 裡看 e.isIntersecting:
       IntersectionObserver 一次會送進來一批 entries,順序不保證等於文件順序,
       而且只包含「這次有變化」的元素。若直接對每個 intersecting 的 entry 就
       套用一次,等於最後一筆決定結果 —— 捲快一點就會選到畫面外的那一節
       (實測會出現「捲到 decision-1 卻指回 xp-safety」這種錯位)。
       改成:記下每一節目前可見與否,再從文件順序取「最上面那個可見的」,
       結果就與捲動速度和 entry 順序無關。 */
(function () {
  var links = document.querySelectorAll('.chnav a[data-sec]');
  if (!links.length || !('IntersectionObserver' in window)) return;

  var back = document.querySelector('.chnav-back[data-resume-default]');
  var base = back ? (back.getAttribute('href') || '').split('#')[0] : '';

  var byId = {};
  links.forEach(function (a) { byId[a.dataset.sec] = a; });

  // 依文件順序排好的 section id,決定「同時可見時要以哪一節為準」
  var order = Object.keys(byId)
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean)
    .sort(function (x, y) {
      return (x.compareDocumentPosition(y) & Node.DOCUMENT_POSITION_FOLLOWING) ? -1 : 1;
    })
    .map(function (sec) { return sec.id; });

  /* 選出「現在正在讀的那一節」。
     不能只看 IntersectionObserver 說誰可見 —— 帶狀區很窄,但章節有高有低,
     一個很長的章節在下一節已經捲到畫面中央時仍然可能碰到帶狀區。
     取文件順序第一個可見的會選到上面那個長章節(實測 #platforms、#transfer、
     #architecture 三處就是這樣被前一節蓋掉的)。
     改成用一條基準線(視窗高度一半,與 rootMargin 的 -45%/-50% 對齊)去量:
     取「最後一個」涵蓋這條線的章節 —— 也就是真正跨在讀者視線上的那一個。 */
  function pick() {
    var line = (window.innerHeight || document.documentElement.clientHeight) * 0.5;
    var chosen = null, lastAbove = null;
    for (var i = 0; i < order.length; i++) {
      var sec = document.getElementById(order[i]);
      if (!sec) continue;
      var r = sec.getBoundingClientRect();
      if (r.top <= line && r.bottom > line) chosen = order[i];
      if (r.top <= line) lastAbove = order[i];
    }
    // 基準線剛好落在兩節之間(章節有間距)時,算成上面那一節
    return chosen || lastAbove;
  }

  function apply() {
    var id = pick();
    if (!id) return;                       // 還沒捲到任何一節就維持現狀,不要閃
    var a = byId[id];
    if (!a) return;
    links.forEach(function (l) { l.classList.toggle('on', l === a); });
    if (back) {
      var target = a.dataset.resume || back.dataset.resumeDefault;
      if (target) back.setAttribute('href', base + '#' + target);
    }
  }

  /* observer 只當「有東西進出帶狀區了,重算一次」的觸發器,
     真正的判斷交給 pick()。捲動事件另外補一層(rAF 節流),
     因為在很長的章節裡捲動時 observer 不會再送任何 entry。 */
  var io = new IntersectionObserver(apply,
    { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
  order.forEach(function (id) { io.observe(document.getElementById(id)); });

  var ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { ticking = false; apply(); });
  }, { passive: true });

  apply();
})();
