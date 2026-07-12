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

## TODO
- [ ] 結合 Jooococo bot Brain 分析 — 對比 bot 方向 vs Polymarket odds，搵 edge
- [ ] Bot 話 Down 65% vs 市場 Down 10¢ → 巨大 edge alert
- [ ] 支援其他 timeframe（1hr, 24hr）
- [ ] launchd plist 開機自動跑
