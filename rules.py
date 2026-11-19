"""政治ニュースの絞り込みの規則。tag.py が使う。規則を直すときはこのファイルだけ直せばよい。

いまの方針（依頼者の判断、2026-11-20）：まず全部載せ、載った記事を見て落とす規則（DROP）を足していく。【速報】の記事は落とす。
"""
import re, unicodedata

def nf(s): return unicodedata.normalize('NFKC', s or '')

# ---- 大カテゴリ：見出しの語で決める（依頼者の判断、2026-11-20。RSS は全部政治なので「政治」は使わない）
# 1本の記事が複数に入ってよい。どれにも当たらなければ「分類なし」
CATS = [
    ('首相動静', re.compile(r'首相動静')),
    ('世論調査', re.compile(r'世論調査')),
    ('地方政治', re.compile(r'知事選')),
    ('国会', re.compile(r'憲法審|参院委|衆院委')),
    ('首相', re.compile(r'^\s*高市首相、')),   # 見出しが「高市首相、」で始まる記事
]
# 説明文（RSS の抜粋）で決める大カテゴリ
PARTY = r'(?:自由民主党|自民党|自民|立憲民主党|立民|立憲|公明党|公明|日本維新の会|維新の会|維新|国民民主党|国民民主|日本共産党|共産党|れいわ新選組|れいわ|社会民主党|社民党|参政党|日本保守党|保守党|チームみらい|減税日本|有志の会)'
CATS_DESC = [
    ('政党', re.compile(r'(?:^|[。」\s])' + PARTY + r'は[^。]*?した。'   # 「（政党名）は〜した。」という文がある（依頼者の判断、2026-11-20）
                       r'|' + PARTY + r'の[^。、「」\s]{0,20}?会は\d{1,2}日、'   # 「（政党名）の〜会は（数字）日、」（同）
                       r'|' + PARTY + r'の[^。「」]{0,20}?(?:政調会長|総務会長|副代表|副総裁|幹事長)は[^。]*?た。')),   # 「（政党名）の〜幹事長などは〜た。」（同）
    ('官房長官', re.compile(r'官房長官は[^。]*?会見で[^。]*?た。')),   # 「〜官房長官は〜会見で〜た。」という文がある（依頼者の判断、2026-11-20）
]
NONE = '分類なし'
CAT_ORDER = [c for c, _ in CATS] + [c for c, _ in CATS_DESC] + [NONE]
def cats(t, desc=''):
    t, desc = nf(t), nf(desc)
    return [c for c, rx in CATS if rx.search(t)] + [c for c, rx in CATS_DESC if rx.search(desc)] or [NONE]

# ---- 落とす規則。見出し（t）・説明文（desc）・サイト名（site）で決める。当たれば載せない
DROP_TITLE = re.compile(r'【速報】')   # 【速報】の記事は載せない（依頼者の判断、2026-11-20）
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

# ---- 今日の新着ページのジャンル。いまは大カテゴリと同じ（記事の最初の大カテゴリ）
GENRE_ORDER = CAT_ORDER
def genre(t, desc=''):
    return cats(t, desc)[0]
