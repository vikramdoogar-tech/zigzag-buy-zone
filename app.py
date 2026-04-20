import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json, time, requests
from datetime import datetime

# ─── LOAD DATA FROM GITHUB ───────────────────────────────────────────────────
# These files are in your zigzag-buy-zone GitHub repo
GITHUB_RAW = "https://raw.githubusercontent.com/vikramdoogar-tech/zigzag-buy-zone/main/"

@st.cache_data(ttl=3600)
def load_json(filename):
    url = GITHUB_RAW + filename
    r = requests.get(url, timeout=30)
    return json.loads(r.text)

with st.spinner("Loading scan data..."):
    STOCK_DATA   = load_json("data_stocks.json")
    REBOUND_DATA = load_json("data_rebound.json")
    MY_WATCHLIST = load_json("data_watchlist.json")

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="ZigZag Terminal", page_icon="📡",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
  .main .block-container{padding:1rem 0.75rem;max-width:100%;}
  h1{font-size:1.3rem!important;margin-bottom:0.2rem!important;}
  h3{font-size:1rem!important;}
  .card{background:#0f172a;border-radius:12px;padding:14px 16px;
        margin-bottom:10px;border-left:4px solid #475569;}
  .card-green {border-left-color:#22c55e;background:#052e16;}
  .card-yellow{border-left-color:#eab308;background:#1c1400;}
  .card-red   {border-left-color:#ef4444;background:#1c0505;}
  .card-blue  {border-left-color:#3b82f6;background:#0c1a2e;}
  .card-teal  {border-left-color:#2dd4bf;background:#031a18;}
  .sym{font-size:1.1rem;font-weight:700;color:#f1f5f9;}
  .badge{font-size:0.65rem;background:#1e3a5f;color:#93c5fd;
         border-radius:4px;padding:1px 5px;margin-left:4px;}
  .badge-green{background:#052e16;color:#22c55e;}
  .badge-red  {background:#1c0505;color:#ef4444;}
  .dist{font-size:1.35rem;font-weight:700;margin:4px 0;}
  .green{color:#22c55e;}.yellow{color:#eab308;}
  .red{color:#ef4444;}.blue{color:#60a5fa;}.teal{color:#2dd4bf;}
  .meta{font-size:0.72rem;color:#64748b;margin-bottom:5px;}
  .prow{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px;}
  .pcol{min-width:65px;}
  .plbl{font-size:0.62rem;color:#475569;}
  .pval{font-size:0.85rem;font-weight:600;color:#e2e8f0;}
  .thesis-box{background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.2);
    border-radius:6px;padding:8px 10px;margin-top:8px;font-size:0.76rem;
    color:#c4b5fd;line-height:1.5;}
  #MainMenu,footer,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Scanner Filters")
    prox       = st.slider("Within X% of crash buy", 3, 25, 15)
    min_score  = st.slider("Min Score", 10, 40, 13)
    min_rr     = st.slider("Min R:R", 1.0, 3.0, 1.2, step=0.1)
    tiers      = st.multiselect("Tiers", ["T1","T2","T3","T4"], default=["T1","T2","T3","T4"])
    sectors    = st.multiselect("Sectors",
        sorted(list(set(s.get("sector","") for s in STOCK_DATA if s.get("sector")))), default=[])
    above_only = st.checkbox("Above 200DMA only", False)

st.markdown("# 📡 ZigZag Terminal")
st.caption(f"{len(STOCK_DATA)} scanner · {len(REBOUND_DATA)} rebound · Scan: 4 Mar 2026 · Live NSE")

tab1, tab2, tab3 = st.tabs(["📡  Buy Zone Scanner", "📈  Rebound Scanner", "🔬  My Research"])

# ─── PRICE FETCHER ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_prices(syms):
    out = {}
    for i in range(0, len(syms), 50):
        batch = syms[i:i+50]
        try:
            raw = yf.download([s+".NS" for s in batch], period="1d", interval="1d",
                              auto_adjust=True, progress=False, threads=True)
            if raw.empty: continue
            cl = raw["Close"].iloc[-1] if isinstance(raw.columns, pd.MultiIndex) else raw.iloc[-1]
            for s in batch:
                try:
                    v = cl.get(s+".NS") if hasattr(cl,"get") else cl[s+".NS"]
                    if v is not None and not np.isnan(float(v)):
                        out[s] = round(float(v), 2)
                except: pass
        except: pass
        time.sleep(0.2)
    return out

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — BUY ZONE SCANNER (live prices)
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    pool = [s for s in STOCK_DATA
            if s["score"] >= min_score and s["rr"] >= min_rr
            and s["tier"] in tiers
            and (not above_only or s["above_200"])
            and (not sectors or s.get("sector","") in sectors)]

    with st.spinner(f"Fetching {len(pool)} live prices…"):
        live = get_prices(tuple(s["sym"] for s in pool))

    st.success(f"✓ {len(live)}/{len(pool)} prices — {datetime.now().strftime('%H:%M:%S')} IST")

    rows = []
    for s in pool:
        if s["sym"] not in live: continue
        p=live[s["sym"]]; cb=s["crash_buy"]
        d=round((p/cb-1)*100,2)
        l2=round(cb*(1-s["avg_drop"]*0.15/100),2)
        l3=round(cb*(1-s["avg_drop"]*0.30/100),2)
        rows.append({**s,"live":p,"dist":d,"l2":l2,"l3":l3,
                     "sl":round(l3*0.95,2),"up":round((s["rot_target"]/p-1)*100,1)})

    sort1 = st.radio("⚡ Sort by",
        ["Closest to zone","Fastest rebound","Best upside %","Highest score"],
        horizontal=True, key="s1")
    if sort1=="Fastest rebound":  rows.sort(key=lambda x: -x.get("rise_speed",0))
    elif sort1=="Best upside %":  rows.sort(key=lambda x: -x["up"])
    elif sort1=="Highest score":  rows.sort(key=lambda x: -x["score"])
    else:                         rows.sort(key=lambda x: x["dist"])

    in_z=[r for r in rows if -3<=r["dist"]<=3]
    near=[r for r in rows if  3< r["dist"]<=prox]
    below=[r for r in rows if r["dist"]< -3]

    c1,c2,c3,c4=st.columns(4)
    c1.metric("🟢 In Zone",len(in_z))
    c2.metric("🟡 Approaching",len(near))
    c3.metric("🔵 Below Zone",len(below))
    c4.metric("📊 Scanned",len(rows))
    st.divider()

    def scan_card(r,mode):
        icons={"zone":"🟢","near":"🟡","below":"🔵"}
        css={"zone":"card-green","near":"card-yellow","below":"card-red"}
        dcol={"zone":"green","near":"yellow","below":"blue"}
        sign="+" if r["dist"]>0 else ""
        ab="↑200" if r["above_200"] else "↓200"
        spd=r.get("rise_speed",0)
        st.markdown(f"""<div class="card {css[mode]}">
          <span class="sym">{icons[mode]} {r["sym"]}</span>
          <span class="badge">{r["tier"]}</span>
          <span class="badge">{r.get("sector","")}</span>
          <span class="badge {"badge-green" if r["above_200"] else "badge-red"}">{ab}</span>
          <div class="dist {dcol[mode]}">{sign}{r["dist"]:.2f}% · ⚡{spd:.1f}%/day</div>
          <div class="meta">Score {r["score"]} · R:R {r["rr"]} · Win {int(r["win_pct"])}% · {r["rot_yr"]}×/yr</div>
          <div class="prow">
            <div class="pcol"><div class="plbl">LIVE</div><div class="pval">₹{r["live"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">L1 BUY</div><div class="pval" style="color:#22c55e">₹{r["crash_buy"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">L2</div><div class="pval">₹{r["l2"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">L3</div><div class="pval">₹{r["l3"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">SL</div><div class="pval" style="color:#ef4444">₹{r["sl"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">TARGET</div><div class="pval" style="color:#2dd4bf">₹{r["rot_target"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">UPSIDE</div><div class="pval" style="color:#22c55e">+{r["up"]}%</div></div>
          </div></div>""", unsafe_allow_html=True)

    if in_z:
        st.markdown(f"### 🟢 In Zone ({len(in_z)})")
        for r in in_z[:25]: scan_card(r,"zone")
    else:
        st.info("No stocks within ±3% right now.")
    if near:
        st.markdown(f"### 🟡 Approaching ({len(near)})")
        for r in near[:30]: scan_card(r,"near")
    with st.expander(f"🔵 Below Zone ({len(below)})"):
        for r in below[:25]: scan_card(r,"below")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REBOUND SCANNER (2057 stocks, scan prices)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📈 Full Market Rebound Scanner")
    st.caption(f"{len(REBOUND_DATA)} stocks · All NSE indexes · Scan prices 4 Mar 2026")

    col_a, col_b = st.columns(2)
    with col_a:
        above_200_rb = st.checkbox("🟢 Above 200DMA only", value=True, key="rb_a")
        show_zone    = st.checkbox("Show In Zone (≤3%)",       value=True,  key="rb_z")
        show_appr    = st.checkbox("Show Approaching (3–20%)", value=True,  key="rb_p")
        show_blw     = st.checkbox("Show Below Zone (<−3%)",   value=False, key="rb_b")
    with col_b:
        idx_opts = ["All Indexes","Nifty 50","Next 50","Nifty 100","Nifty 200",
                    "Nifty 500","Midcap 150","Smallcap 250","IT","Bank","PSU Bank",
                    "Pharma","Auto","FMCG","Metal","Energy","Oil & Gas",
                    "Infra","Financial","Healthcare","Realty","Broader NSE"]
        idx_f  = st.selectbox("Index / Sector", idx_opts, key="rb_i")
        prox2  = st.slider("Approaching band %", 3, 30, 20, key="rb_pr")

    sort2 = st.radio("⚡ Sort by",
        ["Fastest rebound","Closest to zone","Best upside %","Highest score","Most rotations/yr"],
        horizontal=True, key="s2")

    rb = [r for r in REBOUND_DATA
          if (not above_200_rb or r["above"])
          and (idx_f=="All Indexes" or idx_f in r["tags"])]

    for r in rb:
        r["up_scan"] = round((r["target"]/r["price"]-1)*100,1) if r["price"]>0 else 0

    in_z2 =[r for r in rb if -3  <=r["dist"]<=3]
    near2 =[r for r in rb if  3  < r["dist"]<=prox2]
    below2=[r for r in rb if     r["dist"]< -3]

    sk = {"Fastest rebound":  lambda x:-x["speed"],
          "Closest to zone":  lambda x:x["dist"],
          "Best upside %":    lambda x:-x["up_scan"],
          "Highest score":    lambda x:-x["score"],
          "Most rotations/yr":lambda x:-x["roty"]}[sort2]
    in_z2.sort(key=sk); near2.sort(key=sk); below2.sort(key=sk)

    c1,c2,c3,c4=st.columns(4)
    c1.metric("🟢 In Zone",len(in_z2))
    c2.metric("🟡 Approaching",len(near2))
    c3.metric("🔵 Below Zone",len(below2))
    c4.metric("Filtered total",len(rb))
    st.divider()

    def rb_card(r):
        d=r["dist"]
        if -3<=d<=3:   css,dcol,icon="card-green","green","🟢"
        elif d<-3:     css,dcol,icon="card-blue","blue","🔵"
        else:          css,dcol,icon="card-yellow","yellow","🟡"
        sign="+" if d>0 else ""
        ab='<span class="badge badge-green">↑200DMA</span>' if r["above"] else '<span class="badge badge-red">↓200DMA</span>'
        tags=r["tags"].replace("Broader NSE","").replace(" | "," ").strip()[:30]
        st.markdown(f"""<div class="card {css}">
          <span class="sym">{icon} {r["sym"]}</span>{ab}
          <span class="badge">{tags}</span>
          <div class="dist {dcol}">{sign}{d:.2f}% · ⚡{r["speed"]:.1f}%/day</div>
          <div class="meta">Score {r["score"]} · R:R {r["rr"]} · Win {r["win"]}% · {r["roty"]}×/yr · Rise {r["rise"]}%</div>
          <div class="prow">
            <div class="pcol"><div class="plbl">SCAN PRICE</div><div class="pval">₹{r["price"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">L1 BUY</div><div class="pval" style="color:#22c55e">₹{r["l1"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">L2</div><div class="pval">₹{r["l2"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">L3</div><div class="pval">₹{r["l3"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">SL</div><div class="pval" style="color:#ef4444">₹{r["sl"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">TARGET</div><div class="pval" style="color:#2dd4bf">₹{r["target"]:,.2f}</div></div>
            <div class="pcol"><div class="plbl">UPSIDE</div><div class="pval" style="color:#22c55e">+{r["up_scan"]}%</div></div>
          </div></div>""", unsafe_allow_html=True)

    MAX=40
    if show_zone and in_z2:
        st.markdown(f"### 🟢 In Buy Zone ({len(in_z2)})")
        st.caption("At crash buy level — GTC should be set")
        for r in in_z2[:MAX]: rb_card(r)
    if show_appr and near2:
        st.markdown(f"### 🟡 Approaching — within {prox2}% ({len(near2)})")
        for r in near2[:MAX]: rb_card(r)
    if show_blw and below2:
        st.markdown(f"### 🔵 Below Zone ({len(below2)})")
        for r in below2[:MAX]: rb_card(r)
    st.divider()
    st.caption("⚠ Prices are scan-date (4 Mar 2026). Use Tab 1 for live prices on 506 key stocks.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MY RESEARCH (5 portfolios)
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    wl_syms = tuple(w["sym"] for w in MY_WATCHLIST)
    with st.spinner(f"Loading {len(wl_syms)} portfolio stocks…"):
        wl_live = get_prices(wl_syms)

    st.success(f"✓ {len(wl_live)}/{len(wl_syms)} — {datetime.now().strftime('%H:%M:%S')} IST")

    inv=0; cur=0; win3=0; los3=0
    for w in MY_WATCHLIST:
        lp=wl_live.get(w["sym"])
        if lp and w.get("qty",0)>0:
            inv+=w["qty"]*w["entry"]; cur+=w["qty"]*lp
        if lp:
            if lp>=w["entry"]: win3+=1
            else: los3+=1

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Tracked",len(MY_WATCHLIST))
    c2.metric("📈 Above entry",win3)
    c3.metric("📉 Below entry",los3)
    if inv>0:
        pnl=cur-inv
        c4.metric("P&L",f"₹{pnl:+,.0f}",delta=f"{pnl/inv*100:+.1f}%")
    st.divider()

    holder_f=st.selectbox("Portfolio",["All","Vikram","Divya","Shreya","Nidhi","Vivek"])
    sort3=st.radio("Sort by",["% vs entry","Symbol","Upside to target"],horizontal=True,key="s3")

    dl=[]
    for w in MY_WATCHLIST:
        if holder_f!="All" and holder_f not in w.get("holders",""):
            continue
        lp=wl_live.get(w["sym"])
        dl.append({**w,"lp":lp,
                   "chg":(lp/w["entry"]-1)*100 if lp else None,
                   "up":(w["target"]/lp-1)*100 if lp else None})

    if sort3=="% vs entry": dl.sort(key=lambda x:x["chg"] if x["chg"] is not None else -999,reverse=True)
    elif sort3=="Symbol":   dl.sort(key=lambda x:x["sym"])
    else:                   dl.sort(key=lambda x:x["up"] if x["up"] is not None else -999,reverse=True)

    for w in dl:
        sym=w["sym"]; entry=w["entry"]; tgt=w["target"]; sl=w["sl"]
        qty=w.get("qty",0); thesis=w.get("thesis",""); holders=w.get("holders","")
        lp=w["lp"]
        if not lp:
            st.markdown(f'''<div class="card card-blue"><span class="sym">⏳ {sym}</span>
            <span class="badge" style="background:#1a2a40;color:#94a3b8">{holders}</span>
            <div class="thesis-box">📝 {thesis}</div></div>''',unsafe_allow_html=True)
            continue
        chg=w["chg"]; to_t=(tgt/lp-1)*100; to_sl=(sl/lp-1)*100
        rr=abs(to_t/to_sl) if to_sl else 0
        if lp>=tgt:     css,icon="card-teal","🎯"
        elif lp>=entry: css,icon="card-green","📈"
        elif lp<=sl:    css,icon="card-red","⛔"
        else:           css,icon="card-yellow","👁"
        chg_col="green" if chg>=0 else "red"
        st.markdown(f"""<div class="card {css}">
          <span class="sym">{icon} {sym}</span>
          <span class="badge" style="background:#1a2a40;color:#94a3b8">{holders}</span>
          <div class="dist {chg_col}">{chg:+.2f}% vs entry · R:R {rr:.1f}x</div>
          <div class="meta">{""+str(qty)+" shares · ₹"+str(f"{qty*lp:,.0f}") if qty>0 else "Watching"}</div>
          <div class="prow">
            <div class="pcol"><div class="plbl">LIVE</div><div class="pval">₹{lp:,.2f}</div></div>
            <div class="pcol"><div class="plbl">ENTRY</div><div class="pval">₹{entry:,.2f}</div></div>
            <div class="pcol"><div class="plbl">TARGET</div><div class="pval" style="color:#2dd4bf">₹{tgt:,.2f} (+{to_t:.1f}%)</div></div>
            <div class="pcol"><div class="plbl">SL</div><div class="pval" style="color:#ef4444">₹{sl:,.2f} ({to_sl:.1f}%)</div></div>
          </div>
          <div class="thesis-box">📝 {thesis}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.caption("35 stocks · 5 portfolios: Vikram · Divya · Shreya · Nidhi · Vivek")
