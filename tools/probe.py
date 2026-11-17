import subprocess,time
u="https://api.open-meteo.com/v1/forecast?latitude=35.2&longitude=136&current=temperature_2m"
for name,args in [("v4",["-4"]),("v6",["-6"]),("auto",[])]:
    for i in range(3):
        t=time.time()
        r=subprocess.run(["curl","-sS","-m","20","-o","/dev/null","-w","%{http_code} %{time_connect} %{time_appconnect} %{time_total}"]+args+[u],capture_output=True,text=True)
        print(name,i,r.stdout,r.stderr.strip()[:80],round(time.time()-t,1))
