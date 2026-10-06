# Hyperliquid-Leaderboard-Analytics
Hyperliquid analytics right in your terminal. Track top traders by PnL, ROI, and account value, monitor ranking changes over time, and identify consistently profitable wallets while separating them from one-hit wonders.  Powered by Hyperliquid’s public, read-only info API. Unofficial community project, not affiliated with Hyperliquid.
<div align="center">

# 📊 Hyperliquid Leaderboard Analytics

### Hyperliquid leaderboard analytics in your terminal — rank, slice, compare and export top traders by PnL and ROI.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Textual](https://img.shields.io/badge/TUI-textual-7C3AED.svg)](https://textual.textualize.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Hyperliquid](https://img.shields.io/badge/Hyperliquid-L1-9B59B6.svg)](https://hyperliquid.xyz/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](./README.md)

**Slice the Hyperliquid leaderboard any way you like — by ROI, volume, win-rate,
asset, leverage band or time window — and export the result.**

</div>

---

## 📖 Overview

**Hyperliquid Leaderboard Analytics** is a fast, keyboard-driven **terminal dashboard** for
exploring the public Hyperliquid leaderboard — **perp DEX trading statistics and data
analysis** without leaving your shell. The raw leaderboard shows you a single ranked list;
this tool lets you **track top traders by PnL, ROI, and account value**, re-rank, filter,
compare and export them.

It answers the questions the raw board can't: **historical leaderboard snapshots and ranking
changes** over 7d/30d/90d windows, **PnL distribution and percentile statistics across the
leaderboard**, per-asset breakdowns (who makes their money on BTC perps vs. alts), and
**wallet performance over time** — so you can **identify consistently profitable wallets vs
one-hit wonders**. Every view **exports leaderboard data to CSV/JSON** for further analysis.
Built as an **open-source Python analytics tool** with a **terminal dashboard built with
Textual and Rich**, it **uses the public Hyperliquid info API — read-only**, no key required.

> ⚠️ **Read-only.** This is an analytics tool — it reads public leaderboard data and
> never places orders.

---

## ✨ Features

| Area | What you get |
|------|--------------|
| 🏆 **Leaderboard browser** | Re-rank by ROI, volume, win-rate, Sharpe, profit factor, drawdown. |
| 🔪 **Slicing & filters** | By asset, leverage band, side bias, account age, time window. |
| 📈 **Trader detail** | Equity curve, per-asset PnL breakdown, position heatmap. |
| 📅 **Period compare** | 7d vs. 30d vs. 90d side-by-side deltas and ranking changes. |
| 📤 **Export** | CSV / JSON / Markdown tables of any view. |
| 🎛️ **Dashboard** | Single pane: top movers, biggest drawdowns, volume leaders. |
| ⌨️ **Keyboard-first** | Vim bindings, `/` to filter, `e` to export, no mouse needed. |
| 🌑 **Theming** | Multiple built-in palettes. |

---

## 🖥️ Screenshots

```
 ╔════════════════════════════════════════════════════════════════════════════════════════════╗
 ║ 📊 Hyperliquid Leaderboard Analytics       [1]Board [2]Detail [3]Filters [4]Compare [5]Export║
 ╠════════════════════════════════════════════════════════════════════════════════════════════╣
 ║ Window: 90d   Sort: ROI ↓   Asset: ALL   Lev: ALL        1,024 traders shown               ║
 ║ ───────────────────────────────────────────────────────────────────────────────────────── ║
 ║  #  Alias           Address            ROI(90d)   ROI(30d)   Volume        Win%   Sharpe  ║
 ║  1  quant_kappa      0x7f3a…c4e1      +412.8%    +58.2%     4.81M         71.3   1.82    ║
 ║  2  leverage_ape     0xab24…1033      +1274%     +212.4%    9.30M         52.1   0.74    ║
 ║  3  steady_basis     0xc0ff…4444      +84.0%     +11.3%     1.22M         73.1   2.73    ║
 ║  4  delta_neutral    0x1b3e…9f10      +61.4%     +6.8%      2.04M         68.0   2.10    ║
 ║  5  basis_hunter     0x4422…88cc      +47.2%     +9.1%      0.88M         64.5   1.95    ║
 ║  …                                                                                        ║
 ║  TOP MOVERS (24h)                                                                          ║
 ║   ▲ quant_kappa      +18.4%     ▼ leverage_ape     −24.1%                                 ║
 ║                                                                                           ║
 ║  q Quit   / Filter   s Sort   e Export   c Compare   t Theme   ? Help                    ║
 ╚════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## 🚀 Quick start

```bash
git clone https://github.com/jadeapricot27/hyperliquid-leaderboard-analytics.git
cd hyperliquid-leaderboard-analytics
pip install -r requirements.txt

