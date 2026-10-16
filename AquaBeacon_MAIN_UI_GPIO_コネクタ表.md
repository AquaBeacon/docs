# AquaBeacon メイン/UI基板 GPIO割当・コネクタ表（確定）

> 改訂日: 2026-07-21（**2026-07-23 UI統合改訂** / **2026-08-03 レビュー反映: microSD を TF-01A へ、
> P-MAIN の予備ピン削除(J_TETH・J_SPR を XH3 化)、TH_PWM/TX_PWM のケーブル前段抵抗、SD_CS プルアップ**）
> / 対象: `C-MAIN`(子機メイン) / `P-MAIN`(親機メイン)
> 上位仕様は `AquaBeacon_確定仕様メモ.md`(同じフォルダ)の統合確定事項。
> 本表は「発注前に残る必須作業 1(GPIO割当) / 2(コネクタ表)」を確定するもの。
>
> **⚠ 2026-07-23: UI基板を廃止し、スイッチ(3ボタン)・バックライトMOSFET・リセットRCをメイン基板へ統合した。**
> **以下の表で「UI基板」とある機能はすべてメイン基板オンボード。基板間コネクタ `J_UI`(8P) は廃止し、
> LCDのみを外出しする `J_LCD`(9P XH: GND/V3D/SCK/MOSI/CS/DC/RST/LED_A/LED_K) に置き換えた。**
> 実装: `hardware/pcb/build_child_main.py`(C-MAIN v2.3) / `hardware/pcb/build_parent_main.py`(P-MAIN v4.0)。受動部品はSMD化済み。

## 設計判断（GPIO収容）

Raspberry Pi Pico 2 W の実質利用可能GPIOは **26本**（GP0–GP22, GP26–GP28）。
新仕様の全必須機能を直結すると 30本超になるため、以下で **エキスパンダ無し・Pico直結26本**に収める。

- **予備ポート(I2C/UART/GPIO/ADC)は削除**（ユーザ指示: 予備はGPIOが余った時のみ）。
- **LED_PWR は電源直結**（緑=通電表示、常時点灯）→ GPIO消費せず。LED_STATUS のみGPIO。
- **LCD_RST は UI基板上のRC電源投入リセット**（GPIO消費せず）。
- **3ボタンは UI基板上のADC抵抗ラダーで1本化**（`BTN_ADC` = ADC1本）。アクティブLow個別ではなく
  電圧識別方式。UP/ENTER/DOWN + 無押下を1 ADCで判別。
- ~~microSDバス(SPI1)は **LCDと共有**~~ → **2026-08-01 解消**。LCDを I²C 品（NHD-C0216CiZ）へ変更したので
  **SPI1 は microSD 専用**になり、`LCD_CS`/`LCD_DC` の2本も解放された（**2026-08-03 時点で
  P-MAIN=GP14/GP19・C-MAIN=GP7/GP9 とも反映済み**）。LCDは I2C0(GP4/GP5) に相乗り（アドレス 0x3E/7bit）。
- **BNO085 は専用SPI0**（100Hz IMU・ジッタ敏感なのでSD/LCDと分離）。
- **RS485通信(2026-07-23確定)**: **Waveshare TTL-RS485(C) SS-9778 ×1 のみ**を基板へキャステレーション直付け
  （**実物7パッド**: TTL側 `GND/RXD/TXD/VCC`・RS485側 `PE/B/A`。自動方向制御・ガルバニック絶縁・半二重・双方向）。
  カスタムFP=`pcb/footprints/AquaBeacon.pretty/Waveshare_TTL_RS485_C`。
  **音響同期のハードトリガは廃止**（ユーザ判断。旧「2個目のWaveshare/ADM2587E」は削除、Pico GP3解放。
  時刻同期はデータバス上のソフト対応前提）。テザーは**4芯 JST XH(B4B-XH-A)** = `485D_A/B`＋`485D_PE`＋予備1。
  （旧5極端子台+`SHLD`網は廃止）。120Ω終端 `R_TRMD1`(既定DNP)。
