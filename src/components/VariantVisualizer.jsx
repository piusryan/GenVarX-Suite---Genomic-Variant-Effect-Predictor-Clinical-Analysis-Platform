import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Dna } from 'lucide-react';

export default function VariantVisualizer({ variant, vepResult }) {
  const [expanded, setExpanded] = useState(true);
  const [context, setContext] = useState(10); // Default size: 10 bases on each side

  console.log('VariantVisualizer received:', { variant, vepResult });

  if (!vepResult) {
    console.warn('VariantVisualizer: vepResult is null/undefined');
    return null;
  }

  // Parse variant string: "17:43044295:G:A"
  const [chr, pos, refAllele, altAllele] = variant.split(':');

  // Create reference strand (simulated, seeded for stability)
  const refStrand = React.useMemo(() => generateDNAContext(parseInt(pos), refAllele, context), [pos, refAllele, context]);
  const altStrand = React.useMemo(() => generateDNAContext(parseInt(pos), altAllele, context), [pos, altAllele, context]);

  // Protein change info
  const proteinChange = vepResult.amino_acid_change || 'N/A';
  const [refAA, altAA] = parseProteinChange(proteinChange);

  return (
    <div className="glass-panel p-6 border-[rgba(148,163,184,0.15)] hud-frame relative">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between mb-4 text-xs font-bold tracking-widest text-slate-300 font-display hover:text-slate-200 transition"
      >
        <span className="flex items-center gap-2 uppercase">
          <Dna className="w-4 h-4 text-slate-400" />
          DNA Sequence Map — Mutation Locus
        </span>
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {expanded && (
        <div className="space-y-6 animate-data-reveal">
          {/* Resizer Slider for DNA Context */}
          <div className="data-cell flex flex-col sm:flex-row sm:items-center justify-between gap-4 font-mono text-[11px] text-slate-400">
            <span className="font-bold uppercase tracking-widest">
              🧬 Visual Locus Range Resizer:
            </span>
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <span className="text-[10px] text-slate-500">Compact</span>
              <input
                type="range"
                min="5"
                max="25"
                value={context}
                onChange={(e) => setContext(parseInt(e.target.value))}
                className="w-full sm:w-48 accent-cyan-400 h-1 bg-slate-950 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-[10px] text-slate-500">Wide</span>
              <span className="px-2 py-0.5 bg-cyan-950/40 text-cyan-400 border border-cyan-500/20 rounded font-bold">
                {context * 2 + 1} bp
              </span>
            </div>
          </div>

          {/* Chromosome & Position */}
          <div className="data-cell">
            <div className="grid grid-cols-2 gap-4 text-xs font-mono">
              <div>
                <span className="text-slate-500 uppercase tracking-wider">Locus Chromosome</span>
                <p className="text-slate-200 font-semibold mt-1">Chr {chr}</p>
              </div>
              <div>
                <span className="text-slate-500 uppercase tracking-wider">Position Matrix (GRCh38)</span>
                <p className="text-slate-200 font-semibold mt-1">{pos}</p>
              </div>
            </div>
          </div>

          {/* DNA Strand Visualization */}
          <div className="space-y-5">
            <div>
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 font-mono flex items-center gap-2">
                <span>Reference Double Helix (GRCh38)</span>
                <span className="text-[9px] normal-case text-slate-600">— base-pairing shown</span>
              </h4>
              <DNAStrand
                bases={refStrand}
                variantPos={context}
                highlight="ref"
              />
            </div>

            <div className="flex justify-center">
              <div className="text-xs text-slate-500 font-mono tracking-widest uppercase">▼ Substitution Point ▼</div>
            </div>

            <div>
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 font-mono flex items-center gap-2">
                <span>Alternate Double Helix (Subject)</span>
                <span className="text-[9px] normal-case text-slate-600">— base-pairing shown</span>
              </h4>
              <DNAStrand
                bases={altStrand}
                variantPos={context}
                highlight="alt"
              />
            </div>
          </div>

          {/* Allele Change */}
          <div className="data-cell">
            <h4 className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-3 font-mono">
              Base Substitution
            </h4>
            <div className="flex items-center justify-center gap-6">
              <div className="text-center font-mono">
                <div className={`text-xl font-bold px-5 py-2 rounded border ${getBaseStyle(refAllele)}`}>
                  {refAllele}
                </div>
                <p className="text-[9px] text-slate-500 uppercase tracking-widest mt-1.5">Reference Base</p>
              </div>
              <div className="text-lg text-slate-600 font-bold font-mono">▶</div>
              <div className="text-center font-mono">
                <div className={`text-xl font-bold px-5 py-2 rounded border ${getBaseStyle(altAllele)}`}>
                  {altAllele}
                </div>
                <p className="text-[9px] text-slate-500 uppercase tracking-widest mt-1.5">Variant Base</p>
              </div>
            </div>
          </div>

          {/* Protein Impact */}
          {refAA && altAA && (
            <div className="data-cell">
              <h4 className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-3 font-mono">
                Polypeptide Residue Impact
              </h4>
              <div className="flex items-center justify-center gap-6">
                <div className="text-center font-mono">
                  <div className="text-lg font-bold text-emerald-400 bg-emerald-950/40 px-5 py-2 rounded border border-emerald-500/20 neon-text-green">
                    {refAA}
                  </div>
                  <p className="text-[9px] text-slate-500 uppercase tracking-widest mt-1.5">Reference Residue</p>
                </div>
                <div className="text-lg text-slate-600 font-bold font-mono">▶</div>
                <div className="text-center font-mono">
                  <div className="text-lg font-bold text-orange-400 bg-amber-950/40 px-5 py-2 rounded border border-amber-500/20">
                    {altAA}
                  </div>
                  <p className="text-[9px] text-slate-500 uppercase tracking-widest mt-1.5">Mutant Residue</p>
                </div>
              </div>
            </div>
          )}

          {/* Impact Assessment */}
          <ImpactAssessment
            refAllele={refAllele}
            altAllele={altAllele}
            refAA={refAA}
            altAA={altAA}
            consequence={vepResult.consequence}
            sift={vepResult.sift_prediction}
            polyphen={vepResult.polyphen_prediction}
          />

          {/* Legend */}
          <div className="bg-slate-950/60 border border-slate-900/60 rounded-lg p-3 font-mono text-[9px]">
            <p className="text-slate-500 font-bold uppercase tracking-widest mb-2">Base Colour Legend:</p>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span>
                <span className="text-slate-400">Adenine (A)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-sm bg-red-500"></span>
                <span className="text-slate-400">Thymine (T)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-sm bg-amber-400"></span>
                <span className="text-slate-400">Guanine (G)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-sm bg-blue-500"></span>
                <span className="text-slate-400">Cytosine (C)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-sm border border-yellow-400"></span>
                <span className="text-slate-400">Variant Position</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * DNA Strand Display Component
 * Renders a double-stranded segment with base-specific colours and pairing lines.
 */
function DNAStrand({ bases, variantPos, highlight }) {
  return (
    <div className="bg-slate-950 border border-slate-800/50 rounded-lg p-4 overflow-x-auto">
      <div className="flex flex-col items-center min-w-max">
        {/* 5' / 3' direction labels */}
        <div className="flex justify-between w-full text-[10px] text-slate-500 font-mono mb-1 px-1">
          <span>5′</span>
          <span>3′</span>
        </div>

        {/* Top strand */}
        <div className="flex gap-1 font-mono text-sm justify-center">
          {bases.map((base, idx) => {
            const isVariant = idx === variantPos;
            const style = getBaseStyle(base, isVariant);
            return (
              <div
                key={`top-${idx}`}
                className={`w-8 h-8 flex items-center justify-center rounded font-bold ${style} transition`}
                title={`Position ${idx}, Base: ${base}`}
              >
                {base}
              </div>
            );
          })}
        </div>

        {/* Hydrogen bond rungs */}
        <div className="flex gap-1 justify-center py-1">
          {bases.map((base, idx) => {
            const isVariant = idx === variantPos;
            const complement = getComplement(base);
            const bonds = (base === 'A' || base === 'T') ? 2 : 3;
            return (
              <div
                key={`bond-${idx}`}
                className={`w-8 flex flex-col items-center justify-center ${isVariant ? 'text-yellow-400' : 'text-slate-600'}`}
              >
                <div className="flex flex-col gap-[2px] items-center">
                  {Array.from({ length: bonds }).map((_, b) => (
                    <div key={b} className="w-4 h-[1px] bg-current"></div>
                  ))}
                </div>
                <span className="text-[9px] font-bold mt-0.5">{complement}</span>
              </div>
            );
          })}
        </div>

        {/* Bottom strand (complementary) */}
        <div className="flex gap-1 font-mono text-sm justify-center">
          {bases.map((base, idx) => {
            const isVariant = idx === variantPos;
            const complement = getComplement(base);
            const style = getBaseStyle(complement, isVariant);
            return (
              <div
                key={`bottom-${idx}`}
                className={`w-8 h-8 flex items-center justify-center rounded font-bold ${style} transition`}
                title={`Complement: ${complement}`}
              >
                {complement}
              </div>
            );
          })}
        </div>

        <div className="flex justify-between w-full text-[10px] text-slate-500 font-mono mt-1 px-1">
          <span>3′</span>
          <span>5′</span>
        </div>
      </div>

      <div className="text-xs text-slate-500 text-center mt-2">
        Variant position highlighted with a yellow ring. A-T pairs have 2 hydrogen bonds; G-C pairs have 3.
      </div>
    </div>
  );
}

/**
 * Return Tailwind classes for a base tile.
 * When isVariant is true, a yellow ring is added instead of recolouring the tile.
 */
function getBaseStyle(base, isVariant = false) {
  const ring = isVariant ? 'ring-2 ring-yellow-400 ring-offset-1 ring-offset-slate-950' : '';
  switch (base) {
    case 'A':
      return `bg-emerald-950/60 text-emerald-300 border border-emerald-500/30 ${ring}`;
    case 'T':
      return `bg-red-950/60 text-red-300 border border-red-500/30 ${ring}`;
    case 'G':
      return `bg-amber-950/60 text-amber-300 border border-amber-500/30 ${ring}`;
    case 'C':
      return `bg-blue-950/60 text-blue-300 border border-blue-500/30 ${ring}`;
    default:
      return `bg-slate-700 text-slate-300 border border-slate-600 ${ring}`;
  }
}

/**
 * Return the Watson-Crick complement of a DNA base.
 */
function getComplement(base) {
  switch (base) {
    case 'A': return 'T';
    case 'T': return 'A';
    case 'G': return 'C';
    case 'C': return 'G';
    default: return 'N';
  }
}

/**
 * Impact Assessment Box
 */
function ImpactAssessment({ refAllele, altAllele, refAA, altAA, consequence, sift, polyphen }) {
  // Determine conservation impact
  const isConservative = refAllele && altAllele && isSimilarNucleotide(refAllele, altAllele);
  const proteinChangeSeverity = refAA && altAA ? assessProteinChange(refAA, altAA) : 'unknown';

  return (
    <div className="bg-slate-950/60 border border-slate-800/50 rounded-xl p-4">
      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
        Impact Assessment
      </h4>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between items-center">
          <span className="text-slate-400">Nucleotide Change:</span>
          <span className={`font-semibold ${isConservative ? 'text-emerald-400' : 'text-red-400'}`}>
            {isConservative ? 'Conservative' : 'Non-Conservative'}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-400">Consequence:</span>
          <span className="font-semibold text-slate-300">{consequence || 'N/A'}</span>
        </div>
        {refAA && altAA && (
          <div className="flex justify-between items-center">
            <span className="text-slate-400">Protein Change:</span>
            <span className={`font-semibold ${getProteinSeverityColor(proteinChangeSeverity)}`}>
              {proteinChangeSeverity.toUpperCase()}
            </span>
          </div>
        )}
        <div className="flex justify-between items-center">
          <span className="text-slate-400">SIFT Prediction:</span>
          <span className="font-semibold text-slate-300">{sift || 'N/A'}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-400">PolyPhen Prediction:</span>
          <span className="font-semibold text-slate-300">{polyphen || 'N/A'}</span>
        </div>
      </div>
    </div>
  );
}

// Helper Functions

/**
 * Generate simulated DNA context around variant position
 */
function generateDNAContext(pos, allele, context) {
  const bases = ['A', 'T', 'G', 'C'];
  const strand = [];

  // Seeded pseudo-random generator
  const getBase = (seed) => {
    const x = Math.sin(seed) * 10000;
    const r = x - Math.floor(x);
    return bases[Math.floor(r * 4)];
  };

  // Add context before (stable order)
  for (let i = context; i > 0; i--) {
    strand.push(getBase(pos - i));
  }

  // Add the mutation allele
  strand.push(allele);

  // Add context after (stable order)
  for (let i = 1; i <= context; i++) {
    strand.push(getBase(pos + i));
  }

  return strand;
}

/**
 * Parse protein change notation (e.g., "D/V" or "Asp/Val")
 */
function parseProteinChange(notation) {
  if (!notation || notation === 'N/A') return [null, null];

  // Handle single letter format: "D/V"
  if (notation.length <= 3 && notation.includes('/')) {
    const [ref, alt] = notation.split('/');
    return [ref.trim(), alt.trim()];
  }

  // Handle full name format: "Asp/Val"
  const parts = notation.split('/');
  if (parts.length === 2) {
    return [parts[0].trim(), parts[1].trim()];
  }

  return [null, null];
}

/**
 * Check if nucleotide change is conservative
 */
function isSimilarNucleotide(ref, alt) {
  // Purines: A, G
  // Pyrimidines: C, T
  const purines = ['A', 'G'];
  const pyrimidines = ['C', 'T'];

  const refIsPurine = purines.includes(ref);
  const altIsPurine = purines.includes(alt);

  return refIsPurine === altIsPurine;
}

/**
 * Assess protein change severity
 */
function assessProteinChange(refAA, altAA) {
  if (refAA === altAA) return 'synonymous';

  // Hydrophobic amino acids
  const hydrophobic = ['A', 'V', 'I', 'L', 'M', 'F', 'W', 'P'];
  // Polar amino acids
  const polar = ['S', 'T', 'C', 'Y', 'N', 'Q'];
  // Charged positive
  const positive = ['K', 'R', 'H'];
  // Charged negative
  const negative = ['D', 'E'];

  const refHydrophobic = hydrophobic.includes(refAA);
  const altHydrophobic = hydrophobic.includes(altAA);
  const refPolar = polar.includes(refAA);
  const altPolar = polar.includes(altAA);
  const refPositive = positive.includes(refAA);
  const altPositive = positive.includes(altAA);
  const refNegative = negative.includes(refAA);
  const altNegative = negative.includes(altAA);

  // Same property = conservative
  if (
    (refHydrophobic === altHydrophobic && refHydrophobic) ||
    (refPolar === altPolar && refPolar) ||
    (refPositive === altPositive && refPositive) ||
    (refNegative === altNegative && refNegative)
  ) {
    return 'conservative';
  }

  return 'radical';
}

/**
 * Get color for protein severity
 */
function getProteinSeverityColor(severity) {
  switch (severity) {
    case 'synonymous':
      return 'text-emerald-400';
    case 'conservative':
      return 'text-yellow-400';
    case 'radical':
      return 'text-red-400';
    default:
      return 'text-slate-400';
  }
}
