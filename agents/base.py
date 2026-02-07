
import time
def enrich(d):
    d["processed_ts"]=int(time.time()*1000)
    return d
