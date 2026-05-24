"""
米国株テーマランキング - HTML生成スクリプト（GitHub Actions用）
GitHub Actions のサーバー上で実行され、index.html を生成します。
"""

import sys, os, time
from datetime import datetime, timezone, timedelta

try:
    import yfinance as yf
except ImportError:
    os.system(f'"{sys.executable}" -m pip install yfinance -q')
    import yfinance as yf

# ── テーマ定義 ─────────────────────────────────────────
THEMES = [
    # HOT
    {"id":"ai",      "type":"hot",  "icon":"🤖", "name":"AI・人工知能",            "stocks":["NVDA","MSFT","GOOGL","META","PLTR"]},
    {"id":"semi",    "type":"hot",  "icon":"💾", "name":"半導体・チップ",           "stocks":["NVDA","AMD","AVGO","MU","AMAT"]},
    {"id":"defense", "type":"hot",  "icon":"🛡️", "name":"防衛・宇宙航空",           "stocks":["LMT","RTX","NOC","GD","AXON"]},
    {"id":"cyber",   "type":"hot",  "icon":"🔒", "name":"サイバーセキュリティ",      "stocks":["CRWD","PANW","ZS","FTNT","OKTA"]},
    {"id":"cloud",   "type":"hot",  "icon":"☁️", "name":"クラウド・データセンター",  "stocks":["AMZN","MSFT","EQIX","DLR","VRT"]},
    {"id":"grid",    "type":"hot",  "icon":"⚡", "name":"電力インフラ・グリッド",    "stocks":["ETN","GEV","VST","CEG","PWR"]},
    {"id":"nuclear", "type":"hot",  "icon":"☢️", "name":"原子力エネルギー",          "stocks":["CEG","VST","CCJ","NRG","ETR"]},
    {"id":"robot",   "type":"hot",  "icon":"🦾", "name":"ロボティクス・自動化",      "stocks":["ISRG","PATH","TER","RRX","TRMB"]},
    {"id":"glp1",    "type":"hot",  "icon":"💊", "name":"GLP-1・肥満治療薬",        "stocks":["LLY","NVO","VKTX","AMGN","REGN"]},
    {"id":"space",   "type":"hot",  "icon":"🚀", "name":"宇宙開発・衛星",            "stocks":["RKLB","ASTS","LUNR","BA","BWXT"]},
    {"id":"quantum", "type":"hot",  "icon":"⚛️", "name":"量子コンピュータ",          "stocks":["IONQ","RGTI","QBTS","IBM","GOOGL"]},
    {"id":"fintech", "type":"hot",  "icon":"💳", "name":"フィンテック・決済",        "stocks":["V","MA","PYPL","NU","SQ"]},
    {"id":"govtech", "type":"hot",  "icon":"🏛️", "name":"国防テック・DIU",           "stocks":["PLTR","AXON","CACI","LDOS","SAIC"]},
    {"id":"ecom",    "type":"hot",  "icon":"🛒", "name":"eコマース・D2C",            "stocks":["AMZN","SHOP","MELI","ETSY","SE"]},
    {"id":"digad",   "type":"hot",  "icon":"🌐", "name":"デジタル広告",              "stocks":["META","GOOGL","AMZN","TTD","PUBM"]},
    {"id":"bank",    "type":"hot",  "icon":"🏦", "name":"投資銀行・大手金融",        "stocks":["JPM","GS","MS","BAC","BLK"]},
    {"id":"infra",   "type":"hot",  "icon":"🏗️", "name":"インフラ・建機",            "stocks":["CAT","DE","VMC","URI","PWR"]},
    {"id":"auto",    "type":"hot",  "icon":"🚗", "name":"自律走行・モビリティ",      "stocks":["TSLA","UBER","LYFT","GM","F"]},
    {"id":"hlhai",   "type":"hot",  "icon":"🏥", "name":"ヘルスケアAI・デジタル医療","stocks":["ISRG","VEEV","DXCM","GEHC","TDOC"]},
    {"id":"bat",     "type":"hot",  "icon":"🔋", "name":"蓄電池・エネルギー貯蓄",    "stocks":["TSLA","ENPH","FLNC","STEM","BE"]},
    {"id":"photon",  "type":"hot",  "icon":"💡", "name":"光・フォトニクス（光ネットワーク）","stocks":["CIEN","LITE","COHR","AAOI","VIAV"]},
    {"id":"hbm",     "type":"hot",  "icon":"🧠", "name":"HBM・高帯域メモリ",          "stocks":["MU","WDC","LRCX","ONTO","AMAT"]},
    # COLD
    {"id":"canna",   "type":"cold", "icon":"🌿", "name":"大麻・カンナビス",           "stocks":["MSOS","TLRY","CGC","ACB","CRON"]},
    {"id":"chntech", "type":"cold", "icon":"🇨🇳", "name":"中国テック（ADR）",          "stocks":["BABA","JD","PDD","BIDU","NIO"]},
    {"id":"ofcreit", "type":"cold", "icon":"🏢", "name":"オフィス不動産（REIT）",     "stocks":["BXP","VNO","SLG","DEI","PDM"]},
    {"id":"bio",     "type":"cold", "icon":"🔬", "name":"臨床段階バイオテック",        "stocks":["XBI","SRPT","RARE","FOLD","ARQT"]},
    {"id":"coal",    "type":"cold", "icon":"⛽", "name":"石炭・旧来型化石燃料",        "stocks":["BTU","ARCH","AMR","CEIX","HNRG"]},
    {"id":"media",   "type":"cold", "icon":"📺", "name":"旧来型メディア・放送",        "stocks":["PARA","WBD","AMCX","DIS","NWSA"]},
    {"id":"regbk",   "type":"cold", "icon":"🏦", "name":"地方銀行・リージョナル",      "stocks":["KRE","WAL","FHN","HBAN","ZION"]},
    {"id":"chnev",   "type":"cold", "icon":"🚙", "name":"中国EV",                     "stocks":["NIO","XPEV","LI","ZK","KNDI"]},
    {"id":"h2",      "type":"cold", "icon":"🔌", "name":"水素・燃料電池",              "stocks":["PLUG","FCEL","BE","BLDP","CLNE"]},
    {"id":"retail",  "type":"cold", "icon":"🏬", "name":"旧来型小売・百貨店",          "stocks":["TGT","M","KSS","GPS","DDS"]},
    {"id":"agri",    "type":"cold", "icon":"🌱", "name":"農業・肥料",                 "stocks":["MOS","NTR","ADM","BG","CF"]},
    {"id":"gaming",  "type":"cold", "icon":"🎮", "name":"モバイルゲーム・メタバース",  "stocks":["EA","TTWO","RBLX","U","SNAP"]},
    {"id":"hmo",     "type":"cold", "icon":"🩺", "name":"ヘルスケア保険・MCO",         "stocks":["UNH","CVS","HUM","MOH","CNC"]},
    {"id":"telco",   "type":"cold", "icon":"📡", "name":"旧来型通信キャリア",          "stocks":["T","VZ","LUMN","ATUS","TMUS"]},
    {"id":"em",      "type":"cold", "icon":"🌍", "name":"新興国株（EM）",              "stocks":["EEM","EWZ","FXI","TUR","EWY"]},
    {"id":"solar",   "type":"cold", "icon":"☀️", "name":"太陽光・風力（旧来型）",      "stocks":["ENPH","SEDG","RUN","FSLR","NOVA"]},
    {"id":"creit",   "type":"cold", "icon":"🏙️", "name":"商業用不動産・REIT全般",      "stocks":["SPG","O","CBRE","JLL","WPC"]},
    {"id":"gene",    "type":"cold", "icon":"🧬", "name":"遺伝子治療・ゲノム編集",      "stocks":["NTLA","EDIT","CRSP","BEAM","BLUE"]},
    {"id":"shale",   "type":"cold", "icon":"🛢️", "name":"シェールオイル・ガス",        "stocks":["OXY","DVN","HES","FANG","CTRA"]},
    {"id":"cruise",  "type":"cold", "icon":"🚢", "name":"クルーズ・旅行（景気敏感）",  "stocks":["CCL","RCL","NCLH","MAR","H"]},
]

