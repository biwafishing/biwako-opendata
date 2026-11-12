import time,urllib.request
for name,q in (("WXU","&current=temperature_2m,weather_code,wind_speed_10m,wind_direction_10m&hourly=weather_code,precipitation,wind_speed_10m,wind_direction_10m,wind_gusts_10m&daily=precipitation_sum,weather_code,wind_speed_10m_max,temperature_2m_max,temperature_2m_min&timezone=Asia%2FTokyo&wind_speed_unit=ms&past_days=2&forecast_days=2"),("WXFU","&daily=weather_code&timezone=Asia%2FTokyo&forecast_days=14")):
    u="https://api.open-meteo.com/v1/forecast?latitude=35.5023836,35.4482187,35.3876593,35.285681,35.2024571,35.3209525,35.2008873,35.1211542,35.0715445,35.0544148,35.005424&longitude=136.1669634,136.0915766,136.2155335,136.2464279,136.0636766,136.0780844,135.9264253,135.9355907,135.9326148,135.8793787,135.8914975"+q
    for i in range(3):
        t=time.time()
        try:
            r=urllib.request.urlopen(u,timeout=60); b=r.read(); print(name,i,r.status,len(b),round(time.time()-t,2),"s")
        except Exception as e:
            print(name,i,"ERR",e,getattr(e,"read",lambda:b"")()[:200],round(time.time()-t,2),"s")
