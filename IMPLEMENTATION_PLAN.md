# Korfbal Video Analytics Agent - Plan van Aanpak

## Projectomschrijving

Een AI-systeem ontwikkelen dat automatisch korfbalstatistieken genereert op basis van **offline video-materiaal** (later evt. livestreams). Het doel is **95-100% nauwkeurigheid**, waarbij gebruik wordt gemaakt van **4K/60fps opnames** en een **Human-in-the-loop** workflow voor verificatie. Het systeem moet spelers identificeren via rugnummers, acties detecteren (schoten, assists, rebounds), en korfbal-specifieke regels toepassen.

---

## Korfbal-Specifieke Context

### Zaalafmetingen & Speelveld
- **Standaard veld**: 40m x 20m, verdeeld in 2 vakken door middenlijn
- **Korfhoogte**: 3,5m voor volwassenen
- **Korfpositie**: 6,67m vanaf achterlijn (1/6 van veldlengte)
- **Minimale plafondhoogte**: 7-9 meter

### Belangrijke Spelregels
1. **Vakwisseling**: Teams wisselen van vak na elke 2 doelpunten (gecombineerd)
2. **Halftime**: Na rust wisselen teams van korf (maar niet van functie)
3. **Verdedigd schieten**: Niet toegestaan wanneer verdediger tussen aanvaller en korf staat, binnen armlengte, hand omhoog
4. **Gemengd spel**: Jongens verdedigen jongens, meisjes verdedigen meisjes
5. **Geen contact**: Korfbal is geen contactsport

### Belangrijke Statistieken
**Primaire metrics**:
- Doelpunten (per speler)
- Schoten (totaal + rendement %)
- Assists (pass voor doelpunt)
- Rebounds (aanvallend + verdedigend)
- Strafworpen (genomen + benut)
- Vrije ballen
- Doorloopballen

**Secundaire metrics**:
- Schotposities (afstand tot korf)
- Balverlies
- Overtredingen
- Speeltijd per speler
- **Wissels** (wie in, wie uit, tijdstip)
- Rendement per vak (aanval/verdediging)

---

## Technische Mogelijkheden

### Computer Vision Technologieën

#### 1. Object Detection - YOLO (You Only Look Once)
**Mogelijkheden**:
- Real-time detectie van spelers, bal, korf, scheidsrechter
- YOLOv8/YOLOv9/YOLO11 bieden state-of-the-art performance
- 30-60 FPS processing mogelijk op moderne hardware
- Pre-trained modellen beschikbaar voor personen en sportballen

**Voor korfbal**:
- Detectie van alle 8 spelers (4 per team)
- Bal tracking door het hele veld
- Korf detectie voor schotanalyse

#### 2. Player Tracking & Re-identification
**Mogelijkheden**:
- ByteTrack algoritme voor multi-object tracking
- Persistente ID's door video heen
- Tracking door occlusions (spelers die elkaar blokkeren)

**Uitdagingen**:
- Spelers die elkaar kruisen/blokkeren
- Camera-angle wijzigingen
- Snelle bewegingen kunnen blur veroorzaken

#### 3. Jersey Number Recognition (OCR)
**Mogelijkheden**:
- Deep learning modellen (R-CNN) voor digit localisatie
- OCR met SmolVLM2 of vergelijkbare modellen
- Pose-guided regressors voor betere accuracy

**Kritieke uitdagingen** ⚠️:
- **Lage resolutie**: Bij wide-angle shots zijn nummers klein (5-20 pixels)
- **Pose variaties**: Spelers draaien, bukken, springen
- **Occlusions**: Nummers gedeeltelijk bedekt door andere spelers
- **Motion blur**: Bij snelle bewegingen
- **Belichting**: Schaduw, reflecties op shirts

**Oplossing voor 95-100% Accuracy**:
1. **High-Res Video (4K)**: Zorgt voor meer pixels per rugnummer.
2. **2-Pass OCR**: Eerst speler detecteren, dan een High-Res Crop maken voor OCR.
3. **Temporal Voting**: Combineer resultaten van 30 frames (1 seconde) voor consensus.
4. **Human Verification**: Bij twijfel (<99% confidence) vraagt het systeem om menselijke bevestiging.

