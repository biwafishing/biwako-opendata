"""直近15年(2011-2025)の同じ日・同じ時刻の平均気温(平年値の目安)を作り、data/temp_normals.json に保存する。
基準は4地点(北湖北・北湖東・湖西中央・南湖)。出典: Open-Meteo Historical Weather API (ERA5 ほか)。"""
import json, sys, time, urllib.request, urllib.parse
from datetime import date

REFS = [("北湖北", 35.4, 136.1), ("北湖東", 35.27, 136.27), ("湖西中央", 35.2, 135.97), ("南湖", 35.02, 135.88)]
Y0, Y1 = 2011, 2025
CH = 5  # 年ごとにまとめて取得

def fetch(lat, lon, a, b):
    q = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "start_date": a, "end_date": b,
                                "hourly": "temperature_2m", "timezone": "Asia/Tokyo"})
    u = "https://archive-api.open-meteo.com/v1/archive?" + q
    for i in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "biwako-normals/0.1"}), timeout=120) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print("retry", i, e, file=sys.stderr)
            time.sleep(20 * (i + 1))
    raise SystemExit("取得に失敗しました")

def doy_index(d):  # 2月29日を含む366日の通し番号(うるう年基準)
    return date(2000, d.month, d.day).timetuple().tm_yday - 1

out = {"period": f"{Y0}-{Y1}", "source": "Open-Meteo Historical Weather API", "refs": []}
for name, lat, lon in REFS:
    S = [[0.0] * 24 for _ in range(366)]; N = [[0] * 24 for _ in range(366)]
    for y in range(Y0, Y1 + 1, CH):
        j = fetch(lat, lon, f"{y}-01-01", f"{min(y + CH - 1, Y1)}-12-31")
        h = j["hourly"]
        for t, v in zip(h["time"], h["temperature_2m"]):
            if v is None: continue
            d = date(int(t[:4]), int(t[5:7]), int(t[8:10])); i = doy_index(d); hr = int(t[11:13])
            S[i][hr] += v; N[i][hr] += 1
        time.sleep(3)
    M = [[(S[i][k] / N[i][k]) if N[i][k] else None for k in range(24)] for i in range(366)]
    # 前後7日(計15日)で滑らかにする(年またぎあり)
    sm = []
    for i in range(366):
        row = []
        for k in range(24):
            vals = [M[(i + w) % 366][k] for w in range(-7, 8) if M[(i + w) % 366][k] is not None]
            row.append(round(sum(vals) / len(vals), 1))
        sm.append(row)
    out["refs"].append({"name": name, "lat": lat, "lon": lon, "n": sm})
    print(name, "ok", sm[0][12], sm[180][12], flush=True)
json.dump(out, open("data/temp_normals.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("saved")
