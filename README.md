# Korfbal Live Analytics Platform

Deze repository bevat een volledige stack voor live video-analyse van korfbalwedstrijden. De backend gebruikt FastAPI en een YOLO-model om in real-time doelpogingen te detecteren en bij te houden. De Next.js-frontend toont een heatmap van schoten en statistieken per speler. Deploy op Hugging Face Spaces met GPU-ondersteuning.

## Projectstructuur

```text
backend/        FastAPI-toepassing, modelinference en trainingsscripts
frontend/       Next.js-frontend met heatmap en statistieken
models/         Directory voor YOLO-modelgewichten (bijv. `yolo_korfbal.pt`)
data/           Plaats trainingsdata of voorbeeldbestanden
Dockerfile      Containerconfiguratie voor Hugging Face Spaces
hf.yaml         Hugging Face Spaces configuratie (GPU, hardware)
```

## Belangrijkste features

- WebSocket-stream voor live frames vanuit een videobron (bijv. RTSP of WebRTC gateway)
- YOLOv8-model (Ultralytics) getraind om gele korfbalmanden en balinteracties te detecteren
- Shot-tracker die automatisch bepaalt of een poging een doelpunt is
- REST API voor heatmap en spelerstatistieken
- Next.js-dashboard met interactieve heatmap en tabel
- Volledige Dockerfile geoptimaliseerd voor deployment op Hugging Face Spaces met GPU

## Quickstart backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

Zorg dat het bestand `models/yolo_korfbal.pt` aanwezig is. Je kunt het trainen met `backend/scripts/train_detector.py` of handmatig uploaden.

## Quickstart frontend

```bash
cd frontend
npm install
npm run dev
```

Stel de omgevingsvariabele `NEXT_PUBLIC_API_BASE_URL` in (standaard `http://localhost:7860`).

## Trainingspipeline

1. Verzamel videobeelden en label de gele korfbalmand, bal en spelers (zie `backend/scripts/dataset.yaml`).
2. Voer `python backend/scripts/train_detector.py --data backend/scripts/dataset.yaml` uit. Dit traint een YOLOv8-model.
3. Verplaats de resulterende `best.pt` naar `models/yolo_korfbal.pt`.

## Hugging Face Spaces

- Pas `hf.yaml` aan voor de gewenste runtime (`sdk: docker`, `hardware: gpu`).
- Deploy de space door deze repository te koppelen.
- De Dockerfile start zowel de FastAPI-backend als de Next.js-frontend.

## License

MIT