#### 4. Pose Estimation
**Mogelijkheden**:
- YOLOv8-pose voor skelet tracking (17+ keypoints)
- Detectie van schietbewegingen
- Onderscheid tussen aanval/verdediging houding

**Toepassingen**:
- Schot detectie (armen omhoog, bal boven hoofd)
- Verdedigd-schieten detectie (verdediger positie + arm omhoog)
- Rebound detectie (springen naar bal)

#### 5. Action Recognition
**Mogelijkheden**:
- Temporal Convolutional Networks voor actie classificatie
- Detectie van: schot, pass, rebound, doorloopbal

#### 6. GenAI Video Reasoning (Google AI Studio / Gemini)
**Mogelijkheden**:
- **Context**: 1M+ token context window in Gemini 1.5 Pro (tot 2u video)
- **Understanding**: Kan "begrijpen" wat er gebeurt (b.v. "Waarom fluit de scheids?")
- **Function Calling**: Kan user vragen omzetten naar SQL queries
- **Structured Output**: Kan JSON extracten uit video clips (b.v. scoreboard lezen)

---

## Technische Architectuur

### Fase 1: Video Input & Preprocessing
```
Input: YouTube livestream / MP4 video
↓
Split into 2 streams:
1. High-res frames (CV Pipeline) -> 30 FPS
2. Low-res / Clips (GenAI Pipeline) -> Events / On-demand
```

### Fase 2: Hybrid AI Pipeline
```
[Stream A: Hard Stats - YOLO/ByteTrack]
- Speler Locaties (X,Y)
- Bal Trajectory
- Heatmap data
↓
[Stats Database (SQL)]

[Stream B: Soft Stats - Gemini 1.5 Pro]
- "High level" analysis (Video Clips)
- Scoreboard reading (OCR backup)
- Event validation (e.g. "Is dit een goal?")
```

### Fase 3: Analyst Layer (MCP / Agent)
```
User Interface (Chat)
↓
Gemini 1.5 Flash (Router)
├─> Vraag over stats? -> Function Call -> SQL Query -> Stats DB
└─> Vraag over video? -> RAG / Video query -> Gemini 1.5 Pro
```

### Fase 4: Event Detection & Game State
```
Game State Tracker
├─ Score (Team A vs Team B)
├─ Huidige vak per speler (4 aanval, 4 verdediging)
├─ Vakwisseling trigger (elke 2 doelpunten)
├─ Halftime detectie
└─ Speeltijd per speler
```

### Fase 4: Event Detection
```
Event Detector
├─ Schot detectie
│   ├─ Pose: armen omhoog + bal bij handen
│   ├─ Bal trajectory naar korf
│   └─ Verdedigd? (verdediger positie check)
├─ Doelpunt detectie
│   ├─ Bal door korf (computer vision)
│   └─ Score update + vakwisseling trigger
├─ Assist detectie
│   ├─ Laatste pass voor schot (<3 sec)
│   └─ Pass gever ID
├─ Rebound detectie
│   ├─ Gemist schot
│   └─ Speler die bal vangt
└─ Overtreding detectie (beperkt)
```

### Fase 5: Statistics Aggregation
```
Stats Database
├─ Per speler
│   ├─ Doelpunten
│   ├─ Schoten (totaal, raak, mis, %)
│   ├─ Assists
│   ├─ Rebounds
│   ├─ Schotposities (heatmap)
│   └─ Speeltijd
└─ Per team
    ├─ Totale score
    ├─ Rendement per vak
    └─ Balverlies
```

### Fase 6: Output & Visualization
```
Output Formats
├─ Real-time dashboard (web interface)
├─ Post-game rapport (PDF/HTML)
├─ CSV export voor verdere analyse
└─ Video overlay met stats
```

---

## MVP (Minimum Viable Product) Scope

