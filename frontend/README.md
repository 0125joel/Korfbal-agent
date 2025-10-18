# Frontend (Next.js)

Deze Next.js-applicatie toont de heatmap en statistieken die door de FastAPI-backend worden verzameld.

## Ontwikkeling

```bash
npm install
npm run dev
```

Zorg dat `NEXT_PUBLIC_API_BASE_URL` verwijst naar de backend (`http://localhost:7860/api`).

## Export

Tijdens deployment wordt `next export` uitgevoerd zodat de frontend als statische site door FastAPI kan worden geserveerd.
