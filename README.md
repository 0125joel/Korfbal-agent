# Korfbal Analyse Agent — Starter

Een demoproject dat de volledige pipeline voor een korfbal analyse-agent laat
zien. Het project bevat een Streamlit UI, een simpele agentlaag en een aantal
placeholder-pijplijnen (ingest, detectie, OCR en event-afleiding) die klaar
staan om met echte modellen te worden gevuld.

## Projectstructuur

```
korfbal-agent/
├─ app.py                # Streamlit UI
├─ agent/
│  ├─ agent.py           # Agent die FAISS/fallback index gebruikt
│  ├─ tools.py           # Datahelpers + shotmap visualisaties
│  └─ indexer.py         # FAISS-index wrapper
├─ pipeline/
│  ├─ live_ingest.py     # Streamlink ingest placeholder
│  ├─ detect_track.py    # YOLOv8 + ByteTrack mock
│  ├─ jersey_ocr.py      # EasyOCR mock
│  ├─ events.py          # Heuristische eventafleiding
│  └─ summarize.py       # Samenvatting & statistieken
├─ data/
│  ├─ roster.json        # Voorbeeld opstelling
│  └─ competition.json   # Voorbeeldprogramma
├─ outputs/
│  ├─ events.jsonl       # Laatste eventdump
│  └─ summary.json       # Laatste samenvatting
├─ requirements.txt
└─ README.md
```

## Snelstart

1. Installeer de afhankelijkheden: `pip install -r requirements.txt`.
2. Start de Streamlit-app: `streamlit run app.py`.
3. Gebruik de sidebar om een (mock) analyse te starten en stel vragen via de
   Q&A-sectie.

De placeholders in `pipeline/` vormen het haakje voor een echte
computer-vision/LLM-pipeline. Vervang de mocklogica stapsgewijs met echte
modellen, maar behoud de API-contracten zodat de UI en agentlaag blijven
werken.
