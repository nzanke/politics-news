"""政治ニュースの一覧（data/newsall.json）を作る：記事を絞り込み、重複を除き、同じ話題をまとめる。

  python3 tag.py

入力は data/rss.jsonl（rss.py が30分ごとに足す）。絞り込みの規則は rules.py。
- 重複を除く：同じリンク（正規化したもの）は1本。同じサイトで見出しがまったく同じ記事も、前後3日以内なら1本にする。
- 同じ話題をまとめる：違うサイトの記事で、見出しの2文字ずつの組の重なりが 0.25 以上か、「」『』の中身（4文字以上）が同じで 0.12 以上重なれば1行にまとめる。前後4日以内。第2弾と第3弾、前編と後編などは分ける。
大カテゴリ（首相動静・世論調査・分類なし）は見出しの語で決める（rules.py）。
書き出すのは日付・時刻・見出し・リンク・サイト・大カテゴリ・ジャンル（説明文は data/rss.jsonl にだけ残す）。
"""
import datetime, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rules import nf, keep, cats, genre, CAT_ORDER, GENRE_ORDER
from rss import canon

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'data', 'newsall.json')
START = '2026-11-01'   # これより古い記事は載せない

def day(d):
    try: return datetime.date.fromisoformat(d).toordinal()
    except Exception: return 0

items, seen, SEEN_T = [], set(), {}
p = os.path.join(HERE, 'data', 'rss.jsonl')
rows = [json.loads(l) for l in open(p, encoding='utf-8')] if os.path.exists(p) else []
for r in sorted(rows, key=lambda r: (r.get('d', ''), r.get('h', ''))):
    cu = canon(r['u'])
    if cu in seen: continue
    seen.add(cu)
    t = nf(r.get('t'))
    if not t or (r.get('d') or '9') < START: continue
    tk = (re.sub(r'\s', '', nf(r.get('s'))), re.sub(r'\s', '', t))   # 同じサイトで見出しが同じ記事は、前後3日以内なら同じ記事
    dd = SEEN_T.get(tk)
    if dd is not None and r.get('d') and abs(day(r['d']) - dd) <= 3: continue
    if r.get('d'): SEEN_T[tk] = day(r['d'])
    if not keep(t, r.get('desc', ''), r.get('s', '')): continue
    items.append({'d': r.get('d') or '', 'h': r.get('h') or '', 't': r['t'], 'u': r['u'], 's': r.get('s') or '', 'g': cats(t), 'j': genre(t)})

# ---- 同じ話題の記事を1行にまとめる
def bigr(t):
    s = re.sub(r'[\s・!！?？:：~〜～\-－「」『』【】()（）、。,.＆&/／“”"]', '', nf(t).lower())
    return {s[i:i + 2] for i in range(len(s) - 1)}
SAME = 0.25
SAME_BR = 0.12
def brs(t): return set(re.findall(r'[「『]([^」』]{4,60})[」』]', nf(t)))
def mark(t): return tuple(re.findall(r'第\s*\d+\s*[弾回話期章部次]|前編|後編|中編|\d+日目', nf(t)))
clusters = []   # [代表, [記事...], 組の集合, 「」の中身]
for e in sorted(items, key=lambda e: (e['d'], e['h'], e['u'])):
    b, dd, br = bigr(e['t']), day(e['d']), brs(e['t'])
    best, bs = None, 0
    for c in clusters[-600:]:
        if abs(day(c[0]['d']) - dd) > 4: continue
        if e['s'] in {x['s'] for x in c[1]}: continue   # まとめるのは違うサイトの記事だけ
        if mark(e['t']) != mark(c[0]['t']) and mark(e['t']) and mark(c[0]['t']): continue
        sim = 2 * len(b & c[2]) / max(1, len(b) + len(c[2]))
        if br & c[3] and sim >= SAME_BR: sim = max(sim, SAME)
        if sim > bs: best, bs = c, sim
    if best and bs >= SAME: best[1].append(e); best[3] |= br
    else: clusters.append([e, [e], b, br])
out = []
for c in clusters:
    es = c[1]
    m = max(es, key=lambda x: len(x['t']))   # 代表：見出しのいちばん長いもの
    first = min(es, key=lambda x: (x['d'] or '9', x['h'] or '99'))
    r = dict(m); r['d'], r['h'] = first['d'], first['h']   # 日付・時刻はいちばん早く伝えた記事
    g = {x for e in es for x in e['g']}
    if len(g) > 1: g.discard('分類なし')   # まとめた記事のどれかが分類に入れば「分類なし」は外す
    r['g'] = sorted(g, key=lambda x: CAT_ORDER.index(x) if x in CAT_ORDER else 99); r['j'] = r['g'][0]
    if len(es) > 1: r['o'] = [[x['s'], x['u'], x['t']] for x in es if x is not m]; r['c'] = len(es)
    out.append(r)
items = sorted(out, key=lambda e: (e['d'], e['h'], e['u']), reverse=True)
groups = [[c, [c]] for c in CAT_ORDER if any(c in e['g'] for e in items)]
json.dump({'groups': groups, 'genres': [g for g in GENRE_ORDER if any(e['j'] == g for e in items)], 'items': items},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
from collections import Counter
cn = Counter(x for e in items for x in e['g'])
print('書き出し', len(items), '件 →', OUT)
for g, _ in groups: print(' ', g, cn[g])
