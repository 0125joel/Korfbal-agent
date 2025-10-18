'use client';

import useSWR from 'swr';
import { fetcher } from '../lib/api';

interface PlayerShot {
  player_id: string;
  player_name?: string | null;
  scored: boolean;
  timestamp: string;
  confidence: number;
}

interface PlayerStats {
  player_id: string;
  player_name?: string | null;
  attempts: number;
  goals: number;
  accuracy: number;
}

interface StatsResponse {
  shots: PlayerShot[];
  players: PlayerStats[];
}

export function StatsTable() {
  const { data, isLoading } = useSWR<StatsResponse>('/stats', fetcher, {
    refreshInterval: 3_000,
  });

  if (isLoading) {
    return <div className="card">Statistieken laden...</div>;
  }

  if (!data) {
    return <div className="card">Nog geen data beschikbaar.</div>;
  }

  return (
    <div className="card">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>Spelerstatistieken</h2>
          <p className="badge">Live geüpdatet</p>
        </div>
      </header>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Speler</th>
              <th>Pogingen</th>
              <th>Doelpunten</th>
              <th>Nauwkeurigheid</th>
            </tr>
          </thead>
          <tbody>
            {data.players.map((player) => (
              <tr key={player.player_id}>
                <td>
                  <strong>{player.player_name ?? player.player_id}</strong>
                </td>
                <td>{player.attempts}</td>
                <td>{player.goals}</td>
                <td>{(player.accuracy * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h3 style={{ marginTop: '1.5rem' }}>Laatste schoten</h3>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {data.shots.slice(-5).reverse().map((shot) => (
          <li
            key={`${shot.player_id}-${shot.timestamp}`}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              padding: '0.6rem 0',
              borderBottom: '1px solid rgba(148, 163, 184, 0.1)',
            }}
          >
            <span>
              {shot.player_name ?? shot.player_id}
              <span style={{ marginLeft: '0.5rem', fontSize: '0.85rem', opacity: 0.7 }}>
                {new Date(shot.timestamp).toLocaleTimeString()}
              </span>
            </span>
            <span className="badge" style={{ background: shot.scored ? 'rgba(74, 222, 128, 0.2)' : undefined }}>
              {shot.scored ? 'Score' : 'Gemist'}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
