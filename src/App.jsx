import React, { useState, useEffect } from 'react';
import { annotateVariant, fetchGwasAssociations, gwasDatasetAnalysis, getDiseaseAssociations, getDatasetsSummary, searchCompounds, getCompound, getDiseasesByRsid, getComprehensiveDisease } from './services/api';
import { Dna, Search, AlertTriangle, Activity, ShieldAlert, Loader2, Database, Pill, Network, Terminal, Shield, RefreshCw, Copy, ExternalLink, CheckCircle2 } from 'lucide-react';
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
  const [datasetAnalysis, setDatasetAnalysis] = useState(null);
  const [diseaseAssoc, setDiseaseAssoc] = useState(null);
  
  // RSID lookup state
  const [selectedRsid, setSelectedRsid] = useState(null);
  const [rsidDiseases, setRsidDiseases] = useState(null);
  const [rsidLoading, setRsidLoading] = useState(false);
  const [rsidError, setRsidError] = useState(null);
  
  // RSID Search Module State
  const [rsidSearchInput, setRsidSearchInput] = useState('rs6414541');
  const [rsidSearchLoading, setRsidSearchLoading] = useState(false);
  const [rsidSearchResults, setRsidSearchResults] = useState(null);
  const [rsidSearchError, setRsidSearchError] = useState(null);

  // Comprehensive disease lookup (multi-API aggregator)
  const [comprehensiveDisease, setComprehensiveDisease] = useState(null);
  const [compLoading, setCompLoading] = useState(false);
  const [compError, setCompError] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);

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

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const handleComprehensiveDisease = async () => {
    const input = gwasInput.trim();
    if (!input) return;
    setCompLoading(true);
    setCompError(null);
    try {
      const result = await getComprehensiveDisease(input);
      setComprehensiveDisease(result);
    } catch (err) {
      setCompError(err.message);
      setComprehensiveDisease(null);
    } finally {
      setCompLoading(false);
    }
  };

  const handleGwasSearch = async (e) => {
    if (e) e.preventDefault();
    if (!gwasInput.trim()) return;

    setGwasLoading(true);
    setGwasError(null);
    setComprehensiveDisease(null);
    setCompError(null);
    try {
      const [annotationResult, diseaseResult] = await Promise.all([
        annotateVariant(gwasInput.trim()),
        getComprehensiveDisease(gwasInput.trim())
      ]);
      setGwasData(annotationResult);
      setComprehensiveDisease(diseaseResult);
    } catch (err) {
      setGwasError(err.message);
      setGwasData(null);
      setComprehensiveDisease(null);
    } finally {
      setGwasLoading(false);
    }
  };

  const handleRsidLookup = async (rsid) => {
    setSelectedRsid(rsid);
    setRsidLoading(true);
    setRsidError(null);
    try {
      const result = await getDiseasesByRsid(rsid);
      setRsidDiseases(result);
    } catch (err) {
      setRsidError(err.message);
      setRsidDiseases(null);
    } finally {
      setRsidLoading(false);
    }
  };

  const handleRsidModuleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!rsidSearchInput.trim()) return;

    setRsidSearchLoading(true);
    setRsidSearchError(null);
    try {
      const result = await getDiseasesByRsid(rsidSearchInput.trim());
      setRsidSearchResults(result);
    } catch (err) {
      setRsidSearchError(err.message);
      setRsidSearchResults(null);
    } finally {
      setRsidSearchLoading(false);
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

                {/* Preset hotkeys - EXPANDED with tested working variants */}
                <div className="space-y-3 mt-4">
                  <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest font-bold">Preset Variants (All Tested):</div>
                  
                  {/* Cancer - Somatic Driver Mutations */}
                  <div className="space-y-2">
                    <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider ml-1">🔴 Cancer (Somatic Drivers)</div>
                    <div className="flex flex-wrap gap-2">
                      <button type="button" onClick={() => { setVariantInput('7:140753336:A:T'); }} className="hover:text-cyan-400 transition font-mono hover:underline uppercase text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">BRAF V600E (Melanoma)</button>
                      <button type="button" onClick={() => { setVariantInput('17:7673802:C:T'); }} className="hover:text-cyan-400 transition font-mono hover:underline uppercase text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">TP53 R248W (Li-Fraumeni)</button>
                      <button type="button" onClick={() => { setVariantInput('12:25227344:G:T'); }} className="hover:text-cyan-400 transition font-mono hover:underline uppercase text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">KRAS G12D (Pancreas)</button>
                      <button type="button" onClick={() => { setVariantInput('5:112839461:T:A'); }} className="hover:text-cyan-400 transition font-mono hover:underline uppercase text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">APC (Colon/FAP)</button>
                    </div>
                  </div>

                  {/* Hematologic / Blood Disorders */}
                  <div className="space-y-2">
                    <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider ml-1">🟠 Hematologic / Blood</div>
                    <div className="flex flex-wrap gap-2">
                      <button type="button" onClick={() => { setVariantInput('9:5073770:G:T'); }} className="hover:text-cyan-400 transition font-mono hover:underline uppercase text-[9px] bg-amber-950/40 border border-amber-500/20 px-2 py-1 rounded hover:border-amber-500/40">JAK2 V617F (MPN/PV)</button>
                      <button type="button" onClick={() => { setVariantInput('11:5248232:T:A'); }} className="hover:text-cyan-400 transition font-mono hover:underline uppercase text-[9px] bg-amber-950/40 border border-amber-500/20 px-2 py-1 rounded hover:border-amber-500/40">HBB (Sickle Cell)</button>
                    </div>
                  </div>

                  {/* Hereditary Cancer Risk */}
                  <div className="space-y-2">
                    <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider ml-1">🟡 Hereditary Cancer Risk</div>
                    <div className="flex flex-wrap gap-2">
                      <button type="button" onClick={() => { setVariantInput('17:43124016:CT:C'); }} className="hover:text-cyan-400 transition font-mono hover:underline uppercase text-[9px] bg-yellow-950/40 border border-yellow-500/20 px-2 py-1 rounded hover:border-yellow-500/40">BRCA1 185delAG</button>
                      <button type="button" onClick={() => { setVariantInput('13:32340392:GT:G'); }} className="hover:text-cyan-400 transition font-mono hover:underline uppercase text-[9px] bg-yellow-950/40 border border-yellow-500/20 px-2 py-1 rounded hover:border-yellow-500/40">BRCA2 6174delT</button>
                      <button type="button" onClick={() => { setVariantInput('17:31259014:G:A'); }} className="hover:text-cyan-400 transition font-mono hover:underline uppercase text-[9px] bg-yellow-950/40 border border-yellow-500/20 px-2 py-1 rounded hover:border-yellow-500/40">NF1 (Neurofibromatosis)</button>
                    </div>
                  </div>

                  {/* Other Pathogenic */}
                  <div className="space-y-2">
                    <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider ml-1">🔵 Other Pathogenic</div>
                    <div className="flex flex-wrap gap-2">
                      <button type="button" onClick={() => { setVariantInput('7:117559590:ATCT:A'); }} className="hover:text-cyan-400 transition font-mono hover:underline uppercase text-[9px] bg-blue-950/40 border border-blue-500/20 px-2 py-1 rounded hover:border-blue-500/40">CFTR F508del (Cystic Fibrosis)</button>
                      <button type="button" onClick={() => { setVariantInput('10:87952116:G:A'); }} className="hover:text-cyan-400 transition font-mono hover:underline uppercase text-[9px] bg-blue-950/40 border border-blue-500/20 px-2 py-1 rounded hover:border-blue-500/40">PTEN (Cowden Syndrome)</button>
                    </div>
                  </div>
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

                {/* GWAS Preset variants - ALL tested, local datasets scan all */}
                <div className="space-y-3 mt-4">
                  <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest font-bold">Test Presets (All Scanned Against 6 Local Datasets + External APIs):</div>
                  
                  <div className="space-y-2">
                    <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider ml-1">🔴 Best Results (Multi-Source Hits)</div>
                    <div className="flex flex-wrap gap-2">
                      <button type="button" onClick={() => { setGwasInput('9:5073770:G:T'); }} className="hover:text-emerald-400 transition font-mono hover:underline uppercase text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">JAK2 V617F (MPN) ★ 90+ hits</button>
                      <button type="button" onClick={() => { setGwasInput('17:7673802:C:T'); }} className="hover:text-emerald-400 transition font-mono hover:underline uppercase text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">TP53 R248W (Li-Fraumeni)</button>
                      <button type="button" onClick={() => { setGwasInput('7:140753336:A:T'); }} className="hover:text-emerald-400 transition font-mono hover:underline uppercase text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">BRAF V600E (Melanoma)</button>
                      <button type="button" onClick={() => { setGwasInput('5:112839461:T:A'); }} className="hover:text-emerald-400 transition font-mono hover:underline uppercase text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">APC (Colon/FAP)</button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider ml-1">🟠 Cancer / Hematologic</div>
                    <div className="flex flex-wrap gap-2">
                      <button type="button" onClick={() => { setGwasInput('12:25227344:G:T'); }} className="hover:text-emerald-400 transition font-mono hover:underline uppercase text-[9px] bg-amber-950/40 border border-amber-500/20 px-2 py-1 rounded hover:border-amber-500/40">KRAS G12D (Pancreas)</button>
                      <button type="button" onClick={() => { setGwasInput('11:5248232:T:A'); }} className="hover:text-emerald-400 transition font-mono hover:underline uppercase text-[9px] bg-amber-950/40 border border-amber-500/20 px-2 py-1 rounded hover:border-amber-500/40">HBB (Sickle Cell)</button>
                      <button type="button" onClick={() => { setGwasInput('17:31259014:G:A'); }} className="hover:text-emerald-400 transition font-mono hover:underline uppercase text-[9px] bg-amber-950/40 border border-amber-500/20 px-2 py-1 rounded hover:border-amber-500/40">NF1 (Neurofibromatosis)</button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider ml-1">🟡 Hereditary / Pathogenic</div>
                    <div className="flex flex-wrap gap-2">
                      <button type="button" onClick={() => { setGwasInput('17:43124016:CT:C'); }} className="hover:text-emerald-400 transition font-mono hover:underline uppercase text-[9px] bg-yellow-950/40 border border-yellow-500/20 px-2 py-1 rounded hover:border-yellow-500/40">BRCA1 185delAG</button>
                      <button type="button" onClick={() => { setGwasInput('13:32340392:GT:G'); }} className="hover:text-emerald-400 transition font-mono hover:underline uppercase text-[9px] bg-yellow-950/40 border border-yellow-500/20 px-2 py-1 rounded hover:border-yellow-500/40">BRCA2 6174delT</button>
                      <button type="button" onClick={() => { setGwasInput('7:117559590:ATCT:A'); }} className="hover:text-emerald-400 transition font-mono hover:underline uppercase text-[9px] bg-yellow-950/40 border border-yellow-500/20 px-2 py-1 rounded hover:border-yellow-500/40">CFTR F508del (CF)</button>
                      <button type="button" onClick={() => { setGwasInput('10:87952116:G:A'); }} className="hover:text-emerald-400 transition font-mono hover:underline uppercase text-[9px] bg-yellow-950/40 border border-yellow-500/20 px-2 py-1 rounded hover:border-yellow-500/40">PTEN (Cowden)</button>
                    </div>
                  </div>

                  <div className="text-[8px] text-slate-500 mt-3 font-mono-code">
                    💡 All presets scanned against ClinVar VCF (4.4M), GWAS TSV (1.18M), HPO (293K), Disease Names (67K), ClinVar Conflicting (65K), ChEMBL (1K) + external APIs
                  </div>
                </div>
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

              {/* Dataset Analysis Diagnostic */}
              {datasetAnalysis && (
                <HUDFrame title="DATASET ANALYSIS & DIAGNOSTICS" variant="blue" className="neon-glow-blue">
                  <div className="space-y-4">
                    {/* Input & VEP Extraction */}
                    <div className="bg-slate-950/40 border border-slate-800 rounded-lg p-3">
                      <div className="text-[10px] font-bold text-blue-400 uppercase tracking-wider mb-3">VEP Extraction Results</div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] font-mono">
                        <div><span className="text-slate-500">Input Variant:</span> <span className="text-slate-200 font-bold">{datasetAnalysis.variant}</span></div>
                        <div><span className="text-slate-500">Resolved rsID:</span> <span className={datasetAnalysis.vep_extraction.rs_id ? "text-emerald-400 font-bold" : "text-amber-400"}>{datasetAnalysis.vep_extraction.rs_id || 'NOT FOUND'}</span></div>
                        <div><span className="text-slate-500">Gene:</span> <span className="text-slate-200">{datasetAnalysis.vep_extraction.gene_symbol || 'N/A'}</span></div>
                        <div><span className="text-slate-500">Consequence:</span> <span className="text-slate-200">{datasetAnalysis.vep_extraction.consequence || 'N/A'}</span></div>
                        <div className="md:col-span-2"><span className="text-slate-500">Clinical Significance:</span> <span className="text-slate-200">{datasetAnalysis.vep_extraction.clinical_significance || 'N/A'}</span></div>
                      </div>
                    </div>

                    {/* GWAS Catalog Status */}
                    <div className="bg-slate-950/40 border border-slate-800 rounded-lg p-3">
                      <div className="text-[10px] font-bold text-blue-400 uppercase tracking-wider mb-2">GWAS Catalog Status</div>
                      <div className="text-[11px] font-mono space-y-1">
                        <div>
                          <span className="text-slate-500">Status:</span> 
                          {datasetAnalysis.gwas_catalog_status.found ? (
                            <span className="text-emerald-400 font-bold ml-2">✓ FOUND</span>
                          ) : (
                            <span className="text-amber-400 font-bold ml-2">✗ NOT FOUND</span>
                          )}
                        </div>
                        <div><span className="text-slate-500">Associations Found:</span> <span className="text-slate-200 font-bold">{datasetAnalysis.gwas_catalog_status.count}</span></div>
                      </div>
                    </div>

                    {/* Local Datasets Available */}
                    <div className="bg-slate-950/40 border border-slate-800 rounded-lg p-3">
                      <div className="text-[10px] font-bold text-blue-400 uppercase tracking-wider mb-2">Local Datasets Available</div>
                      <div className="text-[11px] font-mono space-y-1">
                        {Object.keys(datasetAnalysis.local_datasets).length > 0 ? (
                          Object.entries(datasetAnalysis.local_datasets).map(([name, info]) => (
                            <div key={name} className="text-slate-300">
                              <span className="text-blue-300 font-bold">📁 {name}</span>
                              <span className="text-slate-500 ml-2">({info.file_count} files)</span>
                              <div className="text-[9px] text-slate-400 ml-4 mt-1">
                                {info.files.slice(0, 3).map(f => `• ${f}`).join(' | ')}
                                {info.files.length > 3 && ` + ${info.files.length - 3} more`}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="text-slate-400">No local datasets found</div>
                        )}
                      </div>
                    </div>

                    {/* Diagnostic Message */}
                    <div className="bg-slate-950/60 border border-blue-600/30 rounded-lg p-3">
                      <div className="text-[11px] font-mono text-slate-300">
                        <span className="text-blue-400 font-bold">Diagnostic:</span> {datasetAnalysis.diagnostic_message}
                      </div>
                    </div>
                  </div>
                </HUDFrame>
              )}

              {/* GWAS associations table */}
              {gwasData && (
                <>
                <HUDFrame title="VARIANT SUMMARY // RSID RESOLUTION" variant="green" className="neon-glow-green">
                  <div className="flex flex-col gap-4">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="text-lg font-mono font-bold text-slate-100">{gwasInput}</span>
                      {gwasData.rs_id && (
                        <button
                          onClick={() => copyToClipboard(gwasData.rs_id)}
                          className="flex items-center gap-2 px-4 py-2 bg-emerald-950/50 border-2 border-emerald-500/50 rounded-lg hover:border-emerald-400 hover:bg-emerald-900/40 transition-all group cursor-pointer"
                          title="Click to copy RSID"
                        >
                          <span className="text-sm font-mono font-bold text-emerald-400 group-hover:text-emerald-300">{gwasData.rs_id}</span>
                          {copySuccess ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-300" />
                          ) : (
                            <Copy className="w-4 h-4 text-emerald-500 group-hover:text-emerald-300" />
                          )}
                        </button>
                      )}
                      {copySuccess && <span className="text-[10px] text-emerald-400 font-mono font-bold animate-pulse">COPIED!</span>}
                      {getImpactBadge(gwasData.impact_level || 'MODERATE')}
                    </div>
                    <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
                      <span>Gene: <strong className="text-emerald-400">{gwasData.gene_symbol || 'N/A'}</strong></span>
                      <span>Consequence: <strong className="text-slate-200">{(gwasData.consequence || 'N/A').replace(/_/g, ' ')}</strong></span>
                    </div>
                    {/* Always show the disease lookup button - local datasets can search by coordinates too */}
                    <button
                      onClick={handleComprehensiveDisease}
                      disabled={compLoading}
                      className="bg-cyan-500 hover:bg-cyan-400 disabled:bg-cyan-900/30 text-slate-950 font-bold px-6 py-3 rounded-lg transition-all flex items-center justify-center gap-2 text-xs tracking-widest font-display btn-neon shadow-[0_0_15px_rgba(0,240,255,0.2)]"
                    >
                      {compLoading ? (
                        <><Loader2 className="w-4 h-4 animate-spin text-slate-950" />SCANNING 6 LOCAL DATASETS + EXTERNAL APIS...</>
                      ) : (
                        <><Network className="w-4 h-4 text-slate-950" />SCAN ALL DATASETS (EXTERNAL + LOCAL)</>
                      )}
                    </button>
                    {!gwasData.rs_id && (
                      <div className="text-[10px] font-mono text-amber-400/70 flex items-center gap-2">
                        <AlertTriangle className="w-3 h-3" />
                        No rsID from VEP, but local ClinVar VCF (4.4M) and GWAS TSV (1.18M) will search by coordinates.
                      </div>
                    )}
                  </div>
                </HUDFrame>

                {/* Informative message when VEP rsID not found */}
                {!gwasData.rs_id && !comprehensiveDisease && (
                  <div className="mb-6 p-4 bg-amber-950/30 border border-amber-500/30 rounded-lg space-y-2">
                    <div className="flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                      <div className="space-y-1">
                        <div className="font-bold text-amber-400 text-xs uppercase tracking-wider">
                          rsID Not Resolved by Ensembl VEP
                        </div>
                        <div className="text-[11px] text-slate-300 leading-relaxed">
                          <strong>Why:</strong> Ensembl VEP couldn&apos;t resolve a public rsID. Scanning <strong>local ClinVar VCF</strong> (4.4M variants) 
                          and <strong>GWAS TSV</strong> (1.18M associations) for direct matches...
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Show when VEP didn't find rsID but local ClinVar did */}
                {!gwasData.rs_id && comprehensiveDisease?.resolved_rsid && (
                  <div className="mb-4 p-3 bg-emerald-950/30 border border-emerald-500/30 rounded-lg">
                    <div className="flex items-center gap-2 text-xs font-mono">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span className="text-emerald-400 font-bold">rsID resolved from local ClinVar VCF:</span>
                      <span className="text-emerald-300 font-bold">{comprehensiveDisease.resolved_rsid}</span>
                    </div>
                  </div>
                )}

                {/* ── COMPREHENSIVE DISEASE ASSOCIATIONS ── */}
                {comprehensiveDisease && (
                  <>
                    {/* Variant Summary with Copyable RSID */}
                    <HUDFrame variant="cyan" className="neon-glow-cyan">
                      <div className="flex flex-col md:flex-row justify-between gap-6">
                        <div className="space-y-3">
                          <div className="flex flex-wrap items-center gap-3">
                            <span className="text-lg font-mono font-bold text-slate-100 neon-text-cyan">
                              {comprehensiveDisease.variant_display}
                            </span>
                            {comprehensiveDisease.resolved_rsid && (
                              <button
                                onClick={() => copyToClipboard(comprehensiveDisease.resolved_rsid)}
                                className="flex items-center gap-2 px-3 py-1.5 bg-cyan-950/50 border border-cyan-500/50 rounded-lg hover:border-cyan-400 transition-all group"
                                title="Click to copy RSID"
                              >
                                <span className="text-sm font-mono font-bold text-cyan-400">{comprehensiveDisease.resolved_rsid}</span>
                                {copySuccess ? <CheckCircle2 className="w-3.5 h-3.5 text-cyan-300" /> : <Copy className="w-3.5 h-3.5 text-cyan-500 group-hover:text-cyan-300" />}
                              </button>
                            )}
                            {copySuccess && <span className="text-[10px] text-cyan-400 font-mono animate-pulse">COPIED!</span>}
                          </div>
                          <div className="text-xs font-mono text-slate-400">
                            Gene: <strong className="text-cyan-400">{comprehensiveDisease.gene_info?.gene_symbol || 'N/A'}</strong>
                          </div>
                        </div>
                        <div className="md:text-right space-y-1">
                          <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest font-mono">Total Associations</span>
                          <div className="text-2xl font-bold text-cyan-400">{comprehensiveDisease.source_counts?.total_associations || 0}</div>
                          <div className="text-[9px] font-mono text-slate-500">
                            <span className="text-blue-400">🌐 {comprehensiveDisease.source_counts?.clinvar_conditions || 0} API</span>
                            {' + '}
                            <span className="text-emerald-400">📁 {(comprehensiveDisease.source_counts?.clinvar_vcf_local || 0) + (comprehensiveDisease.source_counts?.gwas_tsv_local || 0)} Local</span>
                          </div>
                        </div>
                      </div>
                    </HUDFrame>

                    {/* Disease Associations */}
                    <HUDFrame title="DISEASE ASSOCIATIONS // MULTI-SOURCE (EXTERNAL + LOCAL)" variant="green">
                      {comprehensiveDisease.disease_associations?.length > 0 ? (
                        <div className="space-y-2 max-h-96 overflow-y-auto">
                          {comprehensiveDisease.disease_associations.map((d, idx) => (
                            <div key={idx} className="p-3 bg-slate-950/40 border border-emerald-500/20 rounded-lg hover:border-emerald-500/40 transition-all">
                              <div className="flex justify-between items-start gap-2">
                                <div>
                                  <span className="text-xs font-mono text-emerald-400 font-bold">{d.disease}</span>
                                  {d.gene && <div className="text-[9px] text-slate-400 mt-1">Gene: <span className="text-emerald-300">{d.gene}</span></div>}
                                </div>
                                <div className="flex flex-col items-end gap-1">
                                  <span className={`text-[8px] font-bold px-2 py-0.5 rounded font-mono ${d.source?.includes('Local') ? 'bg-emerald-950/50 text-emerald-400 border border-emerald-500/20' : 'bg-blue-950/40 text-blue-300 border border-blue-500/20'}`}>
                                    {d.source?.includes('Local') ? `📁 ${d.source}` : `🌐 ${d.source}`}
                                  </span>
                                  {d.pvalue && <span className="text-[9px] text-emerald-400 font-mono">p={d.pvalue}</span>}
                                </div>
                              </div>
                              {d.clinical_significance && d.clinical_significance !== 'Not Available' && (
                                <div className="text-[9px] text-slate-400 mt-1">Clinical: <span className="text-amber-400">{d.clinical_significance}</span></div>
                              )}
                              {d.risk_allele && <div className="text-[9px] text-slate-500 mt-0.5">Risk Allele: {d.risk_allele}</div>}
                              {d.impact && <div className="text-[9px] text-slate-500 mt-0.5">Impact: <span className={d.impact === 'HIGH' ? 'text-red-400' : d.impact === 'MODERATE' ? 'text-amber-400' : 'text-slate-400'}>{d.impact}</span></div>}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-6 text-slate-500 font-mono text-xs uppercase">No disease associations found across any source</div>
                      )}
                    </HUDFrame>

                    {/* Clinical Significance (ClinVar — External API + Local VCF) */}
                    <HUDFrame title="CLINICAL SIGNIFICANCE // CLINVAR (API + LOCAL VCF)" variant="purple">
                      <div className="space-y-3">
                        <div className="data-cell">
                          <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-1 font-mono">SIGNIFICANCE</span>
                          <span className="text-sm font-mono font-bold text-amber-400">{comprehensiveDisease.clinical_significance || 'Not Available'}</span>
                        </div>
                        {/* External ClinVar conditions */}
                        <div className="data-cell">
                          <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-2 font-mono">CLINVAR API CONDITIONS ({comprehensiveDisease.source_counts?.clinvar_conditions || 0})</span>
                          <div className="flex flex-wrap gap-1.5">
                            {comprehensiveDisease.disease_associations?.filter(d => d.source === 'ClinVar').map((d, idx) => (
                              <span key={idx} className="text-[10px] font-mono bg-purple-950/40 text-purple-300 px-2 py-0.5 rounded border border-purple-500/20">{d.disease}</span>
                            ))}
                            {(!comprehensiveDisease.disease_associations?.some(d => d.source === 'ClinVar')) && (
                              <span className="text-[10px] font-mono text-slate-500">No ClinVar API conditions</span>
                            )}
                          </div>
                        </div>
                        {/* Local ClinVar VCF conditions */}
                        <div className="data-cell">
                          <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-2 font-mono">CLINVAR LOCAL VCF HITS ({comprehensiveDisease.source_counts?.clinvar_vcf_local || 0})</span>
                          <div className="flex flex-wrap gap-1.5">
                            {comprehensiveDisease.disease_associations?.filter(d => d.source === 'ClinVar VCF (Local)').map((d, idx) => (
                              <span key={idx} className="text-[10px] font-mono bg-rose-950/30 text-rose-300 px-2 py-0.5 rounded border border-rose-500/20" title={`Sig: ${d.clinical_significance || 'N/A'} | Impact: ${d.impact || 'N/A'}`}>{d.disease}</span>
                            ))}
                            {(!comprehensiveDisease.disease_associations?.some(d => d.source === 'ClinVar VCF (Local)')) && (
                              <span className="text-[10px] font-mono text-slate-500">No local VCF matches</span>
                            )}
                          </div>
                        </div>
                        {/* ClinVar Conflicting interpretations */}
                        {comprehensiveDisease.clinvar_conflicting?.length > 0 && (
                          <div className="data-cell">
                            <span className="block text-[9px] font-bold text-amber-500 uppercase tracking-widest mb-1 font-mono">⚠ CONFLICTING INTERPRETATIONS ({comprehensiveDisease.clinvar_conflicting.length})</span>
                            <div className="text-[10px] font-mono text-amber-300/70">This variant has conflicting clinical interpretations in ClinVar.</div>
                          </div>
                        )}
                      </div>
                    </HUDFrame>

                    {/* Gene Information & Functional Predictions */}
                    <HUDFrame title="GENE INFORMATION // FUNCTIONAL IMPACT" variant="cyan">
                      <div className="space-y-3">
                        <div className="data-cell flex justify-between">
                          <span className="text-xs text-slate-400 font-mono">GENE SYMBOL</span>
                          <span className="text-xs font-mono font-bold text-cyan-400">{comprehensiveDisease.gene_info?.gene_symbol || 'N/A'}</span>
                        </div>
                        {comprehensiveDisease.gene_info?.full_name && (
                          <div className="data-cell">
                            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest font-mono">FULL NAME</span>
                            <span className="block text-xs text-slate-300 mt-1">{comprehensiveDisease.gene_info.full_name}</span>
                          </div>
                        )}
                        {comprehensiveDisease.gene_info?.description && (
                          <div className="data-cell">
                            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest font-mono">GENE SUMMARY</span>
                            <span className="block text-[11px] text-slate-400 mt-1 leading-relaxed">{comprehensiveDisease.gene_info.description}</span>
                          </div>
                        )}
                        <div className="grid grid-cols-2 gap-2">
                          <div className="data-cell flex justify-between">
                            <span className="text-xs text-slate-400 font-mono">SIFT</span>
                            <span className="text-xs font-mono font-bold text-slate-200">{comprehensiveDisease.gene_info?.sift_prediction || 'N/A'}</span>
                          </div>
                          <div className="data-cell flex justify-between">
                            <span className="text-xs text-slate-400 font-mono">POLYPHEN</span>
                            <span className="text-xs font-mono font-bold text-slate-200">{comprehensiveDisease.gene_info?.polyphen_prediction || 'N/A'}</span>
                          </div>
                          <div className="data-cell flex justify-between">
                            <span className="text-xs text-slate-400 font-mono">AA CHANGE</span>
                            <span className="text-xs font-mono font-bold text-cyan-400">{comprehensiveDisease.gene_info?.amino_acid_change || 'N/A'}</span>
                          </div>
                          <div className="data-cell flex justify-between">
                            <span className="text-xs text-slate-400 font-mono">IMPACT</span>
                            {comprehensiveDisease.gene_info?.impact_level && getImpactBadge(comprehensiveDisease.gene_info.impact_level)}
                          </div>
                        </div>
                      </div>
                    </HUDFrame>

                    {/* ── LOCAL DATASETS SCANNED ── */}
                    <HUDFrame title="LOCAL DATASETS SCANNED // 6 FILES" variant="blue" className="neon-glow-blue">
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                        {[
                          { key: 'clinvar_vcf', label: 'ClinVar VCF', file: 'clinvar.vcf', rows: '4.4M', icon: '📂' },
                          { key: 'gwas_tsv', label: 'GWAS Catalog TSV', file: 'gwas-associations.tsv', rows: '1.18M', icon: '📊' },
                          { key: 'hpo_phenotypes', label: 'HPO Phenotypes', file: 'genes_to_phenotype.csv', rows: '293K', icon: '🧩' },
                          { key: 'disease_names', label: 'Disease Names', file: 'disease_names.tsv', rows: '67K', icon: '🗂️' },
                          { key: 'clinvar_conflicting', label: 'ClinVar Conflicting', file: 'clinvar_conflicting.csv', rows: '65K', icon: '⚠️' },
                          { key: 'chembl_compounds', label: 'ChEMBL Compounds', file: 'chembl_compounds.csv', rows: '1K', icon: '💊' },
                        ].map(ds => {
                          const stats = comprehensiveDisease.local_dataset_stats?.[ds.key] || {};
                          const hits = stats.hits || stats.matches || 0;
                          const used = stats.used || false;
                          return (
                            <div key={ds.key} className={`p-2.5 rounded-lg border transition-all ${used ? 'bg-emerald-950/20 border-emerald-500/30' : 'bg-slate-950/30 border-slate-800'}`}>
                              <div className="flex items-center gap-1.5 mb-1">
                                <span className="text-xs">{ds.icon}</span>
                                <span className={`text-[9px] font-bold uppercase tracking-wider ${used ? 'text-emerald-400' : 'text-slate-500'}`}>{ds.label}</span>
                              </div>
                              <div className="flex items-center justify-between">
                                <span className="text-[9px] font-mono text-slate-500">{ds.rows} rows</span>
                                {used ? (
                                  <span className="text-[9px] font-mono font-bold text-emerald-400">✓ {hits} HIT{hits !== 1 ? 'S' : ''}</span>
                                ) : (
                                  <span className="text-[9px] font-mono text-slate-600">SCANNED</span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                      <div className="mt-3 text-[9px] font-mono text-slate-500 border-t border-slate-800 pt-2">
                        <span className="text-blue-400 font-bold">{comprehensiveDisease.source_counts?.local_datasets_used || 0}/6 datasets produced hits</span>
                        {' · '}
                        <span className="text-slate-400">{comprehensiveDisease.local_datasets_total_hits || 0} total local records matched</span>
                      </div>
                    </HUDFrame>

                    {/* HPO Phenotypes (from local dataset) */}
                    {comprehensiveDisease.hpo_phenotypes?.length > 0 && (
                      <HUDFrame title="HPO PHENOTYPES // LOCAL DATASET (293K GENES)" variant="orange">
                        <div className="space-y-1.5 max-h-60 overflow-y-auto">
                          {comprehensiveDisease.hpo_phenotypes.map((p, idx) => (
                            <div key={idx} className="flex items-center justify-between p-2 bg-slate-950/30 border border-orange-500/10 rounded hover:border-orange-500/30 transition">
                              <div>
                                <span className="text-[10px] font-mono text-orange-300 font-bold">{p.hpo_id}</span>
                                <span className="text-[10px] font-mono text-slate-400 ml-2">{p.phenotype}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                {p.frequency && p.frequency !== '-' && (
                                  <span className="text-[9px] text-slate-500 font-mono">{p.frequency}</span>
                                )}
                                {p.disease_id && (
                                  <span className="text-[9px] text-slate-600 font-mono">{p.disease_id}</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </HUDFrame>
                    )}

                    {/* ChEMBL Drug-Target Compounds (from local dataset) */}
                    {comprehensiveDisease.chembl_compounds?.length > 0 && (
                      <HUDFrame title="CHEMBL DRUG-TARGET COMPOUNDS // LOCAL DATASET" variant="green">
                        <div className="space-y-1.5 max-h-48 overflow-y-auto">
                          {comprehensiveDisease.chembl_compounds.map((c, idx) => (
                            <div key={idx} className="flex items-center justify-between p-2 bg-slate-950/30 border border-emerald-500/10 rounded hover:border-emerald-500/30 transition">
                              <div>
                                <span className="text-[10px] font-mono text-emerald-300 font-bold">{c.name || c.chembl_id}</span>
                                <span className="text-[9px] text-slate-500 font-mono ml-2">{c.chembl_id}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                {c.max_phase && <span className="text-[9px] bg-blue-950/40 text-blue-300 px-1.5 py-0.5 rounded font-mono">Phase {c.max_phase}</span>}
                                {c.type && <span className="text-[9px] text-slate-600 font-mono">{c.type}</span>}
                              </div>
                            </div>
                          ))}
                        </div>
                      </HUDFrame>
                    )}

                    {/* GWAS Findings Table (external API + local TSV) */}
                    {comprehensiveDisease.gwas_findings?.length > 0 && (
                      <HUDFrame title={`GWAS CATALOG FINDINGS // API + LOCAL TSV (${comprehensiveDisease.gwas_findings.length})`} variant="green">
                        <div className="overflow-x-auto">
                          <table className="w-full text-xs font-mono">
                            <thead>
                              <tr className="text-[10px] uppercase tracking-wider text-slate-500 border-b border-slate-800">
                                <th className="text-left py-3 pr-3">TRAIT / DISEASE</th>
                                <th className="text-left py-3 pr-3">P-VALUE</th>
                                <th className="text-left py-3 pr-3">RISK ALLELE</th>
                                <th className="text-left py-3 pr-3">GENE</th>
                                <th className="text-left py-3 pr-3">SOURCE</th>
                                <th className="text-left py-3 pr-3">STUDY</th>
                              </tr>
                            </thead>
                            <tbody>
                              {comprehensiveDisease.gwas_findings.map((g, idx) => (
                                <tr key={idx} className="border-b border-slate-900/60 hover:bg-slate-900/20 transition-all">
                                  <td className="py-3 pr-3 text-slate-200 font-medium">{g.disease}</td>
                                  <td className="py-3 pr-3 text-emerald-400 font-mono-code font-bold">{g.pvalue || 'N/A'}</td>
                                  <td className="py-3 pr-3 text-slate-300 font-mono">{g.risk_allele || 'N/A'}</td>
                                  <td className="py-3 pr-3 text-emerald-300">{g.gene || 'N/A'}</td>
                                  <td className="py-3 pr-3">
                                    <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded ${g.source?.includes('Local') ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-500/20' : 'bg-blue-950/40 text-blue-400 border border-blue-500/20'}`}>
                                      {g.source?.includes('Local') ? 'LOCAL TSV' : 'EBI API'}
                                    </span>
                                  </td>
                                  <td className="py-3 pr-3 text-slate-400">
                                    {g.pubmed_id ? (
                                      <a href={`https://pubmed.ncbi.nlm.nih.gov/${g.pubmed_id}/`} target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
                                        {g.pubmed_id} <ExternalLink className="w-3 h-3" />
                                      </a>
                                    ) : (g.study_id || 'N/A')}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </HUDFrame>
                    )}

                    {/* Publications (PubMed) */}
                    <HUDFrame title="RELATED PUBLICATIONS // PUBMED" variant="blue">
                      {comprehensiveDisease.publications?.length > 0 ? (
                        <div className="space-y-2 max-h-80 overflow-y-auto">
                          {comprehensiveDisease.publications.map((pub, idx) => (
                            <div key={idx} className="p-3 bg-slate-950/40 border border-blue-500/20 rounded-lg hover:border-blue-500/40 transition-all">
                              <a href={pub.url} target="_blank" rel="noopener noreferrer" className="text-xs font-mono text-blue-400 hover:text-blue-300 font-medium flex items-start gap-1">
                                {pub.title} <ExternalLink className="w-3 h-3 mt-0.5 shrink-0" />
                              </a>
                              <div className="text-[9px] text-slate-500 mt-1">{pub.authors}</div>
                              <div className="text-[9px] text-slate-400 mt-0.5 italic">{pub.journal} ({pub.year})</div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-6 text-slate-500 font-mono text-xs uppercase">No publications found</div>
                      )}
                    </HUDFrame>
                  </>
                )}

                {/* Prompt when no comprehensive data yet */}
                {!comprehensiveDisease && !compLoading && !compError && (
                  <div className="text-center py-8 text-slate-500 font-mono text-xs">
                    <Database className="w-8 h-8 mx-auto mb-2 opacity-30" />
                    Click &quot;SCAN ALL DATASETS&quot; to query 6 local datasets + 5 external APIs
                  </div>
                )}

                {compError && (
                  <div className="flex items-start gap-3 p-4 bg-red-950/30 border border-red-500/30 text-red-400 rounded-lg text-xs font-mono">
                    <AlertTriangle className="w-5 h-5 shrink-0" />
                    <div>{compError}</div>
                  </div>
                )}
                </>
              )}

            </div>
          )}

          {/* RSID Search module removed - functionality merged into Disease Associations module */}


          {activeModule === 'drugs' && (
            <div className="flex flex-col gap-6">
              
              <HUDFrame title="CHEMBL COMPOUND SEARCH" variant="purple" className="neon-glow-purple">
                <form onSubmit={handleCompoundSearch} className="space-y-4">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest font-mono">
                    Search compound database (by name, ID, or target):
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

                  {/* Drug Query Presets */}
                  <div className="space-y-3 pt-2 border-t border-slate-800">
                    <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest font-bold">Quick Queries:</div>
                    
                    {/* Cancer Therapeutics */}
                    <div className="space-y-2">
                      <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider ml-1">🔴 Cancer Therapeutics</div>
                      <div className="flex flex-wrap gap-2">
                        <button type="button" onClick={() => { setCompoundQuery('selinexor'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">Selinexor (XPO1)</button>
                        <button type="button" onClick={() => { setCompoundQuery('CHEMBL1201579'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">Trastuzumab (HER2)</button>
                        <button type="button" onClick={() => { setCompoundQuery('tamoxifen'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">Tamoxifen (ER)</button>
                        <button type="button" onClick={() => { setCompoundQuery('paclitaxel'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-red-950/40 border border-red-500/20 px-2 py-1 rounded hover:border-red-500/40">Paclitaxel (Tubulin)</button>
                      </div>
                    </div>

                    {/* Targeted Therapy */}
                    <div className="space-y-2">
                      <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider ml-1">🎯 Targeted Therapy</div>
                      <div className="flex flex-wrap gap-2">
                        <button type="button" onClick={() => { setCompoundQuery('EGFR inhibitor'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-amber-950/40 border border-amber-500/20 px-2 py-1 rounded hover:border-amber-500/40">EGFR Inhibitors</button>
                        <button type="button" onClick={() => { setCompoundQuery('kinase inhibitor'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-amber-950/40 border border-amber-500/20 px-2 py-1 rounded hover:border-amber-500/40">Kinase Inhibitors</button>
                        <button type="button" onClick={() => { setCompoundQuery('checkpoint inhibitor'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-amber-950/40 border border-amber-500/20 px-2 py-1 rounded hover:border-amber-500/40">Checkpoint Inhibitors</button>
                      </div>
                    </div>

                    {/* Cardiovascular */}
                    <div className="space-y-2">
                      <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider ml-1">🔵 Cardiovascular</div>
                      <div className="flex flex-wrap gap-2">
                        <button type="button" onClick={() => { setCompoundQuery('statin'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-blue-950/40 border border-blue-500/20 px-2 py-1 rounded hover:border-blue-500/40">Statins (Cholesterol)</button>
                        <button type="button" onClick={() => { setCompoundQuery('ACE inhibitor'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-blue-950/40 border border-blue-500/20 px-2 py-1 rounded hover:border-blue-500/40">ACE Inhibitors</button>
                        <button type="button" onClick={() => { setCompoundQuery('beta blocker'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-blue-950/40 border border-blue-500/20 px-2 py-1 rounded hover:border-blue-500/40">Beta Blockers</button>
                      </div>
                    </div>

                    {/* Antibiotic/Antimicrobial */}
                    <div className="space-y-2">
                      <div className="text-[9px] font-bold text-slate-600 uppercase tracking-wider ml-1">🟢 Antibiotics</div>
                      <div className="flex flex-wrap gap-2">
                        <button type="button" onClick={() => { setCompoundQuery('penicillin'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-green-950/40 border border-green-500/20 px-2 py-1 rounded hover:border-green-500/40">Penicillins</button>
                        <button type="button" onClick={() => { setCompoundQuery('fluoroquinolone'); }} className="hover:text-purple-400 transition font-mono text-[9px] bg-green-950/40 border border-green-500/20 px-2 py-1 rounded hover:border-green-500/40">Fluoroquinolones</button>
                      </div>
                    </div>
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
