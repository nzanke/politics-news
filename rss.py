"""feeds.json の RSS を読み、新しい記事を data/rss.jsonl に足す（30分ごと、.github/workflows/pages.yml）。

1行 = {u: 元記事のリンク, t: 見出し（末尾の（媒体名）を外したもの）, d: 日付, h: 時刻, s: 媒体名, cat: RSS の分類, feed: RSS の名前, desc: RSS の説明文（書き出し）}
説明文もそのまま保存する。すでにある記事で説明文がまだないものは付け足す。記事そのものは読まない。RSS ごとに1秒あける。読めない RSS は飛ばして次へ。"""
import datetime, email.utils, html, json, os, re, time, urllib.request
from urllib.parse import urlsplit, parse_qsl, urlencode

DROP_Q = {'c', 'g', 'from', 'ref', 'rf', 'fbclid', 'gclid', 'display', 'page', 'cx_testId', 'cx_testVariant', 'cx_artPos', 'via', 'source', 'share'}
def canon(u):
    """同じ記事かどうかを見るためのリンク：http/https・www・末尾の / の違いと、追跡用の値（utm_ や ?c= など）を外す"""
    p = urlsplit((u or '').strip())
    q = [(k, v) for k, v in parse_qsl(p.query) if not (k.startswith('utm_') or k in DROP_Q)]
    return re.sub(r'^www\.', '', p.netloc.lower()) + p.path.rstrip('/') + ('?' + urlencode(sorted(q)) if q else '')

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'data', 'rss.jsonl')
UA = 'Mozilla/5.0 (compatible; politics-news; +https://nzanke.github.io/politics-news/)'
JST = datetime.timezone(datetime.timedelta(hours=9))

if __name__ == '__main__':
    rows = [json.loads(l) for l in open(OUT, encoding='utf-8')] if os.path.exists(OUT) else []
    idx = {canon(x['u']): n for n, x in enumerate(rows)}
    added = filled = 0
    for f in json.load(open(os.path.join(HERE, 'feeds.json'), encoding='utf-8'))['feeds']:
        try:
            x = urllib.request.urlopen(urllib.request.Request(f['url'], headers={'User-Agent': UA}), timeout=30).read().decode('utf-8', 'replace')
        except Exception as e:
            print('読めませんでした:', f['name'], e); time.sleep(1); continue
        n = 0
        for it in re.findall(r'<item\b.*?</item>', x, re.S):
            g = lambda k: html.unescape((re.search(r'<' + k + r'>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</' + k + '>', it, re.S) or [None, ''])[1].strip())
            u, t = g('link'), g('title')
            if not u: continue
            desc = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', g('description'))).strip()
            c = canon(u)
            if c in idx:
                if desc and not rows[idx[c]].get('desc'): rows[idx[c]]['desc'] = desc; filled += 1
                continue
            m = re.match(r'(.*?)\s*[(（]([^()（）]{1,30})[)）]\s*$', t)
            title, site = (m.group(1), m.group(2)) if m else (t, '')
            try:
                dt = email.utils.parsedate_to_datetime(g('pubDate')).astimezone(JST); d, h = dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M')
            except Exception: d = h = ''
            rec = {'u': u, 't': title, 'd': d, 'h': h, 's': site, 'cat': g('category'), 'feed': f['name'], 'desc': desc}
            idx[c] = len(rows); rows.append(rec); n += 1
        ds = sorted(re.findall(r'<pubDate>(.*?)</pubDate>', x))
        newest = max((email.utils.parsedate_to_datetime(d).astimezone(JST) for d in ds), default=None) if ds else None
        print(f"{f['name']}：RSS に {x.count('<item>') + x.count('<item ')}件（いちばん新しい記事 {newest:%m-%d %H:%M}）、{n}件 追加" if newest else f"{f['name']}：RSS に記事なし"); added += n
        time.sleep(1)
    with open(OUT, 'w', encoding='utf-8') as out:
        for x in rows: out.write(json.dumps(x, ensure_ascii=False) + '\n')
    print('説明文を付け足した記事', filled, '件')
    print('RSS 合計', added, '件 追加')
