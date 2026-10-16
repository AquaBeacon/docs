# AquaBeacon 詳細設計書 — 筐体・基板・機体設計（基板分割・電源確定版）


> **改訂日: 2026-07-21** (2026-09-04: §3.1 親機の機体構成に改訂注記を追加)  
> 本版では、親機・子機の基板分割、搭載センサ、電源方式、microSD実装方式を確定した。


本書は確定仕様メモの下流にあたる実装設計。**回路の数値はすべて計算で検証済み**（支配式・assert付き）、**配線はERC（構造チェック）合格のネットリスト**、**バンドパスはSPICE（ngspice）でAC解析済み**、**部品配置は実寸で最適化済み**（親機プレート・子機チューブとも制約違反ゼロ）。


> **統合改訂（2026-07-21）— 本節を旧記述より優先すること**  
> 親機・子機のメイン制御を Raspberry Pi Pico 2 W に統一し、表示・操作・RS485・温度計測・microSD配置・物理電源スイッチまで確定した。旧版中の SPRESENSE 主制御、BMI270、DS18B20、RS485トランシーバ直載せ、OLED に関する記述は廃止する。

## 2026-07-21 統合確定事項

### 基板分割

- 親機：`P-MAIN` / `P-TX` / `P-PWR` / 共通UI基板 / 独立SPRESENSE IMUロガー
- 子機：`C-MAIN` / `C-RX` / `C-PWR` / 共通UI基板
- 電源基板はメイン基板から分離する。音響基板もメイン基板から分離する。
- 大電流電源はXT30、センサ・低電流信号はJST XHを使用する。

### 共通メイン基板

- メインMCU：**Raspberry Pi Pico 2 W**。
- 実装：Pico 2 Wへ2列ピンヘッダを実装し、メイン基板のメスソケットへ交換可能に搭載する。
- microSD：Molex 104031-0811相当の表面実装ソケット。基板端かつPicoのSPI接続部近くへ配置し、カード挿入口を基板外側・筐体開口側へ向ける。
- LED：緑色`LED_PWR`と黄/橙色`LED_STATUS`の2個。
- 操作：UP / ENTER / DOWNの3ボタン。共通UI基板に搭載し、アクティブLowで使用する。
- 予備ポート：I2C×1、3.3V TTL UART×1、GPIO×2＋ADC×1のXHコネクタ×1。

### 表示・操作UI

- LCD：**Newhaven Display NHD-C12864WO-B1TFH#-M**。
- 方式：128×64、FSTNポジティブ、半透過型、白色LEDバックライト、ST7567系、4線SPI。
- LCDと3ボタンは親機・子機共通の独立UI基板へ搭載する。
- UI基板の初期外形目安：**100 mm × 65 mm**。LCD外形・取付穴・FFC位置はメーカー機械図を正とする。
- バックライトはGPIO直結禁止。UI基板上のNch MOSFETでPWM制御し、日中は消灯、操作後30〜60秒で消灯可能とする。
- メイン基板―UI基板間は専用JST XH多極コネクタを使用する。SPI、LCD制御、BL PWM、3ボタン、3.3V、GNDを収容する。

### RS485

- 採用品：**Waveshare TTL TO RS485 (C)**（スイッチサイエンス製品9778）。
- 親機・子機とも2枚搭載：`DATA`用1枚、音響同期`TRIGGER`用1枚。
- メイン基板へキャステレーション端子で直接はんだ付けする。TTL側をPico側、A/B/PE側をテザー側へ向ける。
- モジュールの絶縁・保護・自動送受信切替を利用し、MAX3485等のトランシーバ回路はメイン基板へ重複実装しない。
- 終端抵抗はモジュールの設定を確認し、各バス両端のみ120Ωを有効化する。追加終端はDNPとする。
- トリガ経路は実機で伝搬遅延とジッタを測定し、固定遅延は較正値として扱う。

### 親機 P-MAIN

- 主制御：Raspberry Pi Pico 2 W。
- GNSS：NEO-M9N＋ANN-MB1-00、UART＋PPS。
- RTC：DS3231。
- 水温：指定品 **Celsius Fast-Response ±0.1°C Temperature Sensor R2** をI2C接続し、音速補正に使用する。旧Celsius Fast-Response Temperature Sensor R2案は廃止。
- P-TX温度：P-TXにNTCLE100E3103GB0と分圧・フィルタ回路を実装。P-MAINはXHから来る`TX_TEMP_ADC`のみをPico ADCへ入力する。
- P-MAIN側ADC入口：直列抵抗、RCフィルタ、未接続検出、テストポイントを設ける。
- SPRESENSEはメイン制御に使用しない。独立IMUロガーとしてMulti-IMU Add-on Boardを制御し、**SPRESENSE自身のmicroSD**へ記録する。
- P-MAINとSPRESENSEはPPS・イベントマーカー・必要に応じたUART時刻情報だけを接続する。

### 子機 C-MAIN

- 主制御：Raspberry Pi Pico 2 W。
- IMU：**BNO085**。SPI＋INT＋RESET、Rotation Vector 100 Hz。旧BNO085案は廃止。
- RTC：DS3231。GNSS/通信同期断時の絶対時刻保持、再起動後のログ時刻、映像照合に使用する。
- 深度・水温：MS5837-30BA / Bar30相当。
- 音響：C-RXから`CMP_OUT`、`ENV_ADC`、`RX_EN`を接続する。
- 漏水検知、ライト制御、C-PWRのINA226監視を行う。

### 電源・物理スイッチ

- P-PWR/C-PWRはメイン基板から分離する。
- 主電源スイッチは**物理直列方式**とし、P-PWR/C-PWRのLiPo正極入力経路に配置する。
- 電源経路：`3S LiPo → XT30 → ヒューズ → 逆接保護 → 物理スイッチ → TVS → INA226 → 各電源レール`。
- スイッチ電流をJST XHへ流さない。基板直付け、はんだ配線、または大電流対応コネクタを使用する。
- スイッチ要求目安：DC 15 V以上、連続5 A以上、突入電流に耐えること。筐体外露出時はIP67以上。
- C-RX用`3V3_ANALOG`はC-PWRからC-RXへ直接供給し、C-MAINを経由させない。

### 初期基板外形目安

| 基板 | 初期外形目安 | 備考 |
|---|---:|---|
| P-MAIN | 100 × 70 mm | 配置後に90 × 65 mm前後を検討 |
| C-MAIN | 95 × 60 mm | 円筒収納を考慮し幅55〜60 mmを優先 |
| 共通UI | 100 × 65 mm | LCD＋3ボタン＋BL回路 |
| P-PWR | 約80 × 50 mm | 最大電流確定後に縮小可 |
| C-PWR | 約80 × 50 mm | ライト電源を含む |

