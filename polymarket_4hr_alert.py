#!/usr/bin/env python3
"""
Polymarket BTC 4HR Up/Down Alert — 本地 macOS 通知

每 30 秒 poll Gamma API，當 Up/Down odds ≤ 10¢ 時彈 macOS notification。
新 window 開時也通知（附 priceToBeat）。

用法：python3 polymarket_4hr_alert.py
終止：Ctrl+C
"""
import subprocess
import time
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Set

GAMMA_API = "https://gamma-api.polymarket.com/events?series_slug=btc-up-or-down-4h&active=true&closed=false&limit=1&order=startDate&ascending=false"
BINANCE_API = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
POLL_INTERVAL = 30  # seconds
ODDS_THRESHOLD = 0.10  # alert when odds ≤ 10¢
HKT = timezone(timedelta(hours=8))

_last_slug: Optional[str] = None
_last_alerted_side: Dict[str, Set[str]] = {}  # slug -> set(side), 避免重複 alert


def notify(title: str, message: str):
    """macOS Notification Center"""
    script = f'display notification "{message}" with title "{title}" sound name "Glass"'
    subprocess.call(["osascript", "-e", script])


def fetch_active_market() -> Optional[Dict]:
    """從 Gamma API 攞目前活躍嘅 4hr market"""
    try:
        req = urllib.request.Request(GAMMA_API, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        if not data:
            return None
        event = data[0]
        market = event["markets"][0]
        prices = json.loads(market["outcomePrices"])
        meta = event.get("eventMetadata", {})
        start_time = event.get("startTime", "")
        end_date = event.get("endDate", "")
        return {
            "slug": event["slug"],
            "title": event["title"],
            "price_to_beat": meta.get("priceToBeat"),
            "up_odds": float(prices[0]) if prices else None,
            "down_odds": float(prices[1]) if len(prices) > 1 else None,
            "start_time": start_time,
            "end_date": end_date,
        }
    except Exception as e:
        print(f"[ERROR] fetch failed: {e}")
        return None


def fetch_btc_price() -> Optional[float]:
    """從 Binance 攞即時 BTC 價格"""
    try:
        req = urllib.request.Request(BINANCE_API, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        return float(data["price"])
    except Exception:
        return None


def fmt_hkt(iso_str: str) -> str:
    """ISO -> HKT HH:MM"""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.astimezone(HKT).strftime("%H:%M")
    except Exception:
        return iso_str[:16]


def fmt_odds(odds: float) -> str:
    """0.10 -> 10¢ (10:1)"""
    cents = int(odds * 100)
    payout = round(100 / cents) if cents > 0 else 999
    return f"{cents}¢ ({payout}:1)"


def time_remaining(end_iso: str) -> str:
    """計剩幾耐收盤"""
    try:
        end = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = end - now
        if diff.total_seconds() <= 0:
            return "已收盤"
        h = int(diff.total_seconds() // 3600)
        m = int((diff.total_seconds() % 3600) // 60)
        return f"{h}h{m}m"
    except Exception:
        return "?"


def calc_distance(btc_price: float, ptb: float, side: str) -> str:
    """計 BTC 要升/跌幾多先贏"""
    diff = ptb - btc_price
    pct = (diff / btc_price) * 100
    if side == "Up":
        # Up 贏 = BTC ≥ PTB，所以要升返上去
        if diff <= 0:
            return f"已贏（高過PTB ${-diff:,.0f}）"
        return f"要升 ${diff:,.0f} (+{pct:.2f}%)"
    else:
        # Down 贏 = BTC < PTB，所以要跌落去
        if diff >= 0:
            return f"已贏（低過PTB ${diff:,.0f}）"
        return f"要跌 ${-diff:,.0f} ({pct:.2f}%)"


def process(market: Dict):
    global _last_slug, _last_alerted_side

    slug = market["slug"]
    up = market["up_odds"]
    down = market["down_odds"]
    ptb = market["price_to_beat"]
    btc = fetch_btc_price()

    # 新 window 開啟
    if slug != _last_slug:
        _last_slug = slug
        _last_alerted_side = {}
        ptb_str = f"${ptb:,.0f}" if ptb else "未公布"
        btc_str = f"${btc:,.0f}" if btc else "?"
        print(f"\n[{datetime.now(HKT).strftime('%H:%M:%S')}] 新 window: {market['title']}")
        print(f"  BTC: {btc_str} | PTB: {ptb_str} | Up: {fmt_odds(up)} | Down: {fmt_odds(down)}")
        notify(
            "Polymarket 4hr 新窗口",
            f"{fmt_hkt(market['start_time'])} - {fmt_hkt(market['end_date'])} HKT\n"
            f"BTC: {btc_str} | PTB: {ptb_str}\n"
            f"Up: {fmt_odds(up)} | Down: {fmt_odds(down)}",
        )
        time.sleep(2)
        return

    # odds ≤ threshold → alert
    for side, odds in [("Up", up), ("Down", down)]:
        if odds is None:
            continue
        if odds <= ODDS_THRESHOLD and side not in _last_alerted_side.get(slug, set()):
            print(f"\n[{datetime.now(HKT).strftime('%H:%M:%S')}] 🔔 {side} {fmt_odds(odds)}")
            ptb_str = f"${ptb:,.0f}" if ptb else "?"
            btc_str = f"${btc:,.0f}" if btc else "?"
            remaining = time_remaining(market["end_date"])
            dist = ""
            if btc and ptb:
                dist = calc_distance(btc, ptb, side)
            notify(
                f"🔔 {side} {fmt_odds(odds)}",
                f"BTC: {btc_str} | PTB: {ptb_str}\n"
                f"{dist}\n"
                f"收盤剩: {remaining}",
            )
            _last_alerted_side.setdefault(slug, set()).add(side)

    # 狀態打印（每 30 秒一行）
    ptb_str = f"${ptb:,.0f}" if ptb else "?"
    btc_str = f"${btc:,.0f}" if btc else "?"
    remaining = time_remaining(market["end_date"])
    dist_str = ""
    if btc and ptb:
        diff = ptb - btc
        pct = (diff / btc) * 100
        dist_str = f"距PTB {pct:+.2f}% "
    print(
        f"\r[{datetime.now(HKT).strftime('%H:%M:%S')}] "
        f"BTC={btc_str} {dist_str}"
        f"Up={fmt_odds(up)} Down={fmt_odds(down)} "
        f"剩{remaining}    ",
        end="",
        flush=True,
    )


def main():
    print("Polymarket BTC 4HR Alert — 啟動")
    print(f"Odds threshold: ≤ {int(ODDS_THRESHOLD * 100)}¢")
    print(f"Poll interval: {POLL_INTERVAL}s")
    print("Ctrl+C 終止\n")

    while True:
        market = fetch_active_market()
        if market:
            process(market)
        else:
            print(f"\r[{datetime.now(HKT).strftime('%H:%M:%S')}] 搵唔到活躍 market...    ", end="", flush=True)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n終止")
