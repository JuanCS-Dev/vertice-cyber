/**
 * Vertice Cyber Dashboard v3.0
 * 
 * Optimized Architecture:
 * - TelemetryProvider: Manages WebSocket & Logs (LogBuffer)
 * - AgentStateProvider: Manages Agent logic
 * - AppLayout: Pure UI Skeleton
 * 
 * "Zero Technical Debt, Maximum Lethality"
 */

import React from 'react';
import { TelemetryProvider } from './contexts/TelemetryContext';
import { AgentStateProvider } from './contexts/AgentStateContext';
import { AppLayout } from './components/layout/AppLayout';

// Root Component
const App: React.FC = () => {
  return (
    <TelemetryProvider>
        <AgentStateProvider>
            <AppLayout />
        </AgentStateProvider>
    </TelemetryProvider>
  );
};

export default App;