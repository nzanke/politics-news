"""ページの読み込みの速さを測る（改善の前後で同じ手順で測るためのもの）。

  python3 tools/measure.py _site [回数=5]

- 組み立てたページ（_site）を手元で配り（python3 -m http.server と同じ）、headless の Chrome（Playwright）で開く。
- 毎回新しいブラウザー環境で開くので、キャッシュは使わない。
- 外部の字体（Google Fonts）とアクセス解析（GoatCounter）は止める（測る値をぶらさないため）。
- 「読み込み完了」＝一覧（index.html は #today、search.html は #list）に記事が出た時刻（ページを開き始めてからのミリ秒）。
- 読み込んだファイルの一覧と大きさ（圧縮前・gzip 後）も出す。10Mbps での転送時間は大きさからの計算値。
"""
import functools, gzip, http.server, os, socketserver, statistics, sys, threading
from playwright.sync_api import sync_playwright

SITE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '_site')
N = int(sys.argv[2]) if len(sys.argv) > 2 else 5
PAGES = [('index.html', '#today li'), ('search.html', '#list li')]
BLOCK = ('fonts.googleapis.com', 'fonts.gstatic.com', 'gc.zgo.at', 'goatcounter.com')

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=SITE))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{srv.server_address[1]}/'

def size(path):
    b = open(os.path.join(SITE, path), 'rb').read()
    return len(b), len(gzip.compress(b, 9))

with sync_playwright() as p:
    br = p.chromium.launch()
    for page_name, sel in PAGES:
        times, files = [], []
        for i in range(N):
            ctx = br.new_context(viewport={'width': 420, 'height': 900})
            ctx.route('**/*', lambda r: r.abort() if any(h in r.request.url for h in BLOCK) else r.continue_())
            pg = ctx.new_page()
            pg.goto(BASE + page_name)
            pg.wait_for_selector(sel, timeout=20000)
            times.append(pg.evaluate('performance.now()'))
            if i == 0:
                files = pg.evaluate("[location.pathname].concat(performance.getEntriesByType('resource').map(function (e) { return new URL(e.name).pathname; }))")
            ctx.close()
        files = [f.lstrip('/') for f in files if f.lstrip('/') and os.path.exists(os.path.join(SITE, f.lstrip('/')))]
        raw = sum(size(f)[0] for f in files); gz = sum(size(f)[1] for f in files)
        print(f'## {page_name}')
        for f in files: print(f'  {f}：{size(f)[0]:,} B（gzip {size(f)[1]:,} B）')
        print(f'  合計：{raw:,} B（gzip {gz:,} B）／10Mbps での転送の目安（計算値）：{gz * 8 / 10e6 * 1000:.1f} ms')
        print(f'  読み込み完了（ms）：{", ".join(f"{t:.0f}" for t in times)}／中央値 {statistics.median(times):.0f}')
    br.close()
srv.shutdown()
