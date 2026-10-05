/*
 * board.js — موتور مشترک همه‌ی تابلوها
 * داده‌ی نمونه، قالب‌بندی اعداد فارسی، تاریخ شمسی، ساعت زنده،
 * شبیه‌سازی نوسان قیمت، اسپارک‌لاین و مقیاس‌دهی تابلو به اندازه‌ی صفحه.
 *
 * در نسخه‌ی واقعی (Next.js) فقط تابع fetchPrices جایگزین API واقعی می‌شود؛
 * بقیه‌ی رفتارها (data-v / data-d / data-spark ...) همین قرارداد را نگه می‌دارند.
 */
(function () {
  'use strict';

  // ---- داده‌ی نمونه (تومان) — فقط برای نمایش طرح، قیمت واقعی نیست ----
  var DATA = {
    gold18:  { label: 'طلای ۱۸ عیار',      unit: 'هر گرم',   buy: 10780000,  sell: 10850000,  chg: 0.62 },
    gold24:  { label: 'طلای ۲۴ عیار',      unit: 'هر گرم',   buy: 14380000,  sell: 14465000,  chg: 0.58 },
    used:    { label: 'طلای دست دوم',      unit: 'هر گرم',   buy: 10450000,  sell: 10520000,  chg: -0.21 },
    melted:  { label: 'طلای آبشده',        unit: 'هر مثقال', buy: 46800000,  sell: 47000000,  chg: 0.44 },
    mesghal: { label: 'مثقال طلا',         unit: 'هر مثقال', buy: 46900000,  sell: 47020000,  chg: 0.47 },
    mazaneh: { label: 'مظنه بازار',        unit: 'هر مثقال', buy: 46950000,  sell: 46950000,  chg: 0.39 },
    emami:   { label: 'سکه امامی',         unit: 'طرح جدید', buy: 115200000, sell: 115800000, chg: 0.91 },
    bahar:   { label: 'سکه بهار آزادی',    unit: 'طرح قدیم', buy: 108000000, sell: 108900000, chg: 0.74 },
    nim:     { label: 'نیم سکه',           unit: 'بهار آزادی', buy: 60500000, sell: 61200000, chg: -0.33 },
    rob:     { label: 'ربع سکه',           unit: 'بهار آزادی', buy: 36000000, sell: 36600000, chg: 0.12 },
    usd:     { label: 'دلار آمریکا',       unit: 'USD', sym: '$',  buy: 114500, sell: 114900, chg: 0.35 },
    eur:     { label: 'یورو',              unit: 'EUR', sym: '€',  buy: 133500, sell: 134100, chg: 0.18 },
    try:     { label: 'لیر ترکیه',         unit: 'TRY', sym: '₺',  buy: 2740,   sell: 2770,   chg: -0.40 },
    aed:     { label: 'درهم امارات',       unit: 'AED', sym: 'د.إ', buy: 31150, sell: 31280,  chg: 0.29 },
    cny:     { label: 'یوان چین',          unit: 'CNY', sym: '¥',  buy: 16000,  sell: 16090,  chg: -0.08 },
    ounce:   { label: 'اونس جهانی طلا',    unit: 'دلار', buy: 3862.40, sell: 3862.40, chg: 0.27, decimals: 2 }
  };

  var params = new URLSearchParams(location.search);
  var STILL = params.has('still');          // ?still → بدون نوسان (برای اسکرین‌شات)

  var faInt = new Intl.NumberFormat('fa-IR', { maximumFractionDigits: 0 });
  var faDec = new Intl.NumberFormat('fa-IR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  var faPct = new Intl.NumberFormat('fa-IR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  var faTime = new Intl.DateTimeFormat('fa-IR', { hour: '2-digit', minute: '2-digit', hour12: false });
  var faSec = new Intl.DateTimeFormat('fa-IR', { second: '2-digit' });
  var faTimeFull = new Intl.DateTimeFormat('fa-IR', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
  var faWeekday = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { weekday: 'long' });
  var faDate = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { day: 'numeric', month: 'long', year: 'numeric' });
  var faDay = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { day: 'numeric' });
  var faMonth = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { month: 'long' });
  var faYear = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { year: 'numeric' });
  var enDate = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });

  function fmt(key, field) {
    var d = DATA[key];
    if (!d) return '';
    var v = field === 'buy' ? d.buy : field === 'mid' ? (d.buy + d.sell) / 2 : d.sell;
    return d.decimals ? faDec.format(v) : faInt.format(Math.round(v));
  }

  // ---- مقدار پایه‌ی روز (برای محاسبه‌ی درصد تغییر) ----
  Object.keys(DATA).forEach(function (k) {
    var d = DATA[k];
    d.open = d.sell / (1 + d.chg / 100);
    d.hist = seedHistory(d.open, d.sell, 48);
  });

  // تاریخچه‌ی ساختگی ولی پایدار (بدون Math.random) تا اسکرین‌شات‌ها ثابت بمانند
  function seedHistory(from, to, n) {
    var out = [];
    for (var i = 0; i < n; i++) {
      var t = i / (n - 1);
      var base = from + (to - from) * t;
      var wave = Math.sin(i * 0.9) * 0.0011 + Math.sin(i * 0.37 + 1.3) * 0.0016;
      out.push(base * (1 + wave * (1 - t * 0.6)));
    }
    out[n - 1] = to;
    return out;
  }

  function pct(key) {
    var d = DATA[key];
    return (d.sell - d.open) / d.open * 100;
  }

  // ---- رندر مقادیر ----
  function renderValues(changedKeys) {
    each('[data-v]', function (el) {
      var p = el.getAttribute('data-v').split('.');
      if (changedKeys && changedKeys.indexOf(p[0]) < 0) return;
      el.textContent = fmt(p[0], p[1] || 'sell');
    });
    each('[data-d]', function (el) {
      var key = el.getAttribute('data-d');
      if (changedKeys && changedKeys.indexOf(key) < 0) return;
      var c = pct(key);
      var dir = c > 0.004 ? 'up' : c < -0.004 ? 'down' : 'flat';
      el.setAttribute('data-dir', dir);
      var arrow = dir === 'up' ? '▲' : dir === 'down' ? '▼' : '●';
      var mode = el.getAttribute('data-d-mode');
      var num = faPct.format(Math.abs(c)) + '٪';
      if (mode === 'amount') {
        var d = DATA[key];
        num = (d.decimals ? faDec : faInt).format(Math.abs(d.sell - d.open));
      }
      el.innerHTML = '<span class="arrow" aria-hidden="true">' + arrow + '</span><span class="num">' + num + '</span>';
      el.setAttribute('aria-label', (dir === 'up' ? 'افزایش ' : dir === 'down' ? 'کاهش ' : 'بدون تغییر ') + num);
    });
    each('[data-spark]', function (el) {
      var key = el.getAttribute('data-spark');
      if (changedKeys && changedKeys.indexOf(key) < 0) return;
      drawSpark(el, DATA[key].hist, pct(key) >= 0);
    });
  }

  function drawSpark(svg, hist, up) {
    var w = +svg.getAttribute('width') || 200;
    var h = +svg.getAttribute('height') || 48;
    var pad = 3;
    var min = Math.min.apply(null, hist), max = Math.max.apply(null, hist);
    var span = max - min || 1;
    var pts = hist.map(function (v, i) {
      // RTL: زمان از چپ به راست پیش می‌رود چون نمودار قیمت جهانی‌ست
      var x = pad + i / (hist.length - 1) * (w - pad * 2);
      var y = pad + (1 - (v - min) / span) * (h - pad * 2);
      return [x, y];
    });
    var line = pts.map(function (p) { return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
    var last = pts[pts.length - 1];
    var area = 'M' + pts[0][0] + ',' + h + ' L' + line.replace(/ /g, ' L') + ' L' + last[0] + ',' + h + ' Z';
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    svg.setAttribute('data-trend', up ? 'up' : 'down');
    svg.innerHTML =
      '<path class="spark-area" d="' + area + '"></path>' +
      '<polyline class="spark-line" fill="none" points="' + line + '"></polyline>' +
      '<circle class="spark-dot" cx="' + last[0].toFixed(1) + '" cy="' + last[1].toFixed(1) + '" r="3.5"></circle>';
  }

  // ---- ساعت و تاریخ ----
  var lastUpdate = new Date();
  function renderClock() {
    var now = new Date();
    each('[data-clock]', function (el) { el.textContent = faTime.format(now); });
    each('[data-sec]', function (el) { el.textContent = faSec.format(now).padStart(2, '۰'); });
    each('[data-weekday]', function (el) { el.textContent = faWeekday.format(now); });
    each('[data-date]', function (el) { el.textContent = faDate.format(now); });
    each('[data-day]', function (el) { el.textContent = faDay.format(now); });
    each('[data-month]', function (el) { el.textContent = faMonth.format(now); });
    each('[data-year]', function (el) { el.textContent = faYear.format(now); });
    each('[data-date-en]', function (el) { el.textContent = enDate.format(now); });
    each('[data-updated]', function (el) { el.textContent = faTimeFull.format(lastUpdate); });
  }

  // ---- شبیه‌سازی نوسان؛ در نسخه‌ی واقعی با پاسخ API جایگزین می‌شود ----
  function tick() {
    var keys = Object.keys(DATA);
    var changed = [];
    var count = 2 + Math.floor(Math.random() * 3);
    for (var i = 0; i < count; i++) {
      var k = keys[Math.floor(Math.random() * keys.length)];
      if (changed.indexOf(k) >= 0) continue;
      var d = DATA[k];
      var step = (Math.random() - 0.48) * 0.0012;
      var spread = d.sell - d.buy;
      var sell = d.sell * (1 + step);
      var unitStep = d.decimals ? 0.1 : d.sell > 1e6 ? 5000 : d.sell > 1e4 ? 10 : 1;
      sell = Math.round(sell / unitStep) * unitStep;
      if (sell === d.sell) continue;
      var dir = sell > d.sell ? 'up' : 'down';
      d.sell = sell;
      d.buy = sell - spread;
      d.hist.push(sell);
      d.hist.shift();
      changed.push(k);
      flash(k, dir);
    }
    if (changed.length) {
      lastUpdate = new Date();
      renderValues(changed);
      renderClock();
    }
  }

  function flash(key, dir) {
    each('[data-row="' + key + '"]', function (el) {
      el.classList.remove('flash-up', 'flash-down');
      void el.offsetWidth;
      el.classList.add(dir === 'up' ? 'flash-up' : 'flash-down');
    });
  }

  // ---- پیام‌های چرخشی (تبلیغات فروشگاه) ----
  function initRotators() {
    each('[data-rotate]', function (box) {
      var items = box.children;
      if (items.length < 2) return;
      var i = 0;
      items[0].classList.add('is-on');
      if (STILL) return;
      var every = +box.getAttribute('data-rotate') || 7000;
      setInterval(function () {
        items[i].classList.remove('is-on');
        i = (i + 1) % items.length;
        items[i].classList.add('is-on');
      }, every);
    });
  }

  // ---- تیکر افقی: محتوا دو بار تکرار می‌شود تا حلقه بی‌درز باشد ----
  function initTickers() {
    each('[data-ticker]', function (track) {
      track.innerHTML += track.innerHTML;
      if (STILL) track.style.animationPlayState = 'paused';
    });
  }

  // ---- مقیاس تابلو: طراحی روی ۱۹۲۰×۱۰۸۰ (یا ۱۰۸۰×۱۹۲۰) و تطبیق با هر نمایشگر ----
  function fit() {
    var stage = document.querySelector('.stage');
    if (!stage) return;
    var W = stage.offsetWidth, H = stage.offsetHeight;
    var s = Math.min(window.innerWidth / W, window.innerHeight / H);
    var x = (window.innerWidth - W * s) / 2;
    var y = (window.innerHeight - H * s) / 2;
    stage.style.transform = 'translate(' + x + 'px,' + y + 'px) scale(' + s + ')';
  }

  function each(sel, fn) { Array.prototype.forEach.call(document.querySelectorAll(sel), fn); }

  function start() {
    renderValues();
    renderClock();
    initRotators();
    initTickers();
    fit();
    window.addEventListener('resize', fit);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    setInterval(renderClock, 1000);
    if (!STILL) setInterval(tick, 3200);
    document.documentElement.classList.add('is-ready');
  }

  window.GoldBoard = { data: DATA, format: fmt, pct: pct };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
