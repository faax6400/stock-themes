"""
日本株テーマランキング - HTML生成スクリプト（GitHub Actions用）
東京市場引け後 17:00 JST に自動更新
"""

import sys, os, time, json, base64, webbrowser, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

try:
    import yfinance as yf
except ImportError:
    os.system(f'"{sys.executable}" -m pip install yfinance -q')
    import yfinance as yf

# ── テーマ定義（.T サフィックスで yfinance 取得）─────────────
THEMES = [
    # ── HOT ──────────────────────────────────────────────
    {"id":"semi_eq",  "type":"hot",  "icon":"🔬", "name":"半導体製造装置",
     "stocks":["8035.T","6857.T","6920.T","6146.T","4063.T"]},

    {"id":"ai_dx",    "type":"hot",  "icon":"🤖", "name":"AI・DXシステム",
     "stocks":["6701.T","6702.T","6501.T","4307.T","3626.T"]},

    {"id":"defense",  "type":"hot",  "icon":"🛡️", "name":"防衛・宇宙航空",
     "stocks":["7011.T","7013.T","7012.T","6268.T","6503.T"]},

    {"id":"photon",   "type":"hot",  "icon":"💡", "name":"光・フォトニクス",
     "stocks":["6965.T","7741.T","5803.T","6758.T","6762.T"]},

    {"id":"hbm",      "type":"hot",  "icon":"🧠", "name":"HBM・先端半導体材料",
     "stocks":["8035.T","6146.T","6857.T","4063.T","3407.T"]},

    {"id":"power",    "type":"hot",  "icon":"⚡", "name":"電力インフラ・送電",
     "stocks":["6504.T","6506.T","5631.T","6273.T","6361.T"]},

    {"id":"nuclear",  "type":"hot",  "icon":"☢️", "name":"原子力エネルギー",
     "stocks":["9501.T","9503.T","7011.T","1963.T","6503.T"]},

    {"id":"robot",    "type":"hot",  "icon":"🦾", "name":"ロボティクス・工場自動化",
     "stocks":["6954.T","6506.T","7013.T","6326.T","6302.T"]},

    {"id":"pharma",   "type":"hot",  "icon":"💊", "name":"医薬品・創薬",
     "stocks":["4519.T","4523.T","4503.T","4568.T","4502.T"]},

    {"id":"inbound",  "type":"hot",  "icon":"🗼", "name":"訪日インバウンド",
     "stocks":["9202.T","9201.T","4661.T","9603.T","3543.T"]},

    {"id":"megabank", "type":"hot",  "icon":"🏦", "name":"大手金融・証券",
     "stocks":["8306.T","8316.T","8411.T","8604.T","8601.T"]},

    {"id":"fintech",  "type":"hot",  "icon":"💳", "name":"フィンテック・決済",
     "stocks":["3769.T","4385.T","8473.T","4689.T","3774.T"]},

    {"id":"auto",     "type":"hot",  "icon":"🚗", "name":"自動車・モビリティ",
     "stocks":["7203.T","7267.T","7201.T","7261.T","7269.T"]},

    {"id":"infra",    "type":"hot",  "icon":"🏗️", "name":"建設・インフラ",
     "stocks":["6301.T","6326.T","1801.T","1802.T","1803.T"]},

    {"id":"ecom",     "type":"hot",  "icon":"🛒", "name":"eコマース・D2C",
     "stocks":["4755.T","4385.T","9983.T","4689.T","3064.T"]},

    {"id":"hlhai",    "type":"hot",  "icon":"🏥", "name":"ヘルスケアIT・デジタル医療",
     "stocks":["2413.T","4307.T","6701.T","4523.T","3626.T"]},

    {"id":"energy",   "type":"hot",  "icon":"⛽", "name":"資源・エネルギー自立",
     "stocks":["1605.T","5020.T","9531.T","5019.T","1662.T"]},

    {"id":"telecom",  "type":"hot",  "icon":"📡", "name":"通信インフラ",
     "stocks":["9432.T","9433.T","9434.T","9719.T","4307.T"]},

    {"id":"chem",     "type":"hot",  "icon":"🧪", "name":"素材・特殊化学",
     "stocks":["4063.T","4183.T","4188.T","4004.T","3407.T"]},

    {"id":"insurance","type":"hot",  "icon":"🏛️", "name":"保険・ノンバンク金融",
     "stocks":["8766.T","8725.T","8630.T","8591.T","8697.T"]},

    # ── COLD ─────────────────────────────────────────────
    {"id":"oldmedia", "type":"cold", "icon":"📺", "name":"旧来型メディア・放送",
     "stocks":["9404.T","9401.T","9413.T","4324.T","2433.T"]},

    {"id":"regbank",  "type":"cold", "icon":"🏦", "name":"地方銀行",
     "stocks":["8354.T","8383.T","8377.T","8341.T","8381.T"]},

    {"id":"creit",    "type":"cold", "icon":"🏢", "name":"商業不動産",
     "stocks":["8801.T","8802.T","8830.T","8804.T","3003.T"]},

    {"id":"retail",   "type":"cold", "icon":"🏬", "name":"旧来型小売・百貨店",
     "stocks":["3382.T","9843.T","3099.T","8233.T","7453.T"]},

    {"id":"fossil",   "type":"cold", "icon":"🛢️", "name":"旧来型化石燃料",
     "stocks":["1605.T","5020.T","1662.T","5019.T","9502.T"]},

    {"id":"mobgame",  "type":"cold", "icon":"🎮", "name":"モバイルゲーム・メタバース",
     "stocks":["3765.T","2432.T","3632.T","4751.T","9684.T"]},

    {"id":"oldtech",  "type":"cold", "icon":"📷", "name":"旧来型デジタル機器",
     "stocks":["7751.T","7731.T","4902.T","7740.T","7912.T"]},

    {"id":"h2",       "type":"cold", "icon":"🔌", "name":"水素・燃料電池",
     "stocks":["7203.T","7267.T","5020.T","7011.T","4063.T"]},

    {"id":"agri",     "type":"cold", "icon":"🌱", "name":"農業・肥料・食品素材",
     "stocks":["4004.T","4188.T","4183.T","2002.T","2801.T"]},

    {"id":"oldmfg",   "type":"cold", "icon":"🏭", "name":"旧来型製造業（景気敏感）",
     "stocks":["5411.T","6471.T","5108.T","7259.T","5105.T"]},

    {"id":"shipping", "type":"cold", "icon":"🚢", "name":"海運",
     "stocks":["9104.T","9101.T","9107.T","9110.T","9119.T"]},

    {"id":"solar",    "type":"cold", "icon":"☀️", "name":"太陽光・再エネ（苦戦）",
     "stocks":["6753.T","9502.T","9504.T","9506.T","7004.T"]},

    {"id":"china",    "type":"cold", "icon":"🇨🇳", "name":"中国景気敏感",
     "stocks":["9984.T","7203.T","7267.T","8591.T","6752.T"]},

    {"id":"pachink",  "type":"cold", "icon":"🎰", "name":"パチンコ・アミューズメント",
     "stocks":["6460.T","9766.T","7832.T","4680.T","9697.T"]},

    {"id":"paper",    "type":"cold", "icon":"📰", "name":"紙・パルプ",
     "stocks":["3861.T","3863.T","3880.T","3865.T","3877.T"]},

    {"id":"steel",    "type":"cold", "icon":"🔩", "name":"鉄鋼",
     "stocks":["5401.T","5411.T","5423.T","5444.T","5471.T"]},

    {"id":"autopart", "type":"cold", "icon":"⚙️", "name":"自動車部品（景気敏感）",
     "stocks":["7259.T","5108.T","5105.T","6902.T","7240.T"]},

    {"id":"lifeins",  "type":"cold", "icon":"🩺", "name":"旧来型生命保険",
     "stocks":["8750.T","7181.T","7182.T","8308.T","8795.T"]},

    {"id":"travel",   "type":"cold", "icon":"✈️", "name":"クルーズ・旅行（景気敏感）",
     "stocks":["9202.T","9201.T","9603.T","4680.T","6098.T"]},

    {"id":"railway",  "type":"cold", "icon":"🚃", "name":"旧来型鉄道・私鉄",
     "stocks":["9022.T","9020.T","9021.T","9005.T","9008.T"]},
]

