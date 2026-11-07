# AquaBeacon ドキュメント索引

## 知識をためる・つなぐ

[Obsidianナレッジベース](https://github.com/AquaBeacon/obsidian/blob/main/knowledge/README.md)を追加しました。[ホーム](https://github.com/AquaBeacon/obsidian/blob/main/knowledge/ホーム.md)から分野別の索引と出典付き知識へ進めます。自由メモ・調査・実験・判断・日誌を残す型、Basesの一覧、Canvasの関係図を用意しています。個人メモの既定保存先はGit除外の `../obsidian/knowledge/private/` です。

保管庫として開くのは親の `AquaBeacon-OSS` 全体です。初期化・保存先・維持方法は[Obsidian構成](maintainer/obsidian.md)を参照してください。

## 開発内容と動画企画

[開発整理・60秒動画企画の入口](video-plan/README.md)

- [開発概要・開発目標・最終構想](video-plan/01_開発概要・目標・最終構想.md)
- [一般向け60秒動画構成案・ナレーション](video-plan/02_一般向け60秒動画構成案.md)
- [動画デザイン案10選](video-plan/03_動画デザイン案10選.md)
- [制作ツールの選定と選択後の進め方](video-plan/04_制作ツールと選択後の進め方.md)

今回の企画は2026年9月27日に整理。手元の企画資料 `AquaBeacon.pptx` を基準に作成した公開用Markdown文書を上記にまとめています。元のプレゼンテーションはこのリポジトリの配布対象に含みません。[制作データと素材の案内](https://github.com/AquaBeacon/assets/blob/main/aquabeacon-film60/README.md)も参照してください。

## 研究レポート

- [AquaBeaconの開発と実験評価 論文調レポート](research/20261106/README.md)：2026年11月6日整理。プール・南予実海域の位置推定、欠測、マッピングを評価条件と出典付きでまとめたWord版とMarkdown原稿。
- [第15回気象観測機器コンテスト 二次審査報告書](contest/2026-wni/README.md)：公式要項に沿うA4・5ページ以内の実証実験報告書。提出用PDF・編集用Word・出典対応。

## 論文執筆講座

JSST2026 ワークシート 藻場マッピング記入済み版は手元専用です。第三者教材の原本と記入済みの派生文書は、公開リポジトリの配布対象に含めません。

プロジェクト説明資料 `AquaBeacon.pptx` の全44枚の本文・発表者ノートと主要結果図を基に、藻場の地図作成を支える光・音による水中位置推定について、全項目を記入しています。JSST2026の講義に沿って中心文、IMRAD、英語4文、模擬査読、査読回答、次の検証計画を構成しました。シミュレーション、プール音響実験、統合検証の計画を区別し、該当スライド番号を文書内に付けています。元のワークシート、講義スライド、模擬査読用論文は `JSST_scientific_writing/` に保持しています。

## 元資料・設計資料

| 資料 | 内容 |
| --- | --- |
| [確定仕様メモ](AquaBeacon_確定仕様メモ.md) | 構成と仕様。文中に過去時点の前提を含む |
| [詳細設計書](AquaBeacon_詳細設計書.md) | 技術設計、計算、機体構造の更新注記 |
| [実験検証仕様書](AquaBeacon_実験検証仕様書.md) | 要素試験と統合試験の計画・評価方法 |
| [基板・センサ・電源アーキテクチャ決定書](AquaBeacon_基板センサ電源アーキテクチャ決定書.md) | 基板分割と役割分担 |
| [MAIN・UI・GPIO・コネクタ表](AquaBeacon_MAIN_UI_GPIO_コネクタ表.md) | 配線・同期・UIの変更履歴と接続 |

調達台帳、元のプレゼンテーション、過去版・バックアップは手元専用です。公開版の設計と企画は上記のMarkdown文書を参照してください。

資料を追加・削除した場合は、この索引も更新する。

## 開発とライセンス

[開発ガイド](DEVELOPMENT.md)にセットアップ・入口・確認方法をまとめています。自作部分は [Apache License 2.0](LICENSE)。[第三者素材・依存の扱い](THIRD_PARTY.md)も参照してください。

## リポジトリ運用

- [実験で使用した統合ファームウェア](https://github.com/AquaBeacon/obsidian/blob/main/knowledge/notes/実験で使用した統合ファームウェア.md)：2026-10-28取得版の構成・操作・ログと検証状況。

- [OSS移行記録と検証](maintainer/migration.md)
- [紹介サイト・研究結果・写真付きマップの運用記録](maintainer/website-operations.md)
- [Obsidianの構成と維持](maintainer/obsidian.md)
- [全プロジェクト一覧](https://github.com/AquaBeacon/workspace-tools)

## 成果報告会資料

- [未踏成果報告会：現行マスター・原稿改訂版](presentations/未踏成果報告会/README.md)：2026年11月6日更新。知識に登録された現行マスター、本編33枚・補足25枚。最新のプール静止RMS 12.75 cmを反映。原稿3,592字、1文80文字以内。毎分300字で動画等を含め12分35秒の見込み。
- [2026年10月31日版：自己紹介〜プールのマッピング評価（12枚・原稿付き）](presentations/20261031-progress-report/README.md)
