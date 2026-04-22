import json
import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="ZigZag Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

GITHUB_BASE = "https://raw.githubusercontent.com/vikramdoogar-tech/zigzag-buy-zone/main/"

st.markdown("""
<style>
.main .block-container{padding:1rem 0.9rem;max-width:100%;}
.card{background:#0f172a;border-radius:12px;padding:14px 16px;margin-bottom:10px;border-left:4px solid #475569;}
.cg{border-left-color:#22c55e;background:#052e16;}
.cy{border-left-color:#eab308;background:#1c1400;}
.cr{border-left-color:#ef4444;background:#1c0505;}
.cb{border-left-color:#3b82f6;background:#0c1a2e;}
.ct{border-left-color:#2dd4bf;background:#031a18;}
.sym{font-size:1.1rem;font-weight:700;color:#f1f5f9;}
.bx{font-size:0.65rem;background:#1e3a5f;color:#93c5fd;border-radius:4px;padding:1px 5px;margin-left:4px;}
.bg{background:#052e16;color:#22c55e;}
.br{background:#1c0505;color:#ef4444;}
.dt{font-size:1.35rem;font-weight:700;margin:4px 0;}
.gn{color:#22c55e;}
.ye{color:#eab308;}
.rd{color:#ef4444;}
.bl{color:#60a5fa;}
.tl{color:#2dd4bf;}
.mt{font-size:0.72rem;color:#94a3b8;margin-bottom:5px;}
.pr{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px;}
.pc{min-width:72px;}
.pl{font-size:0.62rem;color:#94a3b8;}
.pv{font-size:0.85rem;font-weight:600;color:#e2e8f0;}
.tb{background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.2);border-radius:6px;padding:8px;margin-top:8px;font-size:0.76rem;color:#c4b5fd;}
div[data-testid="stMetricValue"]{font-size:1.35rem;}
</style>
""", unsafe_allow_html=True)


def safe_num(x, default=0.0):
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


@st.cache_data(ttl=1800, show_spinner=False)
def get_json_file(filename: str):
    url = GITHUB_BASE + filename
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"_error": f"Could not load {filename}: {e}"}


def normalize_stock_rows(raw):
    if isinstance(raw, dict) and "_error" in raw:
        return [], raw["_error"]
    rows = []
    for r in raw or []:
        rows.append({
            "sym": str(r.get("s", "")).strip(),
            "tier": str(r.get("t", "")),
            "sector": str(r.get("x", "")),
            "score": safe_num(r.get("sc")),
            "avg_drop": safe_num(r.get("ad")),
            "crash_buy": safe_num(r.get("cb")),
            "rot_target": safe_num(r.get("rt")),
            "win_pct": safe_num(r.get("wp")),
            "rr": safe_num(r.get("rr")),
            "rot_yr": safe_num(r.get("ry")),
            "above_200": bool(r.get("a2", False)),
            "rise_days": int(safe_num(r.get("rd"))),
            "drop_days": int(safe_num(r.get("dd"))),
            "rise_speed": safe_num(r.get("sp")),
        })
    rows = [r for r in rows if r["sym"]]
    return rows, None


def normalize_rebound_rows(raw):
    if isinstance(raw, dict) and "_error" in raw:
        return [], raw["_error"]
    rows = []
    for r in raw or []:
        rows.append({
            "sym": str(r.get("sym", "")).strip(),
            "price": safe_num(r.get("price")),
            "target": safe_num(r.get("target")),
            "dist": safe_num(r.get("dist")),
            "speed": safe_num(r.get("speed")),
            "score": safe_num(r.get("score")),
            "rr": safe_num(r.get("rr")),
            "win": safe_num(r.get("win")),
            "roty": safe_num(r.get("roty")),
            "l1": safe_num(r.get("l1")),
            "l2": safe_num(r.get("l2")),
            "l3": safe_num(r.get("l3")),
            "sl": safe_num(r.get("sl")),
            "rdays": int(safe_num(r.get("rdays"))),
            "ddays": int(safe_num(r.get("ddays"))),
            "above": bool(r.get("above", False)),
            "tags": str(r.get("tags", "")),
        })
    rows = [r for r in rows if r["sym"]]
    return rows, None