### 発注前に残る必須作業

1. 親機・子機のPico 2 W GPIO割当表を確定する。
2. 全XHコネクタの極数・ピン順・向き・シルク表記を確定する。
3. LCDの最新メーカー機械図からUI基板のFFC・取付穴・開口寸法を確定する。
4. P-PWR/C-PWRのDC/DC、ヒューズ、逆接保護、TVS、物理スイッチの具体型番を確定する。
5. 筐体内寸、スペーサ位置、USB・microSD・XHの挿抜空間を実寸で検証する。
6. Waveshare RS485のトリガ遅延・ジッタ、終端設定、長尺テザー波形を実測する。

---

# 第1部　実装にあたって深く決めるべき項目

発注・製作前に決めるべき判断を、影響が大きい順に列挙する。各項に推奨案を付けた。

## 1.1 親機の方位（ヘディング）決定 ★最重要・未解決

カメラで測った角度は「親機基準」の角度である。これを地図（地球座標）に載せるには**親機がどちらを向いているか（方位）**が必要だが、GPSは位置しか与えず、SPRESENSEマルチIMUは6軸（加速度＋ジャイロ）で**磁気センサを持たないため絶対方位が取れない**。これが現状の設計穴。

対策の選択肢: (a) **磁気センサ追加（推奨）** — BMM150/LIS3MDL等をI2Cに追加（数百円〜1500円）。ハード/セミハードアイアン較正が必須で、実現精度1〜2°程度。±0.3°の角度精度に対し方位が1°誤ると10m先で17cmずれるため、**相対位置評価（クライテリア主評価）には影響しないが、絶対マッピング精度は方位精度で頭打ちになる**ことを認識しておく。(b) デュアルアンテナGNSS（Moving Base RTK）— 0.2°級だが+5万円超・複雑。(c) 親機を意図的に動かしGPS進行方位で推定 — 追加ハード不要だが運用が縛られる。**推奨は(a)を今すぐ、将来(b)を予算残で検討。**

## 1.2 エッジウォーク（音響の振幅依存タイミング誤差）★系統誤差の最大要因

包絡線検波＋固定閾値では、**受信振幅が変わると閾値到達時刻が動く**。計算では振幅2倍差で約10.4µs＝**約1.6cm**の系統誤差（τ=15µsのとき）。cm精度を狙うならこれが距離誤差予算の最大項になる。

対策（実装済み設計に織込み）: 包絡線を分圧してPico ADC0でも取得し、**タイムスタンプと同時に振幅を記録→後処理で振幅-時刻ウォーク補正**をかける。加えて既知距離での較正カーブ取得（プール実験の最初にやる）。閾値はPico PWM＋RCで可変にしてあるので、S/Nに応じてソフトから調整できる。

## 1.3 TD04Aの電気特性の実測（TX整合の前提）

TD04Aの静電容量C0・共振特性は公開されていない。TX直列同調インダクタは L=1/(ω²C0) で決まるため、**LCRメータでC0を実測してからL1を巻く/選ぶ**（例: C0=2nFなら200kHzでL1≈317µH）。RX側の入力整合・保護レベルもこの実測が前提。学校や部活でLCRメータを借りられるか先に確認しておくこと。

## 1.4 トランス（TX昇圧）の入手方法

センタタップ1:5昇圧トランス（200kHz、数十W瞬時）は既製品の型番指定が難しい領域。選択肢は (a) フェライトEE/EIコア＋手巻き（コスト最小・要試作）、(b) Coilcraft等のワイドバンドトランス流用、(c) 昇圧をやめてフルブリッジ＋12V直接駆動（振幅は落ちるが単純）。**初期実験は(c)の12V直駆でまず往復が通るか確認し、距離が足りなければ(a)で昇圧**、が低リスク。

## 1.5 テザーの結線・接地の設計

信号のみ4線（2ペア）＋シールド: ペア1=トリガ（RS485差動、親→子の一方向固定）、ペア2=データ（RS485半二重）。**親子は電池独立なので、テザーのシールド/GNDを介して1点でコモン接地**とし、ループを作らない。ケーブルはCat5e系水中ケーブルまたはBlueRobotics Fathom系。トリガ経路の遅延は計算上350ns（ケーブル150ns＋送受信IC200ns）＝距離換算0.53mmの**系統オフセットで、較正で除去可能**。

## 1.6 カメラポッドの窓と防水方式

深度0.5m（0.05bar）なので圧力は問題にならず、課題は**止水と光学**。フラットポート（アクリル板t3〜5mm＋Oリング）を推奨。3Dプリント筐体は積層間浸水があるため、**PETG/ASA印刷後に内面エポキシコートまたは気密試験必須**。ドームポートは画角と屈折で有利だが入手・固定が面倒なので今回は不採用。**キャリブレーションは必ずこのポッド越し・水中で行う。**

## 1.7 子機ステレオ基線（Osmo×2の間隔）

σ_Z = Z²·σ_d/(f·B)。Osmoの水中換算FOV約105°→f≈1474pxとして、**基線B=30cmで距離2mの深度分解能≈9mm/px視差**（1m:2.3mm、5m:57mm）。マッピング対象距離1〜3mを想定しB=30cmを推奨。40cmにすれば5mでも42mmだがフレームが大型化する。**B=30cm、フレームに±5cmの取付穴を複数開けて実験で追い込む。**

## 1.8 音速の実測（温度計測の必達精度）

dc/dT≈2.7 m/s/K。**水温±1Kの不確かさは15mで2.7cmの距離誤差**になり、これだけでcm精度を食い潰す。温度センサ（親機の深度/温度センサ）は±0.5K以下の確度のものを選び、**測距の都度、温度から音速を補正**する（±0.5Kで1.4cm@15m）。プールと海で塩分も違う（淡水約1480m/s、海水約1500m/s超）ので、実験ごとに既知距離1点で音速をその場較正するのが確実。

## 1.9 検出方式の発展余地（今は包絡線＋閾値でよい）

将来精度を上げたくなったら、コンパレータ方式のまま**搬送波ゼロクロス列をPIOで全部記録**し後処理で相関を取る（実質数mm級へ）拡張が可能。今回の基板はコンパレータ出力をPIOに入れているので**ハード変更なしでファーム側の拡張だけで試せる**。

## 1.10 その他の決定済み小項目

リジッド固定に伴うボアサイト較正は陸上で一度実施（チェッカーボード＋治具）。SDログはCSV＋モノトニックµsカウンタ＋RTC秒＋GPS PPS（親機）で共通時刻軸を構成。子機Picoの時刻はトリガパルス自体が親機時刻の伝搬なので、**トリガ受信イベント＝共通時刻マーカー**として使う（別途の時計合わせ不要という有線トリガ同期の利点）。

