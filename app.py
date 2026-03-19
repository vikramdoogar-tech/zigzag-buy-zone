import { useState, useMemo } from "react";

// ─── FULL DATASET (2249 stocks scanned, Mar 2026) ────────────────────────────
const MARKET_HEALTH = 17.3; // % stocks above 200DMA — deeply bearish market
const SCAN_DATE = "Mar 2026";

const T1 = [ // Nifty 50 / 100 — LONG TERM CONFIDENCE LAYER
  {symbol:"TRENT",      last:3722.80,score:19.80,avgRise:39.2,avgDrop:17.3,riseDays:31,dropDays:20,rot:5.8,rr:2.27,win:100,crashBuy:3290.12,panic1:3094.82,panic2:2899.53,rotTarget:5162.60,distTarget:38.7,above200:false},
  {symbol:"ADANIENT",   last:2039.90,score:19.47,avgRise:36.9,avgDrop:17.4,riseDays:26,dropDays:21,rot:5.8,rr:2.13,win:100,crashBuy:1867.40,panic1:1754.58,panic2:1641.76,rotTarget:2791.60,distTarget:36.9,above200:false},
  {symbol:"BEL",        last:468.45, score:16.47,avgRise:29.7,avgDrop:14.9,riseDays:46,dropDays:30,rot:4.8,rr:2.00,win:100,crashBuy:398.79, panic1:377.89, panic2:357.00, rotTarget:495.23, distTarget:5.7,  above200:true},
  {symbol:"BAJFINANCE", last:950.20, score:16.01,avgRise:31.1,avgDrop:17.9,riseDays:34,dropDays:28,rot:3.5,rr:1.74,win:80, crashBuy:896.40, panic1:836.10, panic2:775.80, rotTarget:1237.73,distTarget:30.4, above200:false},
  {symbol:"BAJAJFINSV", last:1868.90,score:15.93,avgRise:30.7,avgDrop:17.1,riseDays:36,dropDays:29,rot:3.3,rr:1.79,win:100,crashBuy:1721.90,panic1:1614.50,panic2:1507.10,rotTarget:2444.80,distTarget:30.7, above200:false},
  {symbol:"SHRIRAMFIN", last:1007.50,score:15.77,avgRise:28.6,avgDrop:16.8,riseDays:36,dropDays:24,rot:4.3,rr:1.70,win:100,crashBuy:916.80, panic1:859.00, panic2:801.20, rotTarget:1295.60,distTarget:28.6, above200:true},
  {symbol:"HINDALCO",   last:958.90, score:15.13,avgRise:27.5,avgDrop:16.4,riseDays:30,dropDays:24,rot:5.4,rr:1.68,win:80, crashBuy:862.30, panic1:804.70, panic2:747.10, rotTarget:1100.60,distTarget:18.4, above200:true},
  {symbol:"TATASTEEL",  last:198.46, score:14.98,avgRise:27.0,avgDrop:15.9,riseDays:28,dropDays:24,rot:5.8,rr:1.69,win:80, crashBuy:179.10, panic1:167.90, panic2:156.70, rotTarget:249.70, distTarget:25.9, above200:true},
  {symbol:"MAXHEALTH",  last:1042.00,score:14.81,avgRise:24.5,avgDrop:13.3,riseDays:32,dropDays:24,rot:4.7,rr:1.84,win:80, crashBuy:958.10, panic1:900.40, panic2:842.70, rotTarget:1187.50,distTarget:14.0, above200:false},
  {symbol:"APOLLOHOSP", last:7724.50,score:14.77,avgRise:26.3,avgDrop:14.0,riseDays:36,dropDays:28,rot:3.7,rr:1.87,win:100,crashBuy:6723.36,panic1:null,  panic2:null,  rotTarget:8567.46,distTarget:10.9, above200:true},
  {symbol:"ADANIPORTS", last:1477.50,score:14.76,avgRise:26.4,avgDrop:15.9,riseDays:32,dropDays:28,rot:4.8,rr:1.66,win:100,crashBuy:1320.70,panic1:null,  panic2:null,  rotTarget:1812.51,distTarget:22.7, above200:true},
  {symbol:"SBIN",       last:822.40, score:14.70,avgRise:27.0,avgDrop:16.2,riseDays:30,dropDays:24,rot:5.2,rr:1.73,win:80, crashBuy:704.20, panic1:662.50, panic2:620.80, rotTarget:1006.40,distTarget:22.4, above200:true},
  {symbol:"ABB",        last:5832.00,score:14.58,avgRise:26.0,avgDrop:15.3,riseDays:38,dropDays:28,rot:4.3,rr:1.70,win:100,crashBuy:5198.00,panic1:null,  panic2:null,  rotTarget:6648.00,distTarget:14.0, above200:true},
  {symbol:"CHOLAFIN",   last:1626.30,score:14.34,avgRise:23.2,avgDrop:14.2,riseDays:38,dropDays:28,rot:6.7,rr:1.63,win:100,crashBuy:1518.30,panic1:null,  panic2:null,  rotTarget:2003.76,distTarget:23.2, above200:true},
  {symbol:"COALINDIA",  last:440.45, score:13.98,avgRise:24.7,avgDrop:15.0,riseDays:32,dropDays:26,rot:4.1,rr:1.65,win:100,crashBuy:382.03, panic1:null,  panic2:null,  rotTarget:503.23, distTarget:14.3, above200:true},
  {symbol:"EICHERMOT",  last:7620.50,score:13.25,avgRise:22.4,avgDrop:13.8,riseDays:38,dropDays:30,rot:4.4,rr:1.62,win:100,crashBuy:7057.32,panic1:null,  panic2:null,  rotTarget:8531.47,distTarget:11.9, above200:true},
  {symbol:"AXISBANK",   last:1315.80,score:13.19,avgRise:23.6,avgDrop:16.1,riseDays:34,dropDays:28,rot:4.0,rr:1.46,win:100,crashBuy:1177.12,panic1:null,  panic2:null,  rotTarget:1291.66,distTarget:0,    above200:true},
  {symbol:"TATAPOWER",  last:416.80, score:15.20,avgRise:28.5,avgDrop:16.2,riseDays:28,dropDays:22,rot:5.8,rr:1.76,win:80, crashBuy:362.40, panic1:338.90, panic2:315.40, rotTarget:536.00, distTarget:28.6, above200:false},
  {symbol:"PERSISTENT", last:5480.00,score:16.80,avgRise:30.1,avgDrop:14.8,riseDays:36,dropDays:24,rot:5.2,rr:2.04,win:80, crashBuy:4948.00,panic1:4661.00,panic2:4374.00,rotTarget:6360.00,distTarget:16.1, above200:false},
  {symbol:"CGPOWER",    last:715.45, score:17.99,avgRise:31.9,avgDrop:17.9,riseDays:28,dropDays:22,rot:8.0,rr:1.78,win:100,crashBuy:596.52, panic1:557.45, panic2:518.38, rotTarget:698.54, distTarget:0,    above200:true},
];

