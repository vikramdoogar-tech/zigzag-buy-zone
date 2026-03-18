import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Crash Zone Scanner", layout="wide")

# ─── CACHE DATA ─────────────────────────────────────
@st.cache_data
def load_data():
    return pd.DataFrame(STOCK_DATA)

# ─── TITLE ──────────────────────────────────────────
st.title("📉 ZigZag Crash Zone Scanner")
st.markdown("Find high probability crash-recovery stocks")

# ─── LOAD DATA ──────────────────────────────────────
df = load_data()

# ─── SIDEBAR FILTERS ────────────────────────────────
st.sidebar.header("Filters")

tier = st.sidebar.multiselect(
    "Select Tier",
    options=df["tier"].unique(),
    default=df["tier"].unique()
)

min_rr = st.sidebar.slider("Min Risk Reward", 1.0, 30.0, 3.0)
min_score = st.sidebar.slider("Min Score", 0, 400, 25)

above_200 = st.sidebar.selectbox("Above 200 DMA", ["All", "Yes", "No"])

# ─── FILTER LOGIC ───────────────────────────────────
filtered = df[df["tier"].isin(tier)]
filtered = filtered[filtered["rr"] >= min_rr]
filtered = filtered[filtered["score"] >= min_score]

if above_200 == "Yes":
    filtered = filtered[filtered["above_200"] == True]
elif above_200 == "No":
    filtered = filtered[filtered["above_200"] == False]

# ─── SORT ───────────────────────────────────────────
filtered = filtered.sort_values(by="score", ascending=False)

# ─── DISPLAY ────────────────────────────────────────
st.subheader(f"Results: {len(filtered)} Stocks")

st.dataframe(
    filtered[[
        "sym", "tier", "score", "rr",
        "crash_buy", "rot_target",
        "win_pct", "above_200"
    ]],
    use_container_width=True
)

# ─── TOP PICKS ──────────────────────────────────────
st.subheader("🔥 Top Opportunities")

top = filtered.head(10)

for _, row in top.iterrows():
    st.markdown(f"""
    **{row['sym']}**  
    Score: {row['score']} | RR: {row['rr']}  
    Buy Zone: ₹{row['crash_buy']} → Target: ₹{row['rot_target']}
    """)

# ─── FOOTER ─────────────────────────────────────────
st.markdown("---")
st.caption("Built for Vikram's Crash Rotation System 🚀")
