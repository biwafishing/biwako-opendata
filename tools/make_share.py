"""SNSカード用の share.html / share.png を最新データから作る。"""
import csv, glob, html, math, os, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://biwafishing.github.io/biwako-opendata/"
TEMPS = [("雄琴沖", "雄琴沖"), ("安曇川沖", "安曇川沖"), ("唐橋(瀬田川)", "瀬田川")]
PINS = {"海津大崎": "海津大崎", "安曇川": "安曇川", "彦根": "彦根", "沖島": "沖島", "琵琶湖大橋": "琵琶湖大橋", "プリンスホテル前": "プリンスホテル前"}

def latest():
    last = {}
    with (ROOT / "data/observations.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            k = "level" if r["level"] else "flow" if r["flow"] else "temp"
            if r[k] == "":
                continue
            last[(r["place"], k)] = (r["time"], float(r[k]))
    return last

def font(size, bold=True):
    names = ["NotoSansCJK-Bold.ttc", "NotoSansCJK-Regular.ttc"] if bold else ["NotoSansCJK-Regular.ttc"]
    for n in names:
        for p in glob.glob("/usr/share/fonts/**/" + n, recursive=True):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

EMO = lambda c: "☀️" if c == 0 else "🌤" if c == 1 else "⛅" if c == 2 else "☁️" if c == 3 else "🌫" if c <= 48 else "🌦" if c <= 57 else "🌧" if c <= 67 else "🌨" if c <= 77 else "🌧" if c <= 82 else "🌨" if c <= 86 else "⛈"

def emoji(im, ch, xy, size):
    for p in glob.glob("/usr/share/fonts/**/NotoColorEmoji.ttf", recursive=True):
        f = ImageFont.truetype(p, 109)
        t = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((0, 0), ch, font=f, embedded_color=True)
        t = t.resize((size, int(size * 128 / 136)))
        im.paste(t, (int(xy[0]), int(xy[1])), t)
        return

def main():
    d = latest()
    lv = d.get(("琵琶湖(平均)", "level"))
    temps = [(lab, d[(p, "temp")]) for p, lab in TEMPS if (p, "temp") in d]
    when = max([v[0] for v in d.values()]) if d else ""
    hhmm = when[11:16]; md = "%d/%d" % (int(when[5:7]), int(when[8:10])) if when else ""
    parts = []
    if temps:
        parts.append("水温 " + " ".join("%s%.1f℃" % (l, t[1]) for l, t in temps))
    if lv:
        parts.append("水位 %+.2fm" % lv[1])
    title = "琵琶湖観測データ %s %s現在" % (md, hhmm)
    desc = " / ".join(parts) or "琵琶湖の水温・水位・天気を自動収集"

    W, H = 1200, 630
    im = Image.new("RGB", (W, H))
    g = ImageDraw.Draw(im)
    for y in range(H):  # 夕焼けグラデーション
        t = y / H
        g.line([(0, y), (W, y)], fill=(int(255 - 40 * t), int(170 - 60 * t), int(90 + 30 * t)))
    g.rounded_rectangle([30, 30, W - 30, H - 30], 28, fill="white")

    # --- 左: 琵琶湖マップ(代表6地点の風) ---
    try:
        src = (ROOT / "index.html").read_text(encoding="utf-8")
        LAKE = eval(re.search(r"const LAKE=(\[\[.*?\]\]);", src).group(1))
        WXP = eval(re.search(r"const WXP=(\[\[.*?\]\]);", src).group(1))
        wx = {}
        with (ROOT / "data/weather_hourly_2026.csv").open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["wind"] != "" and r["dir"] != "":
                    wx[r["place"]] = r
        sc = 0.76; ox, oy = 175, 50
        P = lambda x, y: (ox + x * sc, oy + y * sc)
        g.polygon([P(*p) for p in LAKE], fill=(214, 232, 248), outline=(120, 160, 200))
        col = lambda v: (229, 83, 61) if v >= 6 else (242, 153, 74) if v >= 4 else (60, 140, 90)
        fp = font(24)
        for name, lat, lon, side, x, y in WXP:
            if name not in PINS or name not in wx:
                continue
            v = float(wx[name]["wind"]); d = float(wx[name]["dir"])
            cx, cy = P(x, y)
            a = math.radians(d + 180)  # 風が吹いていく向き
            dx, dy = math.sin(a), -math.cos(a)
            L = 20
            tip = (cx + dx * L, cy + dy * L); tail = (cx - dx * L, cy - dy * L)
            c = col(v)
            g.line([tail, tip], fill=c, width=7)
            px, py = -dy, dx
            g.polygon([tip, (tip[0] - dx * 15 + px * 10, tip[1] - dy * 15 + py * 10),
                       (tip[0] - dx * 15 - px * 10, tip[1] - dy * 15 - py * 10)], fill=c)
            pr = float(wx[name].get("precip") or 0)
            l1 = "%s %.1fm/s" % (PINS[name], v)
            l2 = "(%smm)" % (("%.1f" % pr) if pr else "0")
            w1 = g.textlength(l1, font=fp)
            w2 = 36 + g.textlength(l2, font=font(22))
            wmax = max(w1, w2)
            left = cx + 30 if side == "r" else cx - 30 - wmax
            g.text((left, cy - 30), l1, font=fp, fill="#333")
            emoji(im, EMO(int(wx[name]["code"])), (left, cy + 2), 30)
            g.text((left + 36, cy + 4), l2, font=font(22), fill="#1e40af" if pr else "#7a6a5a")
        # 色分けの凡例(地図の下に小さく)
        fl = font(20, False); lx = 175; ly = H - 30 - 52
        for txt, c in (("風 ~4m/s", (60, 140, 90)), ("4m/s~", (242, 153, 74)), ("6m/s~", (229, 83, 61))):
            g.ellipse([lx, ly + 5, lx + 16, ly + 21], fill=c)
            g.text((lx + 22, ly), txt, font=fl, fill="#7a4a2a")
            lx += 22 + g.textlength(txt, font=fl) + 22
    except Exception as e:
        print("map skipped:", e, file=sys.stderr)

    # --- 右: 水温(全観測地点)と水位 ---
    x0 = 700
    g.text((x0, 55), "琵琶湖観測データ", font=font(46), fill="#c2410c")
    g.text((x0, 118), "%s %s 現在" % (md, hhmm), font=font(30, False), fill="#7a4a2a")
    g.text((x0, 185), "水温", font=font(30, False), fill="#7a4a2a")
    y = 215
    for lab, t in temps:
        g.text((x0, y + 18), lab, font=font(32, False), fill="#7a4a2a")
        g.text((x0 + 210, y), "%.1f" % t[1], font=font(76), fill="#0e7490")
        g.text((x0 + 210 + g.textlength("%.1f" % t[1], font=font(76)) + 6, y + 36), "℃", font=font(36), fill="#0e7490")
        y += 88
    if lv:
        g.text((x0, y + 12), "水位 %+.2f m" % lv[1], font=font(42), fill="#1e40af")
    im = im.quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(ROOT / "share.png", optimize=True)

    img = BASE + "share.png?v=" + when.replace("-", "").replace(":", "").replace("T", "")
    e = html.escape
    (ROOT / "share.html").write_text(f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<title>{e(title)}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{e(img)}">
<meta property="og:url" content="{BASE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{e(img)}">
<meta http-equiv="refresh" content="0; url={BASE}">
</head><body><p><a href="{BASE}">琵琶湖観測データを開く</a></p>
<script>location.replace("{BASE}")</script></body></html>
""", encoding="utf-8")
    print(title, "|", desc)

main()