const T2 = [ // Nifty 500 — TRADING CORE
  {symbol:"ANANDRATHI", last:3198.70,score:24.28,avgRise:44.5,avgDrop:12.0,riseDays:65,dropDays:28,rot:4.1,rr:3.71,win:100,crashBuy:2815.50,panic1:2700.53,panic2:2585.57,rotTarget:4148.17,distTarget:29.7, above200:true},
  {symbol:"AAKASH",     last:1286.00,score:23.80,avgRise:48.2,avgDrop:22.3,riseDays:45,dropDays:28,rot:6.4,rr:2.16,win:100,crashBuy:1048.00,panic1:982.00, panic2:916.00, rotTarget:1906.00,distTarget:48.2, above200:true},
  {symbol:"CUPID",      last:382.00, score:23.40,avgRise:45.0,avgDrop:17.4,riseDays:52,dropDays:30,rot:6.4,rr:2.59,win:100,crashBuy:329.00, panic1:310.00, panic2:291.00, rotTarget:519.00, distTarget:35.9, above200:true},
  {symbol:"BLACKBUCK",  last:586.00, score:20.30,avgRise:38.2,avgDrop:18.5,riseDays:42,dropDays:28,rot:6.3,rr:2.07,win:80, crashBuy:500.00, panic1:469.00, panic2:438.00, rotTarget:790.00, distTarget:34.8, above200:true},
  {symbol:"BSE",        last:2751.60,score:19.10,avgRise:35.4,avgDrop:16.8,riseDays:38,dropDays:24,rot:6.1,rr:2.10,win:100,crashBuy:2642.71,panic1:2482.40,panic2:2322.08,rotTarget:3556.56,distTarget:29.3, above200:true},
  {symbol:"BGRENERGY",  last:830.00, score:19.30,avgRise:34.2,avgDrop:20.1,riseDays:28,dropDays:22,rot:8.9,rr:1.69,win:80, crashBuy:718.00, panic1:672.00, panic2:626.00, rotTarget:1114.00,distTarget:34.2, above200:true},
  {symbol:"BAJAJ-AUTO", last:8920.00,score:18.70,avgRise:37.0,avgDrop:15.3,riseDays:56,dropDays:36,rot:2.4,rr:2.42,win:100,crashBuy:8002.00,panic1:null,  panic2:null,  rotTarget:11040.00,distTarget:23.8, above200:true},
  {symbol:"APARINDS",   last:10394.0,score:16.38,avgRise:28.4,avgDrop:15.2,riseDays:44,dropDays:28,rot:6.5,rr:1.87,win:100,crashBuy:9484.42,panic1:8975.59,panic2:8466.77,rotTarget:12863.24,distTarget:23.8,above200:true},
  {symbol:"APLAPOLLO",  last:2152.80,score:16.70,avgRise:30.1,avgDrop:15.4,riseDays:40,dropDays:28,rot:5.2,rr:1.96,win:100,crashBuy:1929.33,panic1:1823.89,panic2:1718.45,rotTarget:1951.54,distTarget:0,    above200:true},
  {symbol:"CUMMINSIND", last:4800.70,score:16.68,avgRise:31.6,avgDrop:15.9,riseDays:42,dropDays:28,rot:3.7,rr:1.99,win:100,crashBuy:4175.70,panic1:3939.57,panic2:3703.44,rotTarget:5147.41,distTarget:7.2,  above200:true},
  {symbol:"TVSMOTOR",   last:2486.00,score:15.80,avgRise:29.2,avgDrop:15.2,riseDays:38,dropDays:26,rot:4.8,rr:1.92,win:100,crashBuy:2188.00,panic1:null,  panic2:null,  rotTarget:3100.00,distTarget:24.7, above200:true},
  {symbol:"JBCHEPHARM", last:1856.00,score:16.40,avgRise:29.4,avgDrop:13.7,riseDays:46,dropDays:28,rot:4.0,rr:2.15,win:100,crashBuy:1708.00,panic1:null,  panic2:null,  rotTarget:2142.00,distTarget:15.4, above200:true},
  {symbol:"LAURUSLABS", last:568.00, score:16.30,avgRise:29.1,avgDrop:15.2,riseDays:40,dropDays:26,rot:5.4,rr:1.91,win:100,crashBuy:502.00, panic1:null,  panic2:null,  rotTarget:732.00, distTarget:28.9, above200:true},
  {symbol:"POLYCAB",    last:6240.00,score:18.00,avgRise:33.8,avgDrop:15.4,riseDays:38,dropDays:24,rot:4.1,rr:2.20,win:100,crashBuy:5600.00,panic1:5228.00,panic2:4856.00,rotTarget:8000.00,distTarget:28.2, above200:true},
  {symbol:"MUTHOOTFIN", last:2108.00,score:16.10,avgRise:30.2,avgDrop:15.6,riseDays:40,dropDays:26,rot:3.7,rr:1.93,win:100,crashBuy:1842.00,panic1:null,  panic2:null,  rotTarget:2744.00,distTarget:30.2, above200:true},
];

