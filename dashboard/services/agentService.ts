/**
 * Agent Service - Fetches and transforms agent data from MCP
 * 
 * Maps MCP tools to dashboard Agent type format.
 */

import { mcpClient } from './mcpClient';
import type { MCPTool } from '../types/mcp';
import type { Agent, AgentStatus } from '../types';

// =============================================================================
// AGENT CATEGORY MAPPING
// =============================================================================

const CATEGORY_TO_ROLE: Record<string, Agent['role']> = {
    governance: 'Guardian',
    intelligence: 'Analyst',
    offensive: 'Hunter',
    ai: 'Analyst',
};

// =============================================================================
// AGENT SERVICE
// =============================================================================

/**
 * Fetch all agents from MCP tools list
 */
export async function fetchAgents(): Promise<Agent[]> {
    const response = await mcpClient.listTools();

    // Group tools by agent name
    const agentMap = new Map<string, MCPTool[]>();

    for (const tool of response.tools) {
        const agentName = tool.agent;
        if (!agentMap.has(agentName)) {
            agentMap.set(agentName, []);
        }
        agentMap.get(agentName)!.push(tool);
    }

    // Convert to Agent[] with generated positions (Fibonacci sphere)
    const agents: Agent[] = [];
    let index = 0;
    const total = agentMap.size;
    const phi = Math.PI * (3 - Math.sqrt(5)); // Golden angle

    for (const [agentName, tools] of agentMap) {
        // Calculate 3D position using Fibonacci sphere
        const y = total > 1 ? 1 - (index / (total - 1)) * 2 : 0;
        const radius = Math.sqrt(1 - y * y);
        const theta = phi * index;
        const x = Math.cos(theta) * radius;
        const z = Math.sin(theta) * radius;
        const R = 4; // Scale radius

        // Determine role from first tool category
        const category = tools[0]?.category || 'intelligence';
        const role = CATEGORY_TO_ROLE[category] || 'Analyst';

        agents.push({
            id: `AG-${100 + index}`,
            name: agentName,
            role,
            status: 'IDLE' as AgentStatus,
            health: 100,
            position: [x * R, y * R, z * R],
            cpuLoad: Math.floor(Math.random() * 30) + 10,
        });

        index++;
    }

    return agents;
}

/**
 * Execute an agent action (tool)
 */
export async function executeAgentAction<T = unknown>(
    toolName: string,
    args: Record<string, unknown> = {}
): Promise<T> {
    const response = await mcpClient.execute<T>(toolName, args);

    if (!response.success) {
        throw new Error(response.error || 'Action failed');
    }

    return response.data as T;
}

/**
 * Check MCP server health
 */
export async function checkHealth(): Promise<boolean> {
    try {
        const health = await mcpClient.health();
        return health.status === 'healthy';
    } catch {
        return false;
    }
}
