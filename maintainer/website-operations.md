# 公開仕様・運用

## 研究・結果ページの追加（2026-11-02）

既存サイトの `site/` 内に `/research/`、`/research/methods/`、`/research/reports/`、`/research/reports/20261101-static/`、`/map/` を追加。ポスターのQRは `https://aquabeacon.github.io/map/` を固定リンクにする。

静止評価は2026-11-01 10:15〜10:16 JST、平均深度16.44 m、採用32点。姿勢補正後の平均まわり3D RMSEは0.1397 m、親機姿勢固定は1.4545 m（90.4%減）。位置真値に対する誤差ではない。深度は水圧由来の未校正相対深度。公開用に選定した数値・既存派生図・ハッシュのみを配信し、raw、元動画、絶対GNSS位置、ローカル絶対パスは掲載しない。

マッピングは解析中。未確認の地図や架空の結果を掲載せず、`pending` を表示する。後日、検証済みの点群と尺度・座標系・評価条件を追加すると、同じURLで回転・拡大して閲覧できる。自作ローカルJavaScriptだけを使用し、外部JS・CDN・ビルド依存は追加しない。本文・表・リンクはJavaScriptなしで読める。

2026-11-02にGitHub Actions成功と追加5ページの本番HTTP 200を確認した。本番PNG/SVGのSHA-256も公開用来歴と一致。公開元はサイトリポジトリの `86aa128ad12c223699721caa722e759a12b4cf40`、詳細は [PUBLICATION.md](https://github.com/AquaBeacon/aquabeacon.github.io/blob/main/PUBLICATION.md) に記録する。ローカル作成と公開済みを混同しない。地図更新手順は同じリポジトリの `MAP_PUBLISHING.md`、QR原稿と素材は `poster/2026-11/`。

> この文書の2026-09-27の記述は紹介サイト初回公開時の運用記録です。2026-10-15のリポジトリ移行と現在の構成は [migration.md](migration.md) を参照してください。`organization-live/` と作業用 `organization/` は履歴付きの `organization/` に統合しました。

## 現在の状態（2026-09-27）

紹介サイトを https://aquabeacon.github.io/ に公開済み。Organizationの説明・Website・プロフィールと共通テンプレートを反映済み。375px/1280pxの表示・横溢れ、画像、構造化データ、サイトマップを確認した。OSS本体の詳細は引き続き公開準備中。Google Search Consoleへの登録は未実施。

## 目的と受け入れ条件

- 日英で、水中位置推定・マッピング、音による距離、光による方向という概要が読める。
- 詳細は `COMING SOON ...`。実績・精度・公開時期の未確認情報を断定しない。
- JavaScriptなしで本文とGitHubへのリンクが使える。375px/1280pxで横溢れがない。
- title、description、canonical、OGP、Organization/WebSiteのJSON-LDが実在する公開URLと一致する。
- robots.txtはクロールを許可し、sitemap.xmlはトップページを含む。
- Actionsは `site/` だけを配信する。非公開の開発資料を公開用リポジトリに含めない。

サイトの検証方法は `aquabeacon.github.io/AGENTS.md` を参照。2026-09-27の初回公開では実機の詳細資料やファームウェアの移行は範囲外でした。

## GitHubへの初回反映

1. `gh auth login -h github.com` で認証し、Organizationへのリポジトリ作成権限を確認する。
2. `aquabeacon.github.io/` のみを独立したGitリポジトリにする。親ワークスペースをpushしない。
3. `AquaBeacon/aquabeacon.github.io` をpublicで作成。mainに初期コミットをpushする。
4. Settings → Pages → SourceをGitHub Actionsにし、Deploy GitHub Pagesを実行する。
5. OrganizationのWebsiteとリポジトリのAbout URLを `https://aquabeacon.github.io/` にする。descriptionに水中位置推定・マッピングの説明を設定する。
6. リポジトリのTopicsに `aquabeacon`, `underwater-positioning`, `acoustic-ranging`, `optical-tracking`, `mapping` を設定する。
7. 既存 `AquaBeacon/.github` をcloneし、`organization/` の内容を差分として反映する。既存のファイルと履歴を保持する。公開後にプロフィールの「公開準備中」を外す。
8. 本番トップ、CSS、画像、robots、sitemapが200で返り、存在しないURLが404になることを確認する。

## 検索エンジンへの登録

技術的なSEO設定は同梱済み。公開だけで即時の検索掲載や順位は保証されない。

1. Google Search ConsoleでURLプレフィックス `https://aquabeacon.github.io/` を追加する。
2. 所有権確認用HTMLを取得して `site/` に置くか、Google指定のmetaタグをindex.htmlに追加して再デプロイする。値は所有者のGoogleアカウントで取得する。
3. 所有権確認後、`https://aquabeacon.github.io/sitemap.xml` を送信する。
4. URL検査でトップページのインデックス登録をリクエストし、その後のクロール状態を確認する。
5. Organizationプロフィールと各公開リポジトリからサイトへリンクする。詳細公開後は実際の解説ページを追加し、サイトマップも更新する。

参考：[GitHub Pagesの作成](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)、[Googleのサイトマップ説明](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)、[再クロールのリクエスト](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)。

## 今後のOSSリポジトリ構成

用途ごとに分ける案。以下は未作成で、実装を公開するときに必要なものから作成する。

| 候補 | 内容 |
| --- | --- |
| `firmware` | ファームウェア、ビルド手順、対応機器 |
| `hardware` | 回路図、PCB、部品表、製造資料 |
| `mechanical` | CAD、筐体、印刷・組立手順 |
| `analysis` | 位置推定・解析ツールと再現可能なサンプル |
| `docs` | 全体構成、導入、校正、実験方法 |

各リポジトリの入口はREADMEとし、概要、現在の開発状態、前提条件、最短の実行例、構成、検証方法、LICENSE、関連資料のリンクを置く。2026-10-15の実際の分割はmigration.mdを参照してください。

## 未決定・公開前の判断

- ライセンス：2026-10-15にApache License 2.0を指定済み。自作部分へ適用し、第三者部分の条件は保持する。
- 初回リリースの範囲と時期：未定。
- Search Consoleの所有権確認：所有者のGoogleアカウントで設定が必要。

## 日英切り替え（2026-09-27）

サイトは `/` が日本語、`/en/` が英語。両ページのヘッダーから相互移動でき、canonicalとhreflangを言語ごとに設定する。READMEはREADME.mdとREADME.en.mdの相互リンクで切り替える。Organizationプロフィールの中央寄せヘッダー・バッジ・概要・リポジトリ・参加・連絡先・ライセンスの構成を保持する。両言語の375px/1280px表示、言語リンク、公開URLのHTTP応答を確認する。
