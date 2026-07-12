# Polymarket BTC Up/Down — 玩法研究

## 核心 Edge

### 1. Orderbook 延遲套利（最大 edge）
BTC spot price（Binance）毫秒更新，Polymarket orderbook 係人手掛單，滯後幾秒到幾十秒。
- BTC 突然升，Polymarket Up 應該 90¢，但仲掛 50¢ → 買 Up = 執平貨
- 一個錢包用呢個策略 24 筆交易賺 $42,322
- 同時睇 Binance spot + Polymarket odds，spot 大幅移動但 Polymarket 未更新就入手

### 2. 多 Timeframe 過濾（11,717 筆，77% win rate）
- 1hr = 大方向 bias
- 15min = 確認 momentum
- 5min = 實際入場
- **三個 timeframe 全部對齊先入場**

兩個 setup：
- **Momentum burst** — 開頭 30-90 秒突然放量，入 continuation
- **Mean reversion** — 上一支燭過度延伸，呢一支開始反轉

硬規則：**唔入場最後 90 秒** — MEV bot 搶爛 orderbook。

### 3. Mean Reversion（我嘅策略）
> BTC 升到阻力位 → Down odds 變 10¢ → 買 Down → BTC 插返落去 → Down 贏

高手印證：
- "Sharp moves in one direction get faded in the next candle more often than people expect"
- "The crowd overcorrects on 5-minute markets constantly"

## 結合 Jooococo Bot

Bot 已有：LLM Brain（方向 + 信心度）、Signal Grader、CVD、OB、技術面

**Edge = bot 話 Down 65% vs Polymarket Down 10¢（市場 10%）= 55% gap**

用 bot 分析對比市場定價，搵 mispricing。

## 關鍵數字

| 資料 | 數字 |
|------|------|
| Polymarket 虧錢錢包 | 84.1%（多數手動 + 3am bot） |
| 賺錢 bot win rate | 77%（11,717 筆） |
| 最大錯誤 | 開頭 5 分鐘入場 + 輸錢後加倍 |
| 真正成本 | spread 1-2¢（平靜）/ 5-10¢（波動） |
| Edge 出現頻率 | 每日幾次，唔係每 15 分鐘 |
| 套利窗口 | 2024 年 12 秒 → 2026 年 <3 秒（HFT 已食晒） |

## 資料來源
- [11,717 筆交易 bot 策略](https://dev.to/lkto1m/my-polymarket-trading-bot-strategy-across-11717-trades-5m15m1h-framework-explained-3gbl)
- [24 筆交易賺 $42,322](https://medium.com/mountain-movers/how-24-winning-trades-helped-1-polymarket-wallet-hit-a-42-322-total-return-a823c1a74093)
- [5 分鐘 scalper bot 原理](https://medium.com/mountain-movers/how-btc-5-minute-scalpers-actually-work-on-polymarket-building-the-bot-that-trades-stale-order-a16e84eb3140)
- [Polymarket 玩法終極指南](https://www.crypticorn.com/ultimate-guide-polymarket-crypto-trading/)
- [3 個錢包合賺 $2.35M](https://finbold.com/this-insanely-profitable-bitcoin-strategy-can-earn-you-millions-on-polymarket/)
- [Node.js trading bot](https://github.com/BlackCandleLab/polymarket-trading-bot)
