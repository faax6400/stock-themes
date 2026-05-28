"""
米国株テーマランキング - HTML生成スクリプト（GitHub Actions用）
日本株の対応銘柄表示付き
"""

import sys, os, time, json, base64, webbrowser, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

try:
    import yfinance as yf
except ImportError:
    os.system(f'"{sys.executable}" -m pip install yfinance -q')
    import yfinance as yf

# ── テーマ定義（jp = 日本株の対応銘柄）────────────────────
THEMES = [
    # ── HOT ──────────────────────────────────────────────
    {"id":"ai","type":"hot","icon":"🤖","name":"AI・人工知能",
     "stocks":["NVDA","MSFT","GOOGL","META","PLTR"],
     "jp":[{"code":"8035","name":"東京エレクトロン"},{"code":"6857","name":"アドバンテスト"},{"code":"6920","name":"レーザーテック"},{"code":"9984","name":"ソフトバンクG"},{"code":"4307","name":"野村総研"}]},

    {"id":"semi","type":"hot","icon":"💾","name":"半導体・チップ",
     "stocks":["NVDA","AMD","AVGO","MU","AMAT"],
     "jp":[{"code":"8035","name":"東京エレクトロン"},{"code":"6857","name":"アドバンテスト"},{"code":"6920","name":"レーザーテック"},{"code":"6146","name":"ディスコ"},{"code":"4063","name":"信越化学"}]},

    {"id":"defense","type":"hot","icon":"🛡️","name":"防衛・宇宙航空",
     "stocks":["LMT","RTX","NOC","GD","AXON"],
     "jp":[{"code":"7011","name":"三菱重工"},{"code":"7013","name":"IHI"},{"code":"7012","name":"川崎重工"},{"code":"6268","name":"ナブテスコ"},{"code":"7003","name":"三井E&S"}]},

    {"id":"cyber","type":"hot","icon":"🔒","name":"サイバーセキュリティ",
     "stocks":["CRWD","PANW","ZS","FTNT","OKTA"],
     "jp":[{"code":"4704","name":"トレンドマイクロ"},{"code":"2326","name":"デジタルアーツ"},{"code":"6701","name":"NEC"},{"code":"6702","name":"富士通"},{"code":"4307","name":"野村総研"}]},

    {"id":"cloud","type":"hot","icon":"☁️","name":"クラウド・データセンター",
     "stocks":["AMZN","MSFT","EQIX","DLR","VRT"],
     "jp":[{"code":"9432","name":"NTT"},{"code":"3626","name":"TIS"},{"code":"6701","name":"NEC"},{"code":"6702","name":"富士通"},{"code":"4307","name":"野村総研"}]},

    {"id":"grid","type":"hot","icon":"⚡","name":"電力インフラ・グリッド",
     "stocks":["ETN","GEV","VST","CEG","PWR"],
     "jp":[{"code":"6504","name":"富士電機"},{"code":"6506","name":"安川電機"},{"code":"5631","name":"日本製鋼所"},{"code":"6273","name":"SMC"},{"code":"6361","name":"荏原製作所"}]},

    {"id":"nuclear","type":"hot","icon":"☢️","name":"原子力エネルギー",
     "stocks":["CEG","VST","CCJ","NRG","ETR"],
     "jp":[{"code":"1963","name":"日揮HD"},{"code":"7011","name":"三菱重工"},{"code":"9501","name":"東京電力HD"},{"code":"9503","name":"関西電力"},{"code":"6503","name":"三菱電機"}]},

    {"id":"robot","type":"hot","icon":"🦾","name":"ロボティクス・自動化",
     "stocks":["ISRG","PATH","TER","RRX","TRMB"],
     "jp":[{"code":"6954","name":"ファナック"},{"code":"6506","name":"安川電機"},{"code":"7013","name":"IHI"},{"code":"6326","name":"クボタ"},{"code":"6302","name":"住友重機械"}]},

    {"id":"glp1","type":"hot","icon":"💊","name":"GLP-1・肥満治療薬",
     "stocks":["LLY","NVO","VKTX","AMGN","REGN"],
     "jp":[{"code":"4523","name":"エーザイ"},{"code":"4519","name":"中外製薬"},{"code":"4503","name":"アステラス"},{"code":"4502","name":"武田薬品"},{"code":"4151","name":"協和キリン"}]},

    {"id":"space","type":"hot","icon":"🚀","name":"宇宙開発・衛星",
     "stocks":["RKLB","ASTS","LUNR","BA","BWXT"],
     "jp":[{"code":"7011","name":"三菱重工"},{"code":"6503","name":"三菱電機"},{"code":"7013","name":"IHI"},{"code":"6268","name":"ナブテスコ"},{"code":"9022","name":"JR東海"}]},

    {"id":"quantum","type":"hot","icon":"⚛️","name":"量子コンピュータ",
     "stocks":["IONQ","RGTI","QBTS","IBM","GOOGL"],
     "jp":[{"code":"6501","name":"日立製作所"},{"code":"6702","name":"富士通"},{"code":"9432","name":"NTT"},{"code":"6503","name":"三菱電機"},{"code":"6701","name":"NEC"}]},

    {"id":"fintech","type":"hot","icon":"💳","name":"フィンテック・決済",
     "stocks":["V","MA","PYPL","NU","AFRM"],
     "jp":[{"code":"3769","name":"GMO-PG"},{"code":"4385","name":"メルカリ"},{"code":"8473","name":"SBI HD"},{"code":"4689","name":"LINEヤフー"},{"code":"3774","name":"IIJ"}]},

    {"id":"govtech","type":"hot","icon":"🏛️","name":"国防テック・DIU",
     "stocks":["PLTR","AXON","CACI","LDOS","SAIC"],
     "jp":[{"code":"7011","name":"三菱重工"},{"code":"7013","name":"IHI"},{"code":"7012","name":"川崎重工"},{"code":"6701","name":"NEC"},{"code":"6268","name":"ナブテスコ"}]},

    {"id":"ecom","type":"hot","icon":"🛒","name":"eコマース・D2C",
     "stocks":["AMZN","SHOP","MELI","ETSY","SE"],
     "jp":[{"code":"4755","name":"楽天グループ"},{"code":"4385","name":"メルカリ"},{"code":"9983","name":"ファーストリテイリング"},{"code":"4689","name":"LINEヤフー"},{"code":"3064","name":"MonotaRO"}]},

    {"id":"digad","type":"hot","icon":"🌐","name":"デジタル広告",
     "stocks":["META","GOOGL","AMZN","TTD","PUBM"],
     "jp":[{"code":"4324","name":"電通グループ"},{"code":"2433","name":"博報堂DY"},{"code":"4689","name":"LINEヤフー"},{"code":"6098","name":"リクルートHD"},{"code":"2432","name":"DeNA"}]},

    {"id":"bank","type":"hot","icon":"🏦","name":"投資銀行・大手金融",
     "stocks":["JPM","GS","MS","BAC","BLK"],
     "jp":[{"code":"8306","name":"三菱UFJ FG"},{"code":"8316","name":"三井住友FG"},{"code":"8411","name":"みずほFG"},{"code":"8601","name":"大和証券G"},{"code":"8604","name":"野村HD"}]},

    {"id":"infra","type":"hot","icon":"🏗️","name":"インフラ・建機",
     "stocks":["CAT","DE","VMC","URI","PWR"],
     "jp":[{"code":"6301","name":"コマツ"},{"code":"6326","name":"クボタ"},{"code":"7011","name":"三菱重工"},{"code":"1801","name":"大成建設"},{"code":"1802","name":"大林組"}]},

    {"id":"auto","type":"hot","icon":"🚗","name":"自律走行・モビリティ",
     "stocks":["TSLA","UBER","LYFT","GM","F"],
     "jp":[{"code":"7203","name":"トヨタ自動車"},{"code":"7267","name":"本田技研"},{"code":"6954","name":"ファナック"},{"code":"6506","name":"安川電機"},{"code":"7261","name":"マツダ"}]},

    {"id":"hlhai","type":"hot","icon":"🏥","name":"ヘルスケアAI・デジタル医療",
     "stocks":["ISRG","VEEV","DXCM","GEHC","TDOC"],
     "jp":[{"code":"2413","name":"エムスリー"},{"code":"4519","name":"中外製薬"},{"code":"4523","name":"エーザイ"},{"code":"6701","name":"NEC"},{"code":"4307","name":"野村総研"}]},

    {"id":"bat","type":"hot","icon":"🔋","name":"蓄電池・エネルギー貯蓄",
     "stocks":["TSLA","ENPH","FLNC","STEM","BE"],
     "jp":[{"code":"6752","name":"パナソニックHD"},{"code":"6674","name":"GSユアサ"},{"code":"5334","name":"日本特殊陶業"},{"code":"4183","name":"三井化学"},{"code":"6770","name":"アルプスアルパイン"}]},

    {"id":"photon","type":"hot","icon":"💡","name":"光・フォトニクス（光ネットワーク）",
     "stocks":["CIEN","LITE","COHR","AAOI","VIAV"],
     "jp":[{"code":"6965","name":"浜松ホトニクス"},{"code":"7741","name":"HOYA"},{"code":"5803","name":"フジクラ"},{"code":"6920","name":"レーザーテック"},{"code":"6758","name":"ソニーグループ"}]},

    {"id":"hbm","type":"hot","icon":"🧠","name":"HBM・高帯域メモリ",
     "stocks":["MU","WDC","LRCX","ONTO","AMAT"],
     "jp":[{"code":"8035","name":"東京エレクトロン"},{"code":"6146","name":"ディスコ"},{"code":"6857","name":"アドバンテスト"},{"code":"6920","name":"レーザーテック"},{"code":"4063","name":"信越化学"}]},

    # ── COLD ─────────────────────────────────────────────
    {"id":"canna","type":"cold","icon":"🌿","name":"大麻・カンナビス",
     "stocks":["MSOS","TLRY","CGC","ACB","CRON"],
     "jp":[]},

    {"id":"chntech","type":"cold","icon":"🇨🇳","name":"中国テック（ADR）",
     "stocks":["BABA","JD","PDD","BIDU","NIO"],
     "jp":[{"code":"9984","name":"ソフトバンクG"},{"code":"8591","name":"オリックス"},{"code":"6752","name":"パナソニックHD"},{"code":"7203","name":"トヨタ自動車"}]},

    {"id":"ofcreit","type":"cold","icon":"🏢","name":"オフィス不動産（REIT）",
     "stocks":["BXP","VNO","SLG","DEI","PDM"],
     "jp":[{"code":"8801","name":"三井不動産"},{"code":"8802","name":"三菱地所"},{"code":"8830","name":"住友不動産"},{"code":"8804","name":"東京建物"}]},

    {"id":"bio","type":"cold","icon":"🔬","name":"臨床段階バイオテック",
     "stocks":["XBI","SRPT","RARE","ALKS","ARQT"],
     "jp":[{"code":"4503","name":"アステラス"},{"code":"4523","name":"エーザイ"},{"code":"4151","name":"協和キリン"},{"code":"4568","name":"第一三共"},{"code":"4519","name":"中外製薬"}]},

    {"id":"coal","type":"cold","icon":"⛽","name":"石炭・旧来型化石燃料",
     "stocks":["BTU","METC","AMR","ARLP","HNRG"],
     "jp":[{"code":"1605","name":"INPEX"},{"code":"5020","name":"ENEOS HD"},{"code":"1662","name":"石油資源開発"},{"code":"5019","name":"出光興産"}]},

    {"id":"media","type":"cold","icon":"📺","name":"旧来型メディア・放送",
     "stocks":["FOXA","WBD","AMCX","DIS","NWSA"],
     "jp":[{"code":"9404","name":"日本テレビHD"},{"code":"9401","name":"TBS HD"},{"code":"9413","name":"テレビ東京HD"},{"code":"4324","name":"電通グループ"},{"code":"2433","name":"博報堂DY"}]},

    {"id":"regbk","type":"cold","icon":"🏦","name":"地方銀行・リージョナル",
     "stocks":["KRE","WAL","FHN","HBAN","ZION"],
     "jp":[{"code":"8369","name":"京都銀行"},{"code":"8379","name":"広島銀行"},{"code":"8355","name":"静岡銀行"},{"code":"8341","name":"七十七銀行"}]},

    {"id":"chnev","type":"cold","icon":"🚙","name":"中国EV",
     "stocks":["NIO","XPEV","LI","PSNY","KNDI"],
     "jp":[{"code":"7203","name":"トヨタ自動車"},{"code":"7267","name":"本田技研"},{"code":"7201","name":"日産自動車"},{"code":"7261","name":"マツダ"}]},

    {"id":"h2","type":"cold","icon":"🔌","name":"水素・燃料電池",
     "stocks":["PLUG","FCEL","BE","BLDP","CLNE"],
     "jp":[{"code":"7203","name":"トヨタ自動車"},{"code":"7267","name":"本田技研"},{"code":"5020","name":"ENEOS HD"},{"code":"7011","name":"三菱重工"},{"code":"4063","name":"信越化学"}]},

    {"id":"retail","type":"cold","icon":"🏬","name":"旧来型小売・百貨店",
     "stocks":["TGT","M","KSS","ROST","DDS"],
     "jp":[{"code":"8267","name":"イオン"},{"code":"3382","name":"セブン&アイHD"},{"code":"2651","name":"ローソン"},{"code":"7453","name":"良品計画"},{"code":"3099","name":"三越伊勢丹"}]},

    {"id":"agri","type":"cold","icon":"🌱","name":"農業・肥料",
     "stocks":["MOS","NTR","ADM","BG","CF"],
     "jp":[{"code":"4004","name":"レゾナックHD"},{"code":"4188","name":"三菱ケミカルG"},{"code":"4183","name":"三井化学"},{"code":"2002","name":"日清製粉G"}]},

    {"id":"gaming","type":"cold","icon":"🎮","name":"モバイルゲーム・メタバース",
     "stocks":["EA","TTWO","RBLX","U","SNAP"],
     "jp":[{"code":"3765","name":"ガンホー"},{"code":"2432","name":"DeNA"},{"code":"3632","name":"グリー"},{"code":"4751","name":"サイバーエージェント"},{"code":"9684","name":"スクウェア・エニックス"}]},

    {"id":"hmo","type":"cold","icon":"🩺","name":"ヘルスケア保険・MCO",
     "stocks":["UNH","CVS","HUM","MOH","CNC"],
     "jp":[{"code":"8766","name":"東京海上HD"},{"code":"8725","name":"MS&AD"},{"code":"8750","name":"第一生命HD"},{"code":"8630","name":"SOMPO HD"},{"code":"7181","name":"かんぽ生命"}]},

    {"id":"telco","type":"cold","icon":"📡","name":"旧来型通信キャリア",
     "stocks":["T","VZ","LUMN","CHTR","TMUS"],
     "jp":[{"code":"9432","name":"NTT"},{"code":"9433","name":"KDDI"},{"code":"9434","name":"ソフトバンク"},{"code":"9613","name":"NTTデータ"}]},

    {"id":"em","type":"cold","icon":"🌍","name":"新興国株（EM）",
     "stocks":["EEM","EWZ","FXI","TUR","EWY"],
     "jp":[{"code":"9984","name":"ソフトバンクG"},{"code":"8306","name":"三菱UFJ FG"},{"code":"8591","name":"オリックス"},{"code":"7203","name":"トヨタ自動車"}]},

    {"id":"solar","type":"cold","icon":"☀️","name":"太陽光・風力（旧来型）",
     "stocks":["ENPH","SEDG","RUN","FSLR","ARRY"],
     "jp":[{"code":"9501","name":"東京電力HD"},{"code":"9503","name":"関西電力"},{"code":"9531","name":"東京ガス"},{"code":"5020","name":"ENEOS HD"},{"code":"6506","name":"安川電機"}]},

    {"id":"creit","type":"cold","icon":"🏙️","name":"商業用不動産・REIT全般",
     "stocks":["SPG","O","CBRE","JLL","WPC"],
     "jp":[{"code":"8801","name":"三井不動産"},{"code":"8802","name":"三菱地所"},{"code":"8830","name":"住友不動産"},{"code":"8804","name":"東京建物"},{"code":"8905","name":"イオンモール"}]},

    {"id":"gene","type":"cold","icon":"🧬","name":"遺伝子治療・ゲノム編集",
     "stocks":["NTLA","EDIT","CRSP","BEAM","SGMO"],
     "jp":[{"code":"4503","name":"アステラス"},{"code":"4151","name":"協和キリン"},{"code":"4568","name":"第一三共"},{"code":"4523","name":"エーザイ"},{"code":"4519","name":"中外製薬"}]},

    {"id":"shale","type":"cold","icon":"🛢️","name":"シェールオイル・ガス",
     "stocks":["OXY","DVN","APA","FANG","SWN"],
     "jp":[{"code":"1605","name":"INPEX"},{"code":"5020","name":"ENEOS HD"},{"code":"1662","name":"石油資源開発"},{"code":"5019","name":"出光興産"},{"code":"9531","name":"東京ガス"}]},

    {"id":"cruise","type":"cold","icon":"🚢","name":"クルーズ・旅行（景気敏感）",
     "stocks":["CCL","RCL","NCLH","MAR","H"],
     "jp":[{"code":"9202","name":"ANA HD"},{"code":"9201","name":"JAL"},{"code":"9603","name":"H.I.S."},{"code":"3099","name":"三越伊勢丹"},{"code":"9726","name":"近畿日本ツーリスト"}]},
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
                    quote_map[ticker] = {"chg": round((curr - prev) / prev * 100, 2)}
                else:
                    quote_map[ticker] = {"chg": None}
            except Exception:
                quote_map[ticker] = {"chg": None}
    except Exception as e:
        print(f"Batch failed: {e}, trying individual...")
        for i, ticker in enumerate(ALL_TICKERS):
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

            # 米国株チップ
            us_chips = ""
            for s in t["stocks"]:
                chg = quote_map.get(s, {}).get("chg")
                ct  = fmt(chg)
                cc  = "dim" if chg is None else ("pos" if chg >= 0 else "neg")
                chip_cls = "" if chg is None else ("pos-chip" if chg >= 0 else "neg-chip")
                us_chips += f'<a href="https://finance.yahoo.com/quote/{s}" target="_blank" class="chip {chip_cls}"><span class="tkr">{s}</span><span class="chg {cc}">{ct}</span></a>'

            # 日本株チップ
            jp_chips = ""
            if t.get("jp"):
                for jp in t["jp"]:
                    jp_chips += f'<a href="https://minkabu.jp/stock/{jp["code"]}" target="_blank" class="chip jp-chip"><span class="tkr">{jp["code"]}</span><span class="jpname">{jp["name"]}</span></a>'
                jp_row = f'<div class="jp-row"><span class="jp-label">🇯🇵</span><div class="chips">{jp_chips}</div></div>'
            else:
                jp_row = ""

            medal = {1:"🥇",2:"🥈",3:"🥉"}.get(rank, str(rank))
            html += f"""
<div class="item {ttype}">
  <div class="bg-bar" style="width:{bw}"></div>
  <div class="rn">{medal}</div>
  <div class="ti">
    <div class="tn"><span class="tic">{t['icon']}</span><span class="tnt">{t['name']}</span></div>
    <div class="chips">{us_chips}</div>
    {jp_row}
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
--ac:#7c6ff7;--jp:#f5a623;--jpb:rgba(245,166,35,.12);}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--tx);font-family:-apple-system,'Hiragino Sans','Noto Sans JP',sans-serif;min-height:100vh}}
header{{position:sticky;top:0;z-index:100;background:rgba(10,10,15,.95);backdrop-filter:blur(20px);border-bottom:1px solid var(--bd)}}
.hi{{max-width:900px;margin:0 auto;padding:0 18px;height:54px;display:flex;align-items:center;justify-content:space-between}}
.logo{{display:flex;align-items:center;gap:8px}}
.lb{{width:28px;height:28px;border-radius:7px;background:linear-gradient(135deg,#7c6ff7,#a78bfa);display:flex;align-items:center;justify-content:center;font-size:15px}}
.lt{{font-size:14px;font-weight:700}}
.ts{{font-size:11px;color:var(--tm);text-align:right}}
.qr-btn{{background:var(--sf2);border:1px solid var(--bd);color:var(--tm);border-radius:8px;padding:5px 11px;font-size:12px;cursor:pointer;transition:all .15s;display:flex;align-items:center;gap:5px;white-space:nowrap}}
.qr-btn:hover{{border-color:var(--ac);color:var(--ac)}}
.switch-btn{{background:rgba(76,175,80,.12);border:1px solid rgba(76,175,80,.35);color:#66bb6a;border-radius:8px;padding:5px 11px;font-size:12px;cursor:pointer;text-decoration:none;display:flex;align-items:center;gap:5px;white-space:nowrap;transition:all .15s}}
.switch-btn:hover{{background:rgba(76,175,80,.25);border-color:#66bb6a}}
#qr-overlay{{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:200;display:flex;align-items:center;justify-content:center}}
#qr-box{{background:var(--sf);border:1px solid var(--bd);border-radius:20px;padding:28px;text-align:center;z-index:201;max-width:280px;width:90%}}
#qr-box h3{{font-size:15px;margin-bottom:16px}}
#qr-code{{display:flex;justify-content:center;margin-bottom:14px}}
#qr-url{{font-size:11px;color:var(--tm);word-break:break-all;margin-bottom:16px;background:var(--sf2);padding:8px;border-radius:8px}}
#qr-close{{background:var(--ac);border:none;color:#fff;border-radius:8px;padding:8px 20px;font-size:13px;cursor:pointer;font-weight:600}}
.ab{{max-width:900px;margin:14px auto 0;padding:0 18px}}
.ai{{border-radius:12px;padding:11px 16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;background:rgba(124,111,247,.08);border:1px solid rgba(124,111,247,.3)}}
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
.item{{position:relative;overflow:hidden;display:grid;grid-template-columns:44px 1fr 106px;align-items:start;gap:10px;padding:13px 14px;border-radius:14px;border:1px solid transparent;background:var(--sf);margin-bottom:5px;transition:all .15s}}
.item:hover{{border-color:var(--bd);background:var(--sf2);transform:translateY(-1px)}}
.item::before{{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;border-radius:3px 0 0 3px}}
.item.hot::before{{background:var(--g)}} .item.cold::before{{background:var(--r)}}
.bg-bar{{position:absolute;top:0;right:0;bottom:0;pointer-events:none;border-radius:0 14px 14px 0;opacity:.055}}
.item.hot .bg-bar{{background:linear-gradient(90deg,transparent,var(--g))}}
.item.cold .bg-bar{{background:linear-gradient(90deg,transparent,var(--r))}}
.rn{{width:44px;text-align:center;font-size:18px;font-weight:800;color:var(--td);z-index:1;padding-top:2px}}
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
.chip.jp-chip{{background:var(--jpb);border-color:rgba(245,166,35,.3);color:var(--jp);gap:4px}}
.chip.jp-chip:hover{{border-color:rgba(245,166,35,.7);background:rgba(245,166,35,.2)}}
.chip.jp-chip .jpname{{font-size:9px;font-weight:500;color:rgba(245,166,35,.8)}}
.jp-row{{display:flex;align-items:flex-start;gap:5px;margin-top:5px;padding-top:5px;border-top:1px solid var(--bd)}}
.jp-label{{font-size:12px;flex-shrink:0;margin-top:2px}}
.tkr{{letter-spacing:.3px}}
.chg{{font-weight:700}}
.chg.pos{{color:var(--g)}} .chg.neg{{color:var(--r)}} .chg.dim{{color:var(--td)}}
.ret{{z-index:1;text-align:right;padding-top:2px}}
.rp{{font-size:20px;font-weight:800;letter-spacing:-.5px;line-height:1}}
.rp.pos{{color:var(--g)}} .rp.neg{{color:var(--r)}} .rp.dim{{color:var(--td);font-size:14px}}
.rl{{font-size:10px;color:var(--td);margin-top:3px}}
.disc{{max-width:900px;margin:0 auto 40px;padding:16px 18px 0;border-top:1px solid var(--bd);font-size:11px;color:var(--td);line-height:1.7}}
@media(max-width:560px){{
  .item{{grid-template-columns:32px 1fr 82px;padding:11px 10px}}
  .rn{{width:32px;font-size:14px}}
  .rp{{font-size:15px}}
  .chip.jp-chip .jpname{{display:none}}
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
      <a href="jp-themes.html" class="switch-btn">🗾 日本株テーマ</a>
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
        <div class="as">🇺🇸 米国株クリック → Yahoo Finance｜🇯🇵 日本株クリック → みんかぶ</div>
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
  <span class="cl">テーマ / 🇺🇸米国株 / 🇯🇵日本株</span>
  <span class="cl" style="text-align:right">テーマ平均</span>
</div>
<div class="rl">
  <div class="panel active" id="ph">{hot_panel}</div>
  <div class="panel" id="pc">{cold_panel}</div>
</div>
<div class="disc">
  ⚠️ 本ページは情報提供目的のみ。騰落率は yfinance 経由の参考値（前日終値比）。日本株は参考銘柄（騰落率非表示）。投資は自己判断・自己責任で。
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
  document.getElementById('ph').classList.toggle('active',t==='hot');
  document.getElementById('pc').classList.toggle('active',t==='cold');
  document.getElementById('th').className='tab'+(t==='hot'?' hot':'');
  document.getElementById('tc').className='tab'+(t==='cold'?' cold':'');
}}
let qrGenerated=false;
function showQR(){{
  const url=window.location.href;
  document.getElementById('qr-url').textContent=url;
  if(!qrGenerated){{
    try{{
      new QRCode(document.getElementById('qr-code'),{{text:url,width:200,height:200,colorDark:'#ffffff',colorLight:'#12121a',correctLevel:QRCode.CorrectLevel.M}});
      qrGenerated=true;
    }}catch(e){{document.getElementById('qr-code').innerHTML='<p style="color:#6a6a8a;font-size:12px">QRコード生成にはインターネット接続が必要です</p>';}}
  }}
  document.getElementById('qr-overlay').style.display='flex';
}}
function hideQR(){{document.getElementById('qr-overlay').style.display='none';}}
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
        return  # GitHub Actions では config.py 不要（スキップ）

    if "ここにトークンを貼る" in token or not token.startswith("ghp_"):
        print("config.py のトークンが未設定のためアップロードをスキップ")
        return

    print("GitHub Pages へアップロード中...")
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/index.html"
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
    data = {"message": f"Update {jst_now.strftime('%Y-%m-%d %H:%M')} JST", "content": content_b64, "branch": "main"}
    if sha:
        data["sha"] = sha

    try:
        body = json.dumps(data).encode("utf-8")
        req  = urllib.request.Request(api_url, data=body, headers=headers, method="PUT")
        with urllib.request.urlopen(req) as res:
            pass
        pages_url = f"https://{user}.github.io/{repo}/"

        # GitHub Pages を強制再デプロイ
        try:
            pages_api = f"https://api.github.com/repos/{user}/{repo}/pages/builds"
            req2 = urllib.request.Request(pages_api, data=b"{}", headers=headers, method="POST")
            with urllib.request.urlopen(req2) as r2:
                print(f"Pages 再デプロイ要求: {r2.status}")
        except Exception as pe:
            print(f"Pages 再デプロイ要求エラー（無視）: {pe}")

        print(f"アップロード完了！")
        print(f"\n{'='*50}")
        print(f"  スマホURL: {pages_url}")
        print(f"{'='*50}\n")
        webbrowser.open(pages_url)
    except Exception as e:
        print(f"アップロードエラー: {e}")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        out_file = os.path.join(script_dir, "index.html")
        webbrowser.open(f"file:///{out_file.replace(os.sep, '/')}")

def main():
    quote_map  = fetch_quotes()
    theme_data = compute_themes(quote_map)
    jst_now    = datetime.now(timezone(timedelta(hours=9)))
    html       = build_html(theme_data, quote_map, jst_now)

    # ローカルに保存
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved: {out}")

    # GitHub へアップロード（config.py がある場合）
    upload_to_github(html, jst_now)

if __name__ == "__main__":
    main()
