# 研究レポートの出典と評価条件

対象原稿は [AquaBeacon研究レポート](AquaBeacon_研究レポート.md)。2026年11月6日時点で保存されている解析結果を整理した。原データの再解析、既存図の再描画、校正値の変更は行っていない。文献[5]以降の番号は原稿の参考文献番号に対応する。

## 出典対応

| 文献 | 根拠ファイル | 原稿での用途 |
| --- | --- | --- |
| [5] | [実験用ファームウェア仕様](../../../firmware-experiments/docs/spec.md)、[README](../../../firmware-experiments/README.md) | RS485開始マーカー、子機同一時計の時刻差、片道音響測距、音速の扱い |
| [6] | [解析方法と評価指標](../../../aquabeacon-analysis/results/20261103_field_review_000/research_review/03_methods.md)、[校正の説明](../../../aquabeacon-analysis/calibration/README.md) | 時計、画像回転、座標系、名目取付位置、RMS、位置補完の条件 |
| [7] | [最新プール静止評価](../../../aquabeacon-analysis/results/20261028_ngt_002/static_after_immersion_20261105/report.md)、[metrics.json](../../../aquabeacon-analysis/results/20261028_ngt_002/static_after_immersion_20261105/metrics.json) | 要旨、表2、12.75 cm、18.04 cm、54/54、271/300、時間格子の10秒平均差 |
| [8] | [プール光源・位置追加評価](../../../aquabeacon-analysis/results/20261028_ngt_000/optical_followup/pool_multiscale_20261104/report.md) | 280秒、1,400点、62.4→81.4→82.6%、追加546候補中491不採用 |
| [9] | [南予静止評価の説明](../../../aquabeacon-analysis/results/20261103_field_review_000/research_review/05_nanyo.md)、[stationary_summary.csv](../../../aquabeacon-analysis/results/20261103_field_review_000/research_review/stationary_summary.csv) | 表3の6窓、同じ32観測の比較、親機姿勢、視線直交分散、PPK比較 |
| [10] | [南予光源・位置・再構成追加評価](../../../aquabeacon-analysis/results/20261103_field_review_000/optical_followup/optical_fallback_20261104/report.md)、[paired_static_rms.csv](../../../aquabeacon-analysis/results/20261103_field_review_000/optical_followup/optical_fallback_20261104/paired_static_rms.csv) | 表4、同時刻と全有効時刻のRMS、候補確認、局所再構成の成否 |
| [11] | [壁区間のマッピング診断](../../../aquabeacon-analysis/results/20261028_ngt_004/mapping_diagnosis/wall_ablation_v2_20261104/report.md) | 300画像の比較、対応グラフ、三角測量角、拘束あり・なしの比較 |

解析出力は隣接するaquabeacon-analysisのローカルresultsを参照する。文書リポジトリ単独の取得環境では、このリンク先のローカル解析出力は含まれない。生CSV・動画・点群はこのレポートの配布物に複製していない。

## 評価版の区別

- プールの主たる静止値は2026年11月5日の入水基準窓に限る。11月4日の旧区間002の静止値0.153 mとは窓が異なる。旧002の位置CSVは親機動画1110秒までであり、指定窓1056～1116秒の末尾6秒は旧003の位置CSVから参照している。原稿4.1節の区間境界をまたぐ記述に対応する。
- プールは画像回転修正版を採用する。未修正版の旧位置のばらつきや地図尺度は成果値に使わない。
- 表2の100%は記録済み54音響イベントに対する値であり、時間全体の成立率ではない。5 Hzの271/300点には測距結果の再利用がある。
- 表3は音響イベント単位で親機回転だけを変える比較である。表4および5.3節後半は光源候補の見直しと位置補完の時間格子評価であり、独立観測数と混在させない。
- 表4の旧・新位置は同じ位置補完規則を使う。プール同時移動の62.4→81.4→82.6%は同時成立位置、旧光源＋補完、新光源＋補完の3条件である。
- 南予10月31日の全区間分母には投入前・引き上げ後が含まれる。表4は水中限定の検出率ではない。
- 3D RMSは平均周りのばらつきである。独立真値誤差、単純な白色雑音の標準偏差、地図寸法精度として扱わない。
- 地図の記述は2026年11月4日の追加比較と診断に限定する。旧来の写真地図の5区間・82,500点等を、新しい試行の成果として混ぜない。

## 関連研究の確認

文献[1]は出版社の抄録と書誌、[2]はISPRSの公開本文・抄録、[3]はCVFの公開論文、[4]は著者所属機関の論文アーカイブを確認した。書誌に記載した年は掲載巻の年を採用した。市場価格や機器の公称精度との順位比較は、本レポートの対象としない。

- [Abadieほかの出版社ページ](https://onlinelibrary.wiley.com/doi/10.1111/phor.12263)
- [LoほかのISPRS公開ページ](https://isprs-archives.copernicus.org/articles/XLVIII-2-2024/211/2024/)
- [SchönbergerとFrahmのCVF公開ページ](https://openaccess.thecvf.com/content_cvpr_2016/html/Schonberger_Structure-From-Motion_Revisited_CVPR_2016_paper.html)
- [Medwin論文のNaval Postgraduate School公開版](https://calhoun.nps.edu/server/api/core/bitstreams/35d133d5-6956-4912-8597-5f2dc8fc5ad2/content)

## 再生成と来歴

本文の編集元はMarkdownであり、Word版は [build_report.py](build_report.py) で生成する。Wordには見出しスタイル、編集可能な表、ページ番号を設定する。生成コードは本文の数値を変更しない。

実行に使用したPython環境、原稿および参照資料のSHA-256、参照リポジトリのHEAD、出力確認は `manifest.json` に記録する。参照リポジトリには作業中の変更があるため、HEADだけを入力の同一性の根拠にはせず、今回読んだ個々の資料のハッシュを併記する。