## 1.11 基板分割方針（確定）

### 親機

- `P-MAIN`：SPRESENSEキャリア、GNSS、RTC、microSD、RS485、センサI/F
- `P-TX`：200kHz送信回路、保護、整合、TD04Aコネクタ
- `P-PWR`：入力保護、電源分岐、5V×2、3.3V、INA226

### 子機

- `C-MAIN`：Raspberry Pi Pico 2 W、BNO085、RTC、microSD、RS485、センサI/F
- `C-RX`：増幅、BPF、検波、コンパレータ
- `C-PWR`：入力保護、5V、デジタル3.3V、アナログ3.3V、ライト定電流、INA226

RX/TXは高改版領域、メイン基板は安定領域、電源基板は安全・ノイズ管理領域として責務を分ける。各基板は誤挿入防止付きコネクタで接続し、テストポイントを設ける。

### 共通基板間インタフェース

| 信号 | 電圧 | 方向 | 備考 |
|---|---:|---|---|
| `VBAT_PROTECTED` | 9.0〜12.6V | PWR→TX/負荷 | ヒューズ・逆接保護後 |
| `5V_DIGITAL` | 5.0V | PWR→MAIN | MCU、RS485 |
| `3V3_SENSOR` | 3.3V | PWR→MAIN | センサ |
| `3V3_ANALOG` | 3.3V | PWR→RX | 低ノイズLDO |
| `PWM_A/B` | 3.3V | MAIN→TX | 相補PWM |
| `CMP_OUT` | 3.3V | RX→MAIN | PIO入力 |
| `ENV_ADC` | 0〜3.0V | RX→MAIN | 包絡線振幅 |
| `RX_EN` | 3.3V | MAIN→RX | 受信段有効化 |
| `I2C` | 3.3V | 双方向 | センサ・電源監視 |
| `SPI_SD` | 3.3V | MAIN↔SD | microSD |


---

# 第2部　電気設計（検証済み）

## 2.1 設計検証サマリ

| 項目 | 値 | 判定 |
|---|---|---|
| PIO量子化誤差 | 8ns → 0.012mm | 無視可 |
| 水晶±30ppm誤差@15m | 0.45mm | 無視可 |
| トリガ経路遅延(30m) | 350ns → 0.53mm | 系統・較正で除去 |
| 水温±0.5K→距離誤差 | 1.4cm @15m | 温度補正必須（1.8節） |
| エッジウォーク(振幅2倍) | ≈10.4µs → 1.6cm | 振幅記録＋補正必須（1.2節） |
| RX総利得 | 60dB（20×2×25） | GBW検証済み |
| MFB BPF（SPICE実測） | f0=199.5kHz, G=6.03dB(2.0倍), BW=80kHz(Q=2.5) | 設計値一致 |
| 子機電池余裕率(3h) | 2.85（19.5Wh/55.5Wh） | 合格 |
| 親機電池余裕率(3h) | 2.17（11.2Wh/24.4Wh, 3S2200mAh） | 合格・**BOM追加要** |

## 2.2 子機メイン基板（C-MAIN）

**初期実装**：Raspberry Pi Pico 2 Wを2列ソケットで搭載するキャリア基板とする。基板改版時にRP2040周辺回路まで巻き込まないことを優先する。

**搭載・接続**：
- BNO085 9軸IMUブレークアウト基板
  - SPI接続を標準とする
  - INTを専用GPIO割込みへ接続
  - RESETをGPIO制御可能にする
  - BOOT/PS端子はSPIモードになるよう固定
  - 3.3V電源直近に100nF＋4.7〜10µF
  - TXトランス、DC/DCインダクタ、ライト配線、バッテリから可能な限り離す
- DS3231（I2C、バックアップ電池）
- INA226（I2C、C-PWR上でも可）
- MS5837-30BA/Bar30用I2Cコネクタ
- 漏水電極入力
- RS485データ、トリガ受信
- microSD表面実装コネクタ Molex 104031-0811
- C-RX接続：`CMP_OUT`、`ENV_ADC`、`RX_EN`
- SWD/UARTデバッグ端子、リセットボタン、状態LED

**microSD設計**：
- SPIモード、3.3V駆動。
- コネクタ直近に100nF＋10µF。
- CS、SCK、MOSIに22〜47Ωの直列抵抗を実装可能にする。
- Card DetectをGPIOへ接続。
- ロードスイッチでSD電源を再投入できる構成とする。
- 書込み中の電源断を避けるため、バッテリ低電圧割込み後は新規ログを停止してファイルをcloseする。

## 2.3 子機RX基板（C-RX）

**信号チェーン**: TD04A → AC結合(100nF) → [BAV99レール間クランプ＋100kΩでVMID(1.65V)バイアス] → 初段 非反転×20（OPA2607 A回路、帰還脚はAC接地でDCゲイン1） → **MFBバンドパス** f0=200kHz/Q=2.5/G=2（C=330pF, R1=3.01k, R2=12.06k, R3=574Ω、+入力=VMID） → 後段 非反転×25（OPA607） → AC結合 → BAT54＋RC包絡線検波（C=1.5nF, R=10k, τ=15µs） → TLV3501コンパレータ（閾値=GP16 PWM＋RC、ヒステリシス1MΩ） → **GP2（PIO捕捉）**。包絡線は10k:10k分圧で**GP26/ADC0**にも入れ振幅を記録（ウォーク補正用）。

**50kHz差替**: BPF定数を C=1.5nF, R1=2.65k, R2=10.61k, R3=505Ω に交換（必要GBW6MHzに緩和）。**BPF段の5素子をソケット化または2mmピッチのサブ基板化**し、振動子コネクタと合わせて差替えるだけで移行できる。タイミング経路（コンパレータ→PIO）は周波数非依存。

**オペアンプ要件**: 初段・後段とも必要GBW≥20〜25MHz（G×f0×5倍余裕）、MFBは目安GBW≥20Q²f0=25MHz、SR≥2.5V/µs。候補 OPA607(50MHz)/OPA2607。**採用前にデータシートで単電源3.3V動作・入力コモンモード範囲を要確認**（記憶ベースで要検証）。

**電源**: 3S LiPo → ヒューズ3A → スイッチ → BUCK 5V →（Pico VSYS・RS485・トリガIC）→ AP2112系LDO 3.3V（**アナログ専用のクリーン電源**。PicoオンボードSMPSの3.3Vとは分離）。

**旧版RP2040ピン割当（廃止・再設計対象）**（RP2040の機能マルチプレクスに準拠: I2C0=GP4/5, SPI1=GP10-13, UART1=GP8/9）:

