import sys, json, collections
sys.path.insert(0, ".")
import collect as c
for label, fcd, th in c.RIVERS:
    d = c.get_json(c.station_url("stg", fcd))
    hv = d.get("hrValues", [])
    cnt = collections.Counter((v.get("stgCcd"), v.get("stg") == 0) for v in hv)
    bad = [c.to_iso(v["obsTime"]) + "=" + str(v.get("stg")) + "/" + str(v.get("stgCcd")) for v in hv if v.get("stgCcd") not in (0, None)]
    print("RV", label, "n", len(hv), dict((str(k), n) for k, n in cnt.items()), "bad:", bad[:2], "...", bad[-1:] )