- **BNO085は Adafruit 4754**（1×6が2列, 列間17.78mm）。SPIモードは **PS1=P1 / PS0=P0 を共に High**（CEVA `1000-3927` §1.2.4 note5「Both pins must be high from before reset until after the first assertion of H_INTN」／Adafruit公式の配線例も P0・P1 とも 3V）。**⚠ ただし同 note5 は「Pin 6(PS0/WAKE) must be connected to a GPIO」**とも書いており、現状は Pico の26本に空きが無いため V3D 固定にしている（ホスト起点の書込みは BNO 側 INT アサートに相乗りする前提＝Adafruit_BNO08x ライブラリと同じ方式）。WAKE を使うなら GPIO を1本空ける必要がある（`SD_CD` が最も冗長）。データシート実体＝`pcb/datasheets/BNO085_CEVA_datasheet.pdf`。

## C-MAIN（子機メイン）Pico 2 W GPIO割当

| GP | 機能 | ネット | 接続先 |
|---|---|---|---|
| GP0  | UART0 TX | `485D_TXD` | Waveshare DATA RXD |
| GP1  | UART0 RX | `485D_RXD` | Waveshare DATA TXD |
| GP2  | PIO入力 | `CMP_OUT` | C-RX コンパレータ出力（音響エッジ） |
| GP3  | GPIO in | `INA_AL` | C-PWR INA226 ALERT（OC。C-MAIN 側 R_AL 10k でプルアップ）**2026-07-28追加** |
| GP4  | I2C0 SDA | `I2C_SDA` | DS3231 / MS5837 / INA226(C-PWR) / Celsius / LCD(0x3E) |
| GP5  | I2C0 SCL | `I2C_SCL` | 同上 |
| GP6  | **PWM3A out** | `TH_PWM` | C-RX 比較器しきい値（PWM→R15/C8 で平滑→VTH）**2026-07-28 `RX_EN` から変更**。**2026-08-03 (C-MAIN v4.3): ケーブル前段に `R_THP` 1k + `C_THP` 100n を追加し、コネクタ側のネット名は `TH_PWM_F` になった**（J_RX1 pin3 は `TH_PWM_F`）。RX 側 VTH は LM393 の高インピーダンス入力なので**DC 誤差ゼロ＝duty↔VTH の関係もファームも不変** |
| GP7  | - | (予備・未実装) | 旧LCD_CS。v4.1でI²C LCD化し解放 |
| GP8  | **PWM4A out** | `LIGHT_PWM` | C-PWR ライト定電流調光 **2026-07-31 GP7 から変更**（下記PWMスライス注） |
| GP9  | - | (予備・未実装) | 旧LCD_DC。v4.1で解放 |
| GP10 | SPI1 SCK | `SPI_SCK` | microSD専用クロック |
| GP11 | SPI1 TX  | `SPI_MOSI`| microSD専用MOSI |
| GP12 | SPI1 RX  | `SPI_MISO`| microSD MISO |
| GP13 | GPIO out | `SD_CS`   | microSD CS |
| GP14 | GPIO out | `LED_STATUS` | 状態LED（**赤 0805 / LCSC C84256**。2026-08-03 に黄→赤: JLCPCB の 0805 LED の Basic は赤と緑だけで、黄/橙は Extended になり装着費が発生するため） |
| GP15 | GPIO in  | `SD_CD`   | microSD カード検出 |
| GP16 | SPI0 RX  | `BNO_MISO`| BNO085 SDO |
| GP17 | GPIO out | `BNO_CS`  | BNO085 CS |
| GP18 | SPI0 SCK | `BNO_SCK` | BNO085 SCK |
| GP19 | SPI0 TX  | `BNO_MOSI`| BNO085 SDI |
| GP20 | GPIO in  | `BNO_INT` | BNO085 INT（データレディ割込） |
| GP21 | GPIO out | `BNO_RST` | BNO085 RESET |
| GP22 | GPIO in  | `LEAK`    | 漏水電極（プルアップ+割込） |
| GP26 | ADC0 | `ENV_ADC` | C-RX 包絡線振幅 |
| GP27 | ADC1 | `BTN_ADC` | UI基板 3ボタン抵抗ラダー |
| GP28 | PWM out | `BL_PWM` | UI基板 バックライトMOSFETゲート |

