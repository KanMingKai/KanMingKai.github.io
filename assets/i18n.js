/* 中 / 英切換 —— 六頁共用,不需要另一份 HTML。

   用法:在任何元素上加 data-en,值是該元素切到英文時的完整內容(可含 HTML)。
     <h4 data-en='Single navigation architecture'>廠區 AMR 單一導航架構與雙模切換設計</h4>
   沒有 data-en 的元素不會被動到,所以可以一段一段慢慢補,不必一次翻完。

   ★ 中文原文不寫進 HTML —— 第一次切換時才把當下的 innerHTML 記進 JS 的
     Map 裡。這樣中文永遠是檔案裡看得到的那一份,英文是附加的,
     改中文時不必同步改第二個地方。

   ★ 選擇存在 localStorage,跨頁與重新整理都記得;
     <html lang> 也一起換,螢幕閱讀器與瀏覽器翻譯才不會判斷錯語言。 */
(function () {
  var KEY = 'site-lang';
  var zh = new Map();          // 元素 → 中文原始 innerHTML
  var cur = 'zh';

  function nodes() { return document.querySelectorAll('[data-en]'); }

  function apply(lang) {
    nodes().forEach(function (el) {
      if (!zh.has(el)) zh.set(el, el.innerHTML);
      el.innerHTML = (lang === 'en') ? el.getAttribute('data-en') : zh.get(el);
    });
    document.documentElement.lang = (lang === 'en') ? 'en' : 'zh-Hant';
    cur = lang;

    var btn = document.getElementById('lang-btn');
    if (btn) {
      // 按鈕顯示的是「按下去會切到哪」,不是現在的語言
      btn.textContent = (lang === 'en') ? '中文' : 'EN';
      btn.setAttribute('aria-label', (lang === 'en') ? '切換為中文' : 'Switch to English');
      btn.setAttribute('aria-pressed', lang === 'en' ? 'true' : 'false');
    }
  }

  function init() {
    var saved;
    try { saved = localStorage.getItem(KEY); } catch (e) { saved = null; }
    apply(saved === 'en' ? 'en' : 'zh');

    var btn = document.getElementById('lang-btn');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var next = (cur === 'en') ? 'zh' : 'en';
      apply(next);
      try { localStorage.setItem(KEY, next); } catch (e) {}
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
