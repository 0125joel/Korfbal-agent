# Backend (FastAPI)

De backend verwerkt videoframes, beheert events en levert API-endpoints voor heatmaps en statistieken.

## Belangrijkste endpoints

| Methode | Pad | Beschrijving |
| --- | --- | --- |
| `GET` | `/healthz` | Healthcheck met servicenaam en versie |
| `GET` | `/api/model` | Informatie over het YOLO-model |
| `POST` | `/api/frames/analyze` | Analyseer een frame (base64) |
| `GET` | `/api/stats` | Overzicht van spelers en shots |
| `GET` | `/api/heatmap` | Heatmapdata |
| `POST` | `/api/events/batch` | Voeg meerdere events toe (vereist `x-api-key` indien ingesteld) |
| `POST` | `/api/events/reset` | Leeg de eventbuffer (vereist `x-api-key` indien ingesteld) |
| `GET` | `/api/events/all` | Haal events op met paginatie |
| `WS` | `/api/ws/frames` | WebSocket voor realtime frames |

## Windows (PowerShell) setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
# Pas de inhoud van .env aan indien nodig, bijvoorbeeld de API-sleutel of CORS-origins.
uvicorn app.main:app --host 127.0.0.1 --port 7860 --reload
```

## Voorbeeld request

```bash
curl -X POST http://localhost:7860/api/frames/analyze \
  -H "Content-Type: application/json" \
  -d '{
        "image_base64": "<BASE64-FRAME>",
        "metadata": {
          "match_id": "wedstrijd-1",
          "frame_timestamp": "2024-05-01T10:00:00Z",
          "player_id": "speler-12",
          "player_name": "Jan"
        }
      }'
```

De response bevat `null` als er geen geldig schot werd gevonden.