LED_PWR: V3D→R→GND（常時点灯、GPIO非消費）。v4.1でGP7/GP9の2本が予備になった。

> **⚠ PWMスライス制約（2026-07-31 追加。RP2350 は `slice = (GP>>1) % 12` / `ch = GP&1`）**
> 同一スライスの A/B チャネルは **カウンタ・wrap・分周を共有する＝周波数を独立に設定できない**。
> 旧割当は `TH_PWM=GP6`(slice3A) と `LIGHT_PWM=GP7`(slice3B) が同一スライスで、
> TH_PWM が 125kHz 必須（下記）なのでライト調光まで 125kHz に固定されてしまっていた。
> C-PWR のライト側は TO-220 の Q2 を `R_GL=100Ω` で叩く構成なのでゲート遷移が周期の1割を占め、
> スイッチング損と低duty側の非線形（および XH ケーブルからの放射）が問題になる。
> → **`LIGHT_PWM` を GP8(slice4A) へ移動**（GP9はv4.1でLCD_DC廃止後も予備のまま）。
> 現在使用中の PWM は **TH_PWM=slice3A / LIGHT_PWM=slice4A / BL_PWM=GP28=slice2A** の3スライスで、
> すべて独立に周波数設定できる。
>
> **ファーム要求 (`TH_PWM`, 2026-07-28)**: RX 側の平滑 RC が τ=1ms なので **PWM は 100kHz 以上**
> （125kHz 推奨。10kHz だと残留リップル 82mVp-p で比較器ヒステリシス 22mV を超えて誤発火）。
> しきい値の実用 duty は **0〜約26%**（VTH = 3.3V×duty、ENV の上限が約0.85V のため）なので
> **wrap ≥ 1000** にして分解能を確保する。詳細は `pcb/RX_improved_mini/基板仕様書.md` §5。

## P-MAIN（親機メイン）Pico 2 W GPIO割当

BNO085が無い分、TX制御・GNSS・SPRESENSE連携に割当。

