import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json, time, requests
from datetime import datetime

G = "https://raw.githubusercontent.com/vikramdoogar-tech/zigzag-buy-zone/main/"

def gj(f):
    try: return json.loads(requests.get(G+f,timeout=30).text)
    except: return []

_SD=gj("data_stocks_slim.json")
STOCK_DATA=[{"sym":r["s"],"tier":r["t"],"sector":r["x"],"score":r["sc"],
             "avg_drop":r["ad"],"crash_buy":r["cb"],"rot_target":r["rt"],
             "win_pct":r["wp"],"rr":r["rr"],"rot_yr":r["ry"],
             "above_200":r["a2"],"rise_days":r["rd"],"drop_days":r["dd"],
             "rise_speed":r["sp"]} for r in _SD]
REBOUND_DATA=gj("data_rebound.json")
MY_WATCHLIST=gj("data_watchlist.json")

st.set_page_config(page_title="ZigZag Terminal",page_icon="X",
                   layout="wide",initial_sidebar_state="collapsed")

st.markdown("""<style>
.main .block-container{padding:1rem 0.75rem;max-width:100%;}
.card{background:#0f172a;border-radius:12px;padding:14px 16px;margin-bottom:10px;border-left:4px solid #475569;}
.cg{border-left-color:#22c55e;background:#052e16;}
.cy{border-left-color:#eab308;background:#1c1400;}
.cr{border-left-color:#ef4444;background:#1c0505;}
.cb{border-left-color:#3b82f6;background:#0c1a2e;}
.ct{border-left-color:#2dd4bf;background:#031a18;}
.sym{font-size:1.1rem;font-weight:700;color:#f1f5f9;}
.bx{font-size:0.65rem;background:#1e3a5f;color:#93c5fd;border-radius:4px;padding:1px 5px;margin-left:4px;}
.bg{background:#052e16;color:#22c55e;}.br{background:#1c0505;color:#ef4444;}
.dt{font-size:1.35rem;font-weight:700;margin:4px 0;}
.gn{color:#22c55e;}.ye{color:#eab308;}.rd{color:#ef4444;}.bl{color:#60a5fa;}.tl{color:#2dd4bf;}
.mt{font-size:0.72rem;color:#64748b;margin-bottom:5px;}
.pr{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px;}
.pc{min-width:65px;}.pl{font-size:0.62rem;color:#475569;}
.pv{font-size:0.85rem;font-weight:600;color:#e2e8f0;}
.tb{background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.2);border-radius:6px;padding:8px;margin-top:8px;font-size:0.76rem;color:#c4b5fd;}
#MainMenu,footer,header{visibility:hidden;}
</style>""",unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Filters")
    prox=st.slider("Within X% of crash buy",3,25,15)
    msco=st.slider("Min Score",10,40,13)
    mrr=st.slider("Min R:R",1.0,3.0,1.2,step=0.1)
    tiers=st.multiselect("Tiers",["T1","T2","T3","T4"],default=["T1","T2","T3","T4"])
    ab_only=st.checkbox("Above 200DMA only",False)

st.markdown("# ZigZag Terminal")
st.caption(str(len(STOCK_DATA))+" scanner | "+str(len(REBOUND_DATA))+" rebound | Scan: 4 Mar 2026 | Live NSE")
tab1,tab2,tab3=st.tabs(["Buy Zone Scanner","Rebound Scanner","My Research"])

def get_px(syms):
    out={}
    for i in range(0,len(syms),50):
        b=list(syms[i:i+50])
        try:
            raw=yf.download([s+".NS" for s in b],period="1d",interval="1d",auto_adjust=True,progress=False)
            if raw.empty: continue
            if isinstance(raw.columns,pd.MultiIndex):
                if "Close" not in raw.columns.get_level_values(0): continue
                cl=raw["Close"].iloc[-1]
                for s in b:
                    try:
                        v=float(cl[s+".NS"])
                        if not np.isnan(v): out[s]=round(v,2)
                    except: pass
            else:
                if "Close" in raw.columns:
                    try:
                        v=float(raw["Close"].iloc[-1])
                        if not np.isnan(v): out[b[0]]=round(v,2)
                    except: pass
        except: pass
        time.sleep(0.3)
    return out

def mk(sym,tier,sec,ab,dist,spd,score,rr,win,roty,plbl,pval,l1,l2,l3,sl,tgt,up,rd,dd,el,dlf,css,dc):
    sg="+" if dist>0 else ""
    ac="bg" if ab else "br"
    al="200+" if ab else "200-"
    return ('<div class="card '+css+'"><span class="sym">'+sym+'</span>'
            '<span class="bx">'+tier+'</span><span class="bx">'+sec+'</span>'
            '<span class="bx '+ac+'">'+al+'</span>'
            '<div class="dt '+dc+'">'+sg+str(round(dist,2))+'% | '+str(round(spd,1))+'%/day</div>'
            '<div class="mt">Score '+str(score)+' | R:R '+str(rr)+' | Win '+str(win)+'% | '+str(roty)+'x/yr</div>'
            '<div class="pr">'
            '<div class="pc"><div class="pl">'+plbl+'</div><div class="pv">Rs'+f"{pval:,.2f}"+'</div></div>'
            '<div class="pc"><div class="pl">L1</div><div class="pv" style="color:#22c55e">Rs'+f"{l1:,.2f}"+'</div></div>'
            '<div class="pc"><div class="pl">L2</div><div class="pv">Rs'+f"{l2:,.2f}"+'</div></div>'
            '<div class="pc"><div class="pl">L3</div><div class="pv">Rs'+f"{l3:,.2f}"+'</div></div>'
            '<div class="pc"><div class="pl">SL</div><div class="pv" style="color:#ef4444">Rs'+f"{sl:,.2f}"+'</div></div>'
            '<div class="pc"><div class="pl">TGT</div><div class="pv" style="color:#2dd4bf">Rs'+f"{tgt:,.2f}"+'</div></div>'
            '<div class="pc"><div class="pl">UP%</div><div class="pv" style="color:#22c55e">+'+str(up)+'%</div></div>'
            '<div class="pc"><div class="pl">RISE DAYS</div><div class="pv" style="color:#fbbf24">~'+str(rd)+'d</div></div>'
            '<div class="pc"><div class="pl">DROP DAYS</div><div class="pv" style="color:#94a3b8">~'+str(dd)+'d</div></div>'
            '<div class="pc"><div class="pl">ELAPSED</div><div class="pv" style="color:#c084fc">'+el+'</div></div>'
            '<div class="pc"><div class="pl">DAYS LEFT</div><div class="pv" style="color:#2dd4bf">'+dlf+'</div></div>'
            '</div></div>')

with tab1:
    pool=[s for s in STOCK_DATA if s["score"]>=msco and s["rr"]>=mrr
          and s["tier"] in tiers and (not ab_only or s["above_200"])]
    st.write("Fetching "+str(len(pool))+" prices...")
    live=get_px(tuple(s["sym"] for s in pool))
    st.caption(str(len(live))+"/"+str(len(pool))+" loaded | "+datetime.now().strftime("%H:%M:%S")+" IST")
    rows=[]
    for s in pool:
        if s["sym"] not in live: continue
        p=live[s["sym"]]; cb=s["crash_buy"]
        d=round((p/cb-1)*100,2)
        l2=round(cb*(1-s["avg_drop"]*0.15/100),2)
        l3=round(cb*(1-s["avg_drop"]*0.30/100),2)
        rows.append({**s,"live":p,"dist":d,"l2":l2,"l3":l3,
                     "sl":round(l3*0.95,2),"up":round((s["rot_target"]/p-1)*100,1)})
    srt=st.radio("Sort by",["Closest to zone","Fastest rebound","Best upside %","Highest score"],
                 horizontal=True,key="s1")
    if srt=="Fastest rebound": rows.sort(key=lambda x:-x.get("rise_speed",0))
    elif srt=="Best upside %": rows.sort(key=lambda x:-x["up"])
    elif srt=="Highest score": rows.sort(key=lambda x:-x["score"])
    else: rows.sort(key=lambda x:x["dist"])
    iz=[r for r in rows if -3<=r["dist"]<=3]
    nr=[r for r in rows if 3<r["dist"]<=prox]
    bw=[r for r in rows if r["dist"]<-3]
    c1,c2,c3,c4=st.columns(4)
    c1.metric("In Zone",len(iz));c2.metric("Approaching",len(nr))
    c3.metric("Below Zone",len(bw));c4.metric("Scanned",len(rows))
    st.divider()
    def t1(r,css,dc):
        sp=r.get("rise_speed",0);rd=int(r.get("rise_days",0));dd=int(r.get("drop_days",0))
        el="~"+str(round(max(0,(r["live"]/r["crash_buy"]-1)*100/sp),1))+"d" if sp>0 else "Day 0"
        dlf=("~"+str(round(max(0,(r["rot_target"]/r["live"]-1)*100/sp),1))+"d"
             if sp>0 and r["live"]<r["rot_target"] else ("At target" if sp>0 else "-"))
        st.markdown(mk(r["sym"],r["tier"],r.get("sector",""),r["above_200"],r["dist"],sp,
            r["score"],r["rr"],int(r["win_pct"]),r["rot_yr"],"LIVE",r["live"],
            r["crash_buy"],r["l2"],r["l3"],r["sl"],r["rot_target"],r["up"],
            rd,dd,el,dlf,css,dc),unsafe_allow_html=True)
    if iz:
        st.markdown("### In Zone ("+str(len(iz))+")")
        for r in iz[:25]: t1(r,"cg","gn")
    else: st.info("No stocks within 3% of crash buy.")
    if nr:
        st.markdown("### Approaching ("+str(len(nr))+")")
        for r in nr[:30]: t1(r,"cy","ye")
    with st.expander("Below Zone ("+str(len(bw))+")"):
        for r in bw[:25]: t1(r,"cr","bl")

with tab2:
    st.markdown("### Rebound Scanner")
    st.caption("674 stocks | Named indexes + quality Broader NSE | Scan 4 Mar 2026")
    ca,cb2=st.columns(2)
    with ca:
        ab2=st.checkbox("Above 200DMA only",value=True,key="ra")
        shz=st.checkbox("In Zone",value=True,key="rz")
        sha=st.checkbox("Approaching",value=True,key="rp")
        shb=st.checkbox("Below Zone",value=False,key="rb")
    with cb2:
        iopts=["All Indexes","Nifty 50","Next 50","Nifty 100","Nifty 200","Nifty 500",
               "Midcap 150","Smallcap 250","IT","Bank","PSU Bank","Pharma","Auto",
               "FMCG","Metal","Energy","Oil & Gas","Infra","Financial","Healthcare","Realty","Broader NSE"]
        idx=st.selectbox("Index",iopts,key="ri")
        pr2=st.slider("Approaching %",3,30,20,key="rpr")
    srt2=st.radio("Sort by",["Fastest rebound","Closest to zone","Best upside %","Highest score","Most rotations/yr"],
                  horizontal=True,key="s2")
    rb2=[{**r,"up_scan":round((r["target"]/r["price"]-1)*100,1) if r["price"]>0 else 0}
         for r in REBOUND_DATA
         if (not ab2 or r["above"])
         and (idx=="All Indexes" or idx in r["tags"])
         and (r["tags"]!="Broader NSE" or (r["above"] and r["price"]>=20))]
    iz2=[r for r in rb2 if -3<=r["dist"]<=3]
    nr2=[r for r in rb2 if 3<r["dist"]<=pr2]
    bw2=[r for r in rb2 if r["dist"]<-3]
    sk={"Fastest rebound":lambda x:-x["speed"],"Closest to zone":lambda x:x["dist"],
        "Best upside %":lambda x:-x["up_scan"],"Highest score":lambda x:-x["score"],
        "Most rotations/yr":lambda x:-x["roty"]}[srt2]
    iz2.sort(key=sk);nr2.sort(key=sk);bw2.sort(key=sk)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("In Zone",len(iz2));c2.metric("Approaching",len(nr2))
    c3.metric("Below Zone",len(bw2));c4.metric("Filtered",len(rb2))
    st.divider()
    def t2(r,css,dc):
        sp=r.get("speed",0);rd=int(r.get("rdays",0));dd=int(r.get("ddays",0))
        dlf="~"+str(round(max(0,(r["target"]/r["price"]-1)*100/sp),1))+"d" if sp>0 and r["target"]>r["price"] else "-"
        tg=r["tags"].replace("Broader NSE","").replace(" | "," ").strip()[:25]
        st.markdown(mk(r["sym"],tg,"",r["above"],r["dist"],sp,r["score"],r["rr"],
            r["win"],r["roty"],"SCAN",r["price"],r["l1"],r["l2"],r["l3"],r["sl"],
            r["target"],r["up_scan"],rd,dd,"-",dlf,css,dc),unsafe_allow_html=True)
    if shz and iz2:
        st.markdown("### In Zone ("+str(len(iz2))+")")
        for r in iz2[:40]: t2(r,"cg","gn")
    if sha and nr2:
        st.markdown("### Approaching ("+str(len(nr2))+")")
        for r in nr2[:40]: t2(r,"cy","ye")
    if shb and bw2:
        st.markdown("### Below Zone ("+str(len(bw2))+")")
        for r in bw2[:40]: t2(r,"cb","bl")
    st.caption("Scan prices 4 Mar 2026. Max Days Left = upper bound from scan price.")

with tab3:
    st.write("Loading portfolio...")
    wll=get_px(tuple(w["sym"] for w in MY_WATCHLIST))
    st.caption(str(len(wll))+"/"+str(len(MY_WATCHLIST))+" loaded | "+datetime.now().strftime("%H:%M:%S"))
    inv=0;cur=0;w3=0;l3=0
    for w in MY_WATCHLIST:
        lp=wll.get(w["sym"])
        if lp and w.get("qty",0)>0: inv+=w["qty"]*w["entry"];cur+=w["qty"]*lp
        if lp:
            if lp>=w["entry"]: w3+=1
            else: l3+=1
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Tracked",len(MY_WATCHLIST));c2.metric("Above entry",w3);c3.metric("Below entry",l3)
    if inv>0:
        pnl=cur-inv
        c4.metric("P&L","Rs"+f"{pnl:+,.0f}",delta=f"{pnl/inv*100:+.1f}%")
    st.divider()
    hf=st.selectbox("Portfolio",["All","Vikram","Divya","Shreya","Nidhi","Vivek"])
    s3=st.radio("Sort by",["% vs entry","Symbol","Upside to target"],horizontal=True,key="s3")
    dl=[]
    for w in MY_WATCHLIST:
        if hf!="All":
            hl=[h.strip() for h in w.get("holders","").replace(" | ","·").replace(" · ","·").split("·")]
            if hf not in hl: continue
        lp=wll.get(w["sym"])
        dl.append({**w,"lp":lp,"chg":(lp/w["entry"]-1)*100 if lp else None,
                   "up":(w["target"]/lp-1)*100 if lp else None})
    if s3=="% vs entry": dl.sort(key=lambda x:x["chg"] if x["chg"] is not None else -999,reverse=True)
    elif s3=="Symbol": dl.sort(key=lambda x:x["sym"])
    else: dl.sort(key=lambda x:x["up"] if x["up"] is not None else -999,reverse=True)
    for w in dl:
        sym=w["sym"];lp=w["lp"];entry=w["entry"];tgt=w["target"];sl=w["sl"]
        qty=w.get("qty",0);thesis=w.get("thesis","");holders=w.get("holders","")
        if not lp:
            st.markdown('<div class="card cb"><span class="sym">? '+sym+'</span>'                        '<div class="tb">'+thesis+'</div></div>',unsafe_allow_html=True)
            continue
        chg=w["chg"];tot=(tgt/lp-1)*100;tos=(sl/lp-1)*100
        rr=abs(tot/tos) if tos else 0
        if lp>=tgt: css,ic="ct","T"
        elif lp>=entry: css,ic="cg","+"
        elif lp<=sl: css,ic="cr","X"
        else: css,ic="cy","~"
        gc="gn" if chg>=0 else "rd"
        vs=str(qty)+" shares | Rs"+f"{qty*lp:,.0f}" if qty>0 else "Watching"
        st.markdown('<div class="card '+css+'"><span class="sym">'+ic+" "+sym+'</span>'            '<span class="bx" style="background:#1a2a40;color:#94a3b8">'+holders+'</span>'            '<div class="dt '+gc+'">'+f"{chg:+.2f}"+'% vs entry | R:R '+f"{rr:.1f}"+'x</div>'            '<div class="mt">'+vs+'</div>'            '<div class="pr">'            '<div class="pc"><div class="pl">LIVE</div><div class="pv">Rs'+f"{lp:,.2f}"+'</div></div>'            '<div class="pc"><div class="pl">ENTRY</div><div class="pv">Rs'+f"{entry:,.2f}"+'</div></div>'            '<div class="pc"><div class="pl">TARGET</div><div class="pv" style="color:#2dd4bf">Rs'+f"{tgt:,.2f}"+' (+'+f"{tot:.1f}"+'%)</div></div>'            '<div class="pc"><div class="pl">SL</div><div class="pv" style="color:#ef4444">Rs'+f"{sl:,.2f}"+' ('+f"{tos:.1f}"+'%)</div></div>'            '</div><div class="tb">'+thesis+'</div></div>',unsafe_allow_html=True)
    st.caption("34 stocks | 5 portfolios: Vikram Divya Shreya Nidhi Vivek")