def normalize_watchlist(raw):
    if isinstance(raw, dict) and "_error" in raw:
        return [], raw["_error"]
    rows = []
    for r in raw or []:
        rows.append({
            "sym": str(r.get("sym", "")).strip(),
            "entry": safe_num(r.get("entry")),
            "target": safe_num(r.get("target")),
            "sl": safe_num(r.get("sl")),
            "qty": int(safe_num(r.get("qty"))),
            "thesis": str(r.get("thesis", "")),
            "holders": str(r.get("holders", "")),
        })
    rows = [r for r in rows if r["sym"]]
    return rows, None


@st.cache_data(ttl=600, show_spinner=False)
def get_prices(symbols):
    symbols = [str(s).strip().upper() for s in symbols if str(s).strip()]
    if not symbols:
        return {}

    out = {}
    for i in range(0, len(symbols), 25):
        batch = symbols[i:i + 25]
        tickers = [f"{s}.NS" for s in batch]
        try:
            raw = yf.download(
                tickers=" ".join(tickers),
                period="5d",
                interval="1d",
                auto_adjust=True,
                progress=False,
                group_by="ticker",
                threads=False,
            )
            if raw is None or raw.empty:
                continue

            if isinstance(raw.columns, pd.MultiIndex):
                for s in batch:
                    ns = f"{s}.NS"
                    try:
                        series = raw[(ns, "Close")].dropna()
                        if not series.empty:
                            out[s] = round(float(series.iloc[-1]), 2)
                    except Exception:
                        try:
                            series = raw["Close"][ns].dropna()
                            if not series.empty:
                                out[s] = round(float(series.iloc[-1]), 2)
                        except Exception:
                            pass
            else:
                if len(batch) == 1 and "Close" in raw.columns:
                    series = raw["Close"].dropna()
                    if not series.empty:
                        out[batch[0]] = round(float(series.iloc[-1]), 2)
        except Exception:
            pass
        time.sleep(0.15)
    return out


def make_card(sym, tier, sec, ab, dist, spd, score, rr, win, roty, plbl, pval,
              l1, l2, l3, sl, tgt, up, rd, dd, el, dlf, css, dc):
    sg = "+" if dist > 0 else ""
    ac = "bg" if ab else "br"
    al = "200+" if ab else "200-"
    return (
        f'<div class="card {css}"><span class="sym">{sym}</span>'
        f'<span class="bx">{tier}</span><span class="bx">{sec}</span>'
        f'<span class="bx {ac}">{al}</span>'
        f'<div class="dt {dc}">{sg}{round(dist,2)}% | {round(spd,1)}%/day</div>'
        f'<div class="mt">Score {round(score,1)} | R:R {round(rr,2)} | Win {int(win)}% | {round(roty,1)}x/yr</div>'
        f'<div class="pr">'
        f'<div class="pc"><div class="pl">{plbl}</div><div class="pv">₹{pval:,.2f}</div></div>'
        f'<div class="pc"><div class="pl">L1</div><div class="pv" style="color:#22c55e">₹{l1:,.2f}</div></div>'
        f'<div class="pc"><div class="pl">L2</div><div class="pv">₹{l2:,.2f}</div></div>'
        f'<div class="pc"><div class="pl">L3</div><div class="pv">₹{l3:,.2f}</div></div>'
        f'<div class="pc"><div class="pl">SL</div><div class="pv" style="color:#ef4444">₹{sl:,.2f}</div></div>'
        f'<div class="pc"><div class="pl">TGT</div><div class="pv" style="color:#2dd4bf">₹{tgt:,.2f}</div></div>'
        f'<div class="pc"><div class="pl">UP%</div><div class="pv" style="color:#22c55e">{up:+.1f}%</div></div>'
        f'<div class="pc"><div class="pl">RISE DAYS</div><div class="pv" style="color:#fbbf24">~{rd}d</div></div>'
        f'<div class="pc"><div class="pl">DROP DAYS</div><div class="pv" style="color:#94a3b8">~{dd}d</div></div>'
        f'<div class="pc"><div class="pl">ELAPSED</div><div class="pv" style="color:#c084fc">{el}</div></div>'
        f'<div class="pc"><div class="pl">DAYS LEFT</div><div class="pv" style="color:#2dd4bf">{dlf}</div></div>'
        f'</div></div>'
    )


raw_stock = get_json_file("data_stocks_slim.json")
raw_rebound = get_json_file("data_rebound.json")
raw_watch = get_json_file("data_watchlist.json")