| GPIO | 機能 | 接続先 |
|---|---|---|
| GP2 | PIO入力 | コンパレータ出力（音響エッジ） |
| GP3 | 割込 | BNO085 INT1 |
| GP4/GP5 | I2C0 SDA/SCL | BNO085・DS3231 |
| GP6 | PIO入力 | トリガ受信（MAX3485 RO） |
| GP8/GP9 | UART1 TX/RX | RS485データ |
| GP10-13 | SPI1 SCK/MOSI/MISO/CS | microSD |
| GP14 | GPIO | RS485 送受切替 |
| GP16 | PWM | コンパレータ閾値DAC |
| GP17 | GPIO | TLV3501 SHDN |
| GP26 | ADC0 | 包絡線振幅（1/2分圧） |

**旧版参考（廃止）：全ピン配置表・ネットリスト**  
> 以下は旧Pico/BNO085/RS485直載せ構成の参考であり、2026-07-21改訂後の回路図・GPIO割当には使用しない。:

```
=== ピン配置表 ===
J_XD (XDCR_TD04A):
    SIG        -> XD_IN
    GND        -> GND
D_PR (BAV99):
    IO         -> ST1_INP
    VCC        -> V3A
    GND        -> GND
U1 (OPA2607_A):
    OUT_A      -> ST1_OUT
    IN-_A      -> ST1_FB
    IN+_A      -> ST1_INP
    V-         -> GND
    V+         -> V3A
U1B (OPA2607_B):
    OUT_B      -> BPF_OUT
    IN-_B      -> BPF_INN
    IN+_B      -> VMID
U2 (OPA607):
    OUT        -> ST3_OUT
    IN-        -> ST3_FB
    IN+        -> BPF_OUT
    V-         -> GND
    V+         -> V3A
D_ENV (BAT54):
    A          -> DET_IN
    K          -> ENV
U3 (TLV3501):
    OUT        -> CMP_OUT
    IN-        -> VTH
    IN+        -> ENV
    V-         -> GND
    V+         -> V3A
    SHDN       -> U3_EN
PICO (RPi_Pico):
    GP2        -> CMP_OUT
    GP3        -> IMU_INT
    GP4        -> I2C_SDA
    GP5        -> I2C_SCL
    GP6        -> TRG_RO
    GP8        -> U1TX
    GP9        -> U1RX
    GP10       -> SPI_CK
    GP11       -> SPI_TX
    GP12       -> SPI_RX
    GP13       -> SPI_CS
    GP14       -> 485_SE
    GP16       -> TH_PWM
    GP17       -> U3_EN
    GP26_ADC0  -> ENV_ADC
    3V3        -> V3D
    VSYS       -> V5
    GND        -> GND
IMU (BNO085_mod):
    SDA        -> I2C_SDA
    SCL        -> I2C_SCL
    VDD        -> V3D
    GND        -> GND
    INT1       -> IMU_INT
RTC (DS3231_mod):
    SDA        -> I2C_SDA
    SCL        -> I2C_SCL
    VCC        -> V3D
    GND        -> GND
SD (microSD_SPI):
    MISO       -> SPI_RX
    MOSI       -> SPI_TX
    SCK        -> SPI_CK
    CS         -> SPI_CS
    VCC        -> V3D
    GND        -> GND
RS485 (W_TTL_RS485):
    RXD        -> U1TX
    TXD        -> U1RX
    RSE        -> 485_SE
    VCC        -> V5
    GND        -> GND
    A          -> 485D_A
    B          -> 485D_B
TRIG (MAX3485):
    RO         -> TRG_RO
    REn        -> GND
    DE         -> GND
    DI         -> GND
    VCC        -> V5
    GND        -> GND
    A          -> TRG_A
    B          -> TRG_B
BUCK (DCDC_5V):
    VIN        -> VBAT_S
    GND_IN     -> GND
    VOUT       -> V5
    GND_OUT    -> GND
REG33 (AP2112_33):
    VIN        -> V5
    GND        -> GND
    EN         -> V3D
    NC         -> NC
    VOUT       -> V3A
J_BAT (LiPo3S_XT30):
    +          -> VBAT
    -          -> GND
F1 (FUSE_3A):
    1          -> VBAT
    2          -> VBAT_F
SW1 (PWR_SW):
    1          -> VBAT_F
    2          -> VBAT_S
J_TETH (TetherConn):
    TRG_A      -> TRG_A
    TRG_B      -> TRG_B
    D_A        -> 485D_A
    D_B        -> 485D_B
    SHLD       -> GND
R_G1a (1k):
    1          -> ST1_FB
    2          -> ST1_AC
R_G1b (19k):
    1          -> ST1_FB
    2          -> ST1_OUT
R1 (3.01k):
    1          -> ST1_OUT
    2          -> N1
R2 (12.06k):
    1          -> BPF_OUT
    2          -> BPF_INN
R3 (574):
    1          -> N1
    2          -> GND
R_G3a (1k):
    1          -> ST3_FB
    2          -> ST3_AC
R_G3b (24k):
    1          -> ST3_FB
    2          -> ST3_OUT
R_BL (10k):
    1          -> DET_IN
    2          -> GND
R_ENV (10k):
    1          -> ENV
    2          -> GND
R_TH (10k):
    1          -> TH_PWM
    2          -> VTH
R_HYS (1M):
    1          -> ENV
    2          -> CMP_OUT
R_DV1 (10k):
    1          -> ENV
    2          -> ENV_ADC
R_DV2 (10k):
    1          -> ENV_ADC
    2          -> GND
R_B1 (100k):
    1          -> V3A
    2          -> VMID
R_B2 (100k):
    1          -> VMID
    2          -> GND
R_B3 (100k):
    1          -> VMID
    2          -> ST1_INP
R_TRM (120):
    1          -> TRG_A
    2          -> TRG_B
C_AC1 (100n):
    1          -> XD_IN
    2          -> ST1_INP
C_AC2 (1u):
    1          -> ST1_AC
    2          -> GND
C_AC3 (1u):
    1          -> ST3_AC
    2          -> GND
C_AC4 (100n):
    1          -> ST3_OUT
    2          -> DET_IN
C_BPF1 (330p):
    1          -> N1
    2          -> BPF_OUT
C_BPF2 (330p):
    1          -> N1
    2          -> BPF_INN
C_ENV (1n5):
    1          -> ENV
    2          -> GND
C_TH (100n):
    1          -> VTH
    2          -> GND
C_VM (10u):
    1          -> VMID
    2          -> GND
C_D1 (100n):
    1          -> V3A
    2          -> GND
C_D2 (100n):
    1          -> V3A
    2          -> GND
C_D3 (100n):
    1          -> V3A
    2          -> GND
C_D4 (100n):
    1          -> V3D
    2          -> GND
C_D5 (100n):
    1          -> V5
    2          -> GND
C_D6 (100n):
    1          -> V3D
    2          -> GND
C_BK1 (22u):
    1          -> VBAT_S
    2          -> GND
C_BK2 (22u):
    1          -> V5
    2          -> GND
C_AN (10u):
    1          -> V3A
    2          -> GND

=== ネット接続表 ===
485D_A: J_TETH.D_A, RS485.A
485D_B: J_TETH.D_B, RS485.B
485_SE: PICO.GP14, RS485.RSE
BPF_INN: C_BPF2.2, R2.2, U1B.IN-_B
BPF_OUT: C_BPF1.2, R2.1, U1B.OUT_B, U2.IN+
CMP_OUT: PICO.GP2, R_HYS.2, U3.OUT
DET_IN: C_AC4.2, D_ENV.A, R_BL.1
ENV: C_ENV.1, D_ENV.K, R_DV1.1, R_ENV.1, R_HYS.1, U3.IN+
ENV_ADC: PICO.GP26_ADC0, R_DV1.2, R_DV2.1
GND [GND]: BUCK.GND_IN, BUCK.GND_OUT, C_AC2.2, C_AC3.2, C_AN.2, C_BK1.2, C_BK2.2, C_D1.2, C_D2.2, C_D3.2, C_D4.2, C_D5.2, C_D6.2, C_ENV.2, C_TH.2, C_VM.2, D_PR.GND, IMU.GND, J_BAT.-, J_TETH.SHLD, J_XD.GND, PICO.GND, R3.2, REG33.GND, RS485.GND, RTC.GND, R_B2.2, R_BL.2, R_DV2.2, R_ENV.2, SD.GND, TRIG.DE, TRIG.DI, TRIG.GND, TRIG.REn, U1.V-, U2.V-, U3.V-
I2C_SCL: IMU.SCL, PICO.GP5, RTC.SCL
I2C_SDA: IMU.SDA, PICO.GP4, RTC.SDA
IMU_INT: IMU.INT1, PICO.GP3
N1: C_BPF1.1, C_BPF2.1, R1.2, R3.1
SPI_CK: PICO.GP10, SD.SCK
SPI_CS: PICO.GP13, SD.CS
SPI_RX: PICO.GP12, SD.MISO
SPI_TX: PICO.GP11, SD.MOSI
ST1_AC: C_AC2.1, R_G1a.2
ST1_FB: R_G1a.1, R_G1b.1, U1.IN-_A
ST1_INP: C_AC1.2, D_PR.IO, R_B3.2, U1.IN+_A
ST1_OUT: R1.1, R_G1b.2, U1.OUT_A
ST3_AC: C_AC3.1, R_G3a.2
ST3_FB: R_G3a.1, R_G3b.1, U2.IN-
ST3_OUT: C_AC4.1, R_G3b.2, U2.OUT
TH_PWM: PICO.GP16, R_TH.1
TRG_A: J_TETH.TRG_A, R_TRM.1, TRIG.A
TRG_B: J_TETH.TRG_B, R_TRM.2, TRIG.B
TRG_RO: PICO.GP6, TRIG.RO
U1RX: PICO.GP9, RS485.TXD
U1TX: PICO.GP8, RS485.RXD
U3_EN: PICO.GP17, U3.SHDN
V3A [PWR]: C_AN.1, C_D1.1, C_D2.1, C_D3.1, D_PR.VCC, REG33.VOUT, R_B1.1, U1.V+, U2.V+, U3.V+
V3D [PWR]: C_D4.1, C_D6.1, IMU.VDD, PICO.3V3, REG33.EN, RTC.VCC, SD.VCC
V5 [PWR]: BUCK.VOUT, C_BK2.1, C_D5.1, PICO.VSYS, REG33.VIN, RS485.VCC, TRIG.VCC
VBAT [PWR]: F1.1, J_BAT.+
VBAT_F [PWR]: F1.2, SW1.1
VBAT_S [PWR]: BUCK.VIN, C_BK1.1, SW1.2
VMID: C_VM.1, R_B1.2, R_B2.1, R_B3.1, U1B.IN+_B
VTH: C_TH.1, R_TH.2, U3.IN-
XD_IN: C_AC1.1, J_XD.SIG
```

