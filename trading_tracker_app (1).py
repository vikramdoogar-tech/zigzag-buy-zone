import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import gspread
from google.oauth2.service_account import Credentials
import requests, base64
from datetime import datetime

COLUMNS = [
    "script", "nse_symbol", "qty", "buy_price",
    "long_sl", "short_sl",
    "short_tgt", "long_tgt", "intermediate", "final_tgt",
]
NUMERIC_COLS = ["qty","buy_price","long_sl","short_sl","short_tgt","long_tgt","intermediate","final_tgt"]

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="ZigZag Tracker", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

# ─── STYLE ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
:root{--bg:#0a0e1a;--surface:#111827;--card:#151d2e;--border:#1e2d45;--accent:#00d4ff;--accent2:#00ff9d;--danger:#ff4444;--warning:#ffaa00;--text:#e2e8f0;--muted:#64748b;--mono:'IBM Plex Mono',monospace;--sans:'IBM Plex Sans',sans-serif;}
html,body,[class*="css"]{background-color:var(--bg)!important;color:var(--text)!important;font-family:var(--sans)!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1.5rem 2rem!important;max-width:100%!important;}
.app-header{display:flex;align-items:center;gap:16px;padding:18px 0 24px;border-bottom:1px solid var(--border);margin-bottom:24px;}
.app-logo{width:42px;height:42px;background:linear-gradient(135deg,var(--accent),var(--accent2));border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;}
.app-title{font-family:var(--mono);font-size:22px;font-weight:700;color:var(--accent);letter-spacing:-0.5px;}
.app-sub{font-size:12px;color:var(--muted);font-family:var(--mono);margin-top:2px;}
.metric-card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px 18px;position:relative;overflow:hidden;}
.metric-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;}
.metric-card.blue::before{background:var(--accent);}.metric-card.green::before{background:var(--accent2);}
.metric-card.red::before{background:var(--danger);}.metric-card.orange::before{background:var(--warning);}
.metric-card.purple::before{background:#a78bfa;}
.metric-label{font-size:10px;color:var(--muted);font-family:var(--mono);text-transform:uppercase;letter-spacing:1px;}
.metric-value{font-size:22px;font-weight:700;font-family:var(--mono);margin-top:4px;}
.metric-value.blue{color:var(--accent);}.metric-value.green{color:var(--accent2);}.metric-value.red{color:var(--danger);}.metric-value.orange{color:var(--warning);}.metric-value.purple{color:#a78bfa;}
.signal-bar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;}
.signal-pill{display:flex;align-items:center;gap:8px;padding:8px 14px;border-radius:50px;font-family:var(--mono);font-size:12px;font-weight:600;border:1px solid;animation:pulse 2s infinite;}
.signal-pill.danger{background:rgba(255,68,68,0.12);border-color:var(--danger);color:var(--danger);}
.signal-pill.breakout{background:rgba(0,255,157,0.12);border-color:var(--accent2);color:var(--accent2);}
.signal-pill.warning{background:rgba(255,170,0,0.12);border-color:var(--warning);color:var(--warning);}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.7;}}
.tracker-table{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:24px;}
.table-header-row,.table-row,.totals-row{display:grid;grid-template-columns:140px 60px 85px 85px 85px 85px 85px 85px 75px 90px 90px 90px 105px;padding:0 12px;}
.table-header-row{background:var(--surface);border-bottom:1px solid var(--border);}
.th{padding:10px 6px;font-family:var(--mono);font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;text-align:right;}
.th:first-child{text-align:left;}
.table-row{border-bottom:1px solid rgba(30,45,69,0.5);align-items:center;transition:background 0.15s;}
.table-row:hover{background:rgba(0,212,255,0.04);}
.table-row:last-child{border-bottom:none;}
.td{padding:11px 6px;font-family:var(--mono);font-size:11px;text-align:right;}
.td.name{text-align:left;font-weight:600;color:var(--text);font-size:12px;}
.td.price-live{font-weight:700;color:var(--accent);}
.td.sl{color:var(--danger);}.td.tgt{color:var(--accent2);}
.td.loss-val{color:var(--danger);}.td.profit-val{color:var(--accent2);}
.td.exposure{color:var(--warning);font-weight:600;}
.signal-icon{text-align:center!important;font-size:14px;}
.score-badge{display:inline-flex;align-items:center;justify-content:center;width:36px;height:20px;border-radius:4px;font-family:var(--mono);font-size:10px;font-weight:700;}
.score-danger{background:rgba(255,68,68,0.2);color:var(--danger);border:1px solid rgba(255,68,68,0.4);}
.score-warning{background:rgba(255,170,0,0.2);color:var(--warning);border:1px solid rgba(255,170,0,0.4);}
.score-ok{background:rgba(100,116,139,0.2);color:var(--muted);border:1px solid rgba(100,116,139,0.3);}
.score-breakout{background:rgba(0,255,157,0.2);color:var(--accent2);border:1px solid rgba(0,255,157,0.4);}
.totals-row{background:var(--surface);border-top:1px solid var(--border);align-items:center;}
.totals-row .td{font-weight:700;font-size:11px;}
.form-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:20px;}
.form-title{font-family:var(--mono);font-size:13px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;}
div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input{background:var(--surface)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:6px!important;font-family:var(--mono)!important;font-size:12px!important;}
label{color:var(--muted)!important;font-size:11px!important;font-family:var(--mono)!important;}
div[data-testid="stButton"] button{background:linear-gradient(135deg,var(--accent),#0099bb)!important;color:#000!important;font-weight:700!important;font-family:var(--mono)!important;font-size:12px!important;border:none!important;border-radius:7px!important;}
section[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}
section[data-testid="stSidebar"] *{color:var(--text)!important;}
div[data-testid="stTabs"] button{font-family:var(--mono)!important;font-size:11px!important;color:var(--muted)!important;}
div[data-testid="stTabs"] button[aria-selected="true"]{color:var(--accent)!important;border-bottom-color:var(--accent)!important;}
div[data-testid="stExpander"]{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:8px!important;}
.setup-step{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px 20px;margin-bottom:12px;display:flex;gap:16px;align-items:flex-start;}
.step-num{width:28px;height:28px;border-radius:50%;background:var(--accent);color:#000;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-weight:700;font-size:13px;flex-shrink:0;}
.step-title{font-family:var(--mono);font-weight:600;color:var(--text);margin-bottom:4px;}
.step-desc{font-size:12px;color:var(--muted);line-height:1.6;}
</style>
""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS ────────────────────────────────────────────────────────────
def get_worksheet():
    creds_dict = dict(st.secrets["gcp_service_account"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    sh     = client.open_by_key(st.secrets["google_sheet"]["sheet_id"])
    try:
        ws = sh.worksheet("Positions")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet("Positions", rows=500, cols=20)
        ws.append_row(COLUMNS)
    return ws

@st.cache_data(ttl=60)
def load_data():
    try:
        ws      = get_worksheet()
        records = ws.get_all_records()
        if not records:
            return pd.DataFrame(columns=COLUMNS)
        df = pd.DataFrame(records)
        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    try:
        ws = get_worksheet()
        ws.clear()
        df = df.copy().fillna("")
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        data = [COLUMNS] + df[COLUMNS].astype(str).values.tolist()
        ws.update(data, value_input_option="USER_ENTERED")
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Save failed: {e}")
        return False

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fmt_inr(v):
    try:
        v = float(v)
        if np.isnan(v) or v==0: return "—"
        if abs(v)>=1e7: return f"₹{v/1e7:.2f}Cr"
        if abs(v)>=1e5: return f"₹{v/1e5:.1f}L"
        return f"₹{v:,.0f}"
    except: return "—"

def fmt_price(v):
    try:
        v = float(v)
        if np.isnan(v) or v==0: return "—"
        return f"₹{v:,.2f}"
    except: return "—"

@st.cache_data(ttl=300)
def fetch_live_prices(symbols_tuple):
    prices = {}
    for sym in symbols_tuple:
        if not sym or str(sym).strip()=="": continue
        try:
            ticker = str(sym).strip().upper()
            if not ticker.endswith(".NS"): ticker+=".NS"
            data = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
            if data is not None and not data.empty:
                prices[sym] = float(data["Close"].iloc[-1])
        except: pass
    return prices

def compute_signal(row, live, threshold_pct):
    if pd.isna(live) or live==0: return "ok",0,None,None
    short_sl  = float(row.get("short_sl",0) or 0)
    short_tgt = float(row.get("short_tgt",0) or 0)
    sl_pct = (live-short_sl)/short_sl*100 if short_sl>0 else None
    tgt_pct= (short_tgt-live)/live*100    if short_tgt>0 else None
    if sl_pct is not None and sl_pct<=threshold_pct:
        return "danger",  (100 if sl_pct<=0 else int(100-(sl_pct/threshold_pct)*50)), sl_pct, tgt_pct
    if tgt_pct is not None and tgt_pct<=threshold_pct:
        return "breakout",(100 if tgt_pct<=0 else int(100-(tgt_pct/threshold_pct)*50)), sl_pct, tgt_pct
    if sl_pct is not None and sl_pct<=threshold_pct*2:
        return "warning", int(30-(sl_pct/(threshold_pct*2))*20), sl_pct, tgt_pct
    return "ok",0,sl_pct,tgt_pct

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""<div class="app-header">
  <div class="app-logo">📡</div>
  <div>
    <div class="app-title">ZIGZAG ROTATION TRACKER</div>
    <div class="app-sub">NSE Live Feed · Signal Intelligence · Google Sheets Backend</div>
  </div>
</div>""", unsafe_allow_html=True)

# ─── GITHUB PUSH ─────────────────────────────────────────────────────────────
def push_excel_to_github(filepath):
    """Push a local Excel file to GitHub repo via API."""
    try:
        token = st.secrets["github"]["token"]
        repo  = st.secrets["github"]["repo"]
        fname = os.path.basename(filepath)
        url   = f"https://api.github.com/repos/{repo}/contents/{fname}"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

        # Read file as base64
        with open(filepath, "rb") as f:
            content = base64.b64encode(f.read()).decode()

        # Get current SHA (needed for update)
        r = requests.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None

        msg = f"Auto-update: {fname} — {datetime.now().strftime('%d %b %Y %H:%M')}"
        payload = {"message": msg, "content": content}
        if sha:
            payload["sha"] = sha

        resp = requests.put(url, headers=headers, json=payload)
        if resp.status_code in [200, 201]:
            return True, msg
        else:
            return False, resp.json().get("message", "Unknown error")
    except Exception as e:
        return False, str(e)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    threshold_pct = st.slider("Alert Threshold (%)", 1.0, 10.0, 3.0, 0.5,
        help="Signal fires when price is within this % of SL or Target")
    st.markdown("---")
    if st.button("🔄 Refresh Prices", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.markdown("---")

    # ── GitHub Push ──
    if "github" in st.secrets:
        st.markdown("### 📤 GitHub Sync")
        excel_file = "client_tracker_v3.xlsx"
        if os.path.exists(excel_file):
            if st.button("📤 Push Excel to GitHub", use_container_width=True):
                with st.spinner("Pushing to GitHub..."):
                    ok, msg = push_excel_to_github(excel_file)
                if ok:
                    st.success(f"✅ Pushed!\n{msg}")
                else:
                    st.error(f"❌ Failed: {msg}")
        else:
            st.caption("⚠️ client_tracker_v3.xlsx not found in app folder")
        st.markdown("---")

    st.markdown("<span style='font-size:10px;color:#64748b;font-family:monospace'>ZigZag Rotation Tracker<br>NSE · yfinance · Google Sheets</span>", unsafe_allow_html=True)

# ─── SECRETS CHECK — show setup guide if not configured ──────────────────────
secrets_ok = ("gcp_service_account" in st.secrets and "google_sheet" in st.secrets)

if not secrets_ok:
    st.warning("⚠️ Google Sheets not configured. Complete the one-time setup below.")
    steps = [
        ("Create a Google Sheet",
         "Go to sheets.google.com → New spreadsheet → rename it <b>ZigZag Tracker</b>. Copy the Sheet ID from the URL — it's the long string between <code>/d/</code> and <code>/edit</code>."),
        ("Enable APIs in Google Cloud",
         "Go to console.cloud.google.com → Create a new project → search and enable <b>Google Sheets API</b> and <b>Google Drive API</b>."),
        ("Create a Service Account + download JSON key",
         "IAM & Admin → Service Accounts → Create Service Account (any name) → Done. Then click the account → Keys tab → Add Key → JSON → download the file."),
        ("Share your Sheet with the service account",
         "Open your Google Sheet → Share → paste the service account email from the JSON file (looks like <code>name@project.iam.gserviceaccount.com</code>) → give <b>Editor</b> access."),
        ("Add Secrets in Streamlit Cloud",
         "In Streamlit Cloud → your app → ⋮ menu → Settings → Secrets → paste the template below, filled with your values → Save."),
        ("Reboot the app",
         "After saving secrets → Reboot app from Streamlit Cloud dashboard. Done — the tracker connects automatically."),
    ]
    for i,(title,desc) in enumerate(steps,1):
        st.markdown(f"""<div class="setup-step">
            <div class="step-num">{i}</div>
            <div><div class="step-title">{title}</div><div class="step-desc">{desc}</div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### 📋 Paste this into Streamlit Secrets (fill in your values)")
    st.code("""[google_sheet]
sheet_id = "PASTE_YOUR_SHEET_ID_HERE"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = \"\"\"-----BEGIN RSA PRIVATE KEY-----
YOUR PRIVATE KEY LINES HERE
-----END RSA PRIVATE KEY-----\"\"\"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-sa%40your-project.iam.gserviceaccount.com"
""", language="toml")
    st.stop()

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
df = load_data()

tab1, tab2, tab3 = st.tabs(["📊 Live Tracker", "➕ Add / Edit Positions", "📥 Bulk Upload"])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — LIVE TRACKER
# ═══════════════════════════════════════════════════════════════════════════
with tab1:
    if df.empty:
        st.info("No positions yet. Go to **Add / Edit Positions** to add your first trade.")
    else:
        symbols = tuple(df["nse_symbol"].dropna().astype(str).str.strip().tolist())
        with st.spinner("Fetching live NSE prices..."):
            live_prices = fetch_live_prices(symbols)

        rows_enriched = []
        for _, row in df.iterrows():
            sym  = str(row.get("nse_symbol","")).strip()
            live = live_prices.get(sym, np.nan)
            signal, score, sl_pct, tgt_pct = compute_signal(row.to_dict(), live, threshold_pct)
            qty      = float(row.get("qty",0) or 0)
            buy      = float(row.get("buy_price",0) or 0)
            ssl_v    = float(row.get("short_sl",0) or 0)
            stgt_v   = float(row.get("short_tgt",0) or 0)
            exposure     = qty*buy
            short_loss   = qty*(ssl_v-buy)   if ssl_v  else np.nan
            short_profit = qty*(stgt_v-buy)  if stgt_v else np.nan
            live_pnl     = qty*(live-buy)    if not pd.isna(live) else np.nan
            rows_enriched.append({**row.to_dict(),
                "live":live,"signal":signal,"score":score,
                "exposure":exposure,"short_loss":short_loss,
                "short_profit":short_profit,"live_pnl":live_pnl})

        edf = pd.DataFrame(rows_enriched)
        edf["_o"] = edf["signal"].map({"danger":0,"breakout":1,"warning":2,"ok":3})
        edf = edf.sort_values(["_o","score"],ascending=[True,False]).reset_index(drop=True)

        danger_list   = edf[edf["signal"]=="danger"]["script"].tolist()
        breakout_list = edf[edf["signal"]=="breakout"]["script"].tolist()
        warning_list  = edf[edf["signal"]=="warning"]["script"].tolist()

        if danger_list or breakout_list or warning_list:
            pills = '<div class="signal-bar">'
            for s in danger_list:   pills+=f'<div class="signal-pill danger">🔴 {s} — NEAR SL ZONE</div>'
            for s in breakout_list: pills+=f'<div class="signal-pill breakout">🟢 {s} — BREAKOUT WATCH</div>'
            for s in warning_list:  pills+=f'<div class="signal-pill warning">🟡 {s} — APPROACHING SL</div>'
            pills+="</div>"
            st.markdown(pills, unsafe_allow_html=True)

        te=edf["exposure"].sum(); tp=edf["live_pnl"].sum()
        tsl=edf["short_loss"].sum(); tsp=edf["short_profit"].sum()
        asig=len(danger_list)+len(breakout_list)

        m1,m2,m3,m4,m5=st.columns(5)
        with m1: st.markdown(f'<div class="metric-card blue"><div class="metric-label">Total Exposure</div><div class="metric-value blue">{fmt_inr(te)}</div></div>',unsafe_allow_html=True)
        with m2:
            pc="green" if tp>=0 else "red"; ps="+" if tp>=0 else ""
            st.markdown(f'<div class="metric-card {pc}"><div class="metric-label">Live P&L</div><div class="metric-value {pc}">{ps}{fmt_inr(tp)}</div></div>',unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card red"><div class="metric-label">Short Term Risk</div><div class="metric-value red">{fmt_inr(tsl)}</div></div>',unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="metric-card green"><div class="metric-label">ST TGT Profit</div><div class="metric-value green">{fmt_inr(tsp)}</div></div>',unsafe_allow_html=True)
        with m5:
            sc="orange" if asig>0 else "purple"
            st.markdown(f'<div class="metric-card {sc}"><div class="metric-label">Active Signals</div><div class="metric-value {sc}">{asig}</div></div>',unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)

        tbl='<div class="tracker-table">'
        tbl+='''<div class="table-header-row">
            <div class="th">Script</div><div class="th">Sig</div>
            <div class="th">Live ₹</div><div class="th">Buy ₹</div>
            <div class="th">Short SL</div><div class="th">Long SL</div>
            <div class="th">ST TGT</div><div class="th">LT TGT</div>
            <div class="th">Score</div>
            <div class="th">ST Loss</div><div class="th">ST Profit</div>
            <div class="th">Live P&L</div><div class="th">Exposure</div>
        </div>'''

        for _,r in edf.iterrows():
            sig=r["signal"]; sc=r["score"]
            if sig=="danger":    icon="🔴"; bc="score-danger"
            elif sig=="breakout":icon="🟢"; bc="score-breakout"
            elif sig=="warning": icon="🟡"; bc="score-warning"
            else:                icon="⚪"; bc="score-ok"
            lpnl=r.get("live_pnl",np.nan)
            pc="profit-val" if (not pd.isna(lpnl) and lpnl>=0) else "loss-val"
            ps="+" if (not pd.isna(lpnl) and lpnl>=0) else ""
            tbl+=f'''<div class="table-row">
                <div class="td name">{r["script"]}</div>
                <div class="td signal-icon">{icon}</div>
                <div class="td price-live">{fmt_price(r.get("live"))}</div>
                <div class="td">{fmt_price(r.get("buy_price"))}</div>
                <div class="td sl">{fmt_price(r.get("short_sl"))}</div>
                <div class="td sl">{fmt_price(r.get("long_sl"))}</div>
                <div class="td tgt">{fmt_price(r.get("short_tgt"))}</div>
                <div class="td tgt">{fmt_price(r.get("long_tgt"))}</div>
                <div class="td"><span class="score-badge {bc}">{sc}</span></div>
                <div class="td loss-val">{fmt_inr(r.get("short_loss"))}</div>
                <div class="td profit-val">{fmt_inr(r.get("short_profit"))}</div>
                <div class="td {pc}">{ps}{fmt_inr(lpnl)}</div>
                <div class="td exposure">{fmt_inr(r.get("exposure"))}</div>
            </div>'''

        tbl+=f'''<div class="totals-row">
            <div class="td" style="color:#64748b;font-size:10px;">TOTAL ({len(edf)})</div>
            <div class="td"></div><div class="td"></div><div class="td"></div>
            <div class="td"></div><div class="td"></div><div class="td"></div>
            <div class="td"></div><div class="td"></div>
            <div class="td loss-val">{fmt_inr(tsl)}</div>
            <div class="td profit-val">{fmt_inr(tsp)}</div>
            <div class="td {'profit-val' if tp>=0 else 'loss-val'}">{'+' if tp>=0 else ''}{fmt_inr(tp)}</div>
            <div class="td exposure">{fmt_inr(te)}</div>
        </div></div>'''
        st.markdown(tbl, unsafe_allow_html=True)

        with st.expander("📐 Signal Score Guide"):
            st.markdown(f"""
| Badge | Signal | Trigger |
|---|---|---|
| 🔴 | NEAR SL ZONE | Price within **{threshold_pct}%** of Short Term SL |
| 🟢 | BREAKOUT WATCH | Price within **{threshold_pct}%** of Short Term TGT |
| 🟡 | APPROACHING SL | Price within **{threshold_pct*2:.0f}%** of Short Term SL |
| ⚪ | OK | Safe — no action needed |

Score 0–100. Higher = more urgent. 100 = level already breached.
Adjust threshold in the sidebar.""")

        with st.expander("🗑️ Remove a Position"):
            to_del = st.selectbox("Select script to remove", df["script"].tolist())
            if st.button("Remove Position", type="primary"):
                df = df[df["script"]!=to_del].reset_index(drop=True)
                if save_data(df):
                    st.success(f"Removed {to_del}"); st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — ADD / EDIT
# ═══════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="form-card"><div class="form-title">➕ Add New Position</div>', unsafe_allow_html=True)
    with st.form("add_form", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        with c1:
            script    =st.text_input("Script Name",placeholder="e.g. Chambal Fert")
            nse_symbol=st.text_input("NSE Symbol", placeholder="e.g. CHAMBLFERT")
            qty       =st.number_input("Quantity",min_value=1,value=100,step=1)
        with c2:
            buy_price=st.number_input("Buy Price ₹",    min_value=0.01,value=100.0,step=0.05)
            long_sl  =st.number_input("Long Term SL ₹", min_value=0.01,value=90.0, step=0.05)
            short_sl =st.number_input("Short Term SL ₹",min_value=0.01,value=95.0, step=0.05)
        with c3:
            short_tgt   =st.number_input("Short Term TGT ₹",        min_value=0.01,value=115.0,step=0.05)
            long_tgt    =st.number_input("Long Term TGT ₹",          min_value=0.01,value=140.0,step=0.05)
            intermediate=st.number_input("Intermediate TGT ₹ (opt)", min_value=0.0, value=0.0,  step=0.05)
            final_tgt   =st.number_input("Final TGT ₹ (opt)",        min_value=0.0, value=0.0,  step=0.05)
        if st.form_submit_button("Add Position", use_container_width=True):
            if not script or not nse_symbol:
                st.error("Script name and NSE symbol are required.")
            elif script in df["script"].values:
                st.warning(f"'{script}' already exists. Use the Edit section below.")
            else:
                new_row={"script":script.strip(),"nse_symbol":nse_symbol.strip().upper(),
                         "qty":qty,"buy_price":buy_price,"long_sl":long_sl,"short_sl":short_sl,
                         "short_tgt":short_tgt,"long_tgt":long_tgt,
                         "intermediate":intermediate if intermediate>0 else "",
                         "final_tgt":final_tgt if final_tgt>0 else ""}
                df=pd.concat([df,pd.DataFrame([new_row])],ignore_index=True)
                if save_data(df): st.success(f"✅ {script} added!"); st.rerun()
    st.markdown("</div>",unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<div class="form-card"><div class="form-title">✏️ Edit Existing Position</div>',unsafe_allow_html=True)
        es=st.selectbox("Select position to edit",df["script"].tolist())
        er=df[df["script"]==es].iloc[0]
        with st.form("edit_form"):
            ec1,ec2,ec3=st.columns(3)
            with ec1:
                e_nse=st.text_input("NSE Symbol",value=str(er.get("nse_symbol","")))
                e_qty=st.number_input("Quantity",value=int(float(er.get("qty",100) or 100)),step=1)
                e_buy=st.number_input("Buy Price ₹",value=float(er.get("buy_price",0) or 0),step=0.05)
            with ec2:
                e_lsl =st.number_input("Long SL ₹",  value=float(er.get("long_sl",0) or 0), step=0.05)
                e_ssl =st.number_input("Short SL ₹", value=float(er.get("short_sl",0) or 0),step=0.05)
                e_stgt=st.number_input("Short TGT ₹",value=float(er.get("short_tgt",0) or 0),step=0.05)
            with ec3:
                e_ltgt =st.number_input("Long TGT ₹",       value=float(er.get("long_tgt",0) or 0),     step=0.05)
                e_inter=st.number_input("Intermediate TGT ₹",value=float(er.get("intermediate",0) or 0), step=0.05)
                e_final=st.number_input("Final TGT ₹",       value=float(er.get("final_tgt",0) or 0),    step=0.05)
            if st.form_submit_button("Update Position",use_container_width=True):
                idx=df[df["script"]==es].index[0]
                df.at[idx,"nse_symbol"]  =e_nse.strip().upper()
                df.at[idx,"qty"]         =e_qty
                df.at[idx,"buy_price"]   =e_buy
                df.at[idx,"long_sl"]     =e_lsl
                df.at[idx,"short_sl"]    =e_ssl
                df.at[idx,"short_tgt"]   =e_stgt
                df.at[idx,"long_tgt"]    =e_ltgt
                df.at[idx,"intermediate"]=e_inter if e_inter>0 else ""
                df.at[idx,"final_tgt"]   =e_final if e_final>0 else ""
                if save_data(df): st.success(f"✅ {es} updated!"); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — BULK UPLOAD
# ═══════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="form-card"><div class="form-title">📥 Bulk Upload via Excel / CSV</div>',unsafe_allow_html=True)
    st.markdown("""
Upload Excel or CSV with columns: `script` · `nse_symbol` · `qty` · `buy_price` · `long_sl` · `short_sl` · `short_tgt` · `long_tgt` · `intermediate` · `final_tgt`

NSE symbols without `.NS` suffix. Same script name overwrites existing row.
""")
    uploaded=st.file_uploader("Drop Excel or CSV here",type=["xlsx","xls","csv"])
    if uploaded:
        try:
            udf=pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
            udf.columns=[c.strip().lower().replace(" ","_") for c in udf.columns]
            required=["script","nse_symbol","qty","buy_price","long_sl","short_sl","short_tgt","long_tgt"]
            missing=[c for c in required if c not in udf.columns]
            if missing:
                st.error(f"Missing columns: {', '.join(missing)}")
            else:
                st.success(f"✅ {len(udf)} rows detected. Preview:")
                st.dataframe(udf.head(10),use_container_width=True)
                mode=st.radio("Import mode",["Append (keep existing, add new)","Replace all (wipe current data)"])
                if st.button("Confirm Import",type="primary"):
                    if "Replace" in mode:
                        df=udf
                    else:
                        existing=df["script"].tolist()
                        for _,row in udf[udf["script"].isin(existing)].iterrows():
                            idx=df[df["script"]==row["script"]].index[0]
                            for col in udf.columns:
                                if col in df.columns: df.at[idx,col]=row[col]
                        df=pd.concat([df,udf[~udf["script"].isin(existing)]],ignore_index=True)
                    if save_data(df): st.success(f"✅ Import complete! {len(df)} total positions."); st.rerun()
        except Exception as e: st.error(f"Error: {e}")

    st.markdown("---")
    tpl=pd.DataFrame({"script":["Chambal Fert","Dredging Corp","Yes Bank"],
        "nse_symbol":["CHAMBLFERT","DREDGECORP","YESBANK"],
        "qty":[5250,1000,62000],"buy_price":[445,965,20.24],
        "long_sl":[410,847,16],"short_sl":[415,906,18.33],
        "short_tgt":[469,1050,21.6],"long_tgt":[586,1135,24.3],
        "intermediate":["","",""],"final_tgt":[740,1245,27]})
    st.download_button("⬇️ Download CSV Template",tpl.to_csv(index=False).encode(),"zigzag_template.csv","text/csv")
    st.markdown("</div>",unsafe_allow_html=True)
