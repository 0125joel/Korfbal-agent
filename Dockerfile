# Stage 1: bouw de Next.js frontend als statische export
FROM node:20-bullseye AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build && npm run export

# Stage 2: runtime met GPU-ondersteuning voor FastAPI + YOLO
FROM ghcr.io/huggingface/spaces-pytorch:0.2.1-cuda11.8

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

COPY backend/requirements.txt /workspace/backend/requirements.txt
RUN pip install --upgrade pip && pip install -r /workspace/backend/requirements.txt

COPY backend /workspace/backend
COPY --from=frontend-build /app/out /workspace/frontend/out

# Zorg voor lege directories die door gebruikers kunnen worden gevuld
RUN mkdir -p /workspace/models /workspace/data

ENV PYTHONPATH=/workspace/backend
ENV PORT=7860
WORKDIR /workspace/backend

EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
