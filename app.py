import streamlit as st
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Crash Zone System", layout="wide")

st.title("📉 ZigZag Crash Zone Execution System")
st.markdown("From Scanner → To Money-Making Machine")

# ─────────────────────────────────────────────
# LOAD DATA (UPLOAD CSV)
# ─────────────────────────────────────────────
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

uploaded_file = st.file_uploader("Upload your STOCK CSV", type=["csv"])

if uploaded_file is None:
    st.warning("Upload your CSV file to begin")
    st.stop()

df = load_data(uploaded_file)

# ─────────────────────────────────────────────
# REQUIRED COLUMNS CHECK
# ─────────────────────────────────────────────
required_cols = ["sym", "tier", "score", "rr", "crash_buy", "rot_target", "last_high"]

missing = [col for col in required_cols if col not in df.columns]

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

# ─────────────────────────────────────────────
# CALCULATIONS (CORE EDGE)
# ─────────────────────────────────────────────
df["distance_to_buy"] = ((df["crash_buy"] - df["last_high"]) / df["last_high"]) * 100

df["status"] = np.where(
    df["distance_to_buy"] >= -5,
    "🟢 EXECUTE",
    np.where(df["distance_to_buy"] >= -15, "🟡 WATCH", "🔴 IGNORE")
)

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.header("Filters")

tier = st.sidebar.multiselect(
    "Tier",
    options=df["tier"].unique(),
    default=df["tier"].unique()
)

min_rr = st.sidebar.slider("Min RR", 1.0, 30.0, 3.0)
min_score = st.sidebar.slider("Min Score", 0, 400, 25)

capital = st.sidebar.number_input("Total Capital (₹)", value=5000000)

# ─────────────────────────────────────────────
# FILTER LOGIC
# ─────────────────────────────────────────────
filtered = df[df["tier"].isin(tier)]
filtered = filtered[filtered["rr"] >= min_rr]
filtered = filtered[filtered["score"] >= min_score]

filtered = filtered.sort_values(by="score", ascending=False)

# ─────────────────────────────────────────────
# EXECUTION BUCKETS
# ─────────────────────────────────────────────
execute_df = filtered[filtered["status"] == "🟢 EXECUTE"]
watch_df = filtered[filtered["status"] == "🟡 WATCH"]

# ─────────────────────────────────────────────
# CAPITAL ALLOCATION
# ─────────────────────────────────────────────
def allocate(df, capital):
    if len(df) == 0:
        return df
    alloc = capital / len(df)
    df = df.copy()
    df["allocation"] = round(alloc, 0)
    return df

execute_alloc = allocate(execute_df.head(10), capital * 0.4)
watch_alloc = allocate(watch_df.head(10), capital * 0.4)

# ─────────────────────────────────────────────
# DASHBOARD METRICS
# ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

col1.metric("🟢 Execute Stocks", len(execute_df))
col2.metric("🟡 Watch Stocks", len(watch_df))
col3.metric("📊 Total Filtered", len(filtered))

# ─────────────────────────────────────────────
# EXECUTE SECTION
# ─────────────────────────────────────────────
st.subheader("🔥 EXECUTE (Deploy Capital Now)")

if len(execute_alloc) > 0:
    st.dataframe(execute_alloc[[
        "sym", "score", "rr",
        "crash_buy", "rot_target",
        "distance_to_buy", "allocation"
    ]], use_container_width=True)

    st.markdown("### 🎯 Action Plan")
    for _, row in execute_alloc.iterrows():
        st.markdown(f"""
        **{row['sym']}**  
        Buy Near: ₹{row['crash_buy']}  
        Target: ₹{row['rot_target']}  
        Allocate: ₹{int(row['allocation'])}
        """)
else:
    st.info("No execute stocks right now")

# ─────────────────────────────────────────────
# WATCH SECTION
# ─────────────────────────────────────────────
st.subheader("🟡 WATCH (Prepare Capital)")

if len(watch_alloc) > 0:
    st.dataframe(watch_alloc[[
        "sym", "score", "rr",
        "crash_buy", "distance_to_buy"
    ]], use_container_width=True)
else:
    st.info("No watch stocks")

# ─────────────────────────────────────────────
# FULL DATA
# ─────────────────────────────────────────────
st.subheader("📊 Full Data")

st.dataframe(filtered, use_container_width=True)

# ─────────────────────────────────────────────
# RULES (VISIBLE DAILY DISCIPLINE)
# ─────────────────────────────────────────────
st.markdown("---")
st.subheader("⚠️ Trading Rules")

st.markdown("""
- Max 10% capital per stock  
- Book 50% profit at +25–40%  
- Exit fully at rotation target  
- Stop loss: -8% strict  
- Max portfolio drawdown: -10%  
""")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption("Built for disciplined execution 🚀")
