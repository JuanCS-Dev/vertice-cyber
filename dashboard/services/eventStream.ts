
/**
 * Neural Mesh Event Stream
 * Real-time bidirectional link to the Vertice Core.
 */

import { z } from 'zod';

export interface EventHandler {
    (event: any): void;
}

export interface WebSocketMessage {
    type: string;
    [key: string]: any;
}

// Access Vite env
const WS_URL = (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_MCP_WS_URL)
    || 'ws://localhost:8001/mcp/events';

export class VerticeEventStream {
    private ws: WebSocket | null = null;
    private subscriptions = new Map<string, Set<EventHandler>>();
    private reconnectAttempts = 0;
    private readonly MAX_RECONNECT_ATTEMPTS = 10;
    private shouldReconnect = true;

    constructor(private url: string = WS_URL) {
        this.connect();
    }

    public connect(): void {
        if (this.ws?.readyState === WebSocket.OPEN) return;

        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                console.log('[Neural Link] Connected');
                this.reconnectAttempts = 0;
                this.dispatch({ type: 'system.connected', timestamp: new Date().toISOString() });
            };

            this.ws.onmessage = (event) => {
                try {
                    const msg = JSON.parse(event.data);
                    this.dispatch(msg);
                } catch (err) {
                    console.error('[Neural Link] Parse error:', err);
                }
            };

            this.ws.onerror = (error) => {
                console.error('[Neural Link] Error:', error);
            };

            this.ws.onclose = () => {
                console.warn('[Neural Link] Connection closed');
                this.ws = null;
                this.dispatch({ type: 'system.disconnected', timestamp: new Date().toISOString() });
                if (this.shouldReconnect) {
                    this.handleReconnect();
                }
            };
        } catch (err) {
            console.error('[Neural Link] Connection failed:', err);
            this.handleReconnect();
        }
    }

    private handleReconnect(): void {
        if (this.reconnectAttempts >= this.MAX_RECONNECT_ATTEMPTS) {
            console.error('[Neural Link] Critical: Max reconnection attempts reached');
            return;
        }

        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
        console.log(`[Neural Link] Reconnecting in ${delay}ms...`);

        setTimeout(() => {
            this.reconnectAttempts++;
            this.connect();
        }, delay);
    }

    subscribe(pattern: string, handler: EventHandler): () => void {
        if (!this.subscriptions.has(pattern)) {
            this.subscriptions.set(pattern, new Set());
        }
        this.subscriptions.get(pattern)!.add(handler);

        // Send subscription to server if connected
        this.send({ type: 'subscribe', channel: pattern });

        // Return unsubscribe function
        return () => {
            this.subscriptions.get(pattern)?.delete(handler);
            if (this.subscriptions.get(pattern)?.size === 0) {
                this.subscriptions.delete(pattern);
                // Optional: Unsubscribe from server?
            }
        };
    }

    // Alias for compatibility if needed, or prefer subscribe
    on(pattern: string, handler: EventHandler): () => void {
        return this.subscribe(pattern, handler);
    }

    private dispatch(message: WebSocketMessage): void {
        // Dispatch to exact matches and regex matches
        for (const [pattern, handlers] of this.subscriptions) {
            if (this.matchPattern(message.type, pattern)) {
                handlers.forEach(handler => {
                    try {
                        handler(message);
                    } catch (e) {
                        console.error('[Neural Link] Handler error:', e);
                    }
                });
            }
        }
    }

    private matchPattern(eventType: string, pattern: string): boolean {
        if (pattern === '*') return true;
        if (pattern === eventType) return true;
        // Simple wildcard support: "agent.*"
        const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
        return regex.test(eventType);
    }

    send(message: object): void {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('[Neural Link] Socket not ready, message dropped:', message);
        }
    }

    disconnect(): void {
        this.shouldReconnect = false;
        this.ws?.close();
    }
}

// Singleton export
export const eventStream = new VerticeEventStream();
