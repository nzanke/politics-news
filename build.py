"""政治ニュース（https://nzanke.github.io/politics-news/）を _site/ に組み立てる。
  index.html  … 今日の新着（ジャンルごと）
  search.html … 記事一覧（大カテゴリ・検索・サイトで絞り込み）
データは data/newsall.json（tag.py が作る）。記事の本文は載せず、日付・見出し・リンク・サイトだけ。"""
import hashlib, html, json, os, shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *p: os.path.join(HERE, *p)
OUT = D('_site')
SITE = '政治ニュース'
esc = lambda s: html.escape(str(s or ''))
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
for f in ('style.css', 'news.js'): shutil.copy(D('static', f), OUT)
open(os.path.join(OUT, '.nojekyll'), 'w').close()
p = D('data', 'newsall.json')
NEWS = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {'groups': [], 'genres': [], 'items': []}
nj = json.dumps(NEWS, ensure_ascii=False, separators=(',', ':'))
open(os.path.join(OUT, 'newsall.json'), 'w', encoding='utf-8').write(nj)
V = lambda b: hashlib.sha1(b).hexdigest()[:8]
CSS_V, NJS_V, NEWS_V = V(open(D('static', 'style.css'), 'rb').read()), V(open(D('static', 'news.js'), 'rb').read()), V(nj.encode())

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=BIZ+UDPGothic:wght@400;700&display=swap">'
         # 半角の数字・英字・記号だけ BIZ UDゴシック（text= でその文字だけの字体にし、日本語は BIZ UDPゴシック に落ちる）
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=BIZ+UDGothic:wght@400;700&display=swap&text=%21%22%23%24%25%26%27%28%29%2A%2B%2C-.%2F0123456789%3A%3B%3C%3D%3E%3F%40ABCDEFGHIJKLMNOPQRSTUVWXYZ%5B%5C%5D%5E_%60abcdefghijklmnopqrstuvwxyz%7B%7C%7D~">')
HUE = {'政治': 300, '国際': 180, '経済': 150, '社会': 200, '地方・地域': 120, '中国・韓国': 10, '訃報・人事': 270, 'IT': 230, 'サイエンス': 250, 'エンタメ': 330, 'スポーツ': 40, 'その他': 70}
GROUPS = NEWS['groups']

from sitegenre import genre as sgenre, ORDER as GORDER
_sc = Counter(s for e in NEWS['items'] for s in [e['s']] + [o[0] for o in e.get('o', [])])
nsites = [x for x, _ in _sc.most_common()]
SITES = [x for x in [[g, [[s, _sc[s]] for s in nsites if sgenre(s) == g]] for g in GORDER] if x[1]]

ABOUT = '''<details class="about"><summary><span class="qi">?</span>このサイトについて</summary><div class="aboutbox"><p class="abh">このサイトについて</p>
<p>政治に関するニュースを30分ごとに集め、分野ごとに絞り込めるようにした一覧です。上の色のボタンで分野を選ぶと、その分野の記事が出ます（1回で絞り込み、2回で除外、3回で解除）。分野はニュースサイトの RSS の分類です。</p>
<p><b>同じ話題</b>：違うサイトが同じ話題を伝えた記事は1行にまとめ、伝えた記事の数を青い数字で出しています。数字を押すと、ほかのサイトの見出しが広がります（見出しの似ている度合いで機械的にまとめているため、誤りが混じることがあります）。「伝えた記事の多い順」で、多くのサイトが伝えた話題から並べます。</p>
<p><b>検索</b>：スペースで区切ると、すべての語を含むものだけを出します。</p>
<p><b>載せているもの</b>：ニュースサイトの RSS で見つけた記事の日付・見出し・リンク。記事の本文は載せていません。</p>
</div></details>'''

def nav(on):
    return '<nav class="nav">' + ''.join(f'<a href="{h}"{" class=on" if h == on else ""}>{t}</a>' for h, t in [('index.html', '今日の新着'), ('search.html', '記事一覧')]) + '</nav>'

def page(fn, title, desc, body, extra=''):
    doc = f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
{FONTS}<link rel="stylesheet" href="style.css?v={CSS_V}"></head>
<body><div class="wrap">
<h1 class="sitename"><a href="index.html">{esc(SITE)}</a></h1>
{nav(fn)}
<main>
{body}
</main>
<footer class="site"><p>新聞各紙・ニュースサイトの政治に関する記事の見出しとリンクを30分ごとに集めて並べています（記事の本文は載せていません）。</p></footer>
</div><script>window.NEWS="newsall.json?v={NEWS_V}";window.HUE={json.dumps(HUE, ensure_ascii=False)};{extra}</script><script src="news.js?v={NJS_V}"></script><script data-goatcounter="https://nzanke.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script></body></html>
'''
    open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(doc)

# ---- 記事一覧（アニメニュース検索と同じ）
btns = ''.join(f'<button type="button" data-g="{esc(g)}" style="--h:{h}"{" class=on" if not g else ""}>{esc(t)}<span class="n"></span></button>'
               for g, t, h in [('', 'すべて', 250)] + [(x[0], x[0], HUE.get(x[0], 70)) for x in GROUPS])
body = f'''<div class="seg" id="seg">{btns}</div>
<div id="sub" hidden></div>
<div id="exrow" hidden></div>
<div class="sbar"><input type="search" id="q" placeholder="見出しを検索">
<button type="button" id="sitebtn" class="sitebtn" aria-expanded="false"><span>サイト</span><b id="sitelbl">すべて</b><i>▾</i></button></div>
<div id="sitepanel" class="sitepanel" hidden></div>
<div id="siterow" class="siterow" hidden></div>
<div class="opts"><label><input type="checkbox" id="old"> 古い順</label><label><input type="checkbox" id="big"> 伝えた記事の多い順</label></div>
<div class="cbar"><p class="count" id="count"></p>{ABOUT}</div>
<ul class="ulist" id="list"></ul>
<button class="more" id="more" hidden>さらに表示</button>'''
page('search.html', f'記事一覧 | {SITE}', '政治のニュースを30分ごとに集め、分野・サイト・見出しで絞り込める一覧', body, 'window.SITES=' + json.dumps(SITES, ensure_ascii=False))

# ---- 今日の新着（ジャンルごと。どの日を「今日」にするかは見る人の時計で決める）
body = '''<div class="cbar"><p class="count" id="tcount"></p></div>
<div id="today"></div>'''
page('index.html', SITE, '政治のニュースを30分ごとに集め、今日の新着をジャンルごとに並べたページ', body, 'window.GENRES=' + json.dumps(NEWS.get('genres', []), ensure_ascii=False))
print('組み立て', len(NEWS['items']), '件')
