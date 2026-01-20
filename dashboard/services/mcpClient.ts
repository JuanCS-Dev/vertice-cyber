/**
 * MCP Client - Base HTTP/WebSocket client for MCP API
 * 
 * Provides:
 * - HTTP client with error handling
 * - WebSocket connection with auto-reconnect
 * - Environment configuration
 */

import type {
    MCPToolResponse,
    MCPToolListResponse,
    MCPHealthResponse,
    MCPEvent,
    MCPHeartbeat
} from '../types/mcp';

// =============================================================================
// CONFIGURATION
// =============================================================================

const MCP_API_URL = import.meta.env.VITE_MCP_API_URL || 'http://localhost:8001';
const MCP_WS_URL = import.meta.env.VITE_MCP_WS_URL || 'ws://localhost:8001/mcp/events';

// =============================================================================
// HTTP CLIENT
// =============================================================================

class MCPClient {
    private baseUrl: string;

    constructor(baseUrl: string = MCP_API_URL) {
        this.baseUrl = baseUrl;
    }

    /**
     * Health check
     */
    async health(): Promise<MCPHealthResponse> {
        const response = await fetch(`${this.baseUrl}/health`);
        if (!response.ok) {
            throw new Error(`Health check failed: ${response.status}`);
        }
        return response.json();
    }

    /**
     * List all available tools
     */
    async listTools(): Promise<MCPToolListResponse> {
        const response = await fetch(`${this.baseUrl}/mcp/tools/list`);
        if (!response.ok) {
            throw new Error(`Failed to list tools: ${response.status}`);
        }
        return response.json();
    }

    /**
     * Execute a tool
     */
    async executeTool<T = unknown>(
        toolName: string,
        args: Record<string, unknown> = {}
    ): Promise<MCPToolResponse<T>> {
        const response = await fetch(`${this.baseUrl}/mcp/tools/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tool_name: toolName,
                arguments: args,
            }),
        });

        if (!response.ok) {
            throw new Error(`Tool execution failed: ${response.status}`);
        }

        return response.json();
    }
}

// =============================================================================
// EVENT STREAM (WebSocket)
// =============================================================================

type EventCallback = (event: MCPEvent) => void;
type HeartbeatCallback = (event: MCPHeartbeat) => void;
type ConnectionCallback = () => void;

class MCPEventStream {
    private ws: WebSocket | null = null;
    private url: string;
    private listeners: Map<string, Set<EventCallback>> = new Map();
    private heartbeatListeners: Set<HeartbeatCallback> = new Set();
    private onConnectCallbacks: Set<ConnectionCallback> = new Set();
    private onDisconnectCallbacks: Set<ConnectionCallback> = new Set();
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectTimeoutId: number | null = null;

    constructor(url: string = MCP_WS_URL) {
        this.url = url;
    }

    /**
     * Connect to WebSocket
     */
    connect(): void {
        if (this.ws?.readyState === WebSocket.OPEN) {
            console.log('[MCP EventStream] Already connected');
            return;
        }

        console.log('[MCP EventStream] Connecting to', this.url);
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('✅ [MCP EventStream] Connected');
            this.reconnectAttempts = 0;
            this.onConnectCallbacks.forEach(cb => cb());
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === 'heartbeat') {
                    this.heartbeatListeners.forEach(cb => cb(data));
                    return;
                }

                // Emit to type-specific listeners
                const callbacks = this.listeners.get(data.type);
                if (callbacks) {
                    callbacks.forEach(cb => cb(data));
                }

                // Emit to wildcard listeners
                const wildcardCallbacks = this.listeners.get('*');
                if (wildcardCallbacks) {
                    wildcardCallbacks.forEach(cb => cb(data));
                }
            } catch (e) {
                console.error('[MCP EventStream] Failed to parse message:', e);
            }
        };

        this.ws.onerror = (error) => {
            console.error('❌ [MCP EventStream] Error:', error);
        };

        this.ws.onclose = () => {
            console.warn('🔌 [MCP EventStream] Disconnected');
            this.onDisconnectCallbacks.forEach(cb => cb());
            this.attemptReconnect();
        };
    }

    /**
     * Subscribe to specific event type
     */
    on(eventType: string, callback: EventCallback): () => void {
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, new Set());
        }
        this.listeners.get(eventType)!.add(callback);

        // Return unsubscribe function
        return () => {
            this.listeners.get(eventType)?.delete(callback);
        };
    }

    /**
     * Subscribe to all events
     */
    onAny(callback: EventCallback): () => void {
        return this.on('*', callback);
    }

    /**
     * Subscribe to heartbeat events
     */
    onHeartbeat(callback: HeartbeatCallback): () => void {
        this.heartbeatListeners.add(callback);
        return () => this.heartbeatListeners.delete(callback);
    }

    /**
     * Subscribe to connection events
     */
    onConnect(callback: ConnectionCallback): () => void {
        this.onConnectCallbacks.add(callback);
        return () => this.onConnectCallbacks.delete(callback);
    }

    /**
     * Subscribe to disconnection events
     */
    onDisconnect(callback: ConnectionCallback): () => void {
        this.onDisconnectCallbacks.add(callback);
        return () => this.onDisconnectCallbacks.delete(callback);
    }

    /**
     * Attempt reconnection with exponential backoff
     */
    private attemptReconnect(): void {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('[MCP EventStream] Max reconnect attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 30000);

        console.log(`🔄 [MCP EventStream] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

        this.reconnectTimeoutId = window.setTimeout(() => {
            this.connect();
        }, delay);
    }

    /**
     * Disconnect WebSocket
     */
    disconnect(): void {
        if (this.reconnectTimeoutId) {
            clearTimeout(this.reconnectTimeoutId);
            this.reconnectTimeoutId = null;
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        this.listeners.clear();
        this.heartbeatListeners.clear();
        this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnect
    }

    /**
     * Check if connected
     */
    get isConnected(): boolean {
        return this.ws?.readyState === WebSocket.OPEN;
    }
}

// =============================================================================
// SINGLETON EXPORTS
// =============================================================================

export const mcpClient = new MCPClient();
export const mcpEventStream = new MCPEventStream();

// Re-export types
export type { MCPToolResponse, MCPEvent, MCPHeartbeat };
