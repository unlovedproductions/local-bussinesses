import { useEffect, useState } from 'react';
import { FULL_NARRATION_SCRIPT, SCENES } from '../lib/narration';

const SCENE_MS = 9000;

export default function ScenePlayer() {
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [showScript, setShowScript] = useState(false);
  const scene = SCENES[index];
  const progress = ((index + 1) / SCENES.length) * 100;

  useEffect(() => {
    if (!playing) return;
    const t = window.setTimeout(() => {
      setIndex((i) => {
        if (i >= SCENES.length - 1) {
          setPlaying(false);
          return i;
        }
        return i + 1;
      });
    }, SCENE_MS);
    return () => window.clearTimeout(t);
  }, [playing, index]);

  return (
    <div>
      <div className="notice">
        <strong>How POS & Inventory Integration Could Work</strong> — Interactive demo presentation (~90s). Not a
        recording of a real POS.
      </div>
      <div className="scene-player" style={{ marginTop: '1rem' }}>
        <div className="scene-stage">
          <span className="badge badge-demo">Scene {scene.id} / {SCENES.length}</span>
          <h2 style={{ fontFamily: 'Georgia, serif', fontSize: 'clamp(1.5rem, 4vw, 2.2rem)', margin: '0.75rem 0' }}>
            {scene.title}
          </h2>
          <p style={{ maxWidth: '36rem', fontSize: '1.1rem', opacity: 0.92 }}>{scene.caption}</p>
          <p style={{ maxWidth: '40rem', marginTop: '1rem', opacity: 0.75 }}>{scene.narration}</p>
          <div className="progress-track" style={{ width: 'min(420px, 90%)' }}>
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>
        <div className="scene-controls">
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button type="button" className="btn btn-primary btn-sm" onClick={() => setPlaying((p) => !p)}>
              {playing ? 'Pause' : 'Play'}
            </button>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              style={{ color: '#f6f1e8', borderColor: '#445048' }}
              onClick={() => {
                setPlaying(false);
                setIndex((i) => Math.max(0, i - 1));
              }}
            >
              Prev
            </button>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              style={{ color: '#f6f1e8', borderColor: '#445048' }}
              onClick={() => {
                setPlaying(false);
                setIndex((i) => Math.min(SCENES.length - 1, i + 1));
              }}
            >
              Next
            </button>
          </div>
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            style={{ color: '#f6f1e8', borderColor: '#445048' }}
            onClick={() => setShowScript((s) => !s)}
          >
            {showScript ? 'Hide' : 'Show'} narration script
          </button>
        </div>
      </div>
      {showScript ? (
        <pre
          className="card"
          style={{ marginTop: '1rem', whiteSpace: 'pre-wrap', fontSize: '0.9rem', lineHeight: 1.5 }}
        >
          {FULL_NARRATION_SCRIPT}
        </pre>
      ) : null}
    </div>
  );
}
