import os, json, pandas as pd
OUTPUT_DIR = 'outputs'
EVENTS_PATH = os.path.join(OUTPUT_DIR, 'events.jsonl')
SUMMARY_PATH = os.path.join(OUTPUT_DIR, 'summary.json')
def load_events():
    rows=[]
    if os.path.exists(EVENTS_PATH):
        with open(EVENTS_PATH,'r',encoding='utf-8') as f:
            for line in f:
                try: rows.append(json.loads(line))
                except: pass
    import pandas as pd
    return pd.DataFrame(rows)
def save_events(df):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(EVENTS_PATH,'w',encoding='utf-8') as f:
        for _,r in df.iterrows():
            f.write(json.dumps(r.to_dict(), ensure_ascii=False)+'\n')
def save_summary(s):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(SUMMARY_PATH,'w',encoding='utf-8') as f:
        json.dump(s,f,ensure_ascii=False,indent=2)
def seconds_to_ts(s):
    m,sec=divmod(int(s),60)
    h,m=divmod(m,60)
    ms=int((s-int(s))*1000)
    return f"{h:02d}:{m:02d}:{sec:02d}.{ms:03d}"
