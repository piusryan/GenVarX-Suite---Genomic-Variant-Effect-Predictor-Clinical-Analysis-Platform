import React, { useEffect, useRef, useState } from 'react';
import { Play, Pause, Atom, Maximize2, Minimize2, RotateCcw, Info } from 'lucide-react';

// Amino-acid property palette used for e-learning style side-chain colouring.
const AA_PALETTE = {
  A: { name: 'Ala', color: '#facc15', group: 'Hydrophobic' },
  V: { name: 'Val', color: '#facc15', group: 'Hydrophobic' },
  I: { name: 'Ile', color: '#facc15', group: 'Hydrophobic' },
  L: { name: 'Leu', color: '#facc15', group: 'Hydrophobic' },
  M: { name: 'Met', color: '#facc15', group: 'Hydrophobic' },
  F: { name: 'Phe', color: '#facc15', group: 'Hydrophobic' },
  W: { name: 'Trp', color: '#facc15', group: 'Hydrophobic' },
  P: { name: 'Pro', color: '#facc15', group: 'Hydrophobic' },
  G: { name: 'Gly', color: '#94a3b8', group: 'Special' },
  S: { name: 'Ser', color: '#22c55e', group: 'Polar' },
  T: { name: 'Thr', color: '#22c55e', group: 'Polar' },
  C: { name: 'Cys', color: '#22c55e', group: 'Polar' },
  Y: { name: 'Tyr', color: '#22c55e', group: 'Polar' },
  N: { name: 'Asn', color: '#22c55e', group: 'Polar' },
  Q: { name: 'Gln', color: '#22c55e', group: 'Polar' },
  K: { name: 'Lys', color: '#3b82f6', group: 'Basic (+)' },
  R: { name: 'Arg', color: '#3b82f6', group: 'Basic (+)' },
  H: { name: 'His', color: '#3b82f6', group: 'Basic (+)' },
  D: { name: 'Asp', color: '#ef4444', group: 'Acidic (-)' },
  E: { name: 'Glu', color: '#ef4444', group: 'Acidic (-)' },
};

// Backbone atom colours (educational CPK-ish).
const BACKBONE_COLORS = {
  N: '#3b82f6',   // Nitrogen blue
  CA: '#64748b',  // Alpha carbon slate
  C: '#f97316',   // Carbonyl carbon orange
  O: '#ef4444',   // Oxygen red
};

