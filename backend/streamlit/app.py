import streamlit as st
from PIL import Image, ImageDraw
import os, random

st.set_page_config(page_title="Korfbal Analytics", layout="wide")
st.title("Korfbal Analytics — Demo Dashboard")

# In-memory event data (reset bij reload)
if "events" not in st.session_state:
    st.session_state["events"] = []

col1, col2 = st.columns(2)
with col1:
    if st.button("Genereer demo-events"):
        # willekeurige mix van events en posities
        for _ in range(20):
            st.session_state["events"].append({
                "event_type": random.choice(["shot", "goal", "rebound", "assist"]),
                "player_id": f"tracker-{random.randint(1,10)}",
                "x": random.random(),   # genormaliseerd 0..1
                "y": random.random()
            })
    if st.button("Reset data"):
        st.session_state["events"].clear()
with col2:
    st.write(f"**Aantal events:** {len(st.session_state['events'])}")

tab1, tab2 = st.tabs(["📊 Statistieken", "🔥 Heatmap"])

with tab1:
    stats = {}
    for e in st.session_state["events"]:
        pid = e["player_id"]
        stats.setdefault(pid, {"shots":0,"goals":0,"rebounds":0,"assists":0})
        if e["event_type"] == "assist":
            stats[pid]["assists"] += 1
        elif e["event_type"] == "rebound":
            stats[pid]["rebounds"] += 1
        elif e["event_type"] == "goal":
            stats[pid]["goals"] += 1
        elif e["event_type"] == "shot":
            stats[pid]["shots"] += 1
    rows = [{"speler":k, **v} for k,v in stats.items()]
    st.dataframe(rows, use_container_width=True)

with tab2:
    # Laad veld-achtergrond
    img_path = os.path.join(os.path.dirname(__file__), "court.png")
    if not os.path.exists(img_path):
        st.warning("⚠️ Voeg 'streamlit/court.png' toe (veldafbeelding).")
    else:
        bg = Image.open(img_path).convert("RGBA")
        draw = ImageDraw.Draw(bg)
        w, h = bg.size
        # Plot shots/goals als puntjes (rood=shot, zwart=goal)
        for e in st.session_state["events"]:
            if e["event_type"] in ("shot", "goal"):
                x, y = int(e["x"] * w), int(e["y"] * h)
                r = 6
                color = (0,0,0,180) if e["event_type"]=="goal" else (255,0,0,180)
                draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=color)
        st.image(bg, use_container_width=True)

st.caption("Standalone demo — later te koppelen aan FastAPI via HTTP.")
