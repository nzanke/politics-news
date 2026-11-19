"""サイトのジャンル分け（サイトを選ぶパネルの見出し）。名前の形で決まるものは規則で、それ以外は一覧で。どれにも当たらなければ「その他」。"""
import re
ORDER = ['全国紙・通信社', 'テレビ', 'スポーツ紙', '地方紙・地域', 'アニメ・エンタメ', 'ゲーム・ホビー・IT', '経済・ビジネス', '週刊誌・総合', '海外', 'その他']
LIST = {
    '全国紙・通信社': '読売新聞 日本経済新聞 産経新聞 朝日新聞 毎日新聞 東京新聞 時事通信 共同通信 47NEWS : 共同通信 OVO : 共同通信 世界日報 しんぶん赤旗',
    'テレビ': 'NHK FNN : フジテレビ 日本テレビ テレビ朝日 TBSテレビ テレ東BIZ Abema TIMES',
    'スポーツ紙': 'デイリースポーツ 日刊スポーツ スポニチ サンケイスポーツ スポーツ報知 東京スポーツ新聞 THE ANSWER フルカウント バスケットボールキング zakzak',
    'アニメ・エンタメ': 'アニメイトタイムズ アニメ！アニメ！ MANTANWEB ナタリー ORICON STYLE にじめん ザテレビジョン 映画.com シネマカフェ シネマトゥデイ クランクイン！ MOVIE WALKER PRESS MOVIE Collection モデルプレス Entame Plex Astage THE FIRST TIMES リスアニ！ SPICE Billboard JAPAN Musicman-net CDJournal.com BARKS 電波タイムズ ウォーカープラス おたくま経済新聞 Lmaga.jp',
    'ゲーム・ホビー・IT': 'ねとらぼ インサイド Social Game Info 電撃ホビーウェブ Gamer 4Gamer.net Game*Spark HOBBY Watch GIGAZINE TechnoEdge PC Watch AI Watch GAME Watch AUTOMATON GameBusiness.jp ASCII.jp 週アスPLUS 窓の杜 AKIBA PC Hotline! ZDNet Japan CNET Japan gihyo.jp TechTarget ジャパン TechFeed BCN RETAIL RBB TODAY Car Watch トラベル Watch グルメ Watch',
    '経済・ビジネス': '日本貿易振興機構 EconomicNews 東洋経済オンライン QUICK Money World PRESIDENT Online ハーバード・ビジネス・レビュー 現代ビジネス JBpress 日刊工業新聞 日経クロストレンド 日経BOOKプラス ブルームバーグ ログミーファイナンス NewsPicks 週刊エコノミスト 東京商工リサーチ ニッキンONLINE : 日本金融通信 ウォール・ストリート・ジャーナル 日本農業新聞 文化通信 教育新聞',
    '週刊誌・総合': 'ポストセブン デイリー新潮 週刊女性PRIME 女性自身 J-CAST Yahoo!オリジナル・エキスパート マイナビニュース @DIME Smart FLASH 女子SPA! 日刊SPA! 女性セブンプラス 文春オンライン dot. アサ芸プラス 週刊プレイボーイ CREA WEB GQ JAPAN アエラスタイルマガジン COURRiER Japon ハフィントンポスト BuzzFeed Japan ニューズウィーク WWD JAPAN ファッションプレス Fashionsnap.com ＆GP 東京バーゲンマニア えんウチ coki ナゾロジー リセマム 大学ジャーナル まいどなニュース',
    '海外': 'Kstyle レコードチャイナ NNA ASIA AFPBB News BBC ロイター VIETJO 香港経済新聞',
}
# 一覧の名前には空白を含むものがあるので、長い名前から順に切り出す
_MAP = {}
for g, s in LIST.items():
    names = sorted(set(re.findall(r'[^ ]+(?: : [^ ]+)*', s)), key=len, reverse=True)
    for n in names: _MAP[n] = g
for g, s in LIST.items():   # 空白を含む名前（「FNN : フジテレビ」「QUICK Money World」など）
    for n in re.findall(r'(?:[^ ]+ : [^ ]+|QUICK Money World|PRESIDENT Online|Social Game Info|MOVIE WALKER PRESS|MOVIE Collection|Billboard JAPAN|THE FIRST TIMES|HOBBY Watch|PC Watch|AI Watch|GAME Watch|AKIBA PC Hotline!|ZDNet Japan|CNET Japan|TechTarget ジャパン|BCN RETAIL|RBB TODAY|Car Watch|トラベル Watch|グルメ Watch|Abema TIMES|THE ANSWER|Smart FLASH|CREA WEB|GQ JAPAN|COURRiER Japon|BuzzFeed Japan|WWD JAPAN|NNA ASIA|AFPBB News|Entame Plex|ORICON STYLE|テレ東BIZ|Yahoo!オリジナル・エキスパート)', s):
        _MAP[n] = g
def genre(site):
    s = (site or '').strip()
    if s in _MAP: return _MAP[s]
    if re.match(r'^[^:]{1,12} : ', s) and not re.match(r'^(FNN|47NEWS|OVO|ニッキンONLINE) : ', s) and not re.search(r'テレビ|新聞|放送', s): return '海外'   # 「中国 : 人民網」「韓国 : 聯合ニュース」など
    if re.search(r'経済新聞$', s): return '地方紙・地域'   # みんなの経済新聞（地域のニュースサイト）
    if re.search(r'新聞|新報|日報|民報|タイムス$|日日|夕刊', s): return '地方紙・地域'
    if re.search(r'テレビ|放送|TV$|KTS', s): return 'テレビ'
    return 'その他'