| GP | 機能 | ネット | 接続先 |
|---|---|---|---|
| GP0  | UART0 TX | `485D_TXD` | Waveshare DATA RXD |
| GP1  | UART0 RX | `485D_RXD` | Waveshare DATA TXD |
| GP2  | GPIO out | `LED_STATUS` | 状態LED |
| GP3  | GPIO in | `INA_AL` | P-PWR INA226 ALERT（OC。P-MAIN 側 R_AL 10k でプルアップ）**2026-07-31追加。C-MAIN と同一** |
| GP4  | I2C0 SDA | `I2C_SDA` | DS3231/MS5837/INA226/Celsius温度/LIS3MDL/**LCD(0x3E)** |
| GP5  | I2C0 SCL | `I2C_SCL` | 同上 |
| GP6  | PIO入力 | `GNSS_PPS` | NEO-M9N PPS（SPRESENSEへも分配） |
| GP7  | GPIO out | `EVENT_MARK` | SPRESENSE イベントマーカー |
| GP8  | UART1 TX | `GNSS_TX` | NEO-M9N RX |
| GP9  | UART1 RX | `GNSS_RX` | NEO-M9N TX |
| GP10 | SPI1 SCK | `SPI_SCK` | **microSD 専用**（v5.3でLCD共有を解消） |
| GP11 | SPI1 TX  | `SPI_MOSI`| **microSD 専用**（同上） |
| GP12 | SPI1 RX  | `SPI_MISO`| microSD MISO |
| GP13 | GPIO out | `SD_CS`   | microSD CS |
| GP14 | -        | (予備・未実装) | 旧 `LCD_CS`。**2026-08-01 v5.3 でLCDをI2C品(NHD-C0216CiZ)へ変更し解放** |
| GP15 | GPIO in  | `SD_CD`   | microSD カード検出 |
| GP16 | **PWM8A out** | `TX_PWM`  | P-TX 駆動PWM（200kHz 単相）**2026-07-31 `PWM_A` から改称・単相化**。**2026-08-03 (P-MAIN v5.7): `R_TXP` 100Ω を直列に追加**（PPS/EVENT には既に100Ωが入っており、より高速な TX_PWM だけ素通しだったため）。コネクタ側のネット名は `TX_PWM_O`（J_TX1 pin1） |
| GP17 | -        | (予備・未実装) | 旧 `PWM_B`。TX_improved は1石なので不要。**slice8B なので TX_advanced(相補PWM)へ戻す場合の予約枠** |
| GP18 | -        | (予備・未実装) | 旧 `TX_EN`。**TX基板にイネーブル入力が存在しない**ため廃止（送信停止は TX_PWM Low 固定で行う） |
| GP19 | -        | (予備・未実装) | 旧 `LCD_DC`。**2026-08-01 v5.3 でLCDをI2C品へ変更し解放** |
| GP20 | -        | (予備・未実装) | ※GPIO余剰だが予備ポートは付けない |
| GP21 | -        | (予備・未実装) | 同上 |
| GP22 | -        | (予備・未実装) | 同上 |
| GP26 | ADC0 | `BTN_ADC` | UI基板 3ボタン抵抗ラダー |
| GP27 | ADC1 | `TX_TEMP_ADC` | P-TX NTC温度（RCフィルタ後） |
| GP28 | PWM out | `BL_PWM` | UI基板 バックライトMOSFETゲート（slice2A） |

GP17–18・GP20–22は物理的に空くが、予備コネクタは設けない（余剰GPIOはテストポイントのみ）。
使用中のPWMは `TX_PWM`=slice8A / `BL_PWM`=slice2A の2スライスで衝突なし。

> **ファーム要求 (`TX_TEMP_ADC`, 2026-07-31)**: TX基板側は `V3D →(TX)R6 10k 1%→ TEMP_RAW →NTC 10k(B=3977)→ GND`
> の分圧を `(TX)R7 1k` 経由で返す。P-MAIN 側は `R_TT 1k + C_TT 10n + R_TTD 100k`。
> **R_TTD 100k がTX側テブナン(5k)＋直列2kに並列に効くので読み値が約 −5.7% ずれる**
> （未補正だと25℃付近で約 +2.9℃ の誤差）。分圧比は既知なのでファームで補正すること。
> 故障判別: **NTC断線 → TX側 R6 が持ち上げて ≈3.3V** / **J_TXT ケーブル断線 → R_TTD が引き落として ≈0V** /
> NTC短絡 → ≈0V。過熱・断線・短絡いずれでも送信停止すること（25℃≈1.65V, 85℃≈0.32V）。

## コネクタ表

### C-MAIN
> **⚠ 2026-08-01 (C-MAIN v4.0 / C-PWR v2.0): C-PWR との接続を XH9 1本に統合。**
> 旧 `J_PWR1`(XH6) + `J_I2CP`(XH5) + `J_RXA1`(XH3) + `J_LIGHT`(XH2) = **4コネクタ16ピンを
> 1コネクタ9ピンに集約**した（ユーザ要求＝耐圧チューブ内の小型化）。
> あわせて `J_TETH` の予備ピンを削って XH3 化し、**Celsius 水温センサ `J_TEMP` を新設**。
> 外形は **112×88 → 104×88**（C-PWR は 100.35×70 → 62×70）。

| Ref | 種別 | ピン | 用途 |
|---|---|---|---|
| J_PWR1 | **XH9(B9B-XH-A)** | **1:V5D 2:V3D 3:V3A 4:GND 5:I2C_SCL 6:I2C_SDA 7:GND 8:INA_AL 9:LIGHT_PWM** | C-PWR `J_MAIN` と**同一ピン順＝ストレート9芯1本**（**2026-08-01 統合**）。I2C対(5/6)をGND(4/7)で挟み、スイッチングする LIGHT_PWM(9) を電源ピンから離してある。SCL を SDA より先にしたのは C-PWR 側 INA226 東列の並びと揃えて基板内交差を消すため |
| J_RTC | ピンソケット6 | DS3231モジュール | I2C RTC |
| J_PRS | XH4 | 3V3/GND/SDA/SCL | MS5837/Bar30 圧力深度 |
| J_TEMP | **XH4(B4B-XH-A)** | **1:V3D 2:GND 3:I2C_SDA 4:I2C_SCL** | **Blue Robotics Celsius Fast-Response 水温センサ（TSYS01, I2C 0x77）2026-08-01 新設**。**2026-08-03 に JST-GH → XH4 へ変更**: v4.0 では「センサ付属ケーブルが 4極 JST-GH だから基板側も GH にすれば変換不要」として SM04B-GHS-TB を採用していたが、**実際はユーザが XH コネクタでケーブルを自作している**ため嵌合しなかった（GH 1.25mm / XH 2.5mm）。自作ケーブルでピン順が自由なので、**`J_PRS`／P-MAIN の `J_PRS`・`J_MAG`・`J_TEMP` と完全に同一ピン順**に統一した＝I²Cセンサ用ケーブルが親子・センサ間で全て共通になる。シルクは線色順に `R B W G`（赤=Vin/黒=GND/白=SDA/緑=SCL）。アドレス 0x77 は MS5837(0x76)/DS3231(0x68)/AT24C32(0x57)/INA226(0x40) と非衝突 |
| J_BNO | **Adafruit 4754実物FP(1×6が2列)** | 下列 1-6=**VIN(V3D)/3Vo(NC)/GND**/SCK/MISO/INT ・ 上列 7-12=BT(NC)/P0(V3D)/P1(V3D)/RST/MOSI/CS | BNO085ブレークアウト(専用SPI0)。**2026-07-31 pad2/pad3 を修正**（旧 `2=GND / 3=3Vo` は実物と逆で、モジュール内蔵LDO出力を基板GNDへ短絡し本当のGNDを未接続にしていた）。ピン順の一次資料＝ベンダ提供KiCad FP `pcb/datasheets/4754.zip`（`MODULE_4754.kicad_mod` + `4754.kicad_sym`） |
| J_SD | **TF-01A(Korean Hroparts, LCSC C91145)** | SMD microSD push-push | SPI1。**2026-08-03 に Molex 104031-0811 から変更**（JLCPCB に在庫があり SMT 実装対象にできるため。自作FP `AquaBeacon:microSD_TF-01A`、実装高さ1.85mm）。**`R_SDCS` 10k で CS をプルアップ**(v4.3。起動時 GPIO Hi-Z でのフロート防止) |
| U_485D | **Waveshareキャステレーション直付け(7pad)** | TTL:GND/RXD/TXD/VCC, 485:PE/B/A | Waveshare DATA×1(SS-9778, 絶縁・双方向)。トリガ廃止 |
| J_TETH | **XH3(B3B-XH-A)** | 485D_A/485D_B/485D_PE | テザー3芯(単一絶縁リンク)。**2026-08-01 XH4→XH3**: pin4 は「予備」だったので削除（ユーザ要求「予備のXHは全ていらない」）。Waveshare の北へ移設して外形 104mm に収めた |
| J_RX1 | **XH6** | **V3A/GND/TH_PWM_F/ENV_ADC/NC/CMP_OUT** | C-RX (`RX_improved_mini` の `J2`) と**同一ピン順**＝ストレート6芯1本。**2026-07-28 変更**: RX基板は製造済みで変更不可のため本基板を合わせた。旧 XH4(CMP_OUT/ENV_ADC/RX_EN/GND) は本数・順序とも不一致で、かつ RX に `RX_EN` の受け口が無かった。pin5 は RX 側 NC(旧 SHDN)。**pin5 が NC でも XH6 のまま維持する**（RX 基板が製造済みでピン位置を動かせないため。ここは「予備」ではない） |
| J_LEAK | XH2 | LEAK/GND | 漏水電極 |
| J_LCD | **XH7(B7B-XH-A)** | GND/V3D/SDA/SCL/RST/LED_A/LED_K | NHD-C0216CiZ用。P-MAINと同一ピン順 |