export default function AdvancedProtein3D({ proteinChange }) {
  const canvasRef = useRef(null);
  const [rotation] = useState({ x: 0.45, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [animating, setAnimating] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);
  const [canvasHeight, setCanvasHeight] = useState(380);
  const [showLabels, setShowLabels] = useState(true);

  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d', { alpha: false });

    let animationId;
    let rotX = rotation.x;
    let rotY = rotation.y;
    let currentZoom = zoom;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const parts = (proteinChange || 'M/V').split('/').filter(p => p).map(aa => aa?.trim() || '?');
    const refAA = parts[0] || '?';
    const altAA = parts[1] || '?';

    // Build an educational alpha-helix model with labelled residues.
    const residues = generateProteinModel(refAA);

    const rotateX = (p, angle) => {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      return { x: p.x, y: p.y * cos - p.z * sin, z: p.y * sin + p.z * cos };
    };

    const rotateY = (p, angle) => {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      return { x: p.x * cos + p.z * sin, y: p.y, z: -p.x * sin + p.z * cos };
    };

    const rotateZ = (p, angle) => {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      return { x: p.x * cos - p.y * sin, y: p.x * sin + p.y * cos, z: p.z };
    };

    const project3D = (p) => {
      let pt = rotateX({ x: p.x, y: p.y, z: p.z }, rotX);
      pt = rotateY(pt, rotY);
      pt = rotateZ(pt, 0);

      const focalLength = 520;
      const scale = focalLength / (focalLength + pt.z);
      return {
        x: rect.width / 2 + pt.x * scale * currentZoom,
        y: rect.height / 2 + pt.y * scale * currentZoom,
        z: pt.z,
        scale,
      };
    };

    const drawBackground = () => {
      ctx.fillStyle = '#0b101a';
      ctx.fillRect(0, 0, rect.width, rect.height);

      // Very subtle grid
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.04)';
      ctx.lineWidth = 1;
      const step = 48;
      for (let x = 0; x < rect.width; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, rect.height);
        ctx.stroke();
      }
      for (let y = 0; y < rect.height; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(rect.width, y);
        ctx.stroke();
      }
    };

    // Collect all drawable objects (bonds and atoms) with depth.
    const getDrawables = () => {
      const objects = [];

      // Backbone bonds
      for (let i = 0; i < residues.length - 1; i++) {
        const r1 = residues[i];
        const r2 = residues[i + 1];
        objects.push({
          type: 'bond',
          z: (r1.ca.z + r2.ca.z) / 2,
          p1: r1.ca,
          p2: r2.ca,
          color: '#94a3b8',
          width: 2.5,
          dashed: false,
        });
      }

      // Intra-residue backbone bonds (N-CA, CA-C)
      residues.forEach(r => {
        objects.push({ type: 'bond', z: (r.n.z + r.ca.z) / 2, p1: r.n, p2: r.ca, color: '#64748b', width: 2, dashed: false });
        objects.push({ type: 'bond', z: (r.ca.z + r.c.z) / 2, p1: r.ca, p2: r.c, color: '#64748b', width: 2, dashed: false });
        objects.push({ type: 'bond', z: (r.c.z + r.o.z) / 2, p1: r.c, p2: r.o, color: '#ef4444', width: 2, dashed: false });

        // Side-chain stick
        if (r.sideChain) {
          objects.push({
            type: 'bond',
            z: (r.ca.z + r.sideChain.z) / 2,
            p1: r.ca,
            p2: r.sideChain,
            color: r.sideChainColor,
            width: 2.5,
            dashed: false,
          });
        }
      });

      // Hydrogen bonds between turns (i to i+4) - educational alpha-helix feature
      for (let i = 0; i < residues.length - 4; i++) {
        const rO = residues[i].o;
        const rN = residues[i + 4].n;
        objects.push({
          type: 'bond',
          z: (rO.z + rN.z) / 2,
          p1: rO,
          p2: rN,
          color: '#38bdf8',
          width: 1,
          dashed: true,
        });
      }

      // Atoms
      residues.forEach(r => {
        objects.push({ type: 'atom', z: r.n.z, point: r.n, radius: 3.5, color: BACKBONE_COLORS.N, label: null });
        objects.push({ type: 'atom', z: r.ca.z, point: r.ca, radius: r.isMutation ? 10 : 6, color: r.isMutation ? '#f59e0b' : BACKBONE_COLORS.CA, label: r.label, isMutation: r.isMutation });
        objects.push({ type: 'atom', z: r.c.z, point: r.c, radius: 3.2, color: BACKBONE_COLORS.C, label: null });
        objects.push({ type: 'atom', z: r.o.z, point: r.o, radius: 3, color: BACKBONE_COLORS.O, label: null });
        if (r.sideChain) {
          objects.push({
            type: 'atom',
            z: r.sideChain.z,
            point: r.sideChain,
            radius: r.isMutation ? 8 : 4.5,
            color: r.isMutation ? '#ef4444' : r.sideChainColor,
            label: r.isMutation ? `${refAA}→${altAA}` : null,
            isMutation: r.isMutation,
          });
        }
      });

      return objects.sort((a, b) => a.z - b.z);
    };

    const drawBondObject = (obj) => {
      const a = project3D(obj.p1);
      const b = project3D(obj.p2);

      ctx.save();
      ctx.strokeStyle = obj.color;
      ctx.lineWidth = obj.width * ((a.scale + b.scale) / 2) * currentZoom;
      ctx.lineCap = 'round';
      if (obj.dashed) {
        ctx.setLineDash([4, 4]);
        ctx.globalAlpha = 0.35;
      } else {
        ctx.globalAlpha = Math.min(1, 0.65 + ((a.scale + b.scale) / 4));
      }
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
      ctx.restore();
    };

    const drawAtomObject = (obj) => {
      const p = project3D(obj.point);
      const r = obj.radius * p.scale * currentZoom;
      if (r < 0.8) return;

      // Soft shadow
      ctx.fillStyle = 'rgba(0,0,0,0.25)';
      ctx.beginPath();
      ctx.arc(p.x + 1.5, p.y + 1.5, r * 1.15, 0, Math.PI * 2);
      ctx.fill();

      // Main sphere with realistic lighting
      const grad = ctx.createRadialGradient(
        p.x - r * 0.35, p.y - r * 0.35, r * 0.15,
        p.x, p.y, r
      );
      grad.addColorStop(0, adjustBrightness(obj.color, 0.45));
      grad.addColorStop(0.45, obj.color);
      grad.addColorStop(1, adjustBrightness(obj.color, -0.35));
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.fill();

      // Specular highlight
      ctx.fillStyle = 'rgba(255,255,255,0.35)';
      ctx.beginPath();
      ctx.arc(p.x - r * 0.35, p.y - r * 0.35, r * 0.25, 0, Math.PI * 2);
      ctx.fill();

      // Mutation emphasis: thin clean ring, no bloom
      if (obj.isMutation) {
        ctx.strokeStyle = '#f87171';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(p.x, p.y, r * 1.45, 0, Math.PI * 2);
        ctx.stroke();
      }

      // Labels
      if (showLabels && obj.label && r > 4) {
        drawLabel(p.x, p.y - r - 8, obj.label, obj.isMutation ? '#fca5a5' : '#cbd5e1');
      }
    };

    const drawLabel = (x, y, text, color) => {
      ctx.font = 'bold 11px "Inter", system-ui, sans-serif';
      const metrics = ctx.measureText(text);
      const pad = 5;
      const w = metrics.width + pad * 2;
      const h = 18;
      const lx = x - w / 2;
      const ly = y - h / 2;

      // Small pill background
      ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.25)';
      ctx.lineWidth = 1;
      roundRectPath(ctx, lx, ly, w, h, 4);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = color;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, x, y + 1);
    };

    const drawInfoOverlay = () => {
      const panelX = 16;
      const panelY = 16;
      const panelW = 260;
      const panelH = 108;

      ctx.fillStyle = 'rgba(11, 16, 26, 0.82)';
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.2)';
      ctx.lineWidth = 1;
      roundRectPath(ctx, panelX, panelY, panelW, panelH, 8);
      ctx.fill();
      ctx.stroke();

      ctx.textAlign = 'left';
      ctx.textBaseline = 'alphabetic';

      ctx.fillStyle = '#e2e8f0';
      ctx.font = 'bold 13px "Inter", system-ui, sans-serif';
      ctx.fillText('Protein Mutation Analysis', panelX + 14, panelY + 26);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '12px "Inter", system-ui, sans-serif';
      ctx.fillText('Reference residue', panelX + 14, panelY + 52);
      ctx.fillText('Variant residue', panelX + 14, panelY + 76);

      ctx.fillStyle = '#38bdf8';
      ctx.font = 'bold 14px "JetBrains Mono", monospace';
      ctx.fillText(refAA, panelX + 135, panelY + 52);

      ctx.fillStyle = '#888888';
      ctx.font = '14px "JetBrains Mono", monospace';
      ctx.fillText('→', panelX + 160, panelY + 52);

      ctx.fillStyle = '#f87171';
      ctx.font = 'bold 14px "JetBrains Mono", monospace';
      ctx.fillText(altAA, panelX + 180, panelY + 52);

      ctx.fillStyle = '#fbbf24';
      ctx.font = '11px "JetBrains Mono", monospace';
      ctx.fillText('⚠ Substitution at locus 21', panelX + 14, panelY + 96);
    };

    const drawHelp = () => {
      ctx.textAlign = 'left';
      ctx.textBaseline = 'alphabetic';
      ctx.fillStyle = 'rgba(148, 163, 184, 0.7)';
      ctx.font = '11px "Inter", system-ui, sans-serif';
      ctx.fillText('Drag to rotate • Scroll to zoom • Hover/click labels to read residues', 16, rect.height - 16);
    };

    const draw = () => {
      drawBackground();

      const objects = getDrawables();
      objects.forEach(obj => {
        if (obj.type === 'bond') drawBondObject(obj);
        else drawAtomObject(obj);
      });

      drawInfoOverlay();
      drawHelp();

      if (animating) {
        rotX += 0.002;
        rotY += 0.005;
      }

      animationId = requestAnimationFrame(draw);
    };

    draw();

    const handleMouseMove = (e) => {
      if (e.buttons === 1) {
        rotY += (e.movementX || 0) * 0.005;
        rotX += (e.movementY || 0) * 0.005;
      }
    };

    const handleWheel = (e) => {
      e.preventDefault();
      currentZoom += (e.deltaY > 0 ? -0.08 : 0.08);
      currentZoom = Math.max(0.5, Math.min(2.5, currentZoom));
    };

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('wheel', handleWheel, { passive: false });

    return () => {
      cancelAnimationFrame(animationId);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('wheel', handleWheel);
    };
  }, [rotation, zoom, animating, proteinChange, canvasHeight, showLabels]);

  return (
    <div className="glass-panel p-6 border-[rgba(148,163,184,0.15)] hud-frame relative">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-[rgba(148,163,184,0.12)] pb-2">
        <div className="flex items-center gap-2">
          <Atom className="w-5 h-5 text-slate-300" />
          <h3 className="text-xs font-bold tracking-widest font-display text-slate-200 uppercase">
            3D Protein Mutation Simulator
          </h3>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setAnimating(!animating)}
            className="px-2.5 py-1.5 text-[10px] font-mono font-bold bg-slate-800/60 text-slate-200 border border-slate-700/50 rounded hover:bg-slate-700/70 transition flex items-center gap-1"
          >
            {animating ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
            {animating ? 'PAUSE' : 'PLAY'}
          </button>
          <button
            onClick={() => setShowLabels(!showLabels)}
            className={`px-2.5 py-1.5 text-[10px] font-mono font-bold border rounded transition flex items-center gap-1 ${
              showLabels
                ? 'bg-slate-700/70 text-slate-100 border-slate-600/50'
                : 'bg-slate-800/60 text-slate-400 border-slate-700/50 hover:bg-slate-700/70'
            }`}
          >
            <Info className="w-3 h-3" />
            LABELS
          </button>
          <button
            onClick={() => setZoom(1)}
            className="px-2.5 py-1.5 text-[10px] font-mono font-bold bg-slate-800/60 text-slate-200 border border-slate-700/50 rounded hover:bg-slate-700/70 transition flex items-center justify-center"
            title="Reset view"
          >
            <RotateCcw className="w-3 h-3" />
          </button>
          <button
            onClick={() => setFullscreen(!fullscreen)}
            className="px-2.5 py-1.5 text-[10px] font-mono font-bold bg-slate-800/60 text-slate-200 border border-slate-700/50 rounded hover:bg-slate-700/70 transition flex items-center justify-center"
          >
            {fullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      <canvas
        ref={canvasRef}
        className="w-full bg-[#0b101a] rounded-lg border border-slate-800 cursor-grab active:cursor-grabbing"
        style={{ display: 'block', height: fullscreen ? '100vh' : `${canvasHeight}px` }}
      />

      {/* Info panels */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mt-4">
        <div className="data-cell font-mono">
          <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">Reference State</div>
          <div className="text-lg font-bold text-sky-400 mt-1">{proteinChange.split('/')[0]}</div>
          <div className="text-[9px] text-slate-400 mt-0.5 uppercase">Wild-type residue</div>
        </div>

        <div className="data-cell font-mono">
          <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">Mutation Site</div>
          <div className="flex items-center gap-1.5 mt-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            <span className="text-[10px] text-amber-400 font-bold tracking-widest">LOCUS 21</span>
          </div>
          <div className="text-[9px] text-slate-400 mt-0.5 uppercase">Alpha-helix position</div>
        </div>

        <div className="data-cell font-mono">
          <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">Variant State</div>
          <div className="text-lg font-bold text-red-400 mt-1">{proteinChange.split('/')[1]}</div>
          <div className="text-[9px] text-slate-400 mt-0.5 uppercase">Mutant residue</div>
        </div>

        <div className="data-cell font-mono flex flex-col justify-center">
          <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-1 flex justify-between">
            <span>Viewport Height</span>
            <span className="text-slate-300 font-bold">{canvasHeight}px</span>
          </div>
          <input
            type="range"
            min="200"
            max="700"
            value={canvasHeight}
            onChange={(e) => setCanvasHeight(parseInt(e.target.value))}
            className="w-full accent-slate-400 h-1 bg-slate-950 rounded-lg appearance-none cursor-pointer mt-1"
          />
        </div>
      </div>

      {/* Educational legend */}
      <div className="bg-slate-950/50 border border-slate-800/60 rounded-lg p-3 mt-3 font-mono text-[10px]">
        <p className="text-slate-500 font-bold uppercase tracking-widest mb-2">Molecular Model Legend</p>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          <LegendItem color={BACKBONE_COLORS.N} label="Nitrogen (N)" />
          <LegendItem color={BACKBONE_COLORS.CA} label="Alpha carbon (Cα)" />
          <LegendItem color={BACKBONE_COLORS.C} label="Carbonyl carbon (C)" />
          <LegendItem color={BACKBONE_COLORS.O} label="Oxygen (O)" />
          <LegendItem color="#38bdf8" label="H-bond (i → i+4)" dashed />
          <LegendItem color="#facc15" label="Hydrophobic side chain" />
          <LegendItem color="#22c55e" label="Polar side chain" />
          <LegendItem color="#3b82f6" label="Basic (+) side chain" />
          <LegendItem color="#ef4444" label="Acidic (-) side chain" />
          <LegendItem color="#f59e0b" label="Mutation site (Cα)" />
        </div>
      </div>
    </div>
  );
}

function LegendItem({ color, label, dashed }) {
  return (
    <div className="flex items-center gap-1.5">
      <div
        className="w-3 h-3 rounded-full border border-slate-700"
        style={{
          background: dashed ? 'transparent' : color,
          borderColor: color,
          borderStyle: dashed ? 'dashed' : 'solid',
        }}
      />
      <span className="text-slate-400">{label}</span>
    </div>
  );
}

// Generate an alpha-helix with a realistic backbone and property-coloured side chains.
function generateProteinModel(refAA) {
  const residues = [];
  const helixRadius = 34;
  const helixPitch = 5.2;
  const residuesPerTurn = 3.6;
  const mutationIndex = 20;

  for (let i = 0; i < 40; i++) {
    const angle = (i / residuesPerTurn) * Math.PI * 2;
    const cx = helixRadius * Math.cos(angle);
    const cy = i * helixPitch - 95;
    const cz = helixRadius * Math.sin(angle);

    const isMutation = i === mutationIndex;
    const aaCode = isMutation ? refAA : pseudoSequence(i, refAA);
    const aa = AA_PALETTE[aaCode] || AA_PALETTE.A;

    // Backbone geometry (slightly offset around the helix axis)
    residues.push({
      index: i + 1,
      aaCode,
      label: `${aa.name} ${i + 1}`,
      isMutation,
      n: { x: cx + 6 * Math.cos(angle + 0.6), y: cy - 1.8, z: cz + 6 * Math.sin(angle + 0.6) },
      ca: { x: cx, y: cy, z: cz },
      c: { x: cx - 6 * Math.cos(angle - 0.4), y: cy + 1.8, z: cz - 6 * Math.sin(angle - 0.4) },
      o: { x: cx - 10 * Math.cos(angle - 0.4), y: cy + 3.2, z: cz - 10 * Math.sin(angle - 0.4) },
      sideChain: aaCode !== 'G' ? {
        x: cx + 12 * Math.cos(angle + 1.0),
        y: cy + 1.5,
        z: cz + 12 * Math.sin(angle + 1.0),
      } : null,
      sideChainColor: aa.color,
    });
  }

  return residues;
}

// Deterministic pseudo-sequence so the model is stable across renders.
function pseudoSequence(index, refAA) {
  const keys = Object.keys(AA_PALETTE);
  const seed = Math.abs(Math.sin(index * 0.7 + 1.3)) * 10000;
  const pick = Math.floor((seed - Math.floor(seed)) * keys.length);
  const code = keys[pick];
  return code === refAA ? keys[(pick + 1) % keys.length] : code;
}

function adjustBrightness(color, percent) {
  const r = parseInt(color.slice(1, 3), 16);
  const g = parseInt(color.slice(3, 5), 16);
  const b = parseInt(color.slice(5, 7), 16);

  const newR = Math.min(255, Math.max(0, Math.round(r * (1 + percent))));
  const newG = Math.min(255, Math.max(0, Math.round(g * (1 + percent))));
  const newB = Math.min(255, Math.max(0, Math.round(b * (1 + percent))));

  return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
}

function roundRectPath(ctx, x, y, w, h, r) {
  const radius = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + w - radius, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + radius);
  ctx.lineTo(x + w, y + h - radius);
  ctx.quadraticCurveTo(x + w, y + h, x + w - radius, y + h);
  ctx.lineTo(x + radius, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}