python main.py            # live public data
python main.py --demo     # offline dataset
```

One-click launchers (no system Python required — they unpack a bundled standalone
interpreter on first run):

```batch
run.bat        :: Windows
```
```bash
chmod +x run.sh && ./run.sh    # Linux / macOS
```

No API key required — the leaderboard is public.

---

## ⌨️ Keybindings

| Key | Action |
|-----|--------|
| `1`–`6` | Switch tabs: Board · Detail · Filters · Compare · Export · Settings |
| `/` | Filter the focused table |
| `s` | Cycle sort column |
| `w` | Cycle time window (7d / 30d / 90d / all) |
| `Enter` | Open trader detail |
| `c` | Compare selected with current |
| `e` | Export current view (CSV / JSON / Markdown) |
| `t` | Cycle theme |
| `q` | Quit |

---

## 📤 Export

Any view can be exported without leaving the terminal — press `e` inside the TUI on any
table. Exports land in `./exports` as CSV, JSON or Markdown, ready for your own
spreadsheet or notebook.

---

## 🗂️ Project layout

```
hyperliquid-leaderboard-analytics/
├── main.py                       # Entry point (unpacks bundled runtime on first launch)
├── hl_leaderboard_analytics/     # Host package
│   ├── __main__.py               # `python -m hl_leaderboard_analytics` entry
│   ├── cli.py                    # argparse + launch
│   ├── config.py                 # Config loader (TOML)
│   ├── core/                     # models, analytics, export writers, mock data
│   └── tui/                      # Textual app: screens, widgets, styles
├── core/                         # Runtime support library
├── requirements.txt
├── run.bat / run.sh              # One-click launchers
└── release/                      # Pre-compiled binaries (planned)
```

---

## ⚙️ Configuration

```toml
# ~/.hl-leaderboard/config.toml
[network]
api_url = "https://api.hyperliquid.xyz"

[board]
default_window = "90d"        # 7d | 30d | 90d | all
default_sort   = "roi"        # roi | volume | win_rate | sharpe | profit_factor | drawdown
page_size      = 100

[export]
format = "csv"                # csv | json | markdown
out_dir = "./exports"
```

---

## 🔒 Security & responsible use

- **Read-only** — no order placement, no private keys, no trading API.
- **Public data only** — uses the public Hyperliquid leaderboard endpoint.
- **No telemetry.**

---

## ❓ FAQ

<details>
<summary><b>Is this affiliated with Hyperliquid Labs?</b></summary>

No. Independent, unofficial community project. Hyperliquid is a third-party protocol.
</details>

<details>
<summary><b>Does it place trades?</b></summary>

No. Strictly read-only analytics. It ranks, filters, compares and exports.
</details>

<details>
<summary><b>Can I run it offline?</b></summary>

Yes — `python main.py --demo` ships a bundled dataset for previews and CI.
</details>

---

## ⚠️ Disclaimer

This is an **unofficial community analytics tool**, **not affiliated with, endorsed by, or
sponsored by Hyperliquid Labs**. Provided for research purposes — **not financial advice**.

---

## 📄 License

MIT — see [`LICENSE`](./LICENSE).

<div align="center"><sub>Built for analysts who live in the terminal.</sub></div>
