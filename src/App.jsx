import React, { useState, useEffect } from 'react';
import { annotateVariant, fetchGwasAssociations, searchCompounds, getCompound } from './services/api';
import { Dna, Search, AlertTriangle, Activity, ShieldAlert, Loader2, Database, Pill, Network, Terminal, Shield, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import VariantVisualizer from './components/VariantVisualizer';
import AdvancedProtein3D from './components/AdvancedProtein3D';
import ParticleBackground from './components/ParticleBackground';
import HUDFrame from './components/HUDFrame';

export default function App() {
  const [activeModule, setActiveModule] = useState('variant');
  const [variantInput, setVariantInput] = useState('17:43044295:G:A');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const [gwasInput, setGwasInput] = useState('17:43044295:G:A');
  const [gwasLoading, setGwasLoading] = useState(false);
  const [gwasData, setGwasData] = useState(null);
  const [gwasError, setGwasError] = useState(null);

  const [compoundQuery, setCompoundQuery] = useState('selinexor');
  const [compoundLoading, setCompoundLoading] = useState(false);
  const [compoundResults, setCompoundResults] = useState([]);
  const [compoundError, setCompoundError] = useState(null);
  const [selectedCompoundId, setSelectedCompoundId] = useState(null);
  const [compoundDetail, setCompoundDetail] = useState(null);
  const [compoundDetailLoading, setCompoundDetailLoading] = useState(false);

  // Time clock state
  const [systemTime, setSystemTime] = useState(new Date().toISOString());
  useEffect(() => {
    const timer = setInterval(() => {
      setSystemTime(new Date().toISOString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!variantInput.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const result = await annotateVariant(variantInput.trim());
      setData(result);
    } catch (err) {
      setError(err.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleGwasSearch = async (e) => {
    if (e) e.preventDefault();
    if (!gwasInput.trim()) return;

    setGwasLoading(true);
    setGwasError(null);
    try {
      const result = await fetchGwasAssociations(gwasInput.trim());
      setGwasData(result);
    } catch (err) {
      setGwasError(err.message);
      setGwasData(null);
    } finally {
      setGwasLoading(false);
    }
  };

  const handleCompoundSearch = async (e) => {
    if (e) e.preventDefault();
    setCompoundLoading(true);
    setCompoundError(null);
    setCompoundResults([]);
    setSelectedCompoundId(null);
    setCompoundDetail(null);

    try {
      const res = await searchCompounds(compoundQuery.trim(), 20);
      setCompoundResults(res);
    } catch (err) {
      setCompoundError(err.message);
    } finally {
      setCompoundLoading(false);
    }
  };

  const handleCompoundSelect = async (chemblId) => {
    setSelectedCompoundId(chemblId);
    setCompoundDetail(null);
    setCompoundDetailLoading(true);
    try {
      const res = await getCompound(chemblId);
      setCompoundDetail(res);
    } catch (err) {
      setCompoundError(err.message);
    } finally {
      setCompoundDetailLoading(false);
    }
  };

  const getImpactBadge = (impact) => {
    switch (impact) {
      case 'HIGH':
        return <span className="px-2.5 py-0.5 text-[10px] font-bold tracking-widest rounded bg-red-950/40 text-red-400 border border-red-500/30 neon-text-red">HIGH IMPACT</span>;
      case 'MODERATE':
        return <span className="px-2.5 py-0.5 text-[10px] font-bold tracking-widest rounded bg-amber-950/40 text-amber-400 border border-amber-500/30">MODERATE</span>;
      default:
        return <span className="px-2.5 py-0.5 text-[10px] font-bold tracking-widest rounded bg-emerald-950/40 text-emerald-400 border border-emerald-500/30 neon-text-green">LOW IMPACT</span>;
    }
  };

  const modules = [
    {
      id: 'variant',
      label: 'GENE VARIANT',
      description: 'Effect predictor & ClinVar',
      icon: Activity,
      themeColor: 'cyan',
    },
    {
      id: 'gwas',
      label: 'DISEASE ASSOC',
      description: 'GWAS Catalog explorer',
      icon: Network,
      themeColor: 'green',
    },
    {
      id: 'drugs',
      label: 'DRUG DISCOVERY',
      description: 'ChEMBL database query',
      icon: Pill,
      themeColor: 'purple',
    },
  ];

  const activeModuleMeta = modules.find((m) => m.id === activeModule) || modules[0];

  return (
    <div className="relative min-h-screen z-10 px-4 md:px-8 py-6 max-w-7xl mx-auto flex flex-col gap-6 selection:bg-cyan-500/30 selection:text-white">
      {/* Dynamic Animated Particles Background */}
      <ParticleBackground />

      {/* ─── FUTURISTIC TERMINAL HEADER ─── */}
      <header className="glass-panel p-4 md:p-6 border-[rgba(0,240,255,0.15)] hud-frame relative neon-glow-cyan">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          
          {/* Logo & Subtitle */}
          <div className="flex items-center gap-4">
            <div className="relative p-3 bg-cyan-950/40 rounded-lg border border-cyan-500/30 text-cyan-400 neon-glow-cyan animate-pulse-glow">
              <Dna className="w-8 h-8 animate-spin-slow" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-xl md:text-2xl font-black tracking-widest font-display text-white neon-text-cyan">
                  GENVARX // CORE
                </h1>
                <span className="text-[9px] bg-cyan-950/60 text-cyan-400 border border-cyan-500/30 px-2 py-0.5 rounded font-mono">
                  SYS.V1.0.8
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono tracking-wider mt-1 uppercase">
                GENOMIC PATHOLOGY & PHARMACOGENOMICS COMMAND SHELL
              </p>
            </div>
          </div>

          {/* System Status Readouts */}
          <div className="flex flex-wrap items-center gap-4 font-mono text-[10px] tracking-wider text-slate-400 w-full lg:w-auto justify-start lg:justify-end">
            <div className="px-3 py-1.5 bg-slate-950/60 border border-cyan-500/10 rounded flex items-center gap-2">
              <span className="status-dot status-online" />
              <span className="text-cyan-400 uppercase">FASTAPI NODE: ONLINE</span>
            </div>
            <div className="px-3 py-1.5 bg-slate-950/60 border border-purple-500/10 rounded flex items-center gap-2">
              <Terminal className="w-3.5 h-3.5 text-purple-400" />
              <span>LOGS: INTERACTIVE</span>
            </div>
            <div className="px-3 py-1.5 bg-slate-950/60 border border-slate-800 rounded text-slate-300 font-mono-code font-medium">
              {systemTime}
            </div>
          </div>

        </div>
      </header>

      {/* ─── MAIN HUB LAYOUT ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6 items-start">
        
        {/* Navigation Sidebar Panel */}
        <aside className="lg:sticky lg:top-6 flex flex-col gap-6">
          <HUDFrame title="MODULE SELECTION" variant="cyan" className="neon-glow-cyan">
            <div className="space-y-3">
              {modules.map((m) => {
                const Icon = m.icon;
                const isActive = m.id === activeModule;
                
                return (
                  <button
                    key={m.id}
                    onClick={() => setActiveModule(m.id)}
                    className={`w-full text-left rounded-lg p-3 border transition-all duration-300 relative group overflow-hidden ${
                      isActive
                        ? m.themeColor === 'cyan'
                          ? 'bg-cyan-950/30 border-cyan-500/50 text-cyan-300 shadow-[0_0_15px_rgba(0,240,255,0.05)]'
                          : m.themeColor === 'green'
                            ? 'bg-emerald-950/30 border-emerald-500/50 text-emerald-300 shadow-[0_0_15px_rgba(0,255,136,0.05)]'
                            : 'bg-purple-950/30 border-purple-500/50 text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.05)]'
                        : 'bg-slate-950/40 border-slate-900 text-slate-400 hover:text-slate-200 hover:border-slate-800'
                    }`}
                  >
                    <div className="flex items-center gap-3 relative z-10">
                      <div className={`p-2 rounded border transition-colors ${
                        isActive
                          ? m.themeColor === 'cyan'
                            ? 'bg-cyan-900/30 border-cyan-400/30'
                            : m.themeColor === 'green'
                              ? 'bg-emerald-900/30 border-emerald-400/30'
                              : 'bg-purple-900/30 border-purple-400/30'
                          : 'bg-slate-900/50 border-slate-800'
                      }`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="min-w-0">
                        <div className="text-xs font-bold tracking-widest font-display">{m.label}</div>
                        <div className="text-[10px] text-slate-500 truncate font-mono mt-0.5">{m.description}</div>
                      </div>
                    </div>

                    {/* Futuristic active pointer marker */}
                    {isActive && (
                      <div className={`absolute top-0 right-0 w-1 h-full ${
                        m.themeColor === 'cyan' ? 'bg-cyan-400 shadow-[0_0_8px_#00f0ff]' :
                        m.themeColor === 'green' ? 'bg-emerald-400 shadow-[0_0_8px_#00ff88]' :
                        'bg-purple-400 shadow-[0_0_8px_#a855f7]'
                      }`} />
                    )}
                  </button>
                );
              })}
            </div>
          </HUDFrame>

          <HUDFrame title="SYSTEM FEED" variant="purple">
            <div className="font-mono text-[9px] text-slate-400 space-y-2 leading-relaxed">
              <div className="flex justify-between border-b border-slate-900 pb-1">
                <span>API CLIENT</span>
                <span className="text-cyan-400 font-bold">READY</span>
              </div>
              <div className="flex justify-between border-b border-slate-900 pb-1">
                <span>BUFFER STATUS</span>
                <span className="text-emerald-400 font-bold">NOMINAL</span>
              </div>
              <div className="flex justify-between border-b border-slate-900 pb-1">
                <span>3D SUBSYSTEM</span>
                <span className="text-cyan-400 font-bold font-mono">WEBGL2</span>
              </div>
              <div className="text-[8px] text-slate-500 mt-2 font-mono-code">
                READY FOR GENOMIC ENTRY INPUT. SELECT PRESETS TO TEST PIPELINES.
              </div>
            </div>
          </HUDFrame>
        </aside>

        {/* Content Viewer Area */}
        <main className="flex flex-col gap-6">
          
          {/* Active Module Panel */}
          {activeModule === 'variant' && (
            <div className="flex flex-col gap-6">
              
              {/* Variant input panel */}
              <HUDFrame title="VARIANT SELECTION MATRIX // VEP ENGINE" variant="cyan" className="neon-glow-cyan">
                <form onSubmit={handleSearch} className="space-y-4">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest font-mono">
                    Enter Genomic Coordinate (GRCh38 Reference):
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <div className="relative flex-1">
                      <input
                        type="text"
                        value={variantInput}
                        onChange={(e) => setVariantInput(e.target.value)}
                        placeholder="e.g. 17:43044295:G:A"
                        className="w-full bg-slate-950/70 border border-slate-800 focus:border-cyan-500 rounded-lg py-3 pl-4 pr-12 text-slate-100 placeholder-slate-600 outline-none transition font-mono text-sm tracking-wider"
                      />
                      <Search className="absolute right-4 top-3.5 w-4 h-4 text-slate-600" />
                    </div>
                    <button
                      type="submit"
                      disabled={loading}
                      className="bg-cyan-500 hover:bg-cyan-400 disabled:bg-cyan-900/30 text-slate-950 font-bold px-6 py-3 rounded-lg transition-all duration-300 flex items-center justify-center gap-2 text-xs tracking-widest font-display btn-neon shadow-[0_0_15px_rgba(0,240,255,0.2)]"
                    >
                      {loading ? (
                        <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                      ) : (
                        <Activity className="w-4 h-4 text-slate-950" />
                      )}
                      ANALYZE SEQUENCE
                    </button>
                  </div>
                </form>

                {/* Preset hotkeys */}
                <div className="flex flex-wrap items-center gap-2 mt-4 text-[10px] font-mono text-slate-500">
                  <span className="uppercase tracking-widest">Presets:</span>
                  <button
                    type="button"
                    onClick={() => { setVariantInput('17:43044295:G:A'); }}
                    className="hover:text-cyan-400 transition font-mono hover:underline uppercase bg-slate-950/40 border border-slate-850 px-2 py-0.5 rounded"
                  >
                    BRCA1 (Breast cancer)
                  </button>
                  <button
                    type="button"
                    onClick={() => { setVariantInput('13:32316462:G:A'); }}
                    className="hover:text-cyan-400 transition font-mono hover:underline uppercase bg-slate-950/40 border border-slate-850 px-2 py-0.5 rounded"
                  >
                    BRCA2 (Ovarian cancer)
                  </button>
                  <button
                    type="button"
                    onClick={() => { setVariantInput('17:7673802:C:T'); }}
                    className="hover:text-cyan-400 transition font-mono hover:underline uppercase bg-slate-950/40 border border-slate-850 px-2 py-0.5 rounded"
                  >
                    TP53 (Tumor Suppressor)
                  </button>
                </div>
              </HUDFrame>

              {/* Error messages */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-start gap-3 p-4 bg-red-950/30 border border-red-500/30 text-red-400 rounded-lg text-xs font-mono"
                  >
                    <AlertTriangle className="w-5 h-5 shrink-0 text-red-400" />
                    <div>
                      <div className="font-bold tracking-widest uppercase mb-1">SYSTEM EXCEPTION DETECTED</div>
                      <div>{error}</div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Analytical Results */}
              {data && (
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  {/* Summary Card */}
                  <HUDFrame variant="cyan" className="neon-glow-cyan">
                    <div className="flex flex-col md:flex-row justify-between gap-6">
                      <div className="space-y-3">
                        <div className="flex flex-wrap items-center gap-3">
                          <span className="text-lg md:text-xl font-mono font-bold tracking-wider text-slate-100 neon-text-cyan">
                            {data.variant}
                          </span>
                          {getImpactBadge(data.impact_level)}
                          {data.rs_id && (
                            <span className="px-2.5 py-0.5 text-[10px] font-bold rounded bg-slate-950/50 text-slate-300 border border-slate-800 font-mono">
                              {data.rs_id}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                          <Database className="w-4 h-4 text-cyan-400" />
                          <span>Gene Node: <strong className="text-cyan-400 font-semibold">{data.gene_symbol}</strong></span>
                        </div>
                      </div>
                      <div className="md:text-right border-t md:border-t-0 border-slate-900 pt-4 md:pt-0">
                        <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-1 font-mono">Consequence Type</span>
                        <span className="text-md font-bold text-cyan-400 font-display capitalize tracking-wide">
                          {data.consequence.replace(/_/g, ' ')}
                        </span>
                      </div>
                    </div>
                  </HUDFrame>

                  {/* 2D Canvas DNA visualizer */}
                  <VariantVisualizer variant={variantInput} vepResult={data} />
                  
                  {/* 3D Canvas Protein Visualizer */}
                  <AdvancedProtein3D 
                    variant={variantInput} 
                    vepResult={data}
                    proteinChange={data.amino_acid_change || 'N/A/N/A'}
                  />

                  {/* Functional Indicators Columns */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <HUDFrame title="FUNCTIONAL PREDICTIONS" variant="cyan">
                      <div className="space-y-3">
                        <div className="data-cell flex justify-between items-center">
                          <span className="text-xs text-slate-400 font-mono">SIFT PREDICTION</span>
                          <span className="text-xs font-mono font-bold text-slate-200 uppercase">{data.sift_prediction || 'N/A'}</span>
                        </div>
                        <div className="data-cell flex justify-between items-center">
                          <span className="text-xs text-slate-400 font-mono">POLYPHEN PREDICTION</span>
                          <span className="text-xs font-mono font-bold text-slate-200 uppercase">{data.polyphen_prediction || 'N/A'}</span>
                        </div>
                        <div className="data-cell flex justify-between items-center">
                          <span className="text-xs text-slate-400 font-mono">AMINO ACID SHIFT</span>
                          <span className="text-xs font-mono font-bold text-cyan-400">{data.amino_acid_change || 'N/A'}</span>
                        </div>
                      </div>
                    </HUDFrame>

                    <HUDFrame title="CLINVAR PHENOTYPIC MAP" variant="purple">
                      <div className="space-y-3">
                        <div className="data-cell">
                          <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-1 font-mono">CLINICAL SIGNIFICANCE</span>
                          <span className="text-xs font-mono font-medium text-slate-200">{data.clinical_significance || 'UNKNOWN'}</span>
                        </div>
                        <div className="data-cell">
                          <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-2 font-mono">ASSOCIATED PHENOTYPES</span>
                          {data.associated_diseases && data.associated_diseases.length > 0 ? (
                            <div className="flex flex-wrap gap-1.5">
                              {data.associated_diseases.map((dis, idx) => (
                                <span key={idx} className="text-[10px] font-mono bg-slate-950/60 text-slate-300 px-2 py-0.5 rounded border border-slate-800">
                                  {dis}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <span className="text-xs font-mono text-slate-500">NO MAPPED CONDITIONS FOUND</span>
                          )}
                        </div>
                      </div>
                    </HUDFrame>
                  </div>

                </motion.div>
              )}

            </div>
          )}

          {activeModule === 'gwas' && (
            <div className="flex flex-col gap-6">
              
              {/* GWAS catalog explorer */}
              <HUDFrame title="GWAS SYSTEM INTERACTION" variant="green" className="neon-glow-green">
                <form onSubmit={handleGwasSearch} className="space-y-4">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest font-mono">
                    Query Variant Coordinates to check GWAS Trait Associations:
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <div className="relative flex-1">
                      <input
                        type="text"
                        value={gwasInput}
                        onChange={(e) => setGwasInput(e.target.value)}
                        placeholder="e.g. 17:43044295:G:A"
                        className="w-full bg-slate-950/70 border border-slate-800 focus:border-emerald-500 rounded-lg py-3 pl-4 pr-12 text-slate-100 placeholder-slate-600 outline-none transition font-mono text-sm tracking-wider"
                      />
                      <Search className="absolute right-4 top-3.5 w-4 h-4 text-slate-600" />
                    </div>
                    <button
                      type="submit"
                      disabled={gwasLoading}
                      className="bg-emerald-500 hover:bg-emerald-400 disabled:bg-emerald-900/30 text-slate-950 font-bold px-6 py-3 rounded-lg transition-all duration-300 flex items-center justify-center gap-2 text-xs tracking-widest font-display btn-neon shadow-[0_0_15px_rgba(0,255,136,0.2)]"
                    >
                      {gwasLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                      ) : (
                        <Network className="w-4 h-4 text-slate-950" />
                      )}
                      FIND ASSOCIATIONS
                    </button>
                  </div>
                </form>
              </HUDFrame>

              {/* GWAS error */}
              <AnimatePresence>
                {gwasError && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-start gap-3 p-4 bg-red-950/30 border border-red-500/30 text-red-400 rounded-lg text-xs font-mono"
                  >
                    <AlertTriangle className="w-5 h-5 shrink-0" />
                    <div>{gwasError}</div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* GWAS associations table */}
              {gwasData && (
                <HUDFrame title="GWAS PHENOTYPIC INDEX" variant="green" className="neon-glow-green">
                  <div className="flex flex-col sm:flex-row justify-between gap-4 mb-6 font-mono text-xs text-slate-400 border-b border-slate-900 pb-3">
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4 text-emerald-400" />
                      <span>RESOLVED RSID: <span className="font-bold text-slate-200">{gwasData.rs_id || 'N/A'}</span></span>
                    </div>
                    {gwasData.note && <span className="text-slate-500">{gwasData.note}</span>}
                  </div>

                  {gwasData.associations && gwasData.associations.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs font-mono">
                        <thead>
                          <tr className="text-[10px] uppercase tracking-wider text-slate-500 border-b border-slate-800">
                            <th className="text-left py-3 pr-3">ASSOCIATED TRAIT / DISEASE</th>
                            <th className="text-left py-3 pr-3">P-VALUE</th>
                            <th className="text-left py-3 pr-3">RISK ALLELE</th>
                            <th className="text-left py-3 pr-3">STUDY ID</th>
                          </tr>
                        </thead>
                        <tbody>
                          {gwasData.associations.slice(0, 20).map((a, idx) => (
                            <tr key={idx} className="border-b border-slate-900/60 hover:bg-slate-900/20 transition-all">
                              <td className="py-3 pr-3 text-slate-200 font-medium">{a.trait}</td>
                              <td className="py-3 pr-3 text-emerald-400 font-mono-code font-bold">{a.pvalue || 'N/A'}</td>
                              <td className="py-3 pr-3 text-slate-300 font-mono">{a.strongest_allele || 'N/A'}</td>
                              <td className="py-3 pr-3 text-slate-400 font-mono">{a.study_accession || a.pubmed_id || 'N/A'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-6 text-slate-500 font-mono text-xs uppercase">
                      NO GENOME-WIDE ASSOCIATIONS RECORDED
                    </div>
                  )}
                </HUDFrame>
              )}

            </div>
          )}

          {activeModule === 'drugs' && (
            <div className="flex flex-col gap-6">
              
              {/* Drug Search */}
              <HUDFrame title="CHEMBL COMPOUND SEARCH" variant="purple" className="neon-glow-purple">
                <form onSubmit={handleCompoundSearch} className="space-y-4">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest font-mono">
                    Search compound database:
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <div className="relative flex-1">
                      <input
                        type="text"
                        value={compoundQuery}
                        onChange={(e) => setCompoundQuery(e.target.value)}
                        placeholder="e.g. selinexor or CHEMBL237500"
                        className="w-full bg-slate-950/70 border border-slate-800 focus:border-purple-500 rounded-lg py-3 pl-4 pr-12 text-slate-100 placeholder-slate-600 outline-none transition font-mono text-sm tracking-wider"
                      />
                      <Search className="absolute right-4 top-3.5 w-4 h-4 text-slate-600" />
                    </div>
                    <button
                      type="submit"
                      disabled={compoundLoading}
                      className="bg-purple-500 hover:bg-purple-400 disabled:bg-purple-900/30 text-slate-950 font-bold px-6 py-3 rounded-lg transition-all duration-300 flex items-center justify-center gap-2 text-xs tracking-widest font-display btn-neon shadow-[0_0_15px_rgba(168,85,247,0.2)]"
                    >
                      {compoundLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                      ) : (
                        <Pill className="w-4 h-4 text-slate-950" />
                      )}
                      QUERY CHEMICALS
                    </button>
                  </div>
                </form>
              </HUDFrame>

              {/* Compound errors */}
              <AnimatePresence>
                {compoundError && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-start gap-3 p-4 bg-red-950/30 border border-red-500/30 text-red-400 rounded-lg text-xs font-mono"
                  >
                    <AlertTriangle className="w-5 h-5 shrink-0" />
                    <div>{compoundError}</div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Multi columns results & details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* List box */}
                <HUDFrame title="COMPOUNDS MATCHED" variant="purple">
                  {compoundResults && compoundResults.length > 0 ? (
                    <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
                      {compoundResults.slice(0, 20).map((c) => (
                        <button
                          key={c.chembl_id}
                          type="button"
                          onClick={() => handleCompoundSelect(c.chembl_id)}
                          className={`w-full text-left p-3 rounded border transition-all duration-200 font-mono text-xs ${
                            selectedCompoundId === c.chembl_id
                              ? 'bg-purple-950/30 border-purple-500 text-purple-300'
                              : 'bg-slate-950/40 border-slate-900 hover:border-slate-800 text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          <div className="flex items-center justify-between gap-3">
                            <span className="font-bold">{c.chembl_id}</span>
                            <span className="text-[10px] text-slate-500">{c.max_phase ? `Phase ${c.max_phase}` : 'Phase N/A'}</span>
                          </div>
                          <div className="text-xs mt-1 uppercase text-slate-300 font-mono-code tracking-wide">{c.name || 'UNNAMED COMPOUND'}</div>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <span className="text-xs font-mono text-slate-500 uppercase">RUN A SEARCH TO POPULATE LIST</span>
                  )}
                </HUDFrame>

                {/* Details box */}
                <HUDFrame title="CHEMICAL SPEC SHEET" variant="purple">
                  {compoundDetailLoading && (
                    <div className="flex items-center gap-2 text-xs font-mono text-slate-400 py-4">
                      <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                      RETRIEVING COMPOUND BIOCHEMICAL READOUTS...
                    </div>
                  )}

                  {!compoundDetailLoading && compoundDetail && (
                    <div className="space-y-4 font-mono text-xs">
                      <div className="data-cell">
                        <div className="flex items-center justify-between gap-3 border-b border-slate-900 pb-1.5 mb-1.5">
                          <span className="font-bold text-purple-400">{compoundDetail.chembl_id}</span>
                          <span className="text-[10px] text-slate-500 uppercase">{compoundDetail.compound_type || 'N/A'}</span>
                        </div>
                        <div className="text-sm font-bold uppercase text-slate-200">{compoundDetail.name || 'UNNAMED COMPOUND'}</div>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="data-cell">
                          <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest font-mono">MOL WEIGHT</div>
                          <div className="text-xs font-bold text-slate-300 mt-1">{compoundDetail.molecular_weight || 'N/A'}</div>
                        </div>
                        <div className="data-cell">
                          <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest font-mono">ALOGP</div>
                          <div className="text-xs font-bold text-slate-300 mt-1">{compoundDetail.alogp || 'N/A'}</div>
                        </div>
                        <div className="data-cell">
                          <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest font-mono">TARGET COUNT</div>
                          <div className="text-xs font-bold text-slate-300 mt-1">{compoundDetail.targets || 'N/A'}</div>
                        </div>
                        <div className="data-cell">
                          <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest font-mono">BIOACTIVITIES</div>
                          <div className="text-xs font-bold text-slate-300 mt-1">{compoundDetail.bioactivities || 'N/A'}</div>
                        </div>
                      </div>

                      {compoundDetail.smiles && (
                        <div className="data-cell">
                          <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest font-mono mb-1.5">SMILES STRUCTURE</div>
                          <div className="text-[10px] text-purple-300 break-all whitespace-pre-wrap font-mono-code leading-normal">{compoundDetail.smiles}</div>
                        </div>
                      )}
                    </div>
                  )}

                  {!compoundDetailLoading && !compoundDetail && (
                    <span className="text-xs font-mono text-slate-500 uppercase">SELECT A COMPOUND TO MOUNT STRUCTURAL DATA</span>
                  )}
                </HUDFrame>

              </div>

            </div>
          )}

        </main>

      </div>
    </div>
  );
}