const T3 = [ // Midcap / Smallcap — SWING TRADES
  {symbol:"QPOWER",     last:833.75, score:27.19,avgRise:56.6,avgDrop:21.5,riseDays:32,dropDays:26,rot:5.9,rr:2.63,win:100,crashBuy:778.00, panic1:null,  panic2:null,  rotTarget:1233.00,distTarget:47.9, above200:true},
  {symbol:"ADANIPOWER", last:634.00, score:18.40,avgRise:33.0,avgDrop:18.3,riseDays:30,dropDays:22,rot:7.2,rr:1.80,win:100,crashBuy:572.00, panic1:null,  panic2:null,  rotTarget:842.00, distTarget:32.8, above200:true},
  {symbol:"HINDCOPPER", last:286.00, score:18.30,avgRise:33.2,avgDrop:18.3,riseDays:30,dropDays:22,rot:7.1,rr:1.81,win:80, crashBuy:252.00, panic1:null,  panic2:null,  rotTarget:380.00, distTarget:32.9, above200:true},
  {symbol:"JSL",        last:936.00, score:16.60,avgRise:29.1,avgDrop:15.5,riseDays:36,dropDays:26,rot:7.2,rr:1.87,win:100,crashBuy:838.00, panic1:null,  panic2:null,  rotTarget:1208.00,distTarget:29.1, above200:true},
  {symbol:"GPIL",       last:920.00, score:17.80,avgRise:33.2,avgDrop:20.0,riseDays:32,dropDays:24,rot:7.5,rr:1.66,win:100,crashBuy:792.00, panic1:null,  panic2:null,  rotTarget:1225.00,distTarget:33.2, above200:true},
  {symbol:"FORCEMOT",   last:6240.00,score:17.60,avgRise:31.4,avgDrop:16.4,riseDays:40,dropDays:28,rot:6.8,rr:1.91,win:100,crashBuy:5556.00,panic1:null,  panic2:null,  rotTarget:8200.00,distTarget:31.4, above200:true},
  {symbol:"SOLARINDS",  last:8980.00,score:17.40,avgRise:32.1,avgDrop:15.2,riseDays:44,dropDays:26,rot:4.1,rr:2.12,win:100,crashBuy:8080.00,panic1:null,  panic2:null,  rotTarget:11200.00,distTarget:24.7,above200:true},
  {symbol:"TVSHLTD",    last:840.00, score:16.80,avgRise:31.8,avgDrop:17.3,riseDays:40,dropDays:26,rot:4.5,rr:1.84,win:100,crashBuy:746.00, panic1:null,  panic2:null,  rotTarget:1108.00,distTarget:31.9, above200:true},
  {symbol:"CRAFTSMAN",  last:7458.00,score:15.82,avgRise:28.0,avgDrop:14.6,riseDays:52,dropDays:28,rot:4.7,rr:1.92,win:100,crashBuy:6935.25,panic1:6580.12,panic2:6225.00,rotTarget:9502.49,distTarget:27.4, above200:true},
  {symbol:"VEDL",       last:464.00, score:16.20,avgRise:29.6,avgDrop:17.0,riseDays:34,dropDays:24,rot:5.5,rr:1.74,win:80, crashBuy:412.00, panic1:null,  panic2:null,  rotTarget:602.00, distTarget:29.7, above200:true},
  {symbol:"KEI",        last:3680.00,score:16.10,avgRise:29.2,avgDrop:16.0,riseDays:40,dropDays:26,rot:5.8,rr:1.82,win:100,crashBuy:3232.00,panic1:null,  panic2:null,  rotTarget:4750.00,distTarget:29.1, above200:true},
  {symbol:"MCX",        last:5820.00,score:16.10,avgRise:28.4,avgDrop:14.9,riseDays:42,dropDays:26,rot:6.1,rr:1.90,win:100,crashBuy:5188.00,panic1:null,  panic2:null,  rotTarget:7380.00,distTarget:26.8, above200:true},
];

const T4 = [ // Pure Micro — EXPERIMENTS ONLY
  {symbol:"DOLPHIN",    last:444.30, score:58.18,avgRise:132.4,avgDrop:26.7,riseDays:104,dropDays:42,rot:4.0,rr:4.95,win:100,crashBuy:325.58,panic1:null,panic2:null,rotTarget:904.35, distTarget:103.6,above200:true},
  {symbol:"UEL",        last:116.00, score:40.19,avgRise:81.5, avgDrop:23.3,riseDays:62, dropDays:32,rot:5.2,rr:3.50,win:100,crashBuy:98.00, panic1:null,panic2:null,rotTarget:210.00, distTarget:81.0, above200:true},
  {symbol:"JPOLYINVST", last:1101.80,score:36.08,avgRise:73.4, avgDrop:19.8,riseDays:24, dropDays:26,rot:7.5,rr:3.71,win:100,crashBuy:1010.00,panic1:null,panic2:null,rotTarget:1910.00,distTarget:73.4, above200:true},
  {symbol:"VENUSREM",   last:704.85, score:35.12,avgRise:78.4, avgDrop:19.2,riseDays:92, dropDays:39,rot:2.8,rr:4.08,win:100,crashBuy:634.00, panic1:null,panic2:null,rotTarget:1256.00,distTarget:78.2, above200:true},
  {symbol:"AURUM",      last:167.47, score:51.20,avgRise:105.1,avgDrop:17.0,riseDays:27, dropDays:25,rot:7.1,rr:6.18,win:100,crashBuy:156.31,panic1:146.70,panic2:137.09,rotTarget:339.68,distTarget:102.8,above200:false},
  {symbol:"DIACABS",    last:135.33, score:46.34,avgRise:97.3, avgDrop:22.0,riseDays:28, dropDays:26,rot:9.8,rr:4.43,win:100,crashBuy:109.91,panic1:null,panic2:null,rotTarget:238.71,distTarget:76.4, above200:false},
  {symbol:"QPOWER",     last:833.75, score:27.19,avgRise:56.6, avgDrop:21.5,riseDays:32, dropDays:26,rot:5.9,rr:2.63,win:100,crashBuy:778.00, panic1:null,panic2:null,rotTarget:1233.00,distTarget:47.9, above200:true},
];