## 2.4 子機電源・ライト基板（C-PWR）

**入力**：3S LiPo。XT30等のロック可能なコネクタを使用する。

**保護・監視**：
- 3Aヒューズ
- PチャネルMOSFETまたは理想ダイオード方式の逆接保護
- 入力TVS
- INA226＋シャント抵抗
- 低電圧警告。セル当たり3.5Vを警告開始の目安とし、最終値は電池仕様に合わせる

**出力**：
- 5Vデジタル：Pico、RS485、microSD
- 3.3Vデジタル：BNO085、RTC等
- 3.3Vアナログ：C-RX専用LDO
- LED定電流出力：PWM調光、過熱時デューティ制限

スイッチング電源、ライト配線、インダクタはC-RX入力から物理的に離す。アナログ3.3Vは5Vから低ノイズLDOで生成する。

## 2.5 親機メイン基板（P-MAIN）

**役割**：SPRESENSE用キャリア、ログ、GNSS、姿勢・方位、外部センサ、RS485、P-TX制御。

**搭載・接続**：
- SPRESENSEメインボード用コネクタ
- NEO-M9N：UART＋PPS
- SPRESENSE Multi-IMU Add-on Board
- SPRESENSE Multi-IMU Add-on Board：親機高精度6軸IMU。100Hz以上で取得
- LIS3MDL：絶対方位用リモート磁気センサ基板用I2Cコネクタ
- DS3231
- INA226
- MS5837-30BA/Bar30用I2Cコネクタ
- Celsius Fast-Response ±0.1°C Temperature Sensor R2用1-Wireコネクタ
- microSD表面実装コネクタ Molex 104031-0811
- RS485データ、トリガ送信
- P-TX向けPWM_A/B、TX_EN、TRG_TX
- USB/UARTデバッグ端子

磁気センサはP-MAINへ直載せせず、ケーブル接続の小型リモート基板とする。TXトランス、降圧インダクタ、大電流配線から離して配置し、実機で磁場影響を評価する。

## 2.6 親機TX基板（P-TX）

**構成**: SPRESENSE GPIO相補PWMペア（200kHzバースト、例10〜20サイクル） → MIC4427デュアルドライバ → **センタタップ昇圧トランス1:5（CT=12V）プッシュプル** → 直列同調L1（**L=1/(ω²C0)、C0はTD04A実測後に確定**。例C0=2nF→約317µH） → TD04A。一次側にTVS（SMBJ33A）とバルク100µF。**同一GPIOタイミングでトリガ送信**: SPRESENSE TRG_TX → MAX3485（DE=H固定・常時送信）→ テザーTRGペア（120Ω終端は子機側・親機側の両端）。