### ✅ Wat WEL haalbaar is voor MVP

1. **Speler detectie en tracking**
   - 8 spelers detecteren en volgen
   - Bounding boxes met tracking IDs

2. **Bal tracking**
   - Bal positie door video heen
   - Bal bezit per speler (proximity based)

3. **Basis schot detectie**
   - Detectie wanneer speler schiet (pose + bal beweging)
   - Onderscheid raak/mis (bal door korf)

4. **Score tracking**
   - Automatische score bijhouden
   - Vakwisseling trigger na 2 doelpunten

5. **Basis statistieken**
   - Doelpunten per speler (met manuele jersey input)
   - Totaal schoten per team
   - Schot rendement

6. **High-Accuracy Offline Workflow**
   - Upload 4K video (nachtelijke verwerking)
   - 2-Pass OCR op hoge resolutie
   - **Verplichte Verificatie Stap**: Gebruiker checkt twijfelgevallen in UI
   - Output: 100% kloppende stats

7. **"Analyst" Chat Interface (Gemini)**
   - Vragen stellen aan data: "Wie heeft de meeste goals?"
   - High-level samenvatting van wedstrijd
   - "Coach Assistant" functionaliteit

### ⚠️ Uitdagend maar mogelijk (met extra werk)

8. **Smart Player Identification (Hybrid)**
   - **Start**: Manuele input ("Klik op speler -> Dit is Nr 4")
   - **Tijdens wedstrijd**: AI gebruikt "Visual Re-Identification" (uiterlijk, schoenen, haar) om Nr 4 te blijven volgen.
   - **OCR Backup**: AI checkt af en toe het rugnummer ter verificatie.
   - **Wissels**: AI detecteert "Unknown Player" (nieuw gezicht). UI vraagt: "Nieuwe speler gedetecteerd - Wie is dit?" -> Gebruiker selecteert uit wisselbank.
   - **Herstel**: Als tracking breekt, vraagt AI: "Is dit weer Nr 4?"

9. **Assist tracking**
   - Laatste pass voor doelpunt
   - Vereist nauwkeurige bal trajectory + pass detectie

10. **Rebound detectie**
   - Gemist schot + speler die bal vangt
   - Onderscheid aanvallend/verdedigend

### ❌ Niet haalbaar / Zeer moeilijk

11. **Verdedigd-schieten detectie**
    - Vereist zeer nauwkeurige 3D positie bepaling
    - "Binnen armlengte" is subjectief
    - Zelfs scheidsrechters zijn het hier niet over eens

12. **Gemengd verdedigen overtredingen**
    - Vereist gender classificatie (privacy concerns)
    - Zeer context-afhankelijk

13. **Overtreding detectie**
    - Lopen met bal, contact, voetbal: te complex
    - Vereist zeer gedetailleerde bewegingsanalyse

14. **Automatische rugnummer herkenning (betrouwbaar)**
    - Te veel variabelen (camera angle, resolutie, occlusion)
    - Niet betrouwbaar genoeg zonder manuele verificatie

---

## Kritieke Beperkingen

### 📹 Video Kwaliteit Vereisten

> [!IMPORTANT]
> Het systeem is **sterk afhankelijk** van video kwaliteit

**Minimale vereisten voor 95-100% Accuracy**:
- **Resolutie**: **4K (3840x2160)** verplicht voor betrouwbare OCR
- **Frame rate**: **60 FPS** om motion blur te verminderen
- **Camera positie**: Elevated side view + evt. 2e camera achter korf
- **Belichting**: Uitstekende verlichting, geen tegenlicht
- **Stabiliteit**: Statief verplicht

**Problematische scenario's**:
- 720p of lager: Jersey nummers onleesbaar
- Wide-angle shots: Spelers te klein voor pose detection
- Bewegende camera: Tracking wordt instabiel
- Slechte belichting: Detectie accuracy daalt 20-40%
- Multiple camera angles: Vereist camera switching logic

### 🎯 Accuracy Verwachtingen