ALL_TICKERS = list(dict.fromkeys(s for t in THEMES for s in t["stocks"]))

def fetch_quotes():
    print(f"Fetching {len(ALL_TICKERS)} tickers...")
    quote_map = {}
    try:
        raw = yf.download(ALL_TICKERS, period="5d", auto_adjust=True, progress=False, group_by="ticker")
        for ticker in ALL_TICKERS:
            try:
                closes = raw[ticker]["Close"].dropna() if len(ALL_TICKERS) > 1 else raw["Close"].dropna()
                if len(closes) >= 2:
                    prev = float(closes.iloc[-2])
                    curr = float(closes.iloc[-1])
                    quote_map[ticker] = {"chg": round((curr - prev) / prev * 100, 2), "ahChg": None}
                else:
                    quote_map[ticker] = {"chg": None, "ahChg": None}
            except Exception:
                quote_map[ticker] = {"chg": None, "ahChg": None}
    except Exception as e:
        print(f"Batch failed: {e}, trying individual...")
        for i, ticker in enumerate(ALL_TICKERS):
            try:
                h = yf.Ticker(ticker).history(period="5d")
                if len(h) >= 2:
                    prev = float(h["Close"].iloc[-2])
                    curr = float(h["Close"].iloc[-1])
                    quote_map[ticker] = {"chg": round((curr - prev) / prev * 100, 2), "ahChg": None}
                else:
                    quote_map[ticker] = {"chg": None, "ahChg": None}
            except Exception:
                quote_map[ticker] = {"chg": None, "ahChg": None}
            time.sleep(0.1)
    ok = sum(1 for v in quote_map.values() if v["chg"] is not None)
    print(f"Done: {ok}/{len(ALL_TICKERS)} tickers")
    return quote_map

