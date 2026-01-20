import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  neonColor?: 'primary' | 'danger' | 'info' | 'gemini';
}

export const GlassCard: React.FC<GlassCardProps> = ({ 
  children, 
  className = '', 
  title,
  neonColor = 'primary'
}) => {
  const colorMap = {
    primary: 'border-cyber-primary text-cyber-primary bg-cyber-primary',
    danger: 'border-cyber-danger text-cyber-danger bg-cyber-danger',
    info: 'border-cyber-info text-cyber-info bg-cyber-info',
    gemini: 'border-gemini-core text-gemini-core bg-gemini-core',
  };

  const currentColor = colorMap[neonColor];

  return (
    <div className={`glass-panel relative rounded-sm flex flex-col group transition-all duration-500 hover:shadow-[0_0_20px_rgba(0,0,0,0.3)] ${className}`}>
      
      {/* Decorative Brackets (Corners) */}
      <div className={`absolute -top-[1px] -left-[1px] w-4 h-4 border-t-2 border-l-2 ${currentColor.split(' ')[0]} opacity-50 group-hover:opacity-100 transition-opacity duration-300 rounded-tl-sm`} />
      <div className={`absolute -top-[1px] -right-[1px] w-4 h-4 border-t-2 border-r-2 ${currentColor.split(' ')[0]} opacity-50 group-hover:opacity-100 transition-opacity duration-300 rounded-tr-sm`} />
      <div className={`absolute -bottom-[1px] -left-[1px] w-4 h-4 border-b-2 border-l-2 ${currentColor.split(' ')[0]} opacity-50 group-hover:opacity-100 transition-opacity duration-300 rounded-bl-sm`} />
      <div className={`absolute -bottom-[1px] -right-[1px] w-4 h-4 border-b-2 border-r-2 ${currentColor.split(' ')[0]} opacity-50 group-hover:opacity-100 transition-opacity duration-300 rounded-br-sm`} />

      {/* Internal Container with Padding */}
      <div className="flex flex-col h-full w-full p-5 bg-black/20">
        
        {/* Header Section */}
        {title && (
          <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-2 shrink-0">
            <h3 className="font-tech uppercase tracking-[0.15em] text-sm md:text-base font-bold flex items-center gap-2 text-gray-100">
              <span className={`w-1.5 h-1.5 rounded-full ${currentColor.split(' ')[2]} shadow-[0_0_8px_currentColor] animate-pulse`} />
              {title}
            </h3>
            <span className="text-[9px] font-mono opacity-30 tracking-widest">SYS.MON.V1</span>
          </div>
        )}

        {/* Content Section - Strict Overflow Handling */}
        <div className="relative flex-1 min-h-0 w-full">
          {children}
        </div>
      </div>
    </div>
  );
};

export const Badge: React.FC<{ children: React.ReactNode, type?: 'success' | 'warning' | 'error' | 'neutral' }> = ({ children, type = 'neutral' }) => {
  const colors = {
    success: 'bg-cyber-primary/10 text-cyber-primary border-cyber-primary/20 shadow-[0_0_10px_rgba(0,255,159,0.1)]',
    warning: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    error: 'bg-cyber-danger/10 text-cyber-danger border-cyber-danger/20 shadow-[0_0_10px_rgba(255,0,110,0.1)]',
    neutral: 'bg-white/5 text-gray-400 border-white/10',
  }[type];

  return (
    <span className={`px-2 py-1 rounded-[2px] text-[10px] font-mono font-bold border ${colors} uppercase tracking-wider`}>
      {children}
    </span>
  );
};