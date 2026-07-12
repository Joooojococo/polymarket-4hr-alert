# Polymarket BTC 4HR Up/Down Alert

macOS 本地通知 — 監控 Polymarket BTC 4HR Up/Down 市場 odds。

## 功能
- 每 30 秒 poll Gamma API，監控活躍 4hr window
- Up/Down odds ≤ 10¢ 時彈 macOS notification
- 顯示 BTC 即時價 vs priceToBeat 距離（要升/跌幾多先贏）
- 新 window 開時通知（附 priceToBeat）

## 用法
```bash
python3 polymarket_4hr_alert.py
```

## Notification 示例
```
🔔 Down 8¢ (12:1)
BTC: $64,500 | PTB: $64,000
要跌 $500 (-0.78%)
收盤剩: 2h30m
```

## 交易策略

### 規則
- 每個 4hr window 結算前只落 **一次 $1**
- 唔加碼、唔 martingale、唔追價
- 輸咗就輸 $1，贏就 10¢ → $1 = 賺 $9

### 風險
- 每個 window 最多輸 $1
- 一日 6 個 4hr window，最多輸 $6
- 贏一次 10¢ = 賺 $9，10% win rate 就 break even
- Bot 分析如果 65% 準確度，長期一定賺

### 入場條件
1. Polymarket odds ≤ 10¢（市場覺得只有 10% 機會）
2. Jooococo bot Brain 方向同意（bot 話嗰邊有 65% 機會）
3. 兩者出現 gap = edge
4. 只入一次，入咗就等收盤

### 點解唔係每個 window 都賭
- Edge 每日只出現幾次
- 冇 edge 就 skip，唔好硬賭
- 84.1% 虧錢錢包都係亂入場，贏錢 bot 77% win rate 係因為大部分時間唔入場

## TODO
- [ ] 結合 Jooococo bot Brain 分析 — 對比 bot 方向 vs Polymarket odds，搵 edge
- [ ] Bot 話 Down 65% vs 市場 Down 10¢ → 巨大 edge alert
- [ ] 全自動落單（py_clob_client + Polymarket wallet + USDC on Polygon）
- [ ] 每個 window 只入一次嘅 state tracking
- [ ] 支援其他 timeframe（1hr, 24hr）
- [ ] launchd plist 開機自動跑