### P-MAIN
| Ref | 種別 | ピン | 用途 |
|---|---|---|---|
| J_PWR1 | XH6 | **V5D/V5D/GND/GND/V3D/V3D** | P-PWR `J_MAIN` と1:1（**2026-07-31 ピン順修正**。旧 V5D/GND/V3D/GND/SDA/SCL は P-PWR 側と噛み合っていなかった） |
| J_I2CP | **XH5** | V3D/GND/SDA/SCL/INA_AL | P-PWR `J_I2C` と1:1（**2026-07-31 新設**。同時に P-PWR 側も J_I2C を XH4→XH5 化して `J_ALT`(PH2) を廃止＝C系と完全同一） |
| J_RTC | ピンソケット6 | DS3231モジュール | I2C RTC |
| J_PRS | XH4 | 3V3/GND/SDA/SCL | MS5837/Bar30 |
| J_MAG | XH4 | 3V3/GND/SDA/SCL | LIS3MDL リモート方位 |
| J_TEMP | XH4 | 3V3/GND/SDA/SCL | Celsius Fast-Response 温度(I2C) |
| J_GNSS | XH5 | 3V3/GND/GNSS_TX/GNSS_RX/PPS | NEO-M9N |
| J_SD | **TF-01A(Korean Hroparts, LCSC C91145)** | SMD microSD push-push | SPI1。**2026-08-03 に Molex 104031-0811 から変更**（C-MAIN と同一部品・同一FP）。**`R_SDCS` 10k で CS をプルアップ**(v5.7) |
| U_485D | **Waveshareキャステレーション直付け(7pad)** | TTL:GND/RXD/TXD/VCC, 485:PE/B/A | Waveshare DATA×1(SS-9778, 絶縁・双方向)。トリガ廃止 |
| J_TETH | **XH3(B3B-XH-A)** | 485D_A/485D_B/485D_PE | テザー3芯(単一絶縁リンク)。**2026-08-03 XH4→XH3**: pin4 の「予備」を削除し C-MAIN と揃えた（ユーザ要求「予備のXHは全ていらない」が子機にしか適用されていなかった） |
| J_TX1 | **XH2** | TX_PWM_O/GND | **P-TX = `TX_improved`(TC4427+2SK4017 1石)に確定（2026-07-31）**。`TX_improved` の `J2`(PWM_IN/GND) と同一ピン順＝ストレート2芯。旧 XH6(PWM_A/PWM_B/TX_EN/TX_TEMP/3V3/GND) は**対応するTX基板が存在しなかった**（TX_advanced の `J2` は XH3 PWM_A/B/GND のみで TX_EN も温度回路も無し） |
| J_TXT1 | **XH3** | V3D/GND/TX_TEMP_RAW | `TX_improved` の `J5`(V3S/GND/TEMP_ADC) と同一ピン順。**2026-07-31 新設**（TXのNTC分圧に3.3V基準を供給し、温度電圧を受ける）。TX基板の `V3S` は本基板の `V3D` を指す |
| J_SPR | **XH3(B3B-XH-A)** | SPR_PPS_3V3/SPR_EVENT_3V3/GND | SPRESENSE拡張ボードのJP1を3.3V側に設定。各信号は100Ω直列。**2026-08-03 XH4→XH3**: v5.5 で pin4 の V3D 給電を廃止して以来 NC のままだったので削除（拡張ボードは USB 等の正規電源から給電する） |
| J_LCD | **XH7(B7B-XH-A)** | GND/V3D/**SDA/SCL**/RST/LED_A/LED_K | **LCD専用**(旧J_UI廃止)。ボタン/BL/RCは本基板オンボード。**2026-08-01 v5.3 で XH9→XH7**（LCDをI2C品 NHD-C0216CiZ へ変更） |

