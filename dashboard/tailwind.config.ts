export default {
  content: [
    "./index.html",
    "./App.tsx",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Core Palette - Mais vibrante e saturada
        "primary": "#00f2ff",        // Cyan puro
        "primary-dark": "#0891b2",
        "secondary": "#bc6ff1",      // Purple mais suave para contraste
        "accent": "#bc6ff1",
        
        // Deep Backgrounds - Camadas de profundidade
        "background-dark": "#0a0b10",   // Preto "Deep Space"
        "background-card": "#13151c",   // Elevado
        "surface-dark": "#1c1f26",      // Superfície de controle
        
        // Semantic Status
        "status-online": "#00ff9f",     // Green Cyber
        "status-warning": "#ffbd39",    // Gold
        "status-error": "#ff3864",      // Red Crimson
        "status-info": "#00d1ff",
        
        "border-dark": "rgba(255, 255, 255, 0.06)",
      },
      boxShadow: {
        'neon-cyan': '0 0 15px rgba(0, 242, 255, 0.25)',
        'neon-purple': '0 0 15px rgba(188, 111, 241, 0.25)',
        'glow-status': '0 0 10px currentColor',
        'glass-inner': 'inset 0 1px 1px 0 rgba(255, 255, 255, 0.05)',
      },
      letterSpacing: {
        'widest': '0.25em',
        'tightest': '-0.05em',
      }
    },
  },
  plugins: [],
}
