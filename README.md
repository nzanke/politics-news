# 政治ニュース

https://nzanke.github.io/politics-news/

政治のニュースを30分ごとに集め、今日の新着をジャンルごとに並べ（index.html）、記事一覧を大カテゴリ・見出し・サイトで絞り込めるようにしたサイト（search.html）。仕組みと見た目は [アニメニュース検索](https://github.com/nzanke/anime-news-all) と同じ。

- `feeds.json`：取り込む RSS（ceek.jp の「カテゴリ × キーワード」の検索 RSS）。
- `rss.py`：RSS を読み、リンクを正規化して重なりを除き、`data/rss.jsonl` に足す（見出し・日付・時刻・サイト・RSS の説明文）。
- `rules.py`：絞り込みの規則（載せる・落とす）、大カテゴリ、今日の新着のジャンル。
- `tag.py`：重複を除き、同じ話題をまとめて `data/newsall.json` を書き出す。
- `build.py`・`static/`：`_site/` にページを組み立てる。
- `.github/workflows/pages.yml`：30分ごとに rss.py → tag.py → build.py を動かし、データをコミットして GitHub Pages に出す。
