# OSSワークスペースへの移行

## 2026-10-16：GitHub公開

対象17リポジトリを [AquaBeacon](https://github.com/orgs/AquaBeacon/repositories) にpublicで公開しました。公開先・取得方法は [workspace-tools](https://github.com/AquaBeacon/workspace-tools) にまとめています。`habatan-game` は所有者の指定により対象から外しました。

- 自作部分はApache-2.0。第三者のライセンス表示は各リポジトリに保持しています。
- 新設15件は整理済みソースだけを初期コミットにしました。既存の `.github` と `aquabeacon.github.io` は公開済み履歴を引き継いでいます。
- 元の開発履歴は手元に保持し、既存mainは `archive/pre-publication-main-20261016` に退避しました。移行前HEAD・ブランチ・インデックス・設定は手元専用の `.local/publish/backups/` に記録しています。
- 各リポジトリのローカルmainは公開mainを追跡します。新設リポジトリの公開先remote名は `public`、既存2件は `origin` です。従来のremoteは保管しています。
- 生の実験ログ、調達台帳、ローカル設定、SDK、仮想環境は公開対象外です。認証設定を含む保存済みメーカーWebページも手元専用にしました。
- CAD・制作素材のGit LFSデータは約4.5 GiB。公開ツリーの100 MiB以上の通常Git blobは0件です。
- 公開候補の既知の認証情報形式の検査は検出0件。これは全履歴の検査や第三者資料の権利判断を代替しません。
- シミュレーションのGitHub CIはPython 3.10・3.11・3.12ですべて成功しました。

以下は10月15日のローカル移行時点の記録です。18件・未公開・未コミットという記載は当時の状態を示します。

## 2026-10-15：ローカル移行記録

2026-10-15。各プロジェクトを独立したGitリポジトリとして `AquaBeacon-OSS/` へ集約しました。親ディレクトリ自体はGitリポジトリにせず、各プロジェクトから開発・履歴確認を行います。

## ディレクトリの対応

| 旧ディレクトリ | 現在のリポジトリ | 判断 |
| --- | --- | --- |
| `Kicad_project` | `hardware` | 現行の回路・PCB・製造ツール |
| `Body_Models` | `mechanical` | 部品正本とassemblyの関係を維持 |
| `CHILD_MAIN_test` | `firmware` | 親機・子機を同じPlatformIOプロジェクトで開発 |
| `TD04A_test/TD04A_test` | `acoustic-tests` | 不要な二重階層を解消。TX/RX等の共有設定は一か所に維持 |
| `SONYspresenceIMU` | `spresense-imu` | 自作アプリとSDKの管理範囲を分離 |
| `NEO-F9P-RTK-GNSS_test` | `gnss-tools` | GNSS検証スクリプトと依存定義 |
| `GetDJI` | `dji-telemetry` | 動画抽出CLIとして独立 |
| `aquabeacon-analysis` | `aquabeacon-analysis` | 解析コードと実験データの管理区分を維持 |
| `aquabeacon-sim` | `aquabeacon-sim` | 真値付きシミュレーション |
| `TO_printing` | `topopt` | Pythonパッケージと検証用モデルを同じリポジトリに維持 |
| `BambuX1-print-MCPtools` | `bambu-tools` | プリンタ連携ツール |
| `Accoustic_modules` | `acoustic-circuits` | 初期回路を現行hardwareと混同しないよう独立 |
| `assets` | `assets` | ロゴ・図解・映像の相互参照を維持する制作プロジェクト |
| `docs` | `docs` | システム全体の文書と本移行記録 |
| `tools` | `workspace-tools` | 台帳・構成検査・公開候補検査と既存のローカル自動化 |
| `Kicad_project/habatan-game` | `habatan-game` | AquaBeacon本体とは別のプロジェクトとして分離 |
| `AquaBeacon-OSS/aquabeacon.github.io` | `aquabeacon.github.io` | 紹介サイトの既存履歴を保持 |
| `AquaBeacon-OSS/organization-live` | `organization` | `.github` の履歴付きcloneへ統一 |

以前のOrganization作業コピーは `.local/organization-template/`、旧サイト運用資料は `.local/previous-site-docs/` に保全しました。サイト運用文書の参照先は [website-operations.md](website-operations.md) です。ルートの一時ログ・result.json・tmpも `.local/` に移しています。

## 開発とGit

- 18リポジトリすべてにREADME、DEVELOPMENT、AGENTS、LICENSE、NOTICE、THIRD_PARTY、ignore設定を配置しました。
- 既存の履歴・ブランチ・リモートを維持しました。履歴の書換え・リモート変更・新規公開・pushは行っていません。
- Git未導入の8プロジェクトは `main` で初期化しました。初回コミット前です。
- 移行前から存在した未コミット変更を保全し、今回の変更もレビューできる作業ツリーに残しています。
- `firmware/.claude/settings.json` と `habatan-game/.openai/hosting.json` のみ、ローカル設定としてGitインデックスから除外済みです。実ファイルは保持しています。過去の履歴からの除去ではありません。
- `acoustic-tests` の階層整理は、Git上では旧パスの削除と新パスの追加として見えます。内容と移動記録を確認して同時にコミットしてください。旧パスだけをコミットしないでください。
- 所有者の異なる既存チェックアウトも操作できるよう、この18リポジトリの絶対パスだけをGitの `safe.directory` に登録しました。全パスを許可する設定はしていません。

横断開発の配置と入口は [全体README](https://github.com/AquaBeacon/workspace-tools) と [台帳](https://github.com/AquaBeacon/workspace-tools/blob/main/repositories.json) が基準です。親フォルダのREADME・AGENTS・エディタ設定はworkspace-toolsから `python workspace-tools/workspace.py configure` で再生成できます。

旧名のフォルダはWindowsのディレクトリジャンクションです。実体のコピーはありません。既存のMCP設定、editable install、保存済みの絶対パス、過去のチャットを壊さないために保持しています。新しい作業では必ず新しいパスを使ってください。旧TD04Aの二重パスは `.local/legacy-td04a/` を経由します。リポジトリ内に自分自身への循環リンクは置いていません。

## ソース・データ・生成物

- `aquabeacon-analysis/data/`、実験ログ、GNSS記録、SDK、仮想環境、購入台帳、一時ファイルは削除せず手元に保持しました。公開候補からはignore設定で区別します。
- `mechanical` のCAD・STL・3MFと `assets` の画像・音声・動画・BlenderデータはGit LFSを設定しました。LFSはローカル導入済み。まだadd・uploadしていない新規ファイルは通常の実ファイルです。
- 大容量のソルバ中間ファイル（FRD等）はGit対象外。設計入力・結果の要約・既存の回帰試験の根拠は維持します。
- 過去の解析manifest・結果文書の記録値と旧パスは保持します。現行ソース・説明文書の参照は新構成へ更新しました。
- 元データの再取得や実験再実行は必要な場合に各プロジェクトの手順に従います。SDKは `spresense-imu/sdk.lock.json` で既存のv3.4.7コミットを記録し、bootstrapは既存SDKをリセットしません。
- 古い一品専用CAD・映像制作スクリプトの一部には外部ツールやフォントのローカル絶対パスが残っています。制作環境を再現する場合は各READMEの前提とインストール先を確認してください。

## ライセンス

ユーザー指定により、自作部分にApache License 2.0を適用しました。各リポジトリに [公式ライセンス本文](https://www.apache.org/licenses/LICENSE-2.0.txt) とNOTICEを配置し、Pythonパッケージのライセンス表記も更新しています。

SDK、外部ライブラリ、メーカーのCAD・データシート、フォント、提供写真・音声、はばタン素材等は、既存の権利表示と利用条件を保持します。自作部分のライセンス決定を、第三者資料への再許諾と扱いません。適用範囲は各THIRD_PARTY.mdに記載しています。

## 受け入れ条件と検証結果

| 条件・検証 | 結果 |
| --- | --- |
| 18プロジェクトが独立したGitルート、必要な入口が存在する | PASS：`workspace.py check` |
| 元のGit履歴とremoteが維持されている | PASS：SDK・KiCad履歴を含む24箇所でHEADとremoteが一致 |
| 移行で編集したPythonソースの構文 | PASS：29ファイルをAST解析 |
| 公開候補の大容量ファイル・ローカル設定・既知の秘密キー形式 | PASS：`workspace.py audit` の検出0件。大容量CADはLFS属性を検証 |
| 解析 | PASS：73テスト、ruff成功 |
| シミュレーション | PASS：316テスト |
| SPRESENSE姿勢ビューア | PASS：4テスト |
| はばタンゲーム | PASS：`node verify.cjs` |
| メイン基板ファームウェア | PASS：`pio run -e pico2w -e parent`、両環境成功 |
| 音響ファームウェア | PASS：`pio run -d tx`、`pio run -d rx` |
| DJI抽出・Bambu CLI | PASS：両方の `--help` が終了コード0 |
| SDK bootstrapの既存checkout保護 | PASS：既存SDKを変更せず終了 |
| 筐体ツール | 42件中41件成功、材料定義不足による既存エラー1件（下記） |
| topopt | PASS：730件中725件成功・5件skip、終了コード0 |
| 入口文書のローカルリンク | PASS：全体READMEと18リポジトリのREADME・DEVELOPMENT・THIRD_PARTY、移行記録を確認。既存のリンク切れ2件を修正 |

解析テストでは、既存 `.pytest_cache` の書込み権限に関する警告が1件ありました。テスト本体は成功しています。
topoptではNumPyの既存の非推奨APIに関する警告が10件ありました。

筐体ツールの `test_clamp_bambu_material` は、`parts/child/exterior/printed/child_wte4_suspension_clamp/spec/bambu_petg_basic_material.json` が存在しないためエラーになります。この部品や材料値は今回の移行で変更していません。試験を緩めたり材料値を推測して補ったりせず、元の材料カードの復元を課題として残します。

実機への書込み・送信・印刷、KiCad基板の再生成、CADの再生成、SDK全体の再ビルドは実施していません。構成移行の合格と実機・製造の合格は区別します。

監査コマンドは現在の公開候補だけを検査します。Git全履歴の秘密情報検査、第三者資料の配布許諾、LFSの公開先容量は別の確認事項です。ライセンスを追加しただけでこれらを確認済みとは扱いません。

## 保全記録

手元専用の `.local/` に移動記録、移行前Git状態、編集前ファイル、履歴照合結果、公開候補監査を保持しています。これらは公開リポジトリへ追加しません。移動を戻す場合は記録の逆順に対象を確認し、現在の変更を保全してから作業してください。
