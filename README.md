# 🏐 Korfbal Video Analyse Agent — Project Plan

## 1️⃣ Doel & Context
Een open-source AI-agent voor **korfbalanalyse** die:
- wedstrijdvideo’s (of YouTube-livestreams) automatisch verwerkt;
- schoten, doelpunten, rebounds en rolwissels herkent;
- halftime- en eindstatistieken toont;
- via een chatinterface vragen over spelers, teams of events kan beantwoorden;
- gratis te publiceren is via **GitHub + Streamlit Cloud**.

Dit project is ontworpen voor amateurverenigingen die **zonder dure hardware** toch inzicht willen krijgen in spelpatronen, effectiviteit en teamdynamiek.

---

## 2️⃣ Architectuur in vogelvlucht

```bash
korfbal-agent/
├─ app.py                → Streamlit UI (upload/live + analyse + Q&A)
├─ agent/
│  ├─ agent.py           → LangChain-agent of regelgebaseerde fallback
│  ├─ tools.py           → Helpers: laden/opslaan, filteren, plotten
│  └─ indexer.py         → FAISS-index / embeddings (voor Q&A)
├─ pipeline/
│  ├─ live_ingest.py     → YouTube HLS-ingest via Streamlink
│  ├─ detect_track.py    → YOLOv8 + ByteTrack (detectie + tracking)
│  ├─ jersey_ocr.py      → EasyOCR/Tesseract (rugnummerherkenning)
│  ├─ events.py          → Heuristieken: shot, goal, rebound, rolwissel
│  └─ summarize.py       → Statistieken + halftime / fulltime summary
├─ data/
│  ├─ roster.json        → Spelerslijst met rugnummers
│  └─ competition.json   → Competitieprofiel (zaal/veld, shotklok, enz.)
├─ outputs/
│  ├─ events.jsonl       → Log van alle events
│  └─ summary.json       → Samenvatting (shots/goals/rebounds)
├─ requirements.txt
├─ README.md
└─ PROJECT_PLAN.md
```

---

## 3️⃣ Roadmap per fase

| Fase | Doel | Deliverables | Tools |
|------|------|--------------|-------|
| **v0.1 (Mock Demo)** | Proof-of-concept, publiceerbaar op Streamlit | Mock-analyse + Q&A + shotmap | Streamlit, Pandas, Plotly |
| **v0.2 (Live ingest)** | YouTube Live HLS binnenhalen + halftime refresh | `pipeline/live_ingest.py` + auto-summary | Streamlink, yt-dlp |
| **v0.3 (Detectie + Tracking)** | Echte herkenning van spelers, paal, bal | YOLOv8 + ByteTrack integratie | Ultralytics, OpenCV |
| **v0.4 (Rugnummer-OCR)** | Nummerherkenning + spelerkoppeling | OCR-module + mapping naar roster | EasyOCR/Tesseract |
| **v0.5 (Agent-laag)** | Chat-Q&A met FAISS-vectorzoeker | LangChain-agent + tools + embeddings | LangChain, FAISS |
| **v1.0 (Release)** | Volledige coach-versie met rapportages | Real-time stats + privacy + export | Streamlit Cloud deploy |
| **v1.1+** | Optimalisaties (ONNX, blur, training) | CPU-versnelling + AVG-compliance | ONNX Runtime, OpenVINO |

---

## 4️⃣ Kernfunctionaliteit

### 🎥 Videoanalyse
- Ingest via upload of YouTube Live URL  
- Detectie van bal, spelers, paal/korf  
- Tracking met consistente ID’s  
- Rugnummer-OCR → koppeling met `data/roster.json`  
- Eventdetectie:  
  - `shot`, `goal`, `rebound`, `turnover`, `role_switch`, `defended`  
- Output als JSONL (`events.jsonl`) + samenvatting (`summary.json`)

### 💬 Q&A-Agent
- Systemprompt:  
  > Jij bent een AI-analist voor korfbal. Gebruik events.jsonl en summary.json als bron van waarheid.  
  > Antwoord kort, met tijdcodes en relevante details.
