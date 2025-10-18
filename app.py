import random

import pandas as pd
import streamlit as st

from agent.agent import answer
from agent.tools import (
    load_events,
    load_summary,
    plot_shotmap,
    save_events,
    save_summary,
    seconds_to_ts,
)
from pipeline.summarize import summarize

st.set_page_config(page_title='Korfbal Agent', layout='wide')
st.title('Korfbal Analyse Agent — Starter (Demo)')

with st.sidebar:
    uploaded = st.file_uploader('Upload MP4 (demo)', type=['mp4', 'mov', 'mkv'])
    if st.button('Analyse (mock)'):
        rows = []
        timestamp = 0.0
        for _ in range(40):
            rows.append(
                {
                    't': seconds_to_ts(timestamp),
                    'ts': timestamp,
                    'event': random.choice(['shot', 'goal', 'rebound']),
                    'team': random.choice(['Thuis', 'Uit']),
                    'player': random.choice([5, 7, 12, 23]),
                    'defended': random.choice([True, False]),
                    'half': 1 if timestamp < 600 else 2,
                    'x': random.uniform(0.2, 0.8),
                    'y': random.uniform(0.1, 0.9),
                    'confidence': round(random.uniform(0.6, 0.98), 2),
                }
            )
            timestamp += random.uniform(6, 18)
        df = pd.DataFrame(rows)
        save_events(df)
        save_summary(summarize(df))
        st.success('Mock gereed')

events = load_events()
summary = load_summary({})

if summary:
    st.subheader('Samenvatting')
    if headline := summary.get('headline'):
        st.write(headline)
    metrics = summary.get('metrics', {})
    if metrics:
        cols = st.columns(len(metrics))
        for col, (label, value) in zip(cols, metrics.items()):
            col.metric(label, value)

st.subheader('Events (laatste 20)')
if not events.empty:
    st.dataframe(events.tail(20), use_container_width=True, height=300)
    st.plotly_chart(plot_shotmap(events), use_container_width=True)

q = st.text_input('Q&A: vraag iets (demo)')
if st.button('Beantwoord'):
    resp = answer(q or '')
    st.write(resp.get('text', ''))
    items = resp.get('items', [])
    if items:
        st.dataframe(pd.DataFrame(items), use_container_width=True, height=300)
