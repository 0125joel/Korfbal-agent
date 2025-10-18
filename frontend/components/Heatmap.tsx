'use client';

import { useMemo } from 'react';
import HeatMap from 'react-heatmap-grid';
import useSWR from 'swr';
import { fetcher } from '../lib/api';

export interface HeatmapPoint {
  x: number;
  y: number;
  value: number;
}

interface HeatmapResponse {
  points: HeatmapPoint[];
  grid_size: number;
}

const defaultGridSize = 10;

function buildGrid(data: HeatmapResponse) {
  const grid: number[][] = Array.from({ length: data.grid_size }, () =>
    Array.from({ length: data.grid_size }, () => 0)
  );
  data.points.forEach((point) => {
    const gx = Math.min(data.grid_size - 1, Math.floor(point.x * data.grid_size));
    const gy = Math.min(data.grid_size - 1, Math.floor(point.y * data.grid_size));
    grid[gy][gx] = point.value;
  });
  return grid;
}

export function ShotHeatmap() {
  const { data, isLoading } = useSWR<HeatmapResponse>(
    `/heatmap?grid_size=${defaultGridSize}`,
    fetcher,
    { refreshInterval: 3_000 }
  );

  const grid = useMemo(() => (data ? buildGrid(data) : []), [data]);
  const xLabels = useMemo(
    () => Array.from({ length: defaultGridSize }, (_, idx) => `${idx + 1}`),
    []
  );
  const yLabels = xLabels;

  if (isLoading) {
    return <div className="card">Heatmap laden...</div>;
  }

  if (!data || grid.length === 0) {
    return <div className="card">Nog geen schoten geregistreerd.</div>;
  }

  return (
    <div className="card">
      <h2>Schot heatmap</h2>
      <p className="badge">Live geüpdatet elke 3 seconden</p>
      <div style={{ height: 360 }}>
        <HeatMap
          xLabels={xLabels}
          yLabels={yLabels}
          data={grid}
          squares
          xLabelWidth={32}
          yLabelWidth={32}
          cellStyle={(_background, value) => ({
            background: `rgba(56, 189, 248, ${Math.min(1, value / 5)})`,
            color: '#fff',
            fontSize: '0.75rem',
          })}
          cellRender={(_x, _y, value) => (value ? <span>{value.toFixed(1)}</span> : null)}
        />
      </div>
    </div>
  );
}
