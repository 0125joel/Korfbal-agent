import random
from pathlib import Path

import pandas as pd
import streamlit as st

from agent.agent import answer
from agent.tools import load_events, plot_shotmap, save_events, save_summary, seconds_to_ts
from pipeline.live_ingest import LiveIngestError, LiveIngestor, probe_youtube_stream
from pipeline.summarize import summarize

st.set_page_config(page_title="Korfbal Agent", layout="wide")
st.title("Korfbal Analyse Agent — Live ingest (fase 0.2)")


def _generate_mock_events(num_events: int = 60) -> pd.DataFrame:
    rows = []
    timestamp = 0.0
    half_switch = max(1, num_events // 2)
    for idx in range(num_events):
        if idx == half_switch:
            timestamp = 900.0  # start tweede helft bij 15 minuten
        rows.append(
            {
                "t": seconds_to_ts(timestamp),
                "ts": timestamp,
                "event": random.choice(["shot", "goal", "rebound"]),
                "team": random.choice(["Thuis", "Uit"]),
                "player": random.choice([5, 7, 12, 23]),
                "defended": random.choice([True, False]),
                "half": 1 if idx < half_switch else 2,
                "x": random.uniform(0.2, 0.8),
                "y": random.uniform(0.1, 0.9),
                "confidence": round(random.uniform(0.6, 0.98), 2),
            }
        )
        timestamp += random.uniform(6, 18)
    return pd.DataFrame(rows)


def _render_summary_block(summary: dict) -> None:
    st.subheader("Samenvatting")
    status_labels = {"in_progress": "Live", "halftime": "Rust", "fulltime": "Eindtijd", "idle": "Nog niet gestart"}
    status = summary.get("status")
    if status:
        st.caption(f"Status: {status_labels.get(status, status)}")
    if headline := summary.get("headline"):
        st.write(headline)

    metrics = summary.get("metrics", {})
    if metrics:
        cols = st.columns(len(metrics))
        for col, (label, value) in zip(cols, metrics.items()):
            col.metric(label, value)

    halves = summary.get("halves")
    if halves:
        st.markdown("**Per helft**")
        half_df = pd.DataFrame.from_dict(halves, orient="index").rename_axis("Helft")
        st.table(half_df)

    if top := summary.get("top_scorer"):
        st.info(f"Topscorer (mock): speler {top}")


if "live_ingestor" not in st.session_state:
    st.session_state["live_ingestor"] = None
if "live_metadata" not in st.session_state:
    st.session_state["live_metadata"] = None


mock_tab, live_tab = st.tabs(["Mock analyse", "Live ingest"])

with mock_tab:
    st.write("Genereer demo-events zodat de Q&A en samenvatting gevuld worden.")
    uploaded = st.file_uploader("Upload MP4 (optioneel, demo)", type=["mp4", "mov", "mkv"], key="mock_upload")
    if st.button("Analyseer mock", key="mock_button"):
        df = _generate_mock_events()
        save_events(df)
        summary = summarize(df)
        save_summary(summary)
        st.success("Mock events gegenereerd. Samenvatting is bijgewerkt tot rust/eindtijd.")
        if uploaded:
            st.caption(f"Bestand \"{uploaded.name}\" gebruikt als referentie (niet opgeslagen).")

with live_tab:
    st.write("Start een Streamlink ingest van een YouTube-live URL. De output wordt lokaal opgeslagen.")
    url = st.text_input("YouTube live URL", key="live_url")
    col1, col2, col3 = st.columns(3)
    output_dir = Path(col1.text_input("Outputmap", value="data/live", key="live_output"))
    filename = col2.text_input("Bestandsnaam", value="korfbal_live.mp4", key="live_filename")
    duration_minutes = col3.number_input("Max. duur (min, optioneel)", min_value=0, value=5, key="live_duration")

    if st.button("Start live ingest", key="start_live"):
        if not url:
            st.warning("Voer eerst een geldige YouTube-URL in.")
        else:
            ingestor = LiveIngestor(
                youtube_url=url,
                output_dir=output_dir,
                filename=filename or None,
                duration=int(duration_minutes * 60) if duration_minutes else None,
            )
            try:
                output_path = ingestor.start()
            except LiveIngestError as exc:
                st.error(str(exc))
            else:
                st.session_state["live_ingestor"] = ingestor
                try:
                    st.session_state["live_metadata"] = probe_youtube_stream(url)
                except Exception as meta_exc:  # pragma: no cover - UI feedback only
                    st.session_state["live_metadata"] = None
                    st.warning(f"Kon streammetadata niet ophalen: {meta_exc}")
                st.success(f"Live ingest gestart. Output: {output_path}")

    ingestor: LiveIngestor | None = st.session_state.get("live_ingestor")
    if ingestor:
        meta = st.session_state.get("live_metadata")
        if meta:
            live_note = "Live" if meta.get("is_live") else "Onbekende status"
            st.caption(f"Stream: {meta.get('title', 'Onbekend')} — {live_note}")

        st.write(f"Processtatus: {'actief' if ingestor.is_running() else 'gestopt'}")
        st.write(f"Opslagbestand: {ingestor.output_path}")
        logs = ingestor.read_logs()
        if logs:
            st.code("\n".join(logs), language="text")

        if ingestor.is_running() and st.button("Stop ingest", key="stop_live"):
            ingestor.stop()
            st.success("Streamlink proces gestopt.")


events = load_events()
summary = summarize(events)
save_summary(summary)

_render_summary_block(summary)

st.subheader("Events (laatste 20)")
if not events.empty:
    st.dataframe(events.tail(20), use_container_width=True, height=300)
    st.plotly_chart(plot_shotmap(events), use_container_width=True)
else:
    st.info("Nog geen events opgeslagen. Start een analyse of ingest.")

q = st.text_input("Q&A: stel een vraag over de mock events")
if st.button("Beantwoord", key="qa_button"):
    resp = answer(q or "")
    st.write(resp.get("text", ""))
    items = resp.get("items", [])
    if items:
        st.dataframe(pd.DataFrame(items), use_container_width=True, height=300)
