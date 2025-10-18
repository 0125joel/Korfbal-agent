# Backend (FastAPI)

De backend verwerkt videoframes en levert API-endpoints voor heatmaps en statistieken.

## Belangrijkste endpoints

| Methode | Pad | Beschrijving |
| --- | --- | --- |
| `GET` | `/api/health` | Healthcheck |
| `GET` | `/api/model` | Informatie over het YOLO-model |
| `POST` | `/api/frames/analyze` | Analyseer een frame (base64) |
| `GET` | `/api/stats` | Overzicht van spelers en shots |
| `GET` | `/api/heatmap` | Heatmapdata |
| `WS` | `/api/ws/frames` | WebSocket voor realtime frames |

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