音響バーストの物理発射時刻とトリガ電気パルスは同一クロックエッジから生成するので、TX側の系統遅延（ドライバ＋トランス立上り）も較正1回で吸収される。**初期実験は昇圧なし12V直駆（フルブリッジまたはドライバ直結）で開始してよい**（1.4節）。

**旧版参考（廃止）：全ピン配置表・ネットリスト**  
> 以下は旧Pico/BNO085/RS485直載せ構成の参考であり、2026-07-21改訂後の回路図・GPIO割当には使用しない。:

```
=== ピン配置表 ===
J_MCU (From_SPRESENSE):
    PWM_A      -> PWMA
    PWM_B      -> PWMB
    TRG_TX     -> TRG_DI
    GND        -> GND
    V3V3       -> V3T
U1 (MIC4427):
    INA        -> INA
    INB        -> INB
    OUTA       -> DRV_A
    OUTB       -> DRV_B
    VS         -> V12
    GND        -> GND
T1 (XFMR_CT_1to5):
    P1         -> DRV_A
    CT         -> V12
    P2         -> DRV_B
    S1         -> SEC_HI
    S2         -> GND
L1 (L_tune_meas):
    1          -> SEC_HI
    2          -> XD_DRV
J_XD (XDCR_TD04A):
    SIG        -> XD_SIG
    GND        -> GND
TRIG (MAX3485):
    RO         -> NC
    REn        -> GND
    DE         -> V3T
    DI         -> TRG_DI
    VCC        -> V3T
    GND        -> GND
    A          -> TRG_A
    B          -> TRG_B
J_PWR (PWR_12V):
    +          -> V12
    -          -> GND
J_TETH (TetherConn):
    TRG_A      -> TRG_A
    TRG_B      -> TRG_B
    SHLD       -> GND
R_INA (100):
    1          -> PWMA
    2          -> INA
R_INB (100):
    1          -> PWMB
    2          -> INB
R_DMP (10):
    1          -> XD_DRV
    2          -> XD_SIG
R_TRM (120):
    1          -> TRG_A
    2          -> TRG_B
C_VS1 (100n):
    1          -> V12
    2          -> GND
C_VS2 (10u):
    1          -> V12
    2          -> GND
C_BULK (100u):
    1          -> V12
    2          -> GND
C_T1 (100n):
    1          -> XD_SIG
    2          -> GND
C_TR (100n):
    1          -> V3T
    2          -> GND
D_SN1 (SMBJ33A):
    A          -> GND
    K          -> V12

=== ネット接続表 ===
DRV_A: T1.P1, U1.OUTA
DRV_B: T1.P2, U1.OUTB
GND [GND]: C_BULK.2, C_T1.2, C_TR.2, C_VS1.2, C_VS2.2, D_SN1.A, J_MCU.GND, J_PWR.-, J_TETH.SHLD, J_XD.GND, T1.S2, TRIG.GND, TRIG.REn, U1.GND
INA: R_INA.2, U1.INA
INB: R_INB.2, U1.INB
PWMA: J_MCU.PWM_A, R_INA.1
PWMB: J_MCU.PWM_B, R_INB.1
SEC_HI: L1.1, T1.S1
TRG_A: J_TETH.TRG_A, R_TRM.1, TRIG.A
TRG_B: J_TETH.TRG_B, R_TRM.2, TRIG.B
TRG_DI: J_MCU.TRG_TX, TRIG.DI
V12 [PWR]: C_BULK.1, C_VS1.1, C_VS2.1, D_SN1.K, J_PWR.+, T1.CT, U1.VS
V3T [PWR]: C_TR.1, J_MCU.V3V3, TRIG.DE, TRIG.VCC
XD_DRV: L1.2, R_DMP.1
XD_SIG: C_T1.1, J_XD.SIG, R_DMP.2
```

## 2.7 テザー結線表（30m・信号のみ）

| ペア/線 | 用途 | 親機側 | 子機側 | 備考 |
|---|---|---|---|---|
| ペア1 A/B | トリガ（差動・単方向） | MAX3485 DE=H常時送信 | MAX3485 受信固定・120Ω終端 | 遅延350ns=0.53mm系統 |
| ペア2 A/B | RS485データ（半二重） | Waveshareモジュール | Waveshareモジュール | 状態・コマンド・時刻照会 |
| シールド | コモン | 筐体GNDへ1点接地 | 子機GNDへ接続 | 接地ループを作らない（1.5節） |

## 2.8 親機電源基板・システム間配線（箱内・ボード間）

`P-PWR`は3S LiPo入力を受け、ヒューズ、逆接保護、入力TVS、INA226を通した後に次の系統へ分岐する。

1. `VBAT_TX`：P-TXへ供給。大容量電解＋セラミックをP-TX側にも配置する。
2. `5V_LOGIC`：SPRESENSE、GNSS、RS485へ供給。
3. `5V_CAMERA`：Pi Zero 2 W専用。ロジック系とは別の降圧コンバータを用いる。
4. `3V3_SENSOR`：センサ用低ノイズ電源。

SPRESENSEを中心に、GNSSはUART＋PPS、RTC・INA226・外部圧力センサ・磁気センサはI2C、Celsius Fast-Response Temperature Sensor R2は1-Wire、P-TXはPWM_A/B＋TRG_TX＋TX_ENで接続する。Pi Zero 2 Wへは5V/GNDのみ供給し、撮影同期は光学マーカーを使用する。

**主電源にモバイルバッテリーを採用しない。** USB出力の自動停止やPD交渉、TX瞬間負荷、ノイズ評価を避けるためである。

---

# 第3部　機体設計

## 3.1 親機（水上ユニット）

> **2026-09-04 改訂 (機体設計の下流判断)**: 浮子はリング浮子 4 分割ではなく**市販円筒フェンダー ×2**
> をデッキ (`parent_deck`) に紐で固定する双胴構成に変更。**リジッドマストは廃止**し、TD04A とカメラは
> デッキ下面のハードポイント (HP40) に直付け。カメラは Pi Zero + GS カメラのポッドではなく
> **DJI Osmo Action 6 + 純正防水ケース** (外付け・独立電源)。予備浮力はフェンダー実測後に再計算
> (仮 Ø100×300 では 14 % で不足、Ø120×400 級で 55 %)。以下の本文は旧構成の記述。
> 詳細は `mechanical/assemblies/parent_assembly/parent_assembly.md`。

