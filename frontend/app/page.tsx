import { ShotHeatmap } from '../components/Heatmap';
import { StatsTable } from '../components/StatsTable';

export default function HomePage() {
  return (
    <main>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2.25rem', marginBottom: '0.5rem' }}>Korfbal Live Analytics</h1>
          <p style={{ maxWidth: '640px', opacity: 0.85 }}>
            Volg live hoe spelers presteren. Heatmaps laten zien waar schoten genomen worden, terwijl de statistieken de
            efficiëntie per speler tonen. Verbind een videobron via de API om realtime data binnen te krijgen.
          </p>
        </div>
        <a className="button" href="/api/docs">
          API Docs
        </a>
      </header>
      <div className="grid">
        <ShotHeatmap />
        <StatsTable />
      </div>
    </main>
  );
}