STOCK_DATA, stock_err = normalize_stock_rows(raw_stock)
REBOUND_DATA, rebound_err = normalize_rebound_rows(raw_rebound)
MY_WATCHLIST, watch_err = normalize_watchlist(raw_watch)

if stock_err or rebound_err or watch_err:
    st.warning("Some GitHub data files could not be loaded.")
    for err in [stock_err, rebound_err, watch_err]:
        if err:
            st.caption(err)

st.title("ZigZag Terminal")
st.caption(f"{len(STOCK_DATA)} scanner | {len(REBOUND_DATA)} rebound | {len(MY_WATCHLIST)} watchlist")

with st.sidebar:
    st.markdown("### Filters")
    prox = st.slider("Within X% of crash buy", 3, 25, 15)
    msco = st.slider("Min Score", 10, 40, 13)
    mrr = st.slider("Min R:R", 1.0, 3.0, 1.2, step=0.1)
    tiers = st.multiselect("Tiers", ["T1", "T2", "T3", "T4"], default=["T1", "T2", "T3", "T4"])
    ab_only = st.checkbox("Above 200DMA only", False)

tab1, tab2, tab3 = st.tabs(["Buy Zone Scanner", "Rebound Scanner", "My Research"])

with tab1:
    pool = [
        s for s in STOCK_DATA
        if s["score"] >= msco
        and s["rr"] >= mrr
        and s["tier"] in tiers
        and (not ab_only or s["above_200"])
        and s["crash_buy"] > 0
    ]
    st.write(f"Fetching {len(pool)} prices...")
    live = get_prices([s["sym"] for s in pool])
    st.caption(f"{len(live)}/{len(pool)} loaded | {datetime.now().strftime('%H:%M:%S')}")

    rows = []
    for s in pool:
        p = live.get(s["sym"])
        cb = s["crash_buy"]
        rt = s["rot_target"]
        if p is None or cb <= 0 or rt <= 0:
            continue
        d = round((p / cb - 1) * 100, 2)
        l2 = round(cb * (1 - s["avg_drop"] * 0.15 / 100), 2)
        l3 = round(cb * (1 - s["avg_drop"] * 0.30 / 100), 2)
        up = round((rt / p - 1) * 100, 1)
        rows.append({
            **s,
            "live": p,
            "dist": d,
            "l2": l2,
            "l3": l3,
            "sl": round(l3 * 0.95, 2),
            "up": up,
        })

    srt = st.radio("Sort by", ["Closest to zone", "Fastest rebound", "Best upside %", "Highest score"], horizontal=True, key="s1")
    if srt == "Fastest rebound":
        rows.sort(key=lambda x: -x.get("rise_speed", 0))
    elif srt == "Best upside %":
        rows.sort(key=lambda x: -x["up"])
    elif srt == "Highest score":
        rows.sort(key=lambda x: -x["score"])
    else:
        rows.sort(key=lambda x: x["dist"])

    iz = [r for r in rows if -3 <= r["dist"] <= 3]
    nr = [r for r in rows if 3 < r["dist"] <= prox]
    bw = [r for r in rows if r["dist"] < -3]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("In Zone", len(iz))
    c2.metric("Approaching", len(nr))
    c3.metric("Below Zone", len(bw))
    c4.metric("Scanned", len(rows))
    st.divider()

    def show_buy_card(r, css, dc):
        sp = r.get("rise_speed", 0)
        rd = int(r.get("rise_days", 0))
        dd = int(r.get("drop_days", 0))
        elapsed = f"~{round(max(0, (r['live']/r['crash_buy'] - 1) * 100 / sp), 1)}d" if sp > 0 else "-"
        if sp > 0 and r["live"] < r["rot_target"]:
            days_left = f"~{round(max(0, (r['rot_target']/r['live'] - 1) * 100 / sp), 1)}d"
        elif sp > 0:
            days_left = "At target"
        else:
            days_left = "-"
        st.markdown(make_card(r["sym"], r["tier"], r["sector"], r["above_200"], r["dist"], sp, r["score"], r["rr"], r["win_pct"], r["rot_yr"], "LIVE", r["live"], r["crash_buy"], r["l2"], r["l3"], r["sl"], r["rot_target"], r["up"], rd, dd, elapsed, days_left, css, dc), unsafe_allow_html=True)

    if iz:
        st.subheader(f"In Zone ({len(iz)})")
        for r in iz[:25]:
            show_buy_card(r, "cg", "gn")
    else:
        st.info("No stocks within 3% of crash buy.")

    if nr:
        st.subheader(f"Approaching ({len(nr)})")
        for r in nr[:30]:
            show_buy_card(r, "cy", "ye")

    with st.expander(f"Below Zone ({len(bw)})"):
        for r in bw[:25]:
            show_buy_card(r, "cr", "bl")