**全体**: リング浮子（外径30cm・断面8cm、3Dプリント分割＋発泡充填）の中心に防水ボックスを載せ、ボックス底から**リジッドマスト（3Dプリント＋アルミパイプφ20補強）**を水面下50cmまで降ろす。マスト下端に**TD04A（下向き〜前傾20°）とカメラポッド（下向き）**を固定。GPSアンテナはボックス天面（最頂部・金属から離す）。

**浮力・復原性（計算済み）**: 総質量約3.0kg（箱＋電池＋基板1.2、フレーム0.6、ポッド0.5、TD04A＋ケーブル0.3、バラスト0.4）→必要排水量3.0L。リング浮子の全没体積4.74L＞4.5L（予備浮力50%）で成立。**重量物（バラスト0.4kg）をマスト下端に置き重心を水面下へ**下げ、振り子的な復原性を確保する（メタセンタ高は進水時に傾斜試験で確認）。

**防水ボックス**: 配置最適化の結果、**マウントプレート175×180mm・部品高31mm**（違反ゼロ、`parent_layout_preview.png`参照）。したがって**内寸目安 190×190×80mm以上**のタカチ防水ボックス（BCAP/BCASクラス、IP65以上）を選定する（該当サイズの型番は購入時にカタログ照合）。配置の要点: LiPoは西縁（重量物を端に寄せ配線から隔離）、ケーブルグランドは南縁2個（マストへ: TD04A同軸・ポッド電源・テザー）＋北縁1個（GPSアンテナ）、TX基板はグランド直近、SPRESENSEスタックは中央でGPS/RTC/TX/RS485へのハブ（総配線長737mmで最適化済み）。

**カメラポッド**: 3Dプリント円筒（内径φ60×長さ90mm目安）に Pi Zero 2W＋GSカメラ＋4mmレンズ＋520nm BPF を同軸実装。前面はアクリルフラットポートt4mm＋Oリング（1.6節）。CSIケーブルは短距離で完結し、外部とは電源2線のみ（ペネトレーターまたはグランド1個）。**レンズ光軸とTD04A音軸を平行に組み、相対位置をフレーム座標で図面化**しておく（ボアサイト較正の初期値になる）。

## 3.2 子機（水中ユニット）

**耐圧チューブ内**（BlueRobotics 3インチ想定・**内径/内長は実測必須**）: パッキング最適化の結果、**必要内径70mm・内長264mm**（違反ゼロ、`child_layout3d_preview.png`参照）。軸方向の並びは 前端キャップ（ペネトレーター: テザー・XDCRケーブル・ライト電源）→ 配線余裕22mm → **C-RX基板＋C-MAIN＋C-PWRをカードガイドで縦挿し** → **LiPo3S 5000mAh 軸沿い（43×35断面×135mm、面ファスナー＋発泡ウレタンで保持）** → 後端配線余裕。断面対角は基板60.4mm・電池55.4mmでID76.2mmに対し余裕あり。**電池は最重量物なので管の下側（フレーム取付時に下になる向き）へ寄せて重心を下げる。**

**外フレーム**: 3Dプリントのトラス状フレームに、中央=耐圧チューブ（クランプ2点）、左右=**Osmo Action 6 ×2を基線30cmで前向き下20°**（1.7節。取付穴を25/30/35cmに複数用意）、中央下=水中ライト（前向き上向き45°可変、親機を照らす）、下面レール=おもり（自宅在庫、位置調整式）。RX振動子TD04Aは**上向き**（親機TXと対面）でフレーム上面に。フレームは左右対称・ケーブルは中央束ねでOsmoの視野に入れない。

**質量バランス**: 水中で僅かに負浮力（沈む側）〜中性になるようおもりで調整。チューブ浮力（φ76×300mmで約1.4L≈1.4kg浮力）に対し、Osmo2台・電池・フレームでほぼ相殺され、残差をおもりレールで追い込む。

## 3.3 3Dプリント部品一覧（親機・子機）

| 部品 | 材料 | 要点 |
|---|---|---|
| 親機リング浮子（4分割） | PETG＋発泡充填 | 分割嵌合＋ボルト、表面はエポキシ塗布 |
| 親機マスト継手・ポッド筐体 | ASA/PETG | ポッドは内面エポキシコート＋気密試験（1.6節） |
| 親機ボックス内プレート | PETG t3 | 175×180、各モジュールのボス立て |
| 子機カードガイド・電池ホルダ | PETG | チューブ内径に合わせ実測後印刷 |
| 子機フレーム | PETG/ASA | Osmoマウント基線可変、おもりレール |

寸法確定後、各部品のパラメトリックOpenSCAD（.scad）を順次作成する（本書の寸法が入力になる）。

---

# 第4部　較正・検証手順（実装後に必ず実施）

1. **電気**: RX基板単体でファンクションジェネレータ200kHzバースト入力→利得・BPF特性・コンパレータ動作を実測（SPICEとの突合）。TXはダミー負荷（実測C0相当のC＋R）で波形確認後にTD04A接続。
2. **TD04A実測**: LCRでC0・共振点→L1確定（1.3節）。
3. **音響**: 水槽/プールで既知距離3点以上→距離較正直線（系統オフセット＝トリガ遅延＋検波遅延を吸収）＋振幅-ウォーク補正カーブ取得（1.2節）。温度を同時記録し音速補正を適用（1.8節）。
4. **光学**: ポッド完成後、水中チェッカーボードで内部/歪みパラメータ較正→光点重心のサブピクセル精度を既知移動で確認。
5. **ボアサイト**: 陸上治具でカメラ光軸・音軸・GPSアンテナ位相中心・IMU軸の相対姿勢を確定、以後フレーム剛性を信じる（変形が疑われたら再較正）。
6. **磁気較正**: 磁気センサ追加後、親機を全周回転させハード/ソフトアイアン係数を取得（1.1節）。
7. **システム**: プールで親機既知移動→子機相対位置の再現性評価（仕様メモの評価方法どおり）。

---


## 2.9 IMU 100Hz安定取得設計

### 2.9.1 親機：SPRESENSE Multi-IMU Add-on Board

親機のIMUはSPRESENSE Multi-IMU Add-on Boardを使用する。親機では波揺れ補正が重要なため、100Hzは保存周期の最低値とし、取得処理は専用スレッドまたはサブコアへ分離する。

**処理構成**

1. IMUドライバがセンサデータを連続取得する。
2. 取得直後に高分解能タイムスタンプを付与する。
3. 固定長レコードをRAMリングバッファへ投入する。
4. MainCoreは一定件数ごとにSDへブロック書込みする。
5. GNSS PPS、TXイベント、カメラマーカーは同じ時刻軸へ記録する。

**禁止事項**