// EPS / Fundamental data (consensus FY estimates, for confidence layer only)
const EPS = {
  ANANDRATHI: {fy25e:145,  fy26e:185,  fy27e:230,  pe:22,  note:"Wealth mgmt boom, AUM growing 35% YoY"},
  BSE:        {fy25e:95,   fy26e:128,  fy27e:165,  pe:28,  note:"Exchange monopoly + clearing + commodity growth"},
  TRENT:      {fy25e:42,   fy26e:58,   fy27e:78,   pe:85,  note:"Zudio expansion, 400+ stores target"},
  BEL:        {fy25e:6.8,  fy26e:8.5,  fy27e:10.5, pe:38,  note:"Defence order book ₹75,000Cr+, visibility 3Y"},
  CGPOWER:    {fy25e:14,   fy26e:18,   fy27e:23,   pe:52,  note:"Power T&D supercycle + semiconductor foray"},
  APOLLOHOSP: {fy25e:72,   fy26e:95,   fy27e:125,  pe:68,  note:"Hospital expansion + Apollo 24|7 digital"},
  BAJFINANCE: {fy25e:55,   fy26e:68,   fy27e:85,   pe:28,  note:"Credit cycle recovery, NIM stabilising"},
  ADANIPORTS: {fy25e:62,   fy26e:78,   fy27e:98,   pe:22,  note:"Port capacity + logistics integration"},
  PERSISTENT: {fy25e:85,   fy26e:108,  fy27e:135,  pe:52,  note:"AI services revenue acceleration"},
  LAURUSLABS: {fy25e:18,   fy26e:26,   fy27e:34,   pe:22,  note:"CDMO pivot, US generics normalising"},
  JBCHEPHARM: {fy25e:58,   fy26e:72,   fy27e:90,   pe:25,  note:"Domestic branded pharma compounder"},
  TVSMOTOR:   {fy25e:68,   fy26e:82,   fy27e:100,  pe:32,  note:"EV transition leader, NORTON global"},
  CHOLAFIN:   {fy25e:42,   fy26e:54,   fy27e:68,   pe:28,  note:"Vehicle finance, rural credit expansion"},
  POLYCAB:    {fy25e:105,  fy26e:130,  fy27e:162,  pe:42,  note:"Wires & cables infra supercycle"},
  MUTHOOTFIN: {fy25e:98,   fy26e:118,  fy27e:142,  pe:12,  note:"Gold loan growth, rural penetration"},
  HINDALCO:   {fy25e:32,   fy26e:40,   fy27e:50,   pe:12,  note:"Novelis premium + domestic Al demand"},
  SBIN:       {fy25e:68,   fy26e:80,   fy27e:95,   pe:9,   note:"Largest PSU bank, credit cost normalising"},
  COALINDIA:  {fy25e:38,   fy26e:42,   fy27e:46,   pe:9,   note:"Cash cow, 6%+ dividend yield, steady"},
  EICHERMOT:  {fy25e:185,  fy26e:210,  fy27e:240,  pe:32,  note:"Royal Enfield premiumisation, global push"},
};

// ─── CONSTANTS ────────────────────────────────────────────────────────────────
const BG    = "#070710";
const CARD  = "#0d0d1a";
const CARD2 = "#10101f";
const BDR   = "#1a1a30";
const T1C   = "#38bdf8"; // sky blue — confidence
const T2C   = "#34d399"; // emerald — trade
const T3C   = "#a78bfa"; // violet — swing
const T4C   = "#fb923c"; // orange — experiment
const RED   = "#f87171";
const GOLD  = "#fbbf24";
const DIM   = "#4b5580";
const MUTED = "#8892b0";
const WHITE = "#e8eaf6";

const fmt = n => {
  if (!n && n !== 0) return "—";
  if (n >= 10000000) return `₹${(n/10000000).toFixed(1)}Cr`;
  if (n >= 100000)   return `₹${(n/100000).toFixed(1)}L`;
  if (n >= 1000)     return `₹${n.toLocaleString('en-IN',{maximumFractionDigits:0})}`;
  return `₹${Number(n).toFixed(2)}`;
};
const pct = n => n == null ? "—" : `${n>0?"+":""}${Number(n).toFixed(1)}%`;
const fmtEps = n => n == null ? "—" : `₹${n}`;

const TIER_META = {
  T1: { label:"T1 · Liquid Core",     color:T1C,   bg:"#071520", border:"#0e2a40",
    role:"LONG TERM CONFIDENCE",
    rule:"Never sell on bad news. These survive everything. Buy in drops, hold 2-3 years. This is your anchor.",
    size:"40% of capital", stocks:T1 },
  T2: { label:"T2 · Trading Core",    color:T2C,   bg:"#071a10", border:"#0e3020",
    role:"ACTIVE TRADING",
    rule:"This is where you make money. ZigZag in and out. GTC buy at crash levels. Sell at rotation target. Repeat.",
    size:"35% of capital", stocks:T2 },
  T3: { label:"T3 · Swing Trades",    color:T3C,   bg:"#120714", border:"#220e2e",
    role:"MOMENTUM SWINGS",
    rule:"Faster rotations. Tighter stops. Book partial at half-rise, let rest ride. Don't convert these to investments.",
    size:"15% of capital", stocks:T3 },
  T4: { label:"T4 · Micro Lab",       color:T4C,   bg:"#180c04", border:"#301808",
    role:"EXPERIMENTS",
    rule:"Lottery sizing only. If it works — book and move profits to T2. If it dies — you sized it for that. Never average down.",
    size:"10% of capital", stocks:T4 },
};

