/**
 * MCP Event Stream (WebSocket)
 * Real-time events do MCP Server
 */

import type { MCPEvent } from '../types/mcp';

// Access Vite env with proper typing
declare const import_meta_env: { VITE_MCP_WS_URL?: string } | undefined;
const WS_URL = (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_MCP_WS_URL)
    || 'ws://localhost:8001/mcp/events';

type EventCallback = (event: MCPEvent) => void;

export class MCPEventStream {
    private ws: WebSocket | null = null;
    private listeners = new Map<string, Set<EventCallback>>();
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectDelay = 2000;
    private isConnecting = false;
    private shouldReconnect = true;

    /**
     * Conecta ao WebSocket
     */
    connect(): void {
        if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
            return;
        }

        this.isConnecting = true;
        this.shouldReconnect = true;

        try {
            this.ws = new WebSocket(WS_URL);

            this.ws.onopen = () => {
                console.log('✅ Connected to MCP Event Stream');
                this.reconnectAttempts = 0;
                this.isConnecting = false;
                this.emit('_connected', { type: '_connected', timestamp: new Date().toISOString() } as any);
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    // Heartbeat interno (não emitir para UI, apenas log debug)
                    if (data.type === 'heartbeat') {
                        console.debug('💓 Heartbeat received');
                        return;
                    }

                    // Connected message
                    if (data.type === 'connected') {
                        console.log('📡 MCP says:', data.message);
                        return;
                    }

                    // Emitir evento para listeners específicos
                    this.emit(data.type, data);

                    // Também emitir para listener genérico '*'
                    this.emit('*', data);

                } catch (err) {
                    console.error('❌ Failed to parse WebSocket message:', err);
                }
            };

            this.ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.isConnecting = false;
            };

            this.ws.onclose = () => {
                console.warn('🔌 WebSocket closed');
                this.isConnecting = false;
                this.ws = null;
                this.emit('_disconnected', { type: '_disconnected', timestamp: new Date().toISOString() } as any);

                if (this.shouldReconnect) {
                    this.attemptReconnect();
                }
            };

        } catch (err) {
            console.error('❌ WebSocket connection failed:', err);
            this.isConnecting = false;
            this.attemptReconnect();
        }
    }

    /**
     * Desconecta do WebSocket
     */
    disconnect(): void {
        this.shouldReconnect = false;
        this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnect
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.listeners.clear();
    }

    /**
     * Registra listener para tipo de evento
     */
    on(eventType: string, callback: EventCallback): () => void {
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, new Set());
        }

        this.listeners.get(eventType)!.add(callback);

        // Retorna função para unsubscribe
        return () => {
            this.listeners.get(eventType)?.delete(callback);
        };
    }

    /**
     * Emite evento para listeners
     */
    private emit(eventType: string, data: MCPEvent): void {
        const callbacks = this.listeners.get(eventType);
        if (callbacks) {
            callbacks.forEach(cb => {
                try {
                    cb(data);
                } catch (err) {
                    console.error(`Error in event listener for ${eventType}:`, err);
                }
            });
        }
    }

    /**
     * Tenta reconectar com backoff exponencial
     */
    private attemptReconnect(): void {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error(`❌ Max reconnection attempts (${this.maxReconnectAttempts}) reached`);
            this.emit('_max_reconnect', { type: '_max_reconnect' } as any);
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * this.reconnectAttempts;

        console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

        setTimeout(() => this.connect(), delay);
    }

    /**
     * Status da conexão
     */
    get isConnected(): boolean {
        return this.ws?.readyState === WebSocket.OPEN;
    }
}

// Singleton
export const eventStream = new MCPEventStream();
