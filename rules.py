"""政治ニュースの絞り込みの規則。tag.py が使う。規則を直すときはこのファイルだけ直せばよい。

いまの方針（依頼者の判断、2026-11-20）：まず全部載せる。載った記事を見てから、落とす規則（DROP）を足していく。
"""
import re, unicodedata

def nf(s): return unicodedata.normalize('NFKC', s or '')

# ---- 大カテゴリ：RSS のカテゴリ（feeds.json の name の「×」より前）をそのまま使う
CAT_ORDER = ['政治', '国際', '経済', '社会', '地方・地域', '中国・韓国', '訃報・人事', 'IT', 'サイエンス', 'エンタメ', 'スポーツ', 'その他']
def cat(feed_name):
    c = (feed_name or '').split('×')[0].strip()
    return c if c in CAT_ORDER else 'その他'

# ---- 落とす規則。見出し（t）・説明文（desc）・サイト名（site）で決める。当たれば載せない
DROP_TITLE = None   # 例：re.compile(r'株価|為替')
DROP_DESC = None
DROP_SITES = set()   # 例：{'〇〇新聞'}
# 見出しにあれば、DROP に当たっても残す語
KEEP_TITLE = None

def keep(t, desc='', site=''):
    """記事を載せるなら True"""
    t, desc = nf(t), nf(desc)
    if KEEP_TITLE and KEEP_TITLE.search(t): return True
    if site in DROP_SITES: return False
    if DROP_TITLE and DROP_TITLE.search(t): return False
    if DROP_DESC and DROP_DESC.search(desc): return False
    return True

# ---- 今日の新着ページのジャンル。ジャンルは後で決める（依頼者、2026-11-20）。決まるまでは大カテゴリと同じ
GENRE_RX = []   # 例：[('選挙', re.compile(r'選挙|投開票|公認|出馬')), ('外交・安全保障', re.compile(r'外相|首脳会談|防衛'))]
GENRE_ORDER = [g for g, _ in GENRE_RX] + CAT_ORDER   # 今日の新着ページでの並び
def genre(t, c):
    for g, rx in GENRE_RX:
        if rx.search(nf(t)): return g
    return c
