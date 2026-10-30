# Obsidianナレッジベースの構成と維持

2026-10-22に、既存資料をたどりながら知識を蓄積・再利用できる構成を追加しました。

## 配置と管理単位

| 対象 | 配置 | 管理 |
| --- | --- | --- |
| 保管庫ルート | 親の `AquaBeacon-OSS/` | 親をGitリポジトリにしない |
| 共有ノート・索引・型 | `obsidian/knowledge/` | obsidianリポジトリ |
| 自由メモ・日誌・個人添付 | `obsidian/knowledge/private/` | Git除外。ローカルに生成 |
| Obsidian個人設定 | 親の `.obsidian/` | Git除外。ローカルに生成 |
| 設定の生成処理 | `workspace-tools/obsidian.py` | workspace-toolsリポジトリ |
| 配置の台帳 | `workspace-tools/repositories.json` の `obsidian` | workspace-toolsリポジトリ |

共有ノートは2026-10-31にAquaBeacon/obsidianへ分離し、台帳は19リポジトリ構成です。コード・設計元の配置は維持します。サイトの配信対象は引き続き `aquabeacon.github.io/site/` のみです。

## 初期化と検証

親フォルダで実行します。

```sh
python workspace-tools/obsidian.py configure
python workspace-tools/obsidian.py check
python workspace-tools/workspace.py check
```

`configure` は保存先フォルダ、最初の自由メモ、`.obsidian/` の設定を生成します。設定キーの既存値とノート本文は上書きしません。必要なコアプラグインは有効化し、ホーム・一覧・Canvasのブックマークを不足分だけ追加します。追加プラグイン、実機操作、Git操作、公開は行いません。

`check` は共有ノートの明示的な保管庫ルート基準リンク、配置、Canvasのファイル参照とエッジを確認します。個人ノートの未作成リンクとテンプレートのプレースホルダーは検証対象外です。設計内容の正しさやObsidianの画面描画は、このコマンドの検証対象に含みません。リンク先の移動後はObsidianのバックリンクと未解決リンクも確認します。

## 追加・変更時

- 新しいメモは `private/00_Inbox/`。プロパティや分類は必須にしない。
- 共有する知識は `notes/` に置き、元資料・適用条件・関連する分野をリンクする。
- 分野を増やしたら `maps/`、ホーム、必要に応じてCanvasを更新する。
- 新しいノート種別はテンプレートとBasesのビューを対応させる。
- 構成を変更したら、台帳・README・本書を同期する。
- 親READMEの正本は `workspace-tools/workspace-template/README.md`。親の再生成で案内を失わないよう、両方を更新する。

個人メモはGit除外のため、個人のバックアップ手段で保全します。Git除外とObsidian Sync等の同期範囲は別です。共有ノートへ個人ファイルを移すときは、リンク切れ・生データ・認証情報・購入台帳・第三者の配布条件を確認します。

[ナレッジベースの入口](../../obsidian/knowledge/README.md) · [利用方法](../../obsidian/knowledge/使い方.md) · [ドキュメント索引](../README.md)

## 起動時に画面が消える場合

2026-10-22の初回設定では、対話用のObsidianを非表示で起動したため、プロセスが動作していても画面が出ない状態になりました。CLIの `restart` で通常のウィンドウへ復帰しました。ノートと設定の削除は不要でした。

同じ状態でプロセスが残っている場合は、PowerShellで次を実行します。

```powershell
& "$env:LOCALAPPDATA/Programs/Obsidian/Obsidian.com" vault=AquaBeacon-OSS restart
```

対話用のアプリを開くときは非表示起動を使いません。起動確認では、CLIによるファイル読取りやアプリ内スクリーンショットに加えて、ウィンドウが実際に表示されていることも確認します。別の終了原因はこの手順で解決済みと扱わず、ログとプロセスの状態から調べます。