// ─── COMPONENTS ──────────────────────────────────────────────────────────────

function MarketBar() {
  const pctAbove = MARKET_HEALTH;
  const sentiment = pctAbove < 25 ? "BEARISH" : pctAbove < 50 ? "NEUTRAL" : "BULLISH";
  const sentColor = pctAbove < 25 ? RED : pctAbove < 50 ? GOLD : T2C;
  return (
    <div style={{background:CARD,border:`1px solid ${BDR}`,borderRadius:8,padding:"12px 18px",
      display:"flex",gap:32,alignItems:"center",flexWrap:"wrap",marginBottom:20}}>
      <div>
        <div style={{fontSize:9,color:DIM,letterSpacing:3,marginBottom:4}}>MARKET HEALTH</div>
        <div style={{display:"flex",alignItems:"baseline",gap:8}}>
          <span style={{fontSize:24,fontWeight:800,color:sentColor}}>{pctAbove}%</span>
          <span style={{fontSize:11,color:sentColor,fontWeight:700}}>{sentiment}</span>
        </div>
        <div style={{fontSize:10,color:MUTED}}>stocks above 200DMA · {SCAN_DATE}</div>
      </div>
      <div style={{flex:1,minWidth:200}}>
        <div style={{height:6,background:"#1a1a30",borderRadius:3,overflow:"hidden"}}>
          <div style={{height:"100%",width:`${pctAbove}%`,background:`linear-gradient(90deg,${RED},${GOLD})`,borderRadius:3}}/>
        </div>
        <div style={{display:"flex",justifyContent:"space-between",fontSize:9,color:DIM,marginTop:3}}>
          <span>0% (crash)</span><span>50% (neutral)</span><span>100% (bull)</span>
        </div>
      </div>
      <div style={{textAlign:"right"}}>
        <div style={{fontSize:10,color:RED,fontWeight:600}}>Market is in a deep correction</div>
        <div style={{fontSize:10,color:MUTED}}>Best time to set GTC orders below</div>
        <div style={{fontSize:10,color:MUTED}}>2249 stocks scanned · 356 above 200DMA</div>
      </div>
    </div>
  );
}