with tab2:
    st.subheader("Rebound Scanner")
    ca, cb = st.columns(2)
    with ca:
        ab2 = st.checkbox("Above 200DMA only", value=True, key="ra")
        shz = st.checkbox("In Zone", value=True, key="rz")
        sha = st.checkbox("Approaching", value=True, key="rp")
        shb = st.checkbox("Below Zone", value=False, key="rb")
    with cb:
        iopts = ["All Indexes", "Nifty 50", "Next 50", "Nifty 100", "Nifty 200", "Nifty 500", "Midcap 150", "Smallcap 250", "IT", "Bank", "PSU Bank", "Pharma", "Auto", "FMCG", "Metal", "Energy", "Oil & Gas", "Infra", "Financial", "Healthcare", "Realty", "Broader NSE"]
        idx = st.selectbox("Index", iopts, key="ri")
        pr2 = st.slider("Approaching %", 3, 30, 20, key="rpr")

    srt2 = st.radio("Sort by", ["Fastest rebound", "Closest to zone", "Best upside %", "Highest score", "Most rotations/yr"], horizontal=True, key="s2")

    rb2 = []
    for r in REBOUND_DATA:
        tags = r.get("tags", "")
        if ab2 and not r["above"]:
            continue
        if idx != "All Indexes" and idx not in tags:
            continue
        if tags == "Broader NSE" and not (r["above"] and r["price"] >= 20):
            continue
        r2 = dict(r)
        r2["up_scan"] = round((r["target"] / r["price"] - 1) * 100, 1) if r["price"] > 0 else 0
        rb2.append(r2)

    iz2 = [r for r in rb2 if -3 <= r["dist"] <= 3]
    nr2 = [r for r in rb2 if 3 < r["dist"] <= pr2]
    bw2 = [r for r in rb2 if r["dist"] < -3]

    sk = {
        "Fastest rebound": lambda x: -x["speed"],
        "Closest to zone": lambda x: x["dist"],
        "Best upside %": lambda x: -x["up_scan"],
        "Highest score": lambda x: -x["score"],
        "Most rotations/yr": lambda x: -x["roty"],
    }[srt2]

    iz2.sort(key=sk)
    nr2.sort(key=sk)
    bw2.sort(key=sk)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("In Zone", len(iz2))
    c2.metric("Approaching", len(nr2))
    c3.metric("Below Zone", len(bw2))
    c4.metric("Filtered", len(rb2))
    st.divider()

    def show_rebound_card(r, css, dc):
        sp = r.get("speed", 0)
        rd = int(r.get("rdays", 0))
        dd = int(r.get("ddays", 0))
        dlf = f"~{round(max(0, (r['target']/r['price'] - 1) * 100 / sp), 1)}d" if sp > 0 and r["target"] > r["price"] else "-"
        tg = r.get("tags", "").replace("Broader NSE", "").replace(" | ", " ").strip()[:25]
        st.markdown(make_card(r["sym"], tg, "", r["above"], r["dist"], sp, r["score"], r["rr"], r["win"], r["roty"], "SCAN", r["price"], r["l1"], r["l2"], r["l3"], r["sl"], r["target"], r["up_scan"], rd, dd, "-", dlf, css, dc), unsafe_allow_html=True)

    if shz and iz2:
        st.subheader(f"In Zone ({len(iz2)})")
        for r in iz2[:40]:
            show_rebound_card(r, "cg", "gn")

    if sha and nr2:
        st.subheader(f"Approaching ({len(nr2)})")
        for r in nr2[:40]:
            show_rebound_card(r, "cy", "ye")

    if shb and bw2:
        st.subheader(f"Below Zone ({len(bw2)})")
        for r in bw2[:40]:
            show_rebound_card(r, "cb", "bl")

