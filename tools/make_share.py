"""SNSカード用の share.html / share.png を最新データから作る。"""
import csv, glob, html, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://biwafishing.github.io/biwako-opendata/"
TEMPS = [("雄琴沖", "雄琴沖"), ("安曇川沖", "安曇川沖"), ("唐橋(瀬田川)", "瀬田川")]

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
    im = Image.new("RGB", (W, H), "#fff3e0")
    g = ImageDraw.Draw(im)
    for y in range(H):  # 夕焼けグラデーション
        t = y / H
        c = (int(255 - 40 * t), int(170 - 60 * t), int(90 + 30 * t))
        g.line([(0, y), (W, y)], fill=c)
    g.text((60, 40), "琵琶湖観測データ", font=font(54), fill="white")
    g.text((60, 110), "%s %s 現在" % (md, hhmm), font=font(36, False), fill="white")
    y = 190
    g.rounded_rectangle([40, y, W - 40, H - 40], 28, fill=(255, 255, 255))
    if temps:
        g.text((80, y + 30), "水温", font=font(40, False), fill="#7a4a2a")
        step = (W - 160) // max(len(temps), 1)
        for i, (lab, t) in enumerate(temps):
            x = 80 + i * step
            g.text((x, y + 95), "%.1f" % t[1], font=font(110), fill="#c2410c")
            g.text((x + 235 if t[1] >= 10 else x + 235, y + 160), "℃", font=font(44), fill="#c2410c")
            g.text((x, y + 235), lab, font=font(36, False), fill="#7a4a2a")
    if lv:
        g.text((80, y + 310), "水位(琵琶湖平均)  %+.2f m" % lv[1], font=font(44), fill="#1e40af")
    g.text((W - 40 - 380, H - 40 - 52), "biwafishing.github.io", font=font(26, False), fill="#9a7b5a")
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