function RuleBox() {
  const rules = [
    {n:"1", title:"Trading IS the edge. Long term is the confidence.",
     body:"T1 stocks give you confidence to not panic. T2/T3 are where you actually compound. Never confuse them. If you bought CGPOWER for a trade — sell at target. If you bought CGPOWER as a core — hold through drops."},
    {n:"2", title:"News is just the trigger, not the reason.",
     body:"Markets react to news but ZigZag catches the price cycle regardless of cause. When news creates a drop to your crash buy zone — that's your entry signal, not a reason to wait and analyse more."},
    {n:"3", title:"The only decision you make is WHICH TIER.",
     body:"Once you classify a stock, the model tells you everything else: entry price, position size, stop loss, profit target. Your job is classification and patience — not prediction."},
    {n:"4", title:"EPS projections are your boundary fence.",
     body:"If FY27 EPS × historical PE gives you a price far below current — don't buy. If it gives you 40%+ upside in 3 years — even a bad ZigZag trade that gets stopped recovers. EPS is the safety net."},
    {n:"5", title:"The confusion killer: Time horizon per tier.",
     body:"T1 = 2-3 years. T2 = weeks to months. T3 = days to weeks. T4 = one swing or dead. Print this. Stick it above your screen."},
  ];
  return (
    <div style={{marginBottom:20}}>
      <div style={{fontSize:9,color:DIM,letterSpacing:3,marginBottom:12}}>THE 5 RULES THAT STOP THE CONFUSION</div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(280px,1fr))",gap:10}}>
        {rules.map(r=>(
          <div key={r.n} style={{background:CARD,border:`1px solid ${BDR}`,borderRadius:8,padding:"14px 16px",display:"flex",gap:12}}>
            <div style={{fontSize:28,fontWeight:900,color:BDR,lineHeight:1,flexShrink:0}}>{r.n}</div>
            <div>
              <div style={{color:WHITE,fontWeight:700,fontSize:11,marginBottom:5,lineHeight:1.4}}>{r.title}</div>
              <div style={{color:MUTED,fontSize:10,lineHeight:1.7}}>{r.body}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function EpsCard({symbol, last}) {
  const e = EPS[symbol];
  if (!e) return null;
  const fy27target = Math.round(e.fy27e * e.pe);
  const upside = ((fy27target - last) / last * 100).toFixed(0);
  const epsGrowth = (((e.fy27e/e.fy25e)**0.5 - 1)*100).toFixed(0);
  return (
    <div style={{marginTop:10,background:"#080814",border:`1px solid #1a1a35`,borderRadius:6,padding:"10px 12px"}}>
      <div style={{fontSize:9,color:T1C,letterSpacing:2,marginBottom:8}}>FUNDAMENTAL OVERLAY</div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:6,marginBottom:8}}>
        {[["FY25e EPS",fmtEps(e.fy25e)],["FY26e EPS",fmtEps(e.fy26e)],["FY27e EPS",fmtEps(e.fy27e)],["Hist PE",`${e.pe}×`]].map(([l,v])=>(
          <div key={l} style={{textAlign:"center"}}>
            <div style={{fontSize:9,color:DIM}}>{l}</div>
            <div style={{fontSize:12,color:WHITE,fontWeight:600}}>{v}</div>
          </div>
        ))}
      </div>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
        <div style={{fontSize:10,color:MUTED,flex:1}}>{e.note}</div>
        <div style={{textAlign:"right",marginLeft:12,flexShrink:0}}>
          <div style={{fontSize:9,color:DIM}}>FY27 fair value</div>
          <div style={{fontSize:14,fontWeight:700,color:Number(upside)>20?T2C:Number(upside)>0?GOLD:RED}}>{fmt(fy27target)}</div>
          <div style={{fontSize:9,color:DIM}}>{pct(Number(upside))} from today · EPS CAGR +{epsGrowth}%</div>
        </div>
      </div>
    </div>
  );
}

function StockCard({s, tierColor, compact=false}) {
  const [open, setOpen] = useState(false);
  const inZone = s.crashBuy && s.last <= s.crashBuy * 1.03;
  const pctToCrash = s.crashBuy ? ((s.last/s.crashBuy-1)*100).toFixed(1) : null;
  const stopLoss = s.panic2 ? (s.panic2 * 0.95).toFixed(0) : s.crashBuy ? (s.crashBuy * (1 - s.avgDrop/100) * 0.95).toFixed(0) : null;
  const partial = s.crashBuy ? (s.crashBuy * (1 + s.avgRise/2/100)).toFixed(0) : null;

  return (
    <div style={{background:CARD2,border:`1px solid ${inZone?tierColor+"55":BDR}`,
      borderLeft:`3px solid ${inZone?tierColor:BDR}`,
      borderRadius:8,padding:"12px 14px",cursor:"pointer"}}
      onClick={()=>setOpen(o=>!o)}>
      {/* Header row */}
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start"}}>
        <div>
          <div style={{display:"flex",gap:8,alignItems:"center"}}>
            <span style={{color:tierColor,fontWeight:800,fontSize:14,letterSpacing:-0.3}}>{s.symbol}</span>
            {inZone && <span style={{background:tierColor+"22",color:tierColor,fontSize:8,padding:"2px 6px",borderRadius:3,fontWeight:700,letterSpacing:1}}>IN ZONE</span>}
            {s.above200 && <span style={{background:"#0a1f10",color:T2C,fontSize:8,padding:"2px 6px",borderRadius:3}}>↑200DMA</span>}
            {EPS[s.symbol] && <span style={{background:"#0a1520",color:T1C,fontSize:8,padding:"2px 6px",borderRadius:3}}>EPS</span>}
          </div>
          <div style={{fontSize:10,color:MUTED,marginTop:2}}>
            {fmt(s.last)} · Rise <span style={{color:T2C}}>+{s.avgRise}%</span> · Drop <span style={{color:RED}}>-{s.avgDrop}%</span> · R:R <span style={{color:s.rr>=2.5?T2C:s.rr>=1.7?GOLD:RED}}>{s.rr}</span>
          </div>
        </div>
        <div style={{textAlign:"right"}}>
          <div style={{fontSize:14,fontWeight:700,color:s.distTarget>20?T2C:s.distTarget>0?GOLD:RED}}>
            {s.distTarget > 0 ? `+${s.distTarget.toFixed(0)}%` : "AT TGT"}
          </div>
          <div style={{fontSize:9,color:DIM}}>upside to target</div>
          <div style={{fontSize:9,color:DIM,marginTop:2}}>{open?"▲ less":"▼ orders"}</div>
        </div>
      </div>

      {/* Expanded order details */}
      {open && (
        <div style={{marginTop:12,borderTop:`1px solid ${BDR}`,paddingTop:12}}>
          {/* Order levels */}
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8,marginBottom:10}}>
            <div>
              <div style={{fontSize:9,color:T1C,letterSpacing:2,marginBottom:6}}>GTC BUY ORDERS</div>
              {[
                ["L1 — Crash Buy (40%)", s.crashBuy, `High − ${s.avgDrop}%`, T1C],
                ["L2 — Panic (35%)",     s.panic1,   `High − ${(s.avgDrop*1.3).toFixed(0)}%`, GOLD],
                ["L3 — Capitulation (25%)", s.panic2, `High − ${(s.avgDrop*1.6).toFixed(0)}%`, T4C],
              ].map(([l,v,sub,c])=> v ? (
                <div key={l} style={{display:"flex",justifyContent:"space-between",
                  background:"#080818",border:`1px solid ${c}22`,borderRadius:4,padding:"5px 8px",marginBottom:4}}>
                  <div>
                    <div style={{fontSize:10,color:c,fontWeight:600}}>{l}</div>
                    <div style={{fontSize:9,color:DIM}}>{sub}</div>
                  </div>
                  <div style={{color:c,fontWeight:700,fontSize:12}}>{fmt(v)}</div>
                </div>
              ) : null)}
              {stopLoss && (
                <div style={{display:"flex",justifyContent:"space-between",
                  background:"#120808",border:`1px dashed ${RED}44`,borderRadius:4,padding:"5px 8px"}}>
                  <div>
                    <div style={{fontSize:10,color:RED}}>🛑 Stop Loss</div>
                    <div style={{fontSize:9,color:DIM}}>Pattern failed — exit</div>
                  </div>
                  <div style={{color:RED,fontWeight:700,fontSize:12}}>{fmt(stopLoss)}</div>
                </div>
              )}
            </div>
            <div>
              <div style={{fontSize:9,color:T2C,letterSpacing:2,marginBottom:6}}>PROFIT BOOKING</div>
              {[
                ["Partial Exit — 50%", partial, `+${(s.avgRise/2).toFixed(0)}% from entry`, T2C],
                ["Full Target — 50%",  s.rotTarget, `+${s.avgRise}% full swing`, "#4ade80"],
              ].map(([l,v,sub,c])=> v ? (
                <div key={l} style={{display:"flex",justifyContent:"space-between",
                  background:"#080f08",border:`1px solid ${c}22`,borderRadius:4,padding:"5px 8px",marginBottom:4}}>
                  <div>
                    <div style={{fontSize:10,color:c,fontWeight:600}}>{l}</div>
                    <div style={{fontSize:9,color:DIM}}>{sub}</div>
                  </div>
                  <div style={{color:c,fontWeight:700,fontSize:12}}>{fmt(v)}</div>
                </div>
              ) : null)}
              <div style={{background:"#0a0a14",border:`1px solid ${BDR}`,borderRadius:4,padding:"6px 8px",marginTop:4}}>
                <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"3px 8px",fontSize:10}}>
                  <span style={{color:DIM}}>Rot/Yr</span> <span style={{color:GOLD}}>{s.rot}×/yr</span>
                  <span style={{color:DIM}}>Rise Days</span> <span style={{color:WHITE}}>{s.riseDays}d</span>
                  <span style={{color:DIM}}>Drop Days</span> <span style={{color:WHITE}}>{s.dropDays}d</span>
                  <span style={{color:DIM}}>Win Rate</span> <span style={{color:T2C}}>{s.win}%</span>
                </div>
              </div>
            </div>
          </div>
          {/* EPS overlay if available */}
          {EPS[s.symbol] && <EpsCard symbol={s.symbol} last={s.last}/>}
          {/* Proximity note */}
          {pctToCrash && (
            <div style={{marginTop:8,fontSize:10,color:
              inZone?T2C:Number(pctToCrash)<10?GOLD:DIM,textAlign:"center"}}>
              {inZone ? `⚡ Currently ${Math.abs(pctToCrash)}% BELOW crash buy — enter at market` :
               Number(pctToCrash)<10 ? `🎯 Only ${pctToCrash}% above entry zone — set GTC now` :
               `${pctToCrash}% above entry zone — GTC set and wait`}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TierSection({tierKey}) {
  const meta = TIER_META[tierKey];
  const [filter, setFilter] = useState("all"); // all | zone | above200 | eps
  const stocks = meta.stocks;
  const filtered = stocks.filter(s => {
    if (filter==="zone") return s.crashBuy && s.last <= s.crashBuy * 1.05;
    if (filter==="above200") return s.above200;
    if (filter==="eps") return !!EPS[s.symbol];
    return true;
  });

  return (
    <div style={{background:meta.bg,border:`1px solid ${meta.border}`,borderRadius:10,padding:"18px",marginBottom:16}}>
      {/* Tier header */}
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:14,flexWrap:"wrap",gap:10}}>
        <div>
          <div style={{display:"flex",gap:10,alignItems:"baseline"}}>
            <span style={{color:meta.color,fontWeight:800,fontSize:15,letterSpacing:-0.3}}>{meta.label}</span>
            <span style={{fontSize:10,color:meta.color,background:meta.color+"22",padding:"2px 8px",borderRadius:3,fontWeight:700}}>{meta.role}</span>
          </div>
          <div style={{color:MUTED,fontSize:10,marginTop:5,maxWidth:600,lineHeight:1.6}}>{meta.rule}</div>
        </div>
        <div style={{textAlign:"right"}}>
          <div style={{color:meta.color,fontSize:13,fontWeight:700}}>{meta.size}</div>
          <div style={{color:DIM,fontSize:10}}>{stocks.length} stocks tracked</div>
        </div>
      </div>

      {/* Filters */}
      <div style={{display:"flex",gap:6,marginBottom:12,flexWrap:"wrap"}}>
        {[["all","All"],["zone","In Zone"],["above200","↑ 200DMA"],["eps","With EPS"]].map(([v,l])=>(
          <button key={v} onClick={()=>setFilter(v)} style={{
            padding:"4px 12px",fontSize:10,fontFamily:"inherit",
            background:filter===v?meta.color+"22":"transparent",
            color:filter===v?meta.color:DIM,
            border:`1px solid ${filter===v?meta.color+"55":BDR}`,
            borderRadius:4,cursor:"pointer"
          }}>{l} {v==="zone"?`(${stocks.filter(s=>s.crashBuy&&s.last<=s.crashBuy*1.05).length})`:
                v==="above200"?`(${stocks.filter(s=>s.above200).length})`:
                v==="eps"?`(${stocks.filter(s=>!!EPS[s.symbol]).length})`:""}
          </button>
        ))}
      </div>

      {/* Stock grid */}
      <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(340px,1fr))",gap:8}}>
        {filtered.map(s=><StockCard key={s.symbol} s={s} tierColor={meta.color}/>)}
        {filtered.length===0 && <div style={{color:DIM,fontSize:11,padding:12}}>No stocks match this filter.</div>}
      </div>
    </div>
  );
}

function HowToUse() {
  const steps = [
    {phase:"PREPARATION", color:T1C, items:[
      "Every Sunday evening — check market health (% above 200DMA)",
      "If market is below 30% → aggressive GTC setting mode. Below 20% like now = best buying opportunity of the year",
      "Scan your T1 and T2 watchlist — which stocks are within 10% of crash buy?",
      "Set all GTC buy orders for the week. You don't need to watch the market during the day.",
    ]},
    {phase:"ENTRY", color:T2C, items:[
      "GTC fires → you get a SMS/notification. That's your entry — no second-guessing",
      "Immediately set your stop loss (GTC sell-stop below panic2) in the same session",
      "Immediately set your profit target (GTC limit sell at partial target for 50% qty)",
      "For T1: after GTC fires, also note the FY27 fair value — if price is below that, hold the position long term alongside the trade",
    ]},
    {phase:"DURING THE TRADE", color:T3C, items:[
      "Do nothing. The GTC orders are working. This is the hardest part.",
      "News comes out — do NOT cancel your orders unless the business has fundamentally changed (fraud, bankruptcy, loss of licence)",
      "If partial target hits → raise stop on remaining qty to breakeven (your entry price). You are now playing with house money.",
      "If stop fires before target → accept it, reset the GTC at the new crash buy level",
    ]},
    {phase:"EXIT & RESET", color:T4C, items:[
      "Full target hit → full exit. Calculate what you made. Don't hold hoping for more.",
      "Wait for stock to form new confirmed high (usually 4-8 weeks after target)",
      "Recalculate: new crash buy = new high minus avg drop. Set fresh GTC.",
      "T4 profits → move to T2 watchlist. T2 profits → compound within T2. T1 → reinvest dividends.",
    ]},
  ];
  return (
    <div style={{marginBottom:16}}>
      <div style={{fontSize:9,color:DIM,letterSpacing:3,marginBottom:12}}>HOW TO USE THIS MODEL — WEEKLY WORKFLOW</div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(280px,1fr))",gap:10}}>
        {steps.map(s=>(
          <div key={s.phase} style={{background:CARD,border:`1px solid ${s.color}22`,borderLeft:`3px solid ${s.color}`,borderRadius:8,padding:"14px 16px"}}>
            <div style={{color:s.color,fontWeight:700,fontSize:11,letterSpacing:2,marginBottom:10}}>{s.phase}</div>
            <div style={{display:"flex",flexDirection:"column",gap:7}}>
              {s.items.map((item,i)=>(
                <div key={i} style={{display:"flex",gap:8,alignItems:"flex-start"}}>
                  <span style={{color:s.color,fontSize:14,lineHeight:1.2,flexShrink:0}}>›</span>
                  <span style={{fontSize:10,color:MUTED,lineHeight:1.6}}>{item}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────
export default function App() {
  const [tab, setTab] = useState("model"); // model | howto | rules

  const inZoneAll = [...T1,...T2,...T3,...T4].filter(s=>s.crashBuy&&s.last<=s.crashBuy*1.05);

  return (
    <div style={{background:BG,minHeight:"100vh",color:WHITE,
      fontFamily:"'JetBrains Mono','Fira Code',monospace",
      padding:"20px 20px 40px",boxSizing:"border-box"}}>

      {/* Header */}
      <div style={{marginBottom:20}}>
        <div style={{fontSize:9,color:DIM,letterSpacing:5,marginBottom:6}}>VIKRAM · TRUEEDGE REALTY · NSE ZIGZAG</div>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-end",flexWrap:"wrap",gap:12}}>
          <div>
            <h1 style={{margin:0,fontSize:22,fontWeight:800,letterSpacing:-0.5,lineHeight:1.2}}>
              <span style={{color:T1C}}>The</span>{" "}
              <span style={{color:WHITE}}>ZigZag</span>{" "}
              <span style={{color:T2C}}>Trading</span>{" "}
              <span style={{color:WHITE}}>Model</span>
            </h1>
            <div style={{color:MUTED,fontSize:10,marginTop:4}}>
              2,249 stocks · 4-tier system · GTC levels · EPS overlay · Full workflow
            </div>
          </div>
          {inZoneAll.length > 0 && (
            <div style={{background:"#1a0a00",border:`1px solid ${T4C}55`,borderRadius:6,
              padding:"8px 14px",fontSize:11,color:T4C,fontWeight:700}}>
              ⚡ {inZoneAll.length} stocks in entry zone NOW
            </div>
          )}
        </div>
      </div>

      <MarketBar/>

      {/* Tab navigation */}
      <div style={{display:"flex",gap:3,marginBottom:20,borderBottom:`1px solid ${BDR}`,paddingBottom:0}}>
        {[["model","📊 The Model"],["howto","📋 How To Use"],["rules","🧠 The 5 Rules"]].map(([v,l])=>(
          <button key={v} onClick={()=>setTab(v)} style={{
            padding:"9px 18px",fontSize:11,fontFamily:"inherit",background:"transparent",
            color:tab===v?WHITE:DIM,
            border:"none",
            borderBottom:`2px solid ${tab===v?T2C:"transparent"}`,
            cursor:"pointer",marginBottom:-1
          }}>{l}</button>
        ))}
      </div>

      {tab==="rules" && <RuleBox/>}
      {tab==="howto" && <HowToUse/>}
      {tab==="model" && (
        <div>
          {/* Capital allocation summary */}
          <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:10,marginBottom:20}}>
            {Object.entries(TIER_META).map(([k,m])=>(
              <div key={k} style={{background:m.bg,border:`1px solid ${m.border}`,borderRadius:8,padding:"12px 14px"}}>
                <div style={{fontSize:9,color:m.color,letterSpacing:2,marginBottom:6}}>{m.role}</div>
                <div style={{fontSize:16,fontWeight:700,color:m.color}}>{m.size}</div>
                <div style={{fontSize:10,color:MUTED,marginTop:2}}>{m.stocks.length} stocks</div>
                <div style={{fontSize:9,color:DIM,marginTop:2}}>
                  {m.stocks.filter(s=>s.above200).length} above 200DMA ·{" "}
                  {m.stocks.filter(s=>s.crashBuy&&s.last<=s.crashBuy*1.05).length} in zone
                </div>
              </div>
            ))}
          </div>

          {Object.keys(TIER_META).map(k=><TierSection key={k} tierKey={k}/>)}
        </div>
      )}

      <div style={{marginTop:20,textAlign:"center",fontSize:9,color:DIM}}>
        Based on ZigZag swing analysis · Historical averages only · Not financial advice · Verify all levels before order placement
      </div>
    </div>
  );
}
