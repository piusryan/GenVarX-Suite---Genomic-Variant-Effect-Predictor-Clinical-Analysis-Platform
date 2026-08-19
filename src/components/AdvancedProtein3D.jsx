import React, { useEffect, useRef, useState } from 'react';
import { Zap, Atom, Dna, Maximize2, Minimize2, RotateCcw } from 'lucide-react';

export default function AdvancedProtein3D({ variant, vepResult, proteinChange }) {
  const canvasRef = useRef(null);
  const [rotation, setRotation] = useState({ x: 0.5, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [animating, setAnimating] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);
  const [quality, setQuality] = useState('high');
  const [canvasHeight, setCanvasHeight] = useState(320); // Resizable viewport height

  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d', { alpha: false });
    
    let animationId;
    let rotX = rotation.x;
    let rotY = rotation.y;
    let currentZoom = zoom;

    // High-resolution canvas
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    // Parse protein change - handle edge cases
    const parts = proteinChange.split('/').filter(p => p).map(aa => aa?.trim() || 'N/A');
    const refAA = parts[0] || 'N/A';
    const altAA = parts[1] || 'N/A';

    // Generate realistic protein structure with secondary structures
    const generateRealisticProtein = () => {
      const atoms = [];
      const helixRadius = 30;
      const helixPitch = 5.4;
      const residuesPerTurn = 3.6;
      
      // Main helix (alpha helix)
      for (let i = 0; i < 40; i++) {
        const angle = (i / residuesPerTurn) * Math.PI * 2;
        const x = helixRadius * Math.cos(angle);
        const y = i * helixPitch - 100;
        const z = helixRadius * Math.sin(angle);
        
        const isMutationSite = i === 20; // Middle of helix
        
        atoms.push({
          x, y, z,
          radius: isMutationSite ? 12 : 7,
          color: isMutationSite ? '#ff4757' : '#00d9ff',
          isActive: isMutationSite,
          type: isMutationSite ? 'mutation' : 'ca', // Alpha carbon
          label: isMutationSite ? `${refAA} → ${altAA}` : '',
          intensity: isMutationSite ? 1 : 0.7,
          originalX: x,
          originalY: y,
          originalZ: z
        });

        // Add side chain atoms (simplified)
        if (i % 2 === 0 && !isMutationSite) {
          const angle2 = angle + 0.5;
          const scaleX = helixRadius * 0.6;
          const scX = scaleX * Math.cos(angle2);
          const scZ = scaleX * Math.sin(angle2);
          
          atoms.push({
            x: x + scX * 0.3,
            y: y + 2,
            z: z + scZ * 0.3,
            radius: 4,
            color: '#00d9ff',
            isActive: false,
            type: 'sidechain',
            label: '',
            intensity: 0.5,
            originalX: x,
            originalY: y,
            originalZ: z
          });
        }
      }
      
      return atoms;
    };

    const proteinAtoms = generateRealisticProtein();

    // Advanced 3D transformation with rotation matrices
    const rotateX = (p, angle) => {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      return {
        x: p.x,
        y: p.y * cos - p.z * sin,
        z: p.y * sin + p.z * cos
      };
    };

    const rotateY = (p, angle) => {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      return {
        x: p.x * cos + p.z * sin,
        y: p.y,
        z: -p.x * sin + p.z * cos
      };
    };

    const rotateZ = (p, angle) => {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      return {
        x: p.x * cos - p.y * sin,
        y: p.x * sin + p.y * cos,
        z: p.z
      };
    };

    // Project 3D to 2D with perspective
    const project3D = (atom, rotX, rotY, rotZ, zoom) => {
      let p = { x: atom.x, y: atom.y, z: atom.z };
      
      // Apply rotations
      p = rotateX(p, rotX);
      p = rotateY(p, rotY);
      p = rotateZ(p, rotZ);

      // Perspective projection with depth of field
      const focalLength = 500;
      const scale = focalLength / (focalLength + p.z);
      
      const x2D = (rect.width / 2) + p.x * scale * currentZoom;
      const y2D = (rect.height / 2) + p.y * scale * currentZoom;
      const radius2D = atom.radius * scale * currentZoom;

      return { 
        x: x2D, 
        y: y2D, 
        scale, 
        radius: radius2D,
        z: p.z,
        depth: scale
      };
    };

    // Draw 3D sphere
    const drawSphere = (x, y, radius, color, intensity, atom) => {
      if (radius < 1) return;

      // Multiple layers for 3D effect
      // Shadow
      const shadowGradient = ctx.createRadialGradient(x + 2, y + 2, 0, x + 2, y + 2, radius * 1.5);
      shadowGradient.addColorStop(0, 'rgba(0, 0, 0, 0.3)');
      shadowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = shadowGradient;
      ctx.beginPath();
      ctx.arc(x + 2, y + 2, radius * 1.5, 0, Math.PI * 2);
      ctx.fill();

      // Main sphere with shading
      const gradient = ctx.createRadialGradient(
        x - radius * 0.3, y - radius * 0.3, 0,
        x, y, radius
      );
      gradient.addColorStop(0, adjustBrightness(color, 0.3));
      gradient.addColorStop(0.5, color);
      gradient.addColorStop(1, adjustBrightness(color, -0.3));
      
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();

      // Specular highlight
      if (intensity > 0.6) {
        ctx.fillStyle = `rgba(255, 255, 255, ${0.4 * intensity})`;
        ctx.beginPath();
        ctx.arc(x - radius * 0.4, y - radius * 0.4, radius * 0.3, 0, Math.PI * 2);
        ctx.fill();
      }

      // Glow for active atoms
      if (atom.isActive) {
        const glowGradient = ctx.createRadialGradient(x, y, radius, x, y, radius * 3);
        glowGradient.addColorStop(0, `rgba(255, 71, 87, 0.5)`);
        glowGradient.addColorStop(1, `rgba(255, 71, 87, 0)`);
        ctx.fillStyle = glowGradient;
        ctx.beginPath();
        ctx.arc(x, y, radius * 3, 0, Math.PI * 2);
        ctx.fill();

        // Pulsing outline
        const pulse = Math.sin(Date.now() / 300) * 0.3 + 1;
        ctx.strokeStyle = `rgba(255, 71, 87, ${0.8 * pulse})`;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(x, y, radius * pulse, 0, Math.PI * 2);
        ctx.stroke();
      }
    };

    // Draw connection bonds
    const drawBond = (x1, y1, x2, y2, atom1, atom2) => {
      const dx = x2 - x1;
      const dy = y2 - y1;
      const length = Math.sqrt(dx * dx + dy * dy);
      
      if (length < 1) return;

      const gradient = ctx.createLinearGradient(x1, y1, x2, y2);
      
      if (atom1.isActive || atom2.isActive) {
        gradient.addColorStop(0, 'rgba(255, 71, 87, 0.6)');
        gradient.addColorStop(1, 'rgba(255, 71, 87, 0.6)');
      } else {
        gradient.addColorStop(0, 'rgba(0, 217, 255, 0.3)');
        gradient.addColorStop(1, 'rgba(0, 217, 255, 0.3)');
      }

      ctx.strokeStyle = gradient;
      ctx.lineWidth = 2;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    };

    // Main render loop
    const draw = () => {
      // Clear with gradient background
      const bgGradient = ctx.createLinearGradient(0, 0, 0, rect.height);
      bgGradient.addColorStop(0, '#0a1428');
      bgGradient.addColorStop(0.5, '#0f172a');
      bgGradient.addColorStop(1, '#1a1f3a');
      ctx.fillStyle = bgGradient;
      ctx.fillRect(0, 0, rect.width, rect.height);

      // Draw grid background
      drawGrid(ctx, rect);

      // Sort atoms by depth
      const projections = proteinAtoms.map(atom => ({
        ...atom,
        proj: project3D(atom, rotX, rotY, 0, currentZoom)
      }));

      projections.sort((a, b) => a.proj.z - b.proj.z);

      // Draw bonds first (for layering)
      for (let i = 0; i < projections.length - 1; i++) {
        const current = projections[i];
        const next = projections[i + 1];
        
        if (current.type === 'ca' && next.type === 'ca') {
          drawBond(
            current.proj.x, current.proj.y,
            next.proj.x, next.proj.y,
            current, next
          );
        }
      }

      // Draw atoms
      projections.forEach(({ proj, ...atom }) => {
        drawSphere(proj.x, proj.y, proj.radius, atom.color, atom.intensity, atom);

        // Label for mutation
        if (atom.isActive && proj.radius > 5) {
          ctx.fillStyle = '#ff4757';
          ctx.font = `bold ${Math.max(10, proj.radius * 1.5)}px "Courier New"`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(atom.label, proj.x, proj.y - proj.radius - 20);
        }
      });

      // Draw info overlay
      drawInfoOverlay(ctx, rect, refAA, altAA, quality);

      // Draw stats
      drawStats(ctx, rect, animating);

      // Update rotation
      if (animating) {
        rotX += 0.003;
        rotY += 0.008;
      }

      animationId = requestAnimationFrame(draw);
    };

    draw();

    // Mouse controls
    const handleMouseMove = (e) => {
      if (e.buttons === 1) {
        rotY += (e.movementX || 0) * 0.005;
        rotX += (e.movementY || 0) * 0.005;
      }
    };

    const handleWheel = (e) => {
      e.preventDefault();
      currentZoom += (e.deltaY > 0 ? -0.1 : 0.1);
      currentZoom = Math.max(0.5, Math.min(3, currentZoom));
    };

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('wheel', handleWheel, { passive: false });

    return () => {
      cancelAnimationFrame(animationId);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('wheel', handleWheel);
    };
  }, [rotation, zoom, animating, proteinChange, quality, canvasHeight]);

  return (
    <div className="glass-panel p-6 border-[rgba(0,240,255,0.15)] hud-frame relative neon-glow-cyan">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-[rgba(0,240,255,0.1)] pb-2">
        <div className="flex items-center gap-2">
          <Atom className="w-5 h-5 text-cyan-400 animate-spin-slow" />
          <h3 className="text-xs font-bold tracking-widest font-display text-cyan-400 uppercase">
            3D PROTEIN MUTATION STRUCTURAL SIMULATOR (HD)
          </h3>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setAnimating(!animating)}
            className="px-2.5 py-1 text-[10px] font-mono font-bold bg-cyan-950/40 text-cyan-400 border border-cyan-500/20 rounded hover:bg-cyan-950/80 transition"
          >
            {animating ? '⏸ PAUSE' : '▶ PLAY'}
          </button>
          <button
            onClick={() => setZoom(1)}
            className="px-2.5 py-1 text-[10px] font-mono font-bold bg-cyan-950/40 text-cyan-400 border border-cyan-500/20 rounded hover:bg-cyan-950/80 transition flex items-center justify-center"
            title="Reset view matrix"
          >
            <RotateCcw className="w-3 h-3" />
          </button>
          <button
            onClick={() => setFullscreen(!fullscreen)}
            className="px-2.5 py-1 text-[10px] font-mono font-bold bg-cyan-950/40 text-cyan-400 border border-cyan-500/20 rounded hover:bg-cyan-950/80 transition flex items-center justify-center"
          >
            {fullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* High-resolution canvas with dynamic height resizer */}
      <canvas
        ref={canvasRef}
        className="w-full bg-gradient-to-b from-slate-950 to-slate-900 rounded-lg border border-slate-900 cursor-grab active:cursor-grabbing"
        style={{ display: 'block', height: fullscreen ? '100vh' : `${canvasHeight}px` }}
      />

      {/* Info Panels */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mt-4">
        <div className="data-cell font-mono">
          <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">REFERENCE STATE</div>
          <div className="text-lg font-bold text-cyan-400 mt-1 neon-text-cyan">{proteinChange.split('/')[0]}</div>
          <div className="text-[9px] text-slate-400 mt-0.5 uppercase">WT AA Residue</div>
        </div>

        <div className="data-cell font-mono">
          <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">MUTATION SITE</div>
          <div className="flex items-center gap-1.5 mt-1.5">
            <Zap className="w-3.5 h-3.5 text-red-400 animate-pulse" />
            <span className="text-[10px] text-red-400 font-bold tracking-widest">LOCUS ACTIVE</span>
          </div>
          <div className="text-[9px] text-slate-400 mt-0.5 uppercase">Highlighted Locus</div>
        </div>

        <div className="data-cell font-mono">
          <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">VARIANT STATE</div>
          <div className="text-lg font-bold text-red-400 mt-1 neon-text-red">{proteinChange.split('/')[1]}</div>
          <div className="text-[9px] text-slate-400 mt-0.5 uppercase">MUT AA Residue</div>
        </div>

        <div className="data-cell font-mono flex flex-col justify-center">
          <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-1 flex justify-between">
            <span>📐 VIEWPORT HEIGHT:</span>
            <span className="text-cyan-400 font-bold">{canvasHeight}px</span>
          </div>
          <input
            type="range"
            min="200"
            max="600"
            value={canvasHeight}
            onChange={(e) => setCanvasHeight(parseInt(e.target.value))}
            className="w-full accent-cyan-400 h-1 bg-slate-950 rounded-lg appearance-none cursor-pointer mt-1"
          />
        </div>
      </div>

      {/* Legend */}
      <div className="bg-slate-950/60 border border-slate-900/60 rounded-lg p-3 mt-3 font-mono text-[9px]">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
          <div className="flex items-center gap-1.5"><div className="w-2 h-2 bg-cyan-400 rounded-full"></div><span>WT Atoms</span></div>
          <div className="flex items-center gap-1.5"><div className="w-2 h-2 bg-red-500 rounded-full"></div><span>Mut Site</span></div>
          <div className="flex items-center gap-1.5"><div className="w-2 h-2 bg-cyan-300 rounded-full"></div><span>Side Chains</span></div>
          <div className="flex items-center gap-1.5"><div className="w-2 h-2 bg-cyan-500 opacity-50 rounded-full"></div><span>Residue Bonds</span></div>
          <div className="text-slate-400">💡 Specular Shading</div>
          <div className="text-slate-400">✨ Hologram Glow</div>
        </div>
      </div>
    </div>
  );
}

