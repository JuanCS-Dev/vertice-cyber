import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Float, Sparkles } from '@react-three/drei';
import { EffectComposer, Bloom, ChromaticAberration, Noise, Vignette } from '@react-three/postprocessing';
import * as THREE from 'three';
import { Agent, AgentStatus } from '../types';

interface SceneProps {
  agents: Agent[];
}

// ALIEN MATERIALS
const neuronMaterial = new THREE.MeshPhysicalMaterial({
  color: "#00f2ff",
  emissive: "#00f2ff",
  emissiveIntensity: 4,
  roughness: 0,
  metalness: 1,
  clearcoat: 1,
  clearcoatRoughness: 0
});

const inactiveMaterial = new THREE.MeshStandardMaterial({
  color: "#1a1a1a",
  emissive: "#1a1a1a",
  emissiveIntensity: 0.1,
  transparent: true,
  opacity: 0.5
});

const SynapticWeb: React.FC<{ agents: Agent[] }> = React.memo(({ agents }) => {
  const lineGeometry = useMemo(() => {
    const points: THREE.Vector3[] = [];
    const count = agents.length;

    // Organic Web Connection (Voronoi-like feel)
    for (let i = 0; i < count; i++) {
      const p1 = new THREE.Vector3(...agents[i].position);
      points.push(new THREE.Vector3(0, 0, 0), p1); // Connect to Hive Mind (Center)

      for (let j = i + 1; j < count; j++) {
        const p2 = new THREE.Vector3(...agents[j].position);
        if (p1.distanceTo(p2) < 4.5) { // Shorter, denser connections
          points.push(p1, p2);
        }
      }
    }
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [agents]);

  React.useEffect(() => {
    return () => {
      lineGeometry.dispose();
    };
  }, [lineGeometry]);

  return (
    <lineSegments geometry={lineGeometry}>
      <lineBasicMaterial color="#00f2ff" transparent opacity={0.15} linewidth={1} />
    </lineSegments>
  );
});

const AlienNode: React.FC<{ agent: Agent }> = React.memo(({ agent }) => {
  const mesh = useRef<THREE.Mesh>(null);
  const isOnline = agent.status !== AgentStatus.OFFLINE;

  useFrame((state) => {
    if (mesh.current) {
      const t = state.clock.getElapsedTime();
      // Alien Breathing
      const scale = isOnline ? 1 + Math.sin(t * 3 + agent.position[0]) * 0.2 : 0.8;
      mesh.current.scale.set(scale, scale, scale);
      mesh.current.rotation.x = t + agent.position[1];
      mesh.current.rotation.z = t * 0.5;
    }
  });

  return (
    <Float speed={2} rotationIntensity={2} floatIntensity={1}>
      <mesh ref={mesh} position={new THREE.Vector3(...agent.position)}>
        <dodecahedronGeometry args={[0.2, 0]} />
        <primitive object={isOnline ? neuronMaterial : inactiveMaterial} attach="material" />
      </mesh>
    </Float>
  );
});

const HiveMindCore = () => {
  const mesh = useRef<THREE.Mesh>(null);
  useFrame((state) => {
    if (mesh.current) {
      const t = state.clock.getElapsedTime();
      mesh.current.rotation.y = t * 0.2;
      mesh.current.rotation.z = t * 0.1;
      // Pulsing Core
      const s = 1 + Math.sin(t) * 0.1;
      mesh.current.scale.set(s, s, s);
    }
  });

  return (
    <mesh ref={mesh}>
      <icosahedronGeometry args={[1.5, 4]} />
      <meshStandardMaterial
        color="#000"
        emissive="#bc13fe"
        emissiveIntensity={0.8}
        wireframe
        transparent
        opacity={0.3}
      />
    </mesh>
  );
}

export const NeuralNetwork: React.FC<SceneProps> = ({ agents }) => {
  return (
    <div className="w-full h-full relative" style={{ background: '#000' }}>
      <Canvas
        camera={{ position: [0, 0, 10], fov: 50 }}
        dpr={[1, 1.5]}
        gl={{ powerPreference: "high-performance", antialias: false }}
      >
        <color attach="background" args={['#000000']} />
        <fog attach="fog" args={['#000000', 5, 20]} />

        {/* ALIEN LIGHTING */}
        <ambientLight intensity={0.1} />
        <pointLight position={[10, 10, 10]} intensity={1} color="#00f2ff" />
        <pointLight position={[-10, -10, -10]} intensity={1} color="#bc13fe" />

        <group>
          <HiveMindCore />
          <SynapticWeb agents={agents} />
          {agents.map(agent => (
            <AlienNode key={agent.id} agent={agent} />
          ))}
        </group>

        {/* SPACE PARTICLES */}
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        <Sparkles count={200} scale={10} size={2} speed={0.4} opacity={0.5} color="#00f2ff" />

        <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />

        {/* POST PROCESSING - CINEMATIC LOOK */}
        <EffectComposer enableNormalPass={false}>
          <Bloom luminanceThreshold={0.5} mipmapBlur intensity={2.5} radius={0.4} />
          <ChromaticAberration offset={new THREE.Vector2(0.002, 0.002)} />
          <Noise opacity={0.15} />
          <Vignette eskil={false} offset={0.3} darkness={0.8} />
        </EffectComposer>
      </Canvas>
    </div>
  );
};