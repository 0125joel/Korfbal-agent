import streamlit as st, pandas as pd, random, time
from pathlib import Path
from agent.tools import load_events, save_events, save_summary, seconds_to_ts
from pipeline.summarize import summarize
from agent.agent import answer
st.set_page_config(page_title='Korfbal Agent', layout='wide')
st.title('Korfbal Analyse Agent — Starter (Demo)')
with st.sidebar:
    uploaded = st.file_uploader('Upload MP4 (demo)', type=['mp4','mov','mkv'])
    if st.button('Analyse (mock)'):
        rows=[]; t=0.0
        for _ in range(40):
            rows.append({'t':seconds_to_ts(t),'ts':t,'event':random.choice(['shot','goal','rebound']),'team':random.choice(['Thuis','Uit']),'player':random.choice([5,7,12,23]),'defended':random.choice([True,False]),'half':1 if t<300 else 2,'x':random.random(),'y':random.random(),'conf':round(random.uniform(0.6,0.98),2)})
            t += random.uniform(6,18)
        df=pd.DataFrame(rows); save_events(df); save_summary(summarize(df)); st.success('Mock gereed')
ev=load_events()
st.subheader('Events (laatste 20)')
if not ev.empty:
    st.dataframe(ev.tail(20), use_container_width=True, height=300)
q = st.text_input('Q&A: vraag iets (demo)')
if st.button('Beantwoord'):
    resp = answer(q or '')
    st.write(resp.get('text',''))
    items = resp.get('items',[])
    if items:
        st.dataframe(pd.DataFrame(items), use_container_width=True, height=300)
