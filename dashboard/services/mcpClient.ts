/**
 * MCP Client Service - Comunicação com o Bridge HTTP.
 */
/// <reference types="vite/client" />

export interface ToolExecutionResult<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  metadata: {
    latencyMs: number;
    logs: any[];
  };
}

class MCPClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_MCP_API_URL || 'http://localhost:8001';
  }

  /**
   * Executa uma tool MCP.
   */
  async execute<T = any>(toolName: string, arguments_obj: Record<string, any> = {}): Promise<ToolExecutionResult<T>> {
    const start = performance.now();
    try {
      const response = await fetch(`${this.baseUrl}/mcp/tools/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tool_name: toolName,
          arguments: arguments_obj
        })
      });

      const data = await response.json();
      const end = performance.now();

      return {
        success: data.success,
        data: data.result,
        error: data.error,
        metadata: {
          latencyMs: end - start,
          logs: data.logs || []
        }
      };
    } catch (error) {
      const end = performance.now();
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        metadata: {
          latencyMs: end - start,
          logs: []
        }
      };
    }
  }

  /**
   * Lista tools disponíveis.
   */
  async listTools() {
    try {
      const response = await fetch(`${this.baseUrl}/mcp/tools/list`);
      return await response.json();
    } catch (error) {
      console.error('Failed to list tools:', error);
      return { tools: [], total: 0 };
    }
  }

  /**
   * Verifica health do sistema.
   */
  async health() {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return await response.json();
    } catch (error) {
      return { status: 'offline', error: error instanceof Error ? error.message : 'Connection failed' };
    }
  }
}

export const mcpClient = new MCPClient();