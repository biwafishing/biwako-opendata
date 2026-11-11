import sys, json, collections
sys.path.insert(0, ".")
import collect as c
for n in (80, 1, 94, 81):
    fcd = f"06401004{n:05d}"
    d = c.get_json(c.station_url("stg", fcd))
    hv = d.get("hrValues", [])
    cnt = collections.Counter((v.get("stgCcd"), v.get("stg") == 0) for v in hv)
    vals = [v.get("stg") for v in hv if v.get("stgCcd") in (0, None) and v.get("stg") is not None]
    print("RV", fcd, "n", len(hv), dict((str(k), m) for k, m in cnt.items()), "valid", len(vals), "last", vals[:2], "min", min(vals) if vals else None, "max", max(vals) if vals else None)
