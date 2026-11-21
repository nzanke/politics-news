// 政治ニュース：newsall.json を読み、記事一覧（search.html）では大カテゴリ・検索・サイトでその場で絞り込む。今日の新着（index.html）ではジャンルごとに並べる
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var PAGE = 200, all = [], res = [], shown = 0, grp = '', picked = {}, ex = {}, SEL = {}, SUB = {}, G = {}, GI = {}, groups = [];
  var HUE = window.HUE || {};
  // 大カテゴリの印
  var AB = {};
  ['首相動静:動', '世論調査:調', '地方政治:地', '国会:国', '省庁:省', '首相:首', '政党:党', '官房長官:官', '外交:交', '叙勲:勲', '閣僚:閣', '海外:外', '分類なし:他'].forEach(function (x) { x = x.split(':'); AB[x[0]] = x[1]; });
  var WD = '日月火水木金土';
  function esc(s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function norm(s) { return String(s || '').normalize('NFKC').toLowerCase().replace(/[\s・!！?？:：~〜～\-－「」『』【】]/g, ''); }
  function hue(i) { return HUE[GI[i]] || 70; }
  function row(e, tm) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(e.d || ''), i0 = e.g[0];
    var dd = tm ? '<span class="tm">' + esc(e.h || '—') + '</span>' + (e.d !== tm ? '<span class="left">昨日</span>' : '') : (e.h ? '<span class="hm">' + esc(e.h) + '</span>' : '') + (m ? +m[3] + '<small>' + WD[new Date(+m[1], +m[2] - 1, +m[3]).getDay()] + '</small>' : '<span class="dq">—</span>');   // 記事一覧：日付と、左の空きに小さく薄く時刻
    var more = e.o ? '<ul class="olist" hidden>' + e.o.map(function (o) { return '<li><a href="' + esc(o[1]) + '" target="_blank" rel="noopener">' + esc(o[2]) + '</a><span class="os">' + esc(o[0]) + '</span></li>'; }).join('') + '</ul>' : '';
    return '<li class="ur sr"><span class="ud">' + dd + '</span>' +
      '<span class="ic" style="--h:' + hue(i0) + '" title="' + esc(i0) + '">' + esc(AB[i0] || '他') + '</span>' +
      '<span class="sb"><a class="un" href="' + esc(e.u) + '" target="_blank" rel="noopener">' + esc(e.t) + '</a>' +
      more + '</span><span class="st' + (e.c ? '' : ' nc') + '"><span class="sn">' + esc(e.s) + '</span>' + (e.c ? '<button type="button" class="cn" aria-expanded="false" title="伝えた記事の数（押すと見出しを全部広げる）">' + e.c + '</button>' : '') + '</span></li>';
  }
  document.addEventListener('click', function (ev) {   // 青い件数を押すと、同じ話題の見出しを広げる・たたむ
    var b = ev.target.closest && ev.target.closest('button.cn'); if (!b) return;
    var ul = b.closest('li').querySelector('.olist'); if (!ul) return;
    ul.hidden = !ul.hidden; b.setAttribute('aria-expanded', !ul.hidden);
  });
  // ---- 今日の新着（index.html）：今日の記事をジャンルごとに。今日の記事がまだなければ昨日の記事
  if ($('today')) {
    fetch(window.NEWS).then(function (r) { return r.json(); }).then(function (j) {
      (j.groups || []).forEach(function (x) { x[1].forEach(function (i) { GI[i] = x[0]; }); });   // 印の色
      var t = new Date(), y = new Date(t.getTime() - 864e5), items = j.items || [], day = ymd(t), yday = ymd(y);
      var td = items.filter(function (e) { return e.d === day || e.d === yday; });   // 今日と昨日の記事（新しい順）
      var gs = (window.GENRES || []).slice();
      td.forEach(function (e) { if (gs.indexOf(e.j) < 0) gs.push(e.j); });
      var h = '';
      gs.forEach(function (g) {
        var es = td.filter(function (e) { return e.j === g; }); if (!es.length) return;
        h += '<section class="tsec"><h2 class="ug tg2">' + esc(g) + '<span class="n">' + es.length + ' 件</span></h2><ul class="ulist">' + es.map(function (e) { return row(e, day); }).join('') + '</ul></section>';
      });
      var md = function (d) { return (d.getMonth() + 1) + '月' + d.getDate() + '日・' + WD[d.getDay()]; };
      $('tcount').innerHTML = '今日（' + md(t) + '）と昨日（' + md(y) + '）の新着 ' + td.length + ' 件　<a href="search.html">記事一覧へ</a>';
      $('today').innerHTML = h || '<p class="none">まだ記事がありません。</p>';
    });
    return;
  }
  var lastG = '';
  function ymd(t) { return t.getFullYear() + '-' + ('0' + (t.getMonth() + 1)).slice(-2) + '-' + ('0' + t.getDate()).slice(-2); }
  function mon(e) { var m = /^(\d{4})-(\d{2})/.exec(e.d || ''); return m ? m[1] + '年' + (+m[2]) + '月' : '日付なし'; }
  function render(more) {
    if (!more) { $('list').innerHTML = ''; shown = 0; lastG = ''; }
    var big = $('big').checked;
    var h = '';
    res.slice(shown, shown + PAGE).forEach(function (e) { var g = big ? ((e.c || 1) + ' 件が伝えた話題') : mon(e); if (g !== lastG) { h += '<li class="ug">' + esc(g) + '</li>'; lastG = g; } h += row(e); });
    $('list').insertAdjacentHTML('beforeend', h);
    shown = Math.min(shown + PAGE, res.length);
    $('more').hidden = shown >= res.length;
  }
  function subs() {   // 選んだまとまりの項目ボタン
    if (!grp) { $('sub').hidden = true; $('sub').innerHTML = ''; return; }
    $('sub').innerHTML = G[grp].map(function (i) {
      return '<button type="button" data-i="' + esc(i) + '" style="--h:' + hue(i) + '"' + (picked[i] ? ' class="on"' : ex[i] ? ' class="ng"' : '') + ' title="1回で絞り込み、2回で除外、3回で元に戻す"' + '>' + esc(i) + '<span class="n"></span></button>';
    }).join('');
    $('sub').hidden = G[grp].length < 2 && !SUB[grp];
  }
  function exrow() {   // 除外している項目（まとまりを切り替えても効いたまま。押すと除外をやめる）
    var xs = Object.keys(ex);
    $('exrow').hidden = !xs.length;
    $('exrow').innerHTML = xs.length ? '除外中：' + xs.map(function (i) { return '<button type="button" data-i="' + esc(i) + '" style="--h:' + hue(i) + '">' + esc(i) + ' ×</button>'; }).join('') : '';
  }
  function inGroup(e, g) { return e.g.some(function (i) { return GI[i] === g; }); }
  function search() {
    var terms = $('q').value.split(/\s+/).map(norm).filter(Boolean), ss = Object.keys(SEL);
    var base0 = all.filter(function (e) { return (!ss.length || SEL[e.s] || (e.o || []).some(function (o) { return SEL[o[0]]; })) && terms.every(function (t) { return e._t.indexOf(t) >= 0; }); });
    var xs = Object.keys(ex);
    var base = xs.length ? base0.filter(function (e) { return !xs.some(function (i) { return e.g.indexOf(i) >= 0; }); }) : base0;
    exrow();
    [].forEach.call(document.querySelectorAll('#seg button'), function (b) {
      var g = b.getAttribute('data-g'); b.querySelector('.n').textContent = ' ' + (g ? base.filter(function (e) { return inGroup(e, g); }).length : base.length).toLocaleString();
    });
    var inG = grp ? base.filter(function (e) { return inGroup(e, grp); }) : base;
    [].forEach.call(document.querySelectorAll('#sub button'), function (b) {
      var i = b.getAttribute('data-i'); b.querySelector('.n').textContent = ' ' + (ex[i] ? base0.filter(function (e) { return !grp || inGroup(e, grp); }) : inG).filter(function (e) { return e.g.indexOf(i) >= 0; }).length.toLocaleString();
    });
    var ps = Object.keys(picked);
    res = (grp && SUB[grp] && !ps.length) ? [] : ps.length ? inG.filter(function (e) { return ps.some(function (i) { return e.g.indexOf(i) >= 0; }); }) : inG;
    if ($('old').checked) res = res.slice().reverse();
    if ($('big').checked) res = res.slice().sort(function (a, b) { return (b.c || 1) - (a.c || 1); });
    $('count').textContent = (grp && SUB[grp] && !ps.length) ? '小カテゴリを選ぶと記事が出ます' : res.length.toLocaleString() + ' 件 / 全 ' + all.length.toLocaleString() + ' 件';
    render(false);
    var qs = [];
    if ($('q').value) qs.push('q=' + encodeURIComponent($('q').value));
    if (grp) qs.push('g=' + encodeURIComponent(grp));
    if (ps.length) qs.push('i=' + encodeURIComponent(ps.join(',')));
    if (xs.length) qs.push('x=' + encodeURIComponent(xs.join(',')));
    if (ss.length) qs.push('s=' + encodeURIComponent(ss.join('|')));
    siteui();
    try { history.replaceState(null, '', qs.length ? '?' + qs.join('&') : location.pathname); } catch (x) {}
  }
  function setGroup(g) {
    grp = g; picked = {};
    [].forEach.call(document.querySelectorAll('#seg button'), function (x) { x.classList.toggle('on', x.getAttribute('data-g') === g); });
    subs();
  }
  fetch(window.NEWS).then(function (r) { return r.json(); }).then(function (j) {
    groups = j.groups || [];
    groups.forEach(function (x) { G[x[0]] = x[1]; if (x[2]) SUB[x[0]] = 1; x[1].forEach(function (i) { GI[i] = x[0]; }); });
    all = j.items || [];
    all.forEach(function (e) { e._t = norm([e.t, e.n, e.s].concat((e.o || []).map(function (o) { return o[0] + ' ' + o[2]; })).join(' ')); });
    var p = new URLSearchParams(location.search);
    if (p.get('q')) $('q').value = p.get('q');
    (p.get('s') || '').split('|').forEach(function (s) { if (s) SEL[s] = 1; });
    (p.get('x') || '').split(',').forEach(function (i) { if (GI[i]) ex[i] = 1; });
    if (p.get('g') && G[p.get('g')]) { setGroup(p.get('g')); (p.get('i') || '').split(',').forEach(function (i) { if (GI[i] === grp) picked[i] = 1; }); subs(); }
    search();
  });
  var timer;
  $('q').addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(search, 150); });
  ['old', 'big'].forEach(function (id) { $(id).addEventListener('change', search); });
  $('seg').addEventListener('click', function (ev) {
    var b = ev.target.closest('button'); if (!b) return;
    setGroup(b.getAttribute('data-g')); search();
  });
  $('sub').addEventListener('click', function (ev) {
    var b = ev.target.closest('button'); if (!b) return;
    var i = b.getAttribute('data-i');
    if (picked[i]) { delete picked[i]; ex[i] = 1; } else if (ex[i]) delete ex[i]; else picked[i] = 1;   // 1回で絞り込み、2回で除外、3回で元に戻す
    b.classList.toggle('on', !!picked[i]); b.classList.toggle('ng', !!ex[i]); search();
  });
  $('list').addEventListener('click', function (ev) {   // 記事の下の項目・作品名を押すと、その項目だけ／その作品名で検索
    var t = ev.target.closest('.tg'); if (!t) return;
    if (t.getAttribute('data-n')) { $('q').value = t.getAttribute('data-n'); search(); window.scrollTo(0, 0); return; }
    var i = t.getAttribute('data-i'); if (!i) return;
    setGroup(GI[i]); picked = {}; picked[i] = 1; delete ex[i]; subs(); search(); window.scrollTo(0, 0);
  });
  $('exrow').addEventListener('click', function (ev) {
    var b = ev.target.closest('button'); if (!b) return;
    delete ex[b.getAttribute('data-i')]; subs(); search();
  });
  // ---- サイトを選ぶパネル（ジャンルごと。複数選べる）
  function siteui() {
    var ss = Object.keys(SEL);
    $('sitelbl').textContent = ss.length ? (ss.length === 1 ? ss[0] : ss.length + 'サイト') : 'すべて';
    $('sitebtn').classList.toggle('on', ss.length > 0);
    $('siterow').hidden = !ss.length;
    $('siterow').innerHTML = ss.map(function (s) { return '<button type="button" data-s="' + esc(s) + '">' + esc(s) + ' ×</button>'; }).join('') + (ss.length ? '<button type="button" class="clr" data-clr="1">すべて外す</button>' : '');
    [].forEach.call(document.querySelectorAll('#sitepanel [data-s]'), function (b) { b.classList.toggle('on', !!SEL[b.getAttribute('data-s')]); });
    [].forEach.call(document.querySelectorAll('#sitepanel [data-g]'), function (b) {
      var g = (window.SITES || []).filter(function (x) { return x[0] === b.getAttribute('data-g'); })[0];
      b.classList.toggle('on', !!g && g[1].every(function (x) { return SEL[x[0]]; }));
    });
  }
  function sitepanel() {
    $('sitepanel').innerHTML = (window.SITES || []).map(function (g) {
      return '<section><h3><span>' + esc(g[0]) + '</span><button type="button" class="all" data-g="' + esc(g[0]) + '">まとめて選ぶ</button></h3><div class="chips">' +
        g[1].map(function (x) { return '<button type="button" data-s="' + esc(x[0]) + '">' + esc(x[0]) + '<span class="n">' + x[1] + '</span></button>'; }).join('') + '</div></section>';
    }).join('') + '<div class="foot"><button type="button" class="clr" data-clr="1">すべて外す</button><button type="button" class="done" data-done="1">閉じる</button></div>';
  }
  function openpanel(o) { $('sitepanel').hidden = !o; $('sitebtn').setAttribute('aria-expanded', o ? 'true' : 'false'); }
  $('sitebtn').addEventListener('click', function () { if (!$('sitepanel').innerHTML) sitepanel(); siteui(); openpanel($('sitepanel').hidden); });
  function siteclick(ev) {
    var b = ev.target.closest('button'); if (!b) return;
    if (b.getAttribute('data-done')) { openpanel(false); return; }
    if (b.getAttribute('data-clr')) SEL = {};
    else if (b.getAttribute('data-g')) {
      var g = (window.SITES || []).filter(function (x) { return x[0] === b.getAttribute('data-g'); })[0], on = g[1].every(function (x) { return SEL[x[0]]; });
      g[1].forEach(function (x) { if (on) delete SEL[x[0]]; else SEL[x[0]] = 1; });
    } else if (b.getAttribute('data-s')) { var s = b.getAttribute('data-s'); if (SEL[s]) delete SEL[s]; else SEL[s] = 1; }
    search();
  }
  $('sitepanel').addEventListener('click', siteclick);
  $('siterow').addEventListener('click', siteclick);
  $('more').addEventListener('click', function () { render(true); });
})();