- IMU取得ループ内でCSV文字列化しない。
- IMU取得ループ内で`flush()`しない。
- USBシリアル出力を常時行わない。
- SDカードの書込み待ちをIMU取得処理へ伝播させない。

### 2.9.2 子機：BNO085

子機のBNO085はI2Cではなく**SPI接続を標準**とする。理由は、100Hz連続取得時にバス占有時間とホスト側待ち時間を抑え、INT信号に基づく確定的な読み出しを行うためである。

**BNO085信号**

| 信号 | RP2040接続 | 用途 |
|---|---|---|
| SCK | SPI | クロック |
| MOSI | SPI | ホスト→BNO085 |
| MISO | SPI | BNO085→ホスト |
| CS | GPIO/SPI | チップ選択 |
| INT | 専用GPIO割込み | データ準備通知 |
| RESET | GPIO | 異常時再起動 |
| BOOT/PS | 固定 | SPIモード選択 |
| 3V3/GND | C-PWR | センサ電源 |

**取得レポート**

- 基本ログ：Rotation Vector、100Hz。
- デバッグ時：加速度、角速度、磁気、生ステータスを追加可能。
- 同時レポートを増やす場合はSPI転送量とRP2040処理時間を実測し、100Hz条件を再確認する。
- 磁気影響が大きい場合はGame Rotation Vectorも併記し、方位誤差と短期姿勢安定性を比較する。

**ファームウェア構成**

- GPIO割込み：タイムスタンプ取得、`imu_pending`通知のみ。
- IMU高優先度タスク：SHTPパケット読出し、シーケンス確認、固定長レコード化。
- ロガータスク：リングバッファから20〜100サンプルをまとめてmicroSDへ書込み。
- 音響タスク：PIOで独立処理し、IMU処理と競合させない。
- ウォッチドッグ：INTが50ms以上来ない場合に状態確認、復旧不能ならRESETしてイベント記録。

**バッファ**

- 最低256サンプル、推奨512サンプル。
- 100Hz時に2.56〜5.12秒分のSD書込み停止を吸収できる。
- バッファ使用率80%超で警告フラグを立て、低優先度処理を抑制する。

**記録形式**

初期保存はCSVではなく、次の固定長バイナリを推奨する。

```c
struct ImuRecord {
    uint64_t host_time_us;
    uint32_t sequence;
    float quat_i;
    float quat_j;
    float quat_k;
    float quat_real;
    float accuracy_rad;
    uint8_t calibration_status;
    uint8_t flags;
};
```

実験終了後にPC側でCSVへ変換する。これにより文字列変換と不定長書込みによるジッタを避ける。

### 2.9.3 タイミング評価

サンプル間隔 `dt_us` を全サンプルについて保存または集計し、次を算出する。

- 平均周波数
- `dt_us`の中央値
- 標準偏差
- 95/99パーセンタイル
- 最大値
- シーケンス欠損数
- リングバッファオーバーフロー数
- BNO085リセット回数

100Hzを名目上設定できるだけでは合格とせず、音響・SD・RS485を同時動作させた状態で評価する。


---

# 第5部　本設計で新たに発生したBOM追加・変更

| 区分 | 部品・機能 | 数量目安 | 備考 |
|---|---|---:|---|
| 基板 | P-MAIN / P-TX / P-PWR | 各1 | 親機3基板 |
| 基板 | C-MAIN / C-RX / C-PWR | 各1 | 子機3基板 |
| 記録 | Molex 104031-0811 | 2 | 親機・子機microSD |
| センサ | MS5837-30BAまたはBar30相当 | 2 | 親機水温深度・子機深度 |
| センサ | Celsius Fast-Response ±0.1°C Temperature Sensor R2 | 1 | 音速補正用 |
| センサ | LIS3MDL | 1 | 親機リモート方位 |
| 監視 | INA226＋シャント | 2 | 親機・子機電源監視 |
| 安全 | 漏水電極・入力保護 | 1式 | 子機 |
| 電源 | 3S LiPo 2200〜4000mAh | 1 | 親機 |
| 電源 | 3S LiPo 4000〜5000mAh | 1 | 子機 |
| 電源 | バランス充電器・LiPoバッグ | 1式 | 機体外充電 |
| 電源 | ヒューズ、逆接MOSFET、TVS | 2式 | P-PWR/C-PWR |

基板枚数は増えるが、TX/RX改版時にメイン基板と電源基板を再発注せずに済むため、総試作費とデバッグ時間を抑えられる。

---

# 付録　検証に使用した計算・ファイル

`calc1.py`（全設計計算・assert付き）、`net_rx.py`/`net_tx.py`（ERC合格ネットリスト）、`mfb.cir`（SPICE AC解析）、`parent_layout/`・`child_layout/`（配置最適化結果＋プレビューPNG）。いずれも `mechanical/spec/` にある。数値を変えて再検討する場合はこれらを再実行する。

---

# 参考データシート

- TE Connectivity, MS5837-30BA Water-Resistant Pressure & Temperature Sensor.
- Bosch Sensortec, BNO085 Datasheet.
- STMicroelectronics, LIS3MDL Datasheet.
- Texas Instruments, INA226 Datasheet.
- Analog Devices, DS3231 Datasheet.
- Analog Devices, Celsius Fast-Response Temperature Sensor R2 Datasheet.
- Molex, 104031-0811 microSD Memory Card Connector.


## コネクタ方針（確定）

- **センサ類・低電流信号**：JST XHシリーズを使用する。
  - I²C、SPI補助信号、GPIO、RTC、圧力・温度センサ、漏水検知、電源監視など。
  - 2.50mmピッチ。
  - センサごとに極数を固定し、シルクへ信号名と1番ピンを明記する。
  - I²C系は `3V3 / GND / SDA / SCL` の4ピンを基本とする。
  - SPI系は信号数が多いため、必要に応じて6〜8ピンとする。
  - 誤接続防止のため、用途ごとに極数またはキー配置を変える。

- **電源系**：XT30コネクタを使用する。
  - LiPo入力、P-PWR/C-PWRから大電流負荷への給電、TX基板、ライト電源など。
  - 極性は全基板で統一し、基板シルクへ `+` / `-` を明記する。
  - 低電流の3.3V/5Vセンサ給電にはXT30を使わず、XHコネクタを使用する。
  - バッテリ入力にはヒューズ、逆接保護、TVSをXT30直後に配置する。

- **RP2040実装方針**：
  - RP2040の表面実装は行わない。
  - 親機・子機ともRaspberry Pi Pico 2 Wモジュールを使用する。
  - 初期・最終版とも交換可能性を優先し、Picoはピンヘッダまたはキャステレーションはんだ付けで搭載する。