### オンボードUI（旧UI基板を廃止しC-MAIN/P-MAINへ統合, 2026-07-23）

> **2026-08-02反映済み**: P-MAIN v5.5 / C-MAIN v4.1とも同じI²C LCD・XH7ピン順を使用する。

| Ref | 種別 | ピン/ネット | 用途 |
|---|---|---|---|
| J_LCD | **XH7(B7B-XH-A)** | GND/V3D/SDA/SCL/RST/LED_A/LED_K | **NHD-C0216CiZ-FSW-FBW-3V3**（2×16キャラクタ, AiP31032, **I²C アドレス0x3E(7bit)/0x7C(8bit)**）。旧 NHD-C12864WO-B1TFH#-M(ST7567 4線SPI, 30pin FFC) から2026-08-01に変更＝配線簡素化。**昇圧C(VOUT–VDD 1µF / C1+–C1− 1µF)はLCD至近のキャリア基板側に置く**（充電ポンプノードなのでXHケーブルで引き回さない） |
| SW_UP/SW_ENT/SW_DN | タクト6mm(THT) | BTN_ADC抵抗ラダー | 3ボタン(UP=0V/ENT=0.82V(R_E=3.3k実装値)/DN=1.65V/無=3.3V) |
| R_LAD/R_E/R_D | チップ抵抗0603 | 10k/3.3k/10k | ADCラダー(V3D→BTN_ADC=R_LAD10k, ENT枝=R_E3.3k, DN枝=R_D10k) |
| Q_BL | 2N7002(SOT-23) | BL_PWM→R_G100→gate, D=LED_K, S=GND | バックライトPWM。**V5D→R_BL100→LED_A**（2026-08-01 変更: 旧 V3D→R_BL33。新LCDのVLED=2.96V typ に対し3.3Vでは余裕0.34Vしか無く公差で電流が2.3倍ばらつくため。V5Dなら(5−2.96)/(100+RDS(on)≈7)=19.1mA、公差込み18.4–20.8mA）、R_GPD100kプルダウン |
| R_RST/C_RST | 0603/0603 | 10k(V3D)/100n(GND) | LCDリセットRC(電源投入, GPIO非消費)。新LCDでもそのまま流用 |

## BOM 追加必要品（未購入・発注前確定要）
BNO085ブレークアウト(SPI対応)・**Newhaven NHD-C0216CiZ-FSW-FBW-3V3 ×2**(2026-08-01 変更。旧 NHD-C12864WO-B1TFH#-M。DigiKey JP ¥2,248/在庫5,594)・**microSD TF-01A (LCSC C91145) ×2**(2026-08-03 変更。旧 Molex 104031-0811。JLCPCB の SMT 実装対象にできる)・
MS5837-30BA/Bar30 ×2・INA226モジュール ×2・LIS3MDL・NEO-M9N+ANN-MB1・Celsius温度センサ・
Raspberry Pi Pico 2 W ×2・タクトスイッチ ×6・BLゲート用MOSFET。
※旧IMU BMI270(購入済)は子機ではBNO085へ置換（BMI270は予備/別用途）。