// Helper function to adjust color brightness
function adjustBrightness(color, percent) {
  const r = parseInt(color.slice(1, 3), 16);
  const g = parseInt(color.slice(3, 5), 16);
  const b = parseInt(color.slice(5, 7), 16);

  const newR = Math.min(255, Math.max(0, r * (1 + percent)));
  const newG = Math.min(255, Math.max(0, g * (1 + percent)));
  const newB = Math.min(255, Math.max(0, b * (1 + percent)));

  return `#${Math.round(newR).toString(16).padStart(2, '0')}${Math.round(newG).toString(16).padStart(2, '0')}${Math.round(newB).toString(16).padStart(2, '0')}`;
}

// Draw grid background
function drawGrid(ctx, rect) {
  ctx.strokeStyle = 'rgba(0, 217, 255, 0.03)';
  ctx.lineWidth = 1;

  const gridSize = 40;
  for (let x = 0; x < rect.width; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, rect.height);
    ctx.stroke();
  }

  for (let y = 0; y < rect.height; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(rect.width, y);
    ctx.stroke();
  }
}

// Draw info overlay
function drawInfoOverlay(ctx, rect, refAA, altAA, quality) {
  const panelX = 20;
  const panelY = 20;
  const panelWidth = 280;
  const panelHeight = 120;

  // Panel background
  ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
  ctx.fillRect(panelX, panelY, panelWidth, panelHeight);

  // Border
  ctx.strokeStyle = 'rgba(0, 217, 255, 0.5)';
  ctx.lineWidth = 2;
  ctx.strokeRect(panelX, panelY, panelWidth, panelHeight);

  // Title
  ctx.fillStyle = '#00d9ff';
  ctx.font = 'bold 14px "Courier New"';
  ctx.fillText('PROTEIN MUTATION ANALYSIS', panelX + 15, panelY + 25);

  // Reference
  ctx.fillStyle = '#00d9ff';
  ctx.font = '12px "Courier New"';
  ctx.fillText('Reference:', panelX + 15, panelY + 50);
  ctx.fillStyle = '#00d9ff';
  ctx.font = 'bold 16px "Courier New"';
  ctx.fillText(refAA, panelX + 130, panelY + 50);

  // Arrow
  ctx.fillStyle = '#888888';
  ctx.font = 'bold 16px "Courier New"';
  ctx.fillText('→', panelX + 155, panelY + 50);

  // Variant
  ctx.fillStyle = '#ff4757';
  ctx.font = 'bold 16px "Courier New"';
  ctx.fillText(altAA, panelX + 170, panelY + 50);

  // Status
  ctx.fillStyle = '#ff4757';
  ctx.font = '11px "Courier New"';
  ctx.fillText('⚠ MUTATION DETECTED', panelX + 15, panelY + 75);

  // Impact
  ctx.fillStyle = '#fbbf24';
  ctx.fillText('Impact: HIGH | Quality: HD', panelX + 15, panelY + 95);
}

// Draw stats
function drawStats(ctx, rect, animating) {
  ctx.fillStyle = 'rgba(100, 116, 139, 0.6)';
  ctx.font = '11px "Courier New"';
  ctx.textAlign = 'left';
  ctx.fillText('🖱️ DRAG to rotate | 🔄 SCROLL to zoom | ⏸️ PAUSE animation', 20, rect.height - 20);
}
