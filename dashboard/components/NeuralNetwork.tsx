import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Line, Sphere, Icosahedron } from '@react-three/drei';
import { EffectComposer, Bloom, Noise, Vignette } from '@react-three/postprocessing';
import * as THREE from 'three';
import { Agent, AgentStatus } from '../types';

interface SceneProps {
  agents: Agent[];
}

// Reuse geometry and materials to reduce draw calls and GC overhead
const coreMaterial = new THREE.MeshStandardMaterial({
  color: "#4E75F6",
  emissive: "#4E75F6",
  emissiveIntensity: 2,
  roughness: 0.2,
  metalness: 0.8
});

const wireframeMaterial = new THREE.MeshBasicMaterial({
  color: "#00ff9f",
  wireframe: true,
  transparent: true,
  opacity: 0.1
});

const CoreNode = () => {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (meshRef.current) {
      const t = state.clock.getElapsedTime();
      meshRef.current.rotation.x = t * 0.2;
      meshRef.current.rotation.y = t * 0.3;
      const scale = 1 + Math.sin(t * 2) * 0.1;
      meshRef.current.scale.set(scale, scale, scale);
    }
  });

  return (
    <group>
      <Icosahedron args={[1, 1]} ref={meshRef} material={coreMaterial} />
      <Icosahedron args={[1.5, 1]} material={wireframeMaterial} />
    </group>
  );
};

// Memoized Agent Node to prevent material recreation on every render
const AgentNode: React.FC<{ agent: Agent }> = React.memo(({ agent }) => {
  const isEngaged = agent.status === AgentStatus.ENGAGED;
  const isDanger = agent.status === AgentStatus.OFFLINE;
  
  const color = isDanger ? '#ff006e' : isEngaged ? '#F6E05E' : '#00ff9f';
  const intensity = isEngaged ? 3 : 1;

  // Use useMemo for the material so we don't create a new instance every frame/update
  const material = useMemo(() => new THREE.MeshStandardMaterial({
    color: color,
    emissive: color,
    emissiveIntensity: intensity
  }), [color, intensity]);

  return (
    <group position={new THREE.Vector3(...agent.position)}>
      <Sphere args={[0.2, 8, 8]}>
        <primitive object={material} attach="material" />
      </Sphere>
    </group>
  );
}, (prev, next) => {
  // Custom comparison: Only re-render if position or status changes significantly
  return prev.agent.status === next.agent.status && 
         prev.agent.position[0] === next.agent.position[0]; 
});

const Connections = React.memo(({ agents }: { agents: Agent[] }) => {
  const corePos = useMemo(() => new THREE.Vector3(0, 0, 0), []);
  
  // Connect all agents to Core
  const coreConnections = useMemo(() => {
    return agents.map(agent => {
      const end = new THREE.Vector3(...agent.position);
      return [corePos, end] as [THREE.Vector3, THREE.Vector3];
    });
  }, [agents, corePos]);

  // Connect neighbors
  const neighborConnections = useMemo(() => {
    const lines: [THREE.Vector3, THREE.Vector3][] = [];
    const count = agents.length;
    
    // Optimized loop: Calculate distance manually to avoid Vector3 allocation overhead in loop checks
    for (let i = 0; i < count; i++) {
      const pos1 = agents[i].position;
      
      for (let j = i + 1; j < count; j++) {
        const pos2 = agents[j].position;
        
        // Manual squared distance check (x*x + y*y + z*z)
        const dx = pos1[0] - pos2[0];
        const dy = pos1[1] - pos2[1];
        const dz = pos1[2] - pos2[2];
        const distSq = dx*dx + dy*dy + dz*dz;

        // Threshold is 3.5 units squared = 12.25
        if (distSq < 12.25) { 
          const v1 = new THREE.Vector3(pos1[0], pos1[1], pos1[2]);
          const v2 = new THREE.Vector3(pos2[0], pos2[1], pos2[2]);
          lines.push([v1, v2]);
        }
      }
    }
    return lines;
  }, [agents]);

  return (
    <group>
      {coreConnections.map((points, i) => (
        <Line 
          key={`core-${i}`} 
          points={points} 
          color="#4E75F6" 
          opacity={0.3} 
          transparent 
          lineWidth={1} 
          segments={false}
        />
      ))}
      {neighborConnections.map((points, i) => (
        <Line 
          key={`neighbor-${i}`} 
          points={points} 
          color="#00ff9f" 
          opacity={0.1} 
          transparent 
          lineWidth={0.5} 
          segments={false}
        />
      ))}
    </group>
  );
});

const SceneContent: React.FC<SceneProps> = ({ agents }) => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.05;
    }
  });

  return (
    <group ref={groupRef}>
      <CoreNode />
      {agents.map(agent => (
        <AgentNode key={agent.id} agent={agent} />
      ))}
      <Connections agents={agents} />
    </group>
  );
};

export const NeuralNetwork: React.FC<SceneProps> = ({ agents }) => {
  return (
    <div className="w-full h-full relative">
      <Canvas 
        camera={{ position: [0, 0, 12], fov: 45 }} 
        dpr={[1, 1.5]} 
        gl={{ 
          antialias: false,
          alpha: true,
          powerPreference: "high-performance",
          stencil: false,
          depth: true
        }}
      >
        <color attach="background" args={['#050508']} />
        
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        
        <SceneContent agents={agents} />
        
        <OrbitControls 
          enablePan={false} 
          enableZoom={true} 
          minDistance={5} 
          maxDistance={20}
          autoRotate={false}
          enableDamping={true}
          dampingFactor={0.05}
        />

        <EffectComposer 
          disableNormalPass
          multisampling={0}
        >
          <Bloom 
            luminanceThreshold={0.2} 
            mipmapBlur 
            intensity={1.5} 
            radius={0.6}
            levels={8}
          />
          <Noise opacity={0.05} />
          <Vignette eskil={false} offset={0.1} darkness={1.1} />
        </EffectComposer>
      </Canvas>
    </div>
  );
};