with tab3:
    st.subheader("My Research")
    syms = [w["sym"] for w in MY_WATCHLIST]
    st.write(f"Loading {len(syms)} portfolio prices...")
    wll = get_prices(syms)
    st.caption(f"{len(wll)}/{len(MY_WATCHLIST)} loaded | {datetime.now().strftime('%H:%M:%S')}")

    inv = 0.0
    cur = 0.0
    wins = 0
    losses = 0

    for w in MY_WATCHLIST:
        lp = wll.get(w["sym"])
        qty = w.get("qty", 0)
        entry = w.get("entry", 0)
        if lp is not None and qty > 0:
            inv += qty * entry
            cur += qty * lp
            if lp >= entry:
                wins += 1
            else:
                losses += 1

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tracked", len(MY_WATCHLIST))
    c2.metric("Above entry", wins)
    c3.metric("Below entry", losses)
    if inv > 0:
        pnl = cur - inv
        c4.metric("P&L", f"₹{pnl:+,.0f}", delta=f"{(pnl/inv)*100:+.1f}%")

    st.divider()
    hf = st.selectbox("Portfolio", ["All", "Vikram", "Divya", "Shreya", "Nidhi", "Vivek"])
    s3 = st.radio("Sort by", ["% vs entry", "Symbol", "Upside to target"], horizontal=True, key="s3")

    dl = []
    for w in MY_WATCHLIST:
        holders = w.get("holders", "")
        if hf != "All":
            holder_list = [h.strip() for h in holders.replace(" | ", "·").replace(" · ", "·").split("·") if h.strip()]
            if hf not in holder_list:
                continue

        lp = wll.get(w["sym"])
        chg = ((lp / w["entry"] - 1) * 100) if (lp is not None and w["entry"] > 0) else None
        up = ((w["target"] / lp - 1) * 100) if (lp is not None and lp > 0 and w["target"] > 0) else None
        dl.append({**w, "lp": lp, "chg": chg, "up": up})

    if s3 == "% vs entry":
        dl.sort(key=lambda x: x["chg"] if x["chg"] is not None else -9999, reverse=True)
    elif s3 == "Symbol":
        dl.sort(key=lambda x: x["sym"])
    else:
        dl.sort(key=lambda x: x["up"] if x["up"] is not None else -9999, reverse=True)

    for w in dl:
        sym = w["sym"]
        lp = w["lp"]
        entry = w["entry"]
        tgt = w["target"]
        sl = w["sl"]
        qty = w.get("qty", 0)
        thesis = w.get("thesis", "")
        holders = w.get("holders", "")

        if lp is None:
            st.markdown(f'<div class="card cb"><span class="sym">? {sym}</span><div class="tb">{thesis}</div></div>', unsafe_allow_html=True)
            continue

        chg = w["chg"] if w["chg"] is not None else 0
        tot = ((tgt / lp - 1) * 100) if lp > 0 and tgt > 0 else 0
        tos = ((sl / lp - 1) * 100) if lp > 0 and sl > 0 else 0
        rr = abs(tot / tos) if tos else 0

        if lp >= tgt and tgt > 0:
            css, ic = "ct", "T"
        elif lp >= entry:
            css, ic = "cg", "+"
        elif sl > 0 and lp <= sl:
            css, ic = "cr", "X"
        else:
            css, ic = "cy", "~"

        gc = "gn" if chg >= 0 else "rd"
        vs = f"{qty} shares | ₹{qty*lp:,.0f}" if qty > 0 else "Watching"

        st.markdown(
            f'<div class="card {css}"><span class="sym">{ic} {sym}</span>'
            f'<span class="bx" style="background:#1a2a40;color:#94a3b8">{holders}</span>'
            f'<div class="dt {gc}">{chg:+.2f}% vs entry | R:R {rr:.1f}x</div>'
            f'<div class="mt">{vs}</div>'
            f'<div class="pr">'
            f'<div class="pc"><div class="pl">LIVE</div><div class="pv">₹{lp:,.2f}</div></div>'
            f'<div class="pc"><div class="pl">ENTRY</div><div class="pv">₹{entry:,.2f}</div></div>'
            f'<div class="pc"><div class="pl">TARGET</div><div class="pv" style="color:#2dd4bf">₹{tgt:,.2f} ({tot:+.1f}%)</div></div>'
            f'<div class="pc"><div class="pl">SL</div><div class="pv" style="color:#ef4444">₹{sl:,.2f} ({tos:+.1f}%)</div></div>'
            f'</div><div class="tb">{thesis}</div></div>',
            unsafe_allow_html=True,
        )

    st.caption("GitHub-backed watchlist dashboard")