ALL_TICKERS = list(dict.fromkeys(s for t in THEMES for s in t["stocks"]))

def fetch_quotes():
    print(f"Fetching {len(ALL_TICKERS)} JP tickers...")
    quote_map = {}
    try:
        raw = yf.download(ALL_TICKERS, period="5d", auto_adjust=True, progress=False, group_by="ticker")
        for ticker in ALL_TICKERS:
            try:
                closes = raw[ticker]["Close"].dropna() if len(ALL_TICKERS) > 1 else raw["Close"].dropna()
                if len(closes) >= 2:
                    prev = float(closes.iloc[-2])
                    curr = float(closes.iloc[-1])
                    quote_map[ticker] = {"chg": round((curr - prev) / prev * 100, 2)}
                else:
                    quote_map[ticker] = {"chg": None}
            except Exception:
                quote_map[ticker] = {"chg": None}
    except Exception as e:
        print(f"Batch failed: {e}, trying individual...")
        for ticker in ALL_TICKERS:
            try:
                h = yf.Ticker(ticker).history(period="5d")
                if len(h) >= 2:
                    prev = float(h["Close"].iloc[-2])
                    curr = float(h["Close"].iloc[-1])
                    quote_map[ticker] = {"chg": round((curr - prev) / prev * 100, 2)}
                else:
                    quote_map[ticker] = {"chg": None}
            except Exception:
                quote_map[ticker] = {"chg": None}
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
                code = s.replace(".T", "")
                chg  = quote_map.get(s, {}).get("chg")
                ct   = fmt(chg)
                cc   = "dim" if chg is None else ("pos" if chg >= 0 else "neg")
                chip_cls = "" if chg is None else ("pos-chip" if chg >= 0 else "neg-chip")
                chips += f'<a href="https://minkabu.jp/stock/{code}" target="_blank" class="chip {chip_cls}"><span class="tkr">{code}</span><span class="chg {cc}">{ct}</span></a>'
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
<title>日本株テーマランキング {date_str}｜東京市場引け後データ</title>
<style>
:root{{--bg:#0a0f0a;--sf:#121a12;--sf2:#1c281c;--bd:#253525;--tx:#e8f0e8;--tm:#6a8a6a;--td:#3a5a3a;
--g:#00d084;--gb:rgba(0,208,132,.1);--r:#ff4d6a;--rb:rgba(255,77,106,.1);
--ac:#4caf50;--ye:#f7c06f;}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--tx);font-family:-apple-system,'Hiragino Sans','Noto Sans JP',sans-serif;min-height:100vh}}
header{{position:sticky;top:0;z-index:100;background:rgba(10,15,10,.95);backdrop-filter:blur(20px);border-bottom:1px solid var(--bd)}}
.hi{{max-width:900px;margin:0 auto;padding:0 18px;height:54px;display:flex;align-items:center;justify-content:space-between}}
.logo{{display:flex;align-items:center;gap:8px}}
.lb{{width:28px;height:28px;border-radius:7px;background:linear-gradient(135deg,#4caf50,#81c784);display:flex;align-items:center;justify-content:center;font-size:15px}}
.lt{{font-size:14px;font-weight:700}}
.ts{{font-size:11px;color:var(--tm);text-align:right}}
.switch-btn{{background:rgba(124,111,247,.15);border:1px solid rgba(124,111,247,.4);color:#a78bfa;border-radius:8px;padding:5px 11px;font-size:12px;cursor:pointer;text-decoration:none;display:flex;align-items:center;gap:5px;white-space:nowrap;transition:all .15s}}
.switch-btn:hover{{background:rgba(124,111,247,.3);border-color:#a78bfa}}
.ab{{max-width:900px;margin:14px auto 0;padding:0 18px}}
.ai{{border-radius:12px;padding:11px 16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;background:rgba(76,175,80,.08);border:1px solid rgba(76,175,80,.3)}}
.al{{display:flex;align-items:center;gap:10px}}
.ad{{width:8px;height:8px;border-radius:50%;background:var(--ac)}}
.alb{{font-size:13px;font-weight:700;color:var(--ac)}}
.as{{font-size:11px;color:var(--tm)}}
.ar{{font-size:11px;color:var(--tm)}}
.stats{{max-width:900px;margin:12px auto 0;padding:0 18px;display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}
.stat{{background:var(--sf);border:1px solid var(--bd);border-radius:12px;padding:11px 14px;text-align:center}}
.sv{{font-size:20px;font-weight:800;line-height:1}}
.sv.pos{{color:var(--g)}} .sv.neg{{color:var(--r)}} .sv.neu{{color:var(--ac)}}
.sl{{font-size:10px;color:var(--tm);margin-top:4px}}
.tabs{{max-width:900px;margin:14px auto 0;padding:0 18px;display:flex;gap:8px}}
.tab{{flex:1;padding:11px 8px;border-radius:12px;border:1px solid var(--bd);background:var(--sf);color:var(--tm);font-size:13px;font-weight:600;cursor:pointer;transition:all .18s;display:flex;align-items:center;justify-content:center;gap:6px}}
.tab.hot{{background:var(--gb);border-color:var(--g);color:var(--g)}}
.tab.cold{{background:var(--rb);border-color:var(--r);color:var(--r)}}
.ta{{font-size:12px;font-weight:800;padding:1px 7px;border-radius:20px;background:currentColor;color:var(--bg);opacity:.9}}
.ch{{max-width:900px;margin:14px auto 5px;padding:0 18px;display:grid;grid-template-columns:44px 1fr 106px;gap:10px}}
.cl{{font-size:10px;color:var(--td);font-weight:600;text-transform:uppercase;letter-spacing:.5px}}
.rl{{max-width:900px;margin:0 auto 40px;padding:0 18px}}
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
.disc{{max-width:900px;margin:0 auto 40px;padding:16px 18px 0;border-top:1px solid var(--bd);font-size:11px;color:var(--td);line-height:1.7}}
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
      <div class="lb">🗾</div>
      <span class="lt">日本株テーマランキング</span>
    </div>
    <div style="display:flex;align-items:center;gap:10px">
      <div class="ts">
        <div style="color:var(--g);font-weight:700">✅ 東京市場引け後データ</div>
        <div>取得: {jst_str}</div>
      </div>
      <a href="index.html" class="switch-btn">🇺🇸 米国株テーマ</a>
    </div>
  </div>
</header>
<div class="ab">
  <div class="ai">
    <div class="al">
      <div class="ad"></div>
      <div>
        <div class="alb">⚡ 東京市場引け後データ — 日本株テーマ騰落率</div>
        <div class="as">yfinance 取得 / 前日終値比 1日騰落率 / 構成銘柄の単純平均 / みんかぶへリンク</div>
      </div>
    </div>
    <div class="ar">更新: {jst_str}</div>
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
<script>
function sw(t){{
  document.getElementById('ph').classList.toggle('active',t==='hot');
  document.getElementById('pc').classList.toggle('active',t==='cold');
  document.getElementById('th').className='tab'+(t==='hot'?' hot':'');
  document.getElementById('tc').className='tab'+(t==='cold'?' cold':'');
}}
</script>
</body>
</html>"""

def upload_to_github(html, jst_now):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, script_dir)
        import config as cfg
        token = cfg.GITHUB_TOKEN
        user  = cfg.GITHUB_USER
        repo  = cfg.GITHUB_REPO
    except ImportError:
        return

    if "ここにトークンを貼る" in token or not token.startswith("ghp_"):
        return

    print("GitHub Pages へアップロード中...")
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/jp-themes.html"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "stock-themes-uploader"
    }
    sha = None
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req) as res:
            sha = json.loads(res.read()).get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"SHA取得エラー: {e.code}")

    content_b64 = base64.b64encode(html.encode("utf-8")).decode()
    data = {"message": f"Update JP {jst_now.strftime('%Y-%m-%d %H:%M')} JST", "content": content_b64, "branch": "main"}
    if sha:
        data["sha"] = sha

    try:
        body = json.dumps(data).encode("utf-8")
        req  = urllib.request.Request(api_url, data=body, headers=headers, method="PUT")
        with urllib.request.urlopen(req) as res:
            pass

        # Pages 再デプロイ
        try:
            pages_api = f"https://api.github.com/repos/{user}/{repo}/pages/builds"
            req2 = urllib.request.Request(pages_api, data=b"{}", headers=headers, method="POST")
            with urllib.request.urlopen(req2) as r2:
                print(f"Pages 再デプロイ要求: {r2.status}")
        except Exception as pe:
            print(f"Pages 再デプロイ要求エラー（無視）: {pe}")

        pages_url = f"https://{user}.github.io/{repo}/jp-themes.html"
        print(f"アップロード完了！")
        print(f"\n{'='*50}")
        print(f"  日本株URL: {pages_url}")
        print(f"{'='*50}\n")
        webbrowser.open(pages_url)
    except Exception as e:
        print(f"アップロードエラー: {e}")

def main():
    quote_map  = fetch_quotes()
    theme_data = compute_themes(quote_map)
    jst_now    = datetime.now(timezone(timedelta(hours=9)))
    html       = build_html(theme_data, quote_map, jst_now)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jp-themes.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved: {out}")

    upload_to_github(html, jst_now)

if __name__ == "__main__":
    main()
