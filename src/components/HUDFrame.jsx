import React from 'react';

export default function HUDFrame({ children, title, variant = 'cyan', className = '' }) {
  const borderClasses = {
    cyan: 'border-[rgba(14,165,233,0.15)] hover:border-[rgba(14,165,233,0.35)]',
    magenta: 'border-[rgba(6,182,212,0.15)] hover:border-[rgba(6,182,212,0.35)]',
    green: 'border-[rgba(16,185,129,0.15)] hover:border-[rgba(16,185,129,0.35)]',
    purple: 'border-[rgba(100,116,139,0.15)] hover:border-[rgba(100,116,139,0.35)]',
  };

  const frameClass = {
    cyan: 'hud-frame',
    magenta: 'hud-frame hud-frame-alt',
    green: 'hud-frame hud-frame-green',
    purple: 'hud-frame hud-frame-purple',
  };

  const indicatorColors = {
    cyan: 'bg-sky-500',
    magenta: 'bg-cyan-500',
    green: 'bg-emerald-500',
    purple: 'bg-slate-400',
  };

  return (
    <div className={`glass-panel p-6 relative ${borderClasses[variant] || borderClasses.cyan} ${frameClass[variant] || frameClass.cyan} ${className}`}>
      {title && (
        <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-2">
          <span className="font-display text-xs font-bold tracking-widest text-slate-400 uppercase">
            {title}
          </span>
          <span className={`w-1.5 h-1.5 rounded-full ${indicatorColors[variant] || indicatorColors.cyan} opacity-70`} />
        </div>
      )}
      {children}
    </div>
  );
}
