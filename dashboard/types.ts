import * as THREE from 'three';

export enum AgentStatus {
  IDLE = 'IDLE',
  SCANNING = 'SCANNING',
  ENGAGED = 'ENGAGED',
  OFFLINE = 'OFFLINE',
}

export interface Agent {
  id: string;
  name: string;
  role: 'Guardian' | 'Analyst' | 'Hunter';
  status: AgentStatus;
  health: number; // 0-100
  position: [number, number, number]; // 3D coordinates
  cpuLoad: number; // 0-100
}

export interface Threat {
  id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  type: 'Malware' | 'Intrusion' | 'DDoS' | 'Anomaly';
  timestamp: string;
  status: 'DETECTED' | 'MITIGATED';
}

export interface NetworkMetric {
  time: string;
  inbound: number;
  outbound: number;
  latency: number;
}

export interface ComplianceMetric {
  subject: string;
  A: number; // Current
  fullMark: number;
}

// Helpers to generate initial 3D positions (Fibonacci Sphere for even distribution)
export const generateAgents = (count: number): Agent[] => {
  const agents: Agent[] = [];
  const phi = Math.PI * (3 - Math.sqrt(5)); // Golden angle

  for (let i = 0; i < count; i++) {
    const y = 1 - (i / (count - 1)) * 2; // y goes from 1 to -1
    const radius = Math.sqrt(1 - y * y);
    const theta = phi * i;

    const x = Math.cos(theta) * radius;
    const z = Math.sin(theta) * radius;
    
    // Scale up radius for scene
    const R = 4; 

    agents.push({
      id: `AG-${100 + i}`,
      name: `UNIT-${100 + i}`,
      role: i % 3 === 0 ? 'Guardian' : i % 3 === 1 ? 'Hunter' : 'Analyst',
      status: AgentStatus.IDLE,
      health: 100,
      position: [x * R, y * R, z * R],
      cpuLoad: Math.floor(Math.random() * 30) + 10,
    });
  }
  return agents;
};

export const INITIAL_METRICS: ComplianceMetric[] = [
  { subject: 'Encryption', A: 120, fullMark: 150 },
  { subject: 'Firewall', A: 98, fullMark: 150 },
  { subject: 'Integrity', A: 86, fullMark: 150 },
  { subject: 'Protocol', A: 99, fullMark: 150 },
  { subject: 'Auth', A: 85, fullMark: 150 },
  { subject: 'Latency', A: 65, fullMark: 150 },
];

export const INITIAL_THREATS: Threat[] = [
  { id: 'T-9001', severity: 'LOW', type: 'Anomaly', timestamp: '10:42:01', status: 'MITIGATED' },
  { id: 'T-9002', severity: 'MEDIUM', type: 'Intrusion', timestamp: '10:43:15', status: 'DETECTED' },
];