**Accuracy targets met Human-in-the-Loop**:
- Speler detectie: 99% (AI) -> 100% (Human verify)
- Jersey number recognition: 85% (4K Video) -> 100% (Human verify)
- Schot detectie: 95% (AI) -> 100% (Human verify)
- Doelpunt detectie: 98% (AI) -> 100% (Human verify)

**Accuracy targets met Smart Linking**:
- Speler Identificatie: 100% (door combinatie van Manueel Starten + AI Re-ID + OCR Check)
- Jersey number recognition: Ingebouwd als *hulpmiddel*, niet als enige bron.

> [!TIP]
> **Oplossing voor User Zorg**: We vertrouwen niet blind op OCR. We gebruiken "Manual Linking" aan het begin. De AI hoeft daarna alleen de *persoon* te volgen (op basis van uiterlijk), en checkt het nummer alleen als extra bevestiging.

### 🔧 Technische Beperkingen

1. **Processing tijd**
   - Real-time (livestream): Vereist GPU (RTX 3060 of beter)
   - Offline processing: 2-5x video lengte op CPU
   - Cloud processing: Kosten €0.10-0.50 per wedstrijd

2. **Training data vereisten**
   - Custom korfbal dataset nodig (500-1000 gelabelde frames)
   - Jersey number training: 2000-5000 voorbeelden
   - Tijd: 2-4 weken data labeling + training

3. **Edge cases**
   - Occlusions: Spelers die elkaar blokkeren
   - Snelle bewegingen: Motion blur
   - Bal uit beeld: Tracking verlies
   - Wisselingen: Nieuwe spelers detecteren

### 🏀 Korfbal-Specifieke Uitdagingen

1. **Vakwisseling complexiteit**
   - Automatische detectie van 2-doelpunten trigger: Haalbaar
   - Spelers correct toewijzen aan nieuw vak: Vereist positie tracking
   - Halftime detectie: Vereist game clock of manuele input

2. **Gemengd spel**
   - Gender classificatie: Ethisch + privacy gevoelig
   - Alternatief: Manuele input bij setup

3. **Verdedigd schieten**
   - 3D positie bepaling zeer complex
   - "Binnen armlengte" is subjectief
   - Niet betrouwbaar te automatiseren

---

### ⚽ Waarom we de "Harde Laag" (YOLO) NIET kunnen skippen
De gebruiker vroeg of we de computer vision laag kunnen weglaten om kosten te besparen.
**Antwoord: Nee, dat kan helaas niet.**

**Reden:**
1.  **Tracking Consistentie**: Gemini "kijkt" als een mens en kan zeggen "Ik zie een speler". Maar Gemini kan niet **60 minuten lang** onthouden dat "dat poppetje links" de "Pietje Puk met ID 432" is. Voor statistieken ("Piet scoorde 5x") is die *continuïteit* essentieel.
2.  **Precisie**: Voor een shotmap (X,Y coördinaten) heb je pixel-perfecte locaties nodig. LLM's zijn daar (nog) te grofmazig voor ("Speler staat ongeveer links voor").
3.  **Kosten bij schaal**: Een video van 1 uur frame-voor-frame aan Gemini voeren voor *positie* data zou miljoenen tokens kosten (= duur). YOLO doet dit lokaal "gratis".

### 💰 Kosten Optimalisatie Strategie
Om de kosten toch te drukken:
1.  **Draai "Harde Laag" Lokaal**: YOLO vereist een GPU, maar een moderne gaming PC thuis is prima. Dit bespaart €0.50-€1.00/uur aan cloud kosten.
2.  **Gebruik Gemini Flash**: Voor de "Slimme Laag" gebruiken we **Gemini 1.5 Flash** (i.p.v. Pro).
    - Kosten: ~$0.07 per uur video (zeer goedkoop!)
    - Prima geschikt voor "Wat is de score?" en "Was dit een goal?" vragen.