def compute_themes(quote_map):
    results = []
    for t in THEMES:
        vals = [quote_map.get(s, {}).get("chg") for s in t["stocks"]]
        vals = [v for v in vals if v is not None]
        avg  = round(sum(vals)/len(vals), 2) if vals else None
        results.append({**t, "avg": avg})
    return results

def fmt(v):
    if v is None: return "—"
    return ("+" if v >= 0 else "") + f"{v:.2f}%"

def bar_w(v):
    if v is None: return "0%"
    return str(min(abs(v) * 8, 100)) + "%"

def build_html(theme_data, quote_map, timestamp_jst):
    jst_str  = timestamp_jst.strftime("%Y/%m/%d %H:%M JST")
    date_str = timestamp_jst.strftime("%Y-%m-%d")

    def render_panel(ttype):
        items = sorted(
            [t for t in theme_data if t["type"] == ttype],
            key=lambda t: (t["avg"] is None, -t["avg"] if t["avg"] is not None else 0)
            if ttype == "hot"
            else (t["avg"] is None, t["avg"] if t["avg"] is not None else 0)
        )
        html = ""
        for rank, t in enumerate(items, 1):
            av = t["avg"]
            ac = "dim" if av is None else ("pos" if av >= 0 else "neg")
            bw = bar_w(av)
            chips = ""
            for s in t["stocks"]:
                chg = quote_map.get(s, {}).get("chg")
                ct  = fmt(chg)
                cc  = "dim" if chg is None else ("pos" if chg >= 0 else "neg")
                chip_cls = "" if chg is None else ("pos-chip" if chg >= 0 else "neg-chip")
                chips += f'<a href="https://finance.yahoo.com/quote/{s}" target="_blank" class="chip {chip_cls}"><span class="tkr">{s}</span><span class="chg {cc}">{ct}</span></a>'
            medal = {1:"🥇",2:"🥈",3:"🥉"}.get(rank, str(rank))
            html += f"""
<div class="item {ttype}">
  <div class="bg-bar" style="width:{bw}"></div>
  <div class="rn">{medal}</div>
  <div class="ti">
    <div class="tn"><span class="tic">{t['icon']}</span><span class="tnt">{t['name']}</span></div>
    <div class="chips">{chips}</div>
  </div>
  <div class="ret">
    <div class="rp {ac}">{fmt(av)}</div>
    <div class="rl">テーマ平均</div>
  </div>
</div>"""
        return html

    hot_items  = [t for t in theme_data if t["type"] == "hot"  and t["avg"] is not None]
    cold_items = [t for t in theme_data if t["type"] == "cold" and t["avg"] is not None]
    hot_avg    = round(sum(t["avg"] for t in hot_items)  / len(hot_items),  2) if hot_items  else None
    cold_avg   = round(sum(t["avg"] for t in cold_items) / len(cold_items), 2) if cold_items else None
    all_valid  = [t for t in theme_data if t["avg"] is not None]
    best  = max(all_valid, key=lambda t: t["avg"]) if all_valid else None
    worst = min(all_valid, key=lambda t: t["avg"]) if all_valid else None
    best_txt  = f"{best['icon']}  {fmt(best['avg'])}"   if best  else "—"
    worst_txt = f"{worst['icon']} {fmt(worst['avg'])}" if worst else "—"
    best_cls  = "pos" if best  and best["avg"]  >= 0 else "neg"
    worst_cls = "neg" if worst and worst["avg"] <= 0 else "pos"
    hot_panel  = render_panel("hot")
    cold_panel = render_panel("cold")

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>米国株テーマランキング {date_str}｜ミラートレード用引け後データ</title>
<style>
:root{{--bg:#0a0a0f;--sf:#12121a;--sf2:#1c1c28;--bd:#252535;--tx:#e8e8f0;--tm:#6a6a8a;--td:#3a3a5a;
--g:#00d084;--gb:rgba(0,208,132,.1);--r:#ff4d6a;--rb:rgba(255,77,106,.1);
--ac:#7c6ff7;--ye:#f7c06f;}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--tx);font-family:-apple-system,'Hiragino Sans','Noto Sans JP',sans-serif;min-height:100vh}}
header{{position:sticky;top:0;z-index:100;background:rgba(10,10,15,.95);backdrop-filter:blur(20px);border-bottom:1px solid var(--bd)}}
.hi{{max-width:860px;margin:0 auto;padding:0 18px;height:54px;display:flex;align-items:center;justify-content:space-between}}
.logo{{display:flex;align-items:center;gap:8px}}
.lb{{width:28px;height:28px;border-radius:7px;background:linear-gradient(135deg,#7c6ff7,#a78bfa);display:flex;align-items:center;justify-content:center;font-size:15px}}
.lt{{font-size:14px;font-weight:700}}
.ts{{font-size:11px;color:var(--tm);text-align:right}}
.qr-btn{{background:var(--sf2);border:1px solid var(--bd);color:var(--tm);border-radius:8px;padding:5px 11px;font-size:12px;cursor:pointer;transition:all .15s;display:flex;align-items:center;gap:5px;white-space:nowrap}}
.qr-btn:hover{{border-color:var(--ac);color:var(--ac)}}
#qr-overlay{{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:200;display:flex;align-items:center;justify-content:center}}
#qr-box{{background:var(--sf);border:1px solid var(--bd);border-radius:20px;padding:28px;text-align:center;z-index:201;max-width:280px;width:90%}}
#qr-box h3{{font-size:15px;margin-bottom:16px;color:var(--tx)}}
#qr-code{{display:flex;justify-content:center;margin-bottom:14px}}
#qr-code canvas{{border-radius:8px}}
#qr-url{{font-size:11px;color:var(--tm);word-break:break-all;margin-bottom:16px;background:var(--sf2);padding:8px;border-radius:8px}}
#qr-close{{background:var(--ac);border:none;color:#fff;border-radius:8px;padding:8px 20px;font-size:13px;cursor:pointer;font-weight:600}}
.ab{{max-width:860px;margin:14px auto 0;padding:0 18px}}
.ai{{border-radius:12px;padding:11px 16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;background:rgba(124,111,247,.08);border:1px solid rgba(124,111,247,.3)}}
.al{{display:flex;align-items:center;gap:10px}}
.ad{{width:8px;height:8px;border-radius:50%;background:var(--ac)}}
.alb{{font-size:13px;font-weight:700;color:var(--ac)}}
.as{{font-size:11px;color:var(--tm)}}
.ar{{font-size:11px;color:var(--tm)}}
.stats{{max-width:860px;margin:12px auto 0;padding:0 18px;display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}
.stat{{background:var(--sf);border:1px solid var(--bd);border-radius:12px;padding:11px 14px;text-align:center}}
.sv{{font-size:20px;font-weight:800;line-height:1}}
.sv.pos{{color:var(--g)}} .sv.neg{{color:var(--r)}} .sv.neu{{color:var(--ac)}}
.sl{{font-size:10px;color:var(--tm);margin-top:4px}}
.tabs{{max-width:860px;margin:14px auto 0;padding:0 18px;display:flex;gap:8px}}
.tab{{flex:1;padding:11px 8px;border-radius:12px;border:1px solid var(--bd);background:var(--sf);color:var(--tm);font-size:13px;font-weight:600;cursor:pointer;transition:all .18s;display:flex;align-items:center;justify-content:center;gap:6px}}
.tab.hot{{background:var(--gb);border-color:var(--g);color:var(--g)}}
.tab.cold{{background:var(--rb);border-color:var(--r);color:var(--r)}}
.ta{{font-size:12px;font-weight:800;padding:1px 7px;border-radius:20px;background:currentColor;color:var(--bg);opacity:.9}}
.ch{{max-width:860px;margin:14px auto 5px;padding:0 18px;display:grid;grid-template-columns:44px 1fr 106px;gap:10px}}
.cl{{font-size:10px;color:var(--td);font-weight:600;text-transform:uppercase;letter-spacing:.5px}}
.rl{{max-width:860px;margin:0 auto 40px;padding:0 18px}}
.panel{{display:none}} .panel.active{{display:block}}
.item{{position:relative;overflow:hidden;display:grid;grid-template-columns:44px 1fr 106px;align-items:center;gap:10px;padding:13px 14px;border-radius:14px;border:1px solid transparent;background:var(--sf);margin-bottom:5px;transition:all .15s}}
.item:hover{{border-color:var(--bd);background:var(--sf2);transform:translateY(-1px)}}
.item::before{{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;border-radius:3px 0 0 3px}}
.item.hot::before{{background:var(--g)}} .item.cold::before{{background:var(--r)}}
.bg-bar{{position:absolute;top:0;right:0;bottom:0;pointer-events:none;border-radius:0 14px 14px 0;opacity:.055}}
.item.hot .bg-bar{{background:linear-gradient(90deg,transparent,var(--g))}}
.item.cold .bg-bar{{background:linear-gradient(90deg,transparent,var(--r))}}
.rn{{width:44px;text-align:center;font-size:18px;font-weight:800;color:var(--td);z-index:1}}
.ti{{z-index:1;min-width:0}}
.tn{{display:flex;align-items:center;gap:6px;font-size:13px;font-weight:700;margin-bottom:6px;line-height:1.2}}
.tic{{font-size:15px;flex-shrink:0}}
.tnt{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.chips{{display:flex;flex-wrap:wrap;gap:4px}}
.chip{{display:inline-flex;align-items:center;gap:3px;font-size:10px;font-weight:600;padding:2px 6px 2px 7px;border-radius:6px;background:var(--sf2);border:1px solid var(--bd);color:var(--tm);text-decoration:none;cursor:pointer;transition:all .15s}}
.chip:hover{{background:var(--bd);transform:translateY(-1px);box-shadow:0 2px 8px rgba(0,0,0,.3)}}
.chip.pos-chip{{border-color:rgba(0,208,132,.25)}} .chip.neg-chip{{border-color:rgba(255,77,106,.25)}}
.chip.pos-chip:hover{{border-color:rgba(0,208,132,.6);background:rgba(0,208,132,.08)}}
.chip.neg-chip:hover{{border-color:rgba(255,77,106,.6);background:rgba(255,77,106,.08)}}
.tkr{{letter-spacing:.3px}}
.chg{{font-weight:700}}
.chg.pos{{color:var(--g)}} .chg.neg{{color:var(--r)}} .chg.dim{{color:var(--td)}}
.ret{{z-index:1;text-align:right}}
.rp{{font-size:20px;font-weight:800;letter-spacing:-.5px;line-height:1}}
.rp.pos{{color:var(--g)}} .rp.neg{{color:var(--r)}} .rp.dim{{color:var(--td);font-size:14px}}
.rl{{font-size:10px;color:var(--td);margin-top:3px}}
.disc{{max-width:860px;margin:0 auto 40px;padding:16px 18px 0;border-top:1px solid var(--bd);font-size:11px;color:var(--td);line-height:1.7}}
@media(max-width:560px){{
  .item{{grid-template-columns:32px 1fr 82px;padding:11px 10px}}
  .rn{{width:32px;font-size:14px}}
  .rp{{font-size:15px}}
}}
</style>
</head>
<body>
<header>
  <div class="hi">
    <div class="logo">
      <div class="lb">📊</div>
      <span class="lt">米国株テーマランキング</span>
    </div>
    <div style="display:flex;align-items:center;gap:10px">
      <div class="ts">
        <div style="color:var(--g);font-weight:700">✅ 引け後データ（確定値）</div>
        <div>取得: {jst_str}</div>
      </div>
      <button class="qr-btn" onclick="showQR()">📱 QR</button>
    </div>
  </div>
</header>
<div class="ab">
  <div class="ai">
    <div class="al">
      <div class="ad"></div>
      <div>
        <div class="alb">⚡ US市場引け後データ — 東京市場ミラートレード用</div>
        <div class="as">yfinance 取得 / 前日終値比 1日騰落率 / 構成銘柄の単純平均</div>
      </div>
    </div>
    <div class="ar">データ更新: {jst_str}</div>
  </div>
</div>
<div class="stats">
  <div class="stat"><div class="sv {best_cls}">{best_txt}</div><div class="sl">本日最強テーマ</div></div>
  <div class="stat"><div class="sv {worst_cls}">{worst_txt}</div><div class="sl">本日最弱テーマ</div></div>
  <div class="stat"><div class="sv neu">40</div><div class="sl">追跡テーマ数</div></div>
</div>
<div class="tabs">
  <button class="tab hot" id="th" onclick="sw('hot')">🔥 人気テーマ <span class="ta">{fmt(hot_avg)}</span></button>
  <button class="tab" id="tc" onclick="sw('cold')">🧊 不人気テーマ <span class="ta">{fmt(cold_avg)}</span></button>
</div>
<div class="ch">
  <span class="cl">#</span>
  <span class="cl">テーマ / 銘柄（前日比）</span>
  <span class="cl" style="text-align:right">テーマ平均</span>
</div>
<div class="rl">
  <div class="panel active" id="ph">{hot_panel}</div>
  <div class="panel" id="pc">{cold_panel}</div>
</div>
<div class="disc">
  ⚠️ 本ページは情報提供目的のみ。騰落率は yfinance 経由の参考値（前日終値比）。テーマ平均は構成銘柄の単純平均。投資は自己判断・自己責任で。
</div>
<div id="qr-overlay" style="display:none" onclick="hideQR()">
  <div id="qr-box" onclick="event.stopPropagation()">
    <h3>📱 スマホで開く</h3>
    <div id="qr-code"></div>
    <div id="qr-url"></div>
    <button id="qr-close" onclick="hideQR()">閉じる</button>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
<script>
function sw(t){{
  document.getElementById('ph').classList.toggle('active', t==='hot');
  document.getElementById('pc').classList.toggle('active', t==='cold');
  document.getElementById('th').className='tab'+(t==='hot'?' hot':'');
  document.getElementById('tc').className='tab'+(t==='cold'?' cold':'');
}}
let qrGenerated = false;
function showQR() {{
  const url = window.location.href;
  document.getElementById('qr-url').textContent = url;
  if (!qrGenerated) {{
    try {{
      new QRCode(document.getElementById('qr-code'), {{
        text: url, width: 200, height: 200,
        colorDark: '#ffffff', colorLight: '#12121a',
        correctLevel: QRCode.CorrectLevel.M
      }});
      qrGenerated = true;
    }} catch(e) {{
      document.getElementById('qr-code').innerHTML =
        '<p style="color:#6a6a8a;font-size:12px">QRコード生成にはインターネット接続が必要です</p>';
    }}
  }}
  document.getElementById('qr-overlay').style.display = 'flex';
}}
function hideQR() {{
  document.getElementById('qr-overlay').style.display = 'none';
}}
</script>
</body>
</html>"""

def main():
    quote_map  = fetch_quotes()
    theme_data = compute_themes(quote_map)
    jst_now    = datetime.now(timezone(timedelta(hours=9)))
    html       = build_html(theme_data, quote_map, jst_now)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()