- Tools:
  - `search_events(filters)`
  - `plot_shotmap(period)`
  - `get_clip(timestamp)`
- Optioneel FAISS-index voor semantische vragen.

### 📊 Visuals
- Shotmap (veld 0–1 coördinaten)  
- Timeline per eventtype  
- Statistische samenvatting per helft/vak/speler  
- Downloadbare rapporten (MD of PDF)

---

## 5️⃣ Belangrijke bestanden & taken

| Bestand | Verantwoordelijkheid | Status |
|----------|----------------------|--------|
| `app.py` | Streamlit-UI bouwen + tabs voor upload/live/Q&A | ✅ aanwezig |
| `agent/agent.py` | Chatlogica & LangChain-integratie | ⏳ basisversie |
| `pipeline/live_ingest.py` | Streamlink HLS buffer + framequeue | 🔜 bouwen |
| `pipeline/detect_track.py` | YOLOv8 + ByteTrack implementeren | 🔜 bouwen |
| `pipeline/jersey_ocr.py` | Nummerherkenning & mapping | 🔜 bouwen |
| `pipeline/events.py` | Heuristieken (shot, goal, rebound) | 🔜 bouwen |
| `pipeline/summarize.py` | Statistiek-samenvatting | ✅ basisversie |
| `data/roster.json` | Spelers + nummers + geslacht | ✅ voorbeeld |
| `outputs/events.jsonl` | Brondataset voor Q&A/visuals | 🔜 gegenereerd |
| `PROJECT_PLAN.md` | Roadmap en taken | ✅ dit bestand |

---

## 6️⃣ Technische richtlijnen

### 🔧 Performance
- Gebruik **ONNX Runtime** of **OpenVINO** voor CPU-optimalisatie.  
- Vermijd zware frames >1080p bij ingest (downscale via FFmpeg).  

### 🔐 Privacy / AVG
- Anonimiseer of blur gezichten van minderjarigen.  
- Verwijder ruwe video’s na X dagen, behoud alleen statistische samenvattingen.  

### 🧱 Dataformaat
```json
{
  "t": "00:12:04.110",
  "ts": 724.11,
  "event": "goal",
  "team": "Thuis",
  "player": 23,
  "defended": false,
  "half": 1,
  "x": 0.62,
  "y": 0.38,
  "conf": 0.93
}
```

---

## 7️⃣ Samenwerking & ontwikkeling

**Aanbevolen workflow:**
1. **ChatGPT / Codex** → ontwerp & skeleton code.  
2. **Cursor** → implementeer en refactor modules met context-AI.  
3. **GitHub** → versiebeheer & publicatie.  
4. **Streamlit Community Cloud** → gratis hosting voor coaches.

---

## 8️⃣ MVP-Succescriteria
- <60 sec analyse op 10 min video (mock).  
- Correcte halftime-statistieken (FG%, rebounds, rolwissel).  
- Q&A-agent beantwoordt >80% van eenvoudige queries.  
- Coach kan zonder technische kennis via webapp bedienen.  

---

## 9️⃣ Volgende actiepunten

1. ✅ **Push de mock-starter-repo** naar GitHub.  
2. 🚀 **Deploy op Streamlit Cloud** (test met coach).  
3. 🧠 **Open repo in Cursor** → begin met `pipeline/detect_track.py`.  
4. 🔄 Voeg **live_ingest.py** toe voor YouTube-streams.  
5. 💬 Breid `agent.py` uit met FAISS + LangChain.  
6. 📈 Valideer op echte wedstrijdbeelden.  

---

## 10️⃣ Credits & Inspiratie
Ontwikkeld door **Joël Prins** (Microsoft 365 Consultant & sportliefhebber).  
Geïnspireerd door community-projecten in open-source sportanalyse, zoals Ultralytics-YOLO, DeepSORT, Streamlink en LangChain.

---

**💡 Richting:**  
> “Slimme, toegankelijke analyse-tools die de amateur-sport sterker maken met open AI.”