3.  **On-Demand Pro**: Gebruik de duurdere Gemini 1.5 Pro **alleen** voor complexe vragen van de coach achteraf ("Analyseer de tactiek"), niet voor de hele wedstrijd.

---

## Aanbevolen Aanpak


### Strategie: Hybrid Semi-Automated System

> [!TIP]
> **Beste resultaat**: Combineer AI met manuele input waar nodig

**Workflow**:
1. **Pre-game setup** (manueel, 2-3 min)
   - Upload video
   - Voer rugnummers in per team
   - Selecteer spelers in eerste frame
   - Link tracking IDs aan rugnummers

2. **Automated processing** (AI)
1.  **Pre-game setup** (manueel, 2-3 min)
    -   Upload video
    -   Voer rugnummers in per team
    -   Selecteer spelers in eerste frame
    -   Link tracking IDs aan rugnummers

2.  **Automated processing** (AI)
    -   Speler tracking
    -   Schot detectie
    -   Doelpunt detectie
    -   Score tracking + vakwisseling

3.  **Post-processing review (manueel, 5-10 min)**
    -   **Timeline Interface**: Gebruiker ziet een tijdlijn met: "Tracking lost player 4".
    -   **1-Click Fix**: Gebruiker klikt op de nieuwe "Unknown" speler en linkt weer aan "Nr 4".
    -   Verificeer doelpunten & assists.

4.  **Output**
    -   Gedetailleerde statistieken
    -   Video highlights
    -   Exporteerbare data

### Fasering

**Fase 1: Proof of Concept (4-6 weken)**
- Basis speler + bal detectie
- Schot detectie
- Manuele rugnummer input
- Simpele statistieken

**Fase 2: MVP (8-12 weken)**
- Verbeterde tracking
- Doelpunt detectie
- Vakwisseling logic
- Web interface
- CSV export

**Fase 3: Enhanced Features (12-16 weken)**
- Jersey number recognition (custom training)
- Assist tracking
- Rebound detectie
- Heatmaps
- Video overlay

**Fase 4: Production Ready (16-24 weken)**
- Livestream support
- Real-time dashboard
- Multi-camera support
- Cloud deployment
- API voor integraties

---

## Technology Stack Voorstel

### Core AI/ML
- **Object Detection**: YOLOv8 (Ultralytics)
- **Tracking**: ByteTrack
- **GenAI**: Google Gemini API (1.5 Flash & Pro)
- **GenAI Framework**: LangChain of Google Generative AI SDK
- **OCR**: PaddleOCR (Primary) / Gemini (Backup for Scoreboard)
- **Pose Estimation**: YOLOv8-pose
- **Framework**: PyTorch

### Backend
- **Language**: Python 3.10+
- **Video Processing**: OpenCV, FFmpeg
- **API**: FastAPI
- **Database**: PostgreSQL (stats) + Redis (caching)
- **Vector DB**: ChromaDB (optioneel voor RAG)
- **Task Queue**: Celery (voor async processing)

### Frontend
- **Framework**: React + TypeScript
- **Visualization**: D3.js, Chart.js
- **Video Player**: Video.js
- **UI**: Tailwind CSS

### Infrastructure
- **Development**: Docker + Docker Compose
- **GPU**: CUDA 11.8+ (NVIDIA)
- **Cloud**: AWS/GCP (S3 voor video storage)
- **Deployment**: Kubernetes (optioneel voor scale)

### Tools
- **Annotation**: CVAT of Label Studio (voor training data)
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

---

## Kosten Schatting (Geoptimaliseerd)

### Infrastructure (Per Wedstrijd)
- **Harde Laag (YOLO)**: €0.00 (Indien lokaal gedraaid op eigen PC)
- **Slimme Laag (Gemini Flash)**: ~€0.10 - €0.20 per wedstrijd (Video input tokens)
- **Storage**: ~€0.05 per wedstrijd
- **Totaal**: **< €0.50 per wedstrijd** (Excl. dev kosten)

### Development (eenmalig)
- **Developer tijd**: 400-600 uur @ €50-100/uur = **€20.000 - €60.000**

