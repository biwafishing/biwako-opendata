import sys, json
sys.path.insert(0, ".")
import collect as c
for code in ("2203900600001", "2203900600002", "2203900600006"):
    d = c.get_json(c.station_url("qwtr", code))
    print("STATION", code, "keys", list(d.keys()))
    hv = d.get("hrValues", [])
    for v in hv[:3] + hv[-6:]:
        print("HR", code, json.dumps(v, ensure_ascii=False))
    mv = d.get("min10Values", [])
    for v in mv[-3:]:
        print("M10", code, json.dumps(v, ensure_ascii=False))