### Hardware (optioneel, eenmalig)
- **Development GPU**: RTX 4070/4080 = €600-1200
- **Production server**: €2000-5000

---

## Risico's & Mitigaties

| Risico | Impact | Waarschijnlijkheid | Mitigatie |
|--------|--------|-------------------|-----------|
| Jersey recognition te onbetrouwbaar | Hoog | Hoog | Hybrid approach: manuele input + AI verificatie |
| Video kwaliteit te laag | Hoog | Gemiddeld | Minimum kwaliteit eisen communiceren |
| Processing te traag voor livestream | Gemiddeld | Gemiddeld | Start met offline, optimaliseer later |
| Training data te weinig | Hoog | Gemiddeld | Partner met korfbal clubs voor video's |
| Vakwisseling logic te complex | Laag | Laag | Goed getest algoritme + manuele override |
| Budget overschrijding | Gemiddeld | Gemiddeld | Fasering + MVP first approach |

---

## Concurrentie Analyse

### Bestaande Korfbal Tools
- **AKXI.NL**: Manuele statistiek registratie, geen AI
- **AnalyzeTeam**: Semi-automatisch, vereist manuele tagging
- **Teampulse**: Manuele app-based registratie

### Vergelijkbare Sporten
- **Basketball**: Hudl, Catapult, Genius Sports (zeer geavanceerd)
- **Volleyball**: Pixellot, SportsVisio (AI-powered)

**Conclusie**: Er is **geen fully-automated korfbal video analytics tool**. Dit is een **unieke kans** maar ook een **technische uitdaging**.

---

## Aanbevelingen

### ✅ Ga door als:
1. Je toegang hebt tot **high-quality video materiaal** (1080p+, statische camera)
2. Je een **hybrid approach** accepteert (AI + manuele input)
3. Je **budget** hebt voor development (€20k-60k) of tijd voor DIY
4. Je **training data** kunt verzamelen (500+ wedstrijden)
5. Je **realistisch** bent over accuracy (70-85%, niet 100%)

### ⚠️ Overweeg alternatieven als:
1. Video kwaliteit is **inconsistent** (veel 720p of lager)
2. Je **100% automatisering** verwacht zonder manuele input
3. Budget is **zeer beperkt** (<€5k)
4. Je **snel resultaat** wilt (< 3 maanden)

### 🚀 Volgende Stappen

1. **Validatie** (1-2 weken)
   - Verzamel 5-10 representatieve korfbal video's
   - Test basis YOLO detectie op deze video's
   - Evalueer jersey number leesbaarheid

2. **Prototype** (2-4 weken)
   - Bouw simpele speler + bal tracker
   - Test op echte wedstrijden
   - Meet accuracy

3. **Go/No-Go beslissing**
   - Als accuracy > 70%: Door naar MVP
   - Als accuracy < 70%: Herijk aanpak of stop

4. **MVP Development** (8-12 weken)
   - Zie Fase 2 hierboven

---

## Vragen voor Verdere Uitwerking

Ik heb nog enkele vragen om het plan verder te verfijnen:

1. **Video materiaal**:
   - Heb je al toegang tot korfbal video's? Zo ja, wat is de kwaliteit?
   - Zijn dit livestreams of offline opnames?
   - Welke camera setup wordt gebruikt (statisch, bewegend, aantal cameras)?

2. **Doelgroep**:
   - Is dit voor professionele teams, amateurs, of jeugd?
   - Wie gaat het systeem gebruiken (coaches, analisten, fans)?

3. **Prioriteiten**:
   - Wat zijn de **must-have** statistieken?
   - Wat is belangrijker: real-time of nauwkeurigheid?

4. **Budget & Tijd**:
   - Wat is je budget range?
   - Wat is je timeline?
   - Ga je dit zelf bouwen of outsourcen?

5. **Technical**:
   - Heb je GPU hardware beschikbaar?
   - Voorkeur voor cloud of on-premise?
   - Moet het een web app zijn of desktop applicatie?
