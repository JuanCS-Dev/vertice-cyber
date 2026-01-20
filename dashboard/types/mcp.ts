/**
 * MCP Types - TypeScript interfaces for MCP API responses
 * 
 * Maps Python Pydantic models to TypeScript interfaces for type safety.
 */

// =============================================================================
// BASE API TYPES
// =============================================================================

/** Response from /mcp/tools/execute */
export interface MCPToolResponse<T = unknown> {
    success: boolean;
    result?: T;
    error?: string;
    logs: MCPLog[];
    execution_time_ms?: number;
}

/** Log entry from tool execution */
export interface MCPLog {
    level: 'INFO' | 'WARN' | 'ERROR';
    message: string;
    request_id: string;
    timestamp: string;
}

/** Tool info from /mcp/tools/list */
export interface MCPTool {
    name: string;
    agent: string;
    category: 'governance' | 'intelligence' | 'offensive' | 'ai';
    description: string;
    parameters: Record<string, string>;
}

/** Response from /mcp/tools/list */
export interface MCPToolListResponse {
    tools: MCPTool[];
    total: number;
}

/** Health check response */
export interface MCPHealthResponse {
    status: 'healthy' | 'degraded' | 'unhealthy';
    service: string;
    version: string;
    tools_available: number;
}

// =============================================================================
// WEBSOCKET EVENT TYPES
// =============================================================================

/** Event from WebSocket /mcp/events */
export interface MCPEvent {
    type: MCPEventType;
    data: Record<string, unknown>;
    source: string;
    event_id: string;
    timestamp: string;
    correlation_id?: string;
}

/** Heartbeat event (sent every 30s if no activity) */
export interface MCPHeartbeat {
    type: 'heartbeat';
    timestamp: string;
}

/** All possible event types from EventBus */
export type MCPEventType =
    // Threat
    | 'threat.detected'
    | 'threat.predicted'
    | 'threat.mitre.mapped'
    // Ethics
    | 'ethics.validation.requested'
    | 'ethics.validation.completed'
    | 'ethics.human_review.required'
    // OSINT
    | 'osint.investigation.started'
    | 'osint.investigation.completed'
    | 'osint.breach.detected'
    // Wargame
    | 'wargame.simulation.started'
    | 'wargame.simulation.completed'
    // Patch
    | 'patch.validation.requested'
    | 'patch.validation.completed'
    // CyberSec
    | 'cybersec.recon.started'
    | 'cybersec.recon.completed'
    // Immune
    | 'immune.response.triggered'
    | 'immune.antibody.deployed'
    // System
    | 'system.tool.called'
    | 'system.error'
    | 'system.health.check';

// =============================================================================
// TOOL-SPECIFIC RESULT TYPES
// =============================================================================

// --- Ethical Magistrate ---

export type DecisionType =
    | 'approved'
    | 'approved_with_conditions'
    | 'rejected_by_governance'
    | 'rejected_by_ethics'
    | 'rejected_by_privacy'
    | 'requires_human_review'
    | 'error';

export interface EthicalDecision {
    decision_id: string;
    decision_type: DecisionType;
    action: string;
    actor: string;
    is_approved: boolean;
    conditions: string[];
    rejection_reasons: string[];
    reasoning: string;
    duration_ms: number;
}

// --- OSINT Hunter ---

export interface OSINTFinding {
    source: string;
    finding_type: string;
    severity: string;
    data: Record<string, unknown>;
    confidence: number;
}

export interface BreachInfo {
    name: string;
    date: string;
    data_classes: string[];
    is_verified: boolean;
}

export interface OSINTResult {
    target: string;
    depth: 'basic' | 'deep' | 'exhaustive';
    findings: OSINTFinding[];
    breaches: BreachInfo[];
    risk_score: number;
    sources_checked: string[];
}

// --- Threat Prophet ---

export type ThreatLevel = 'low' | 'medium' | 'high' | 'critical';

export interface ThreatIndicator {
    indicator_type: string;
    value: string;
    confidence: number;
    first_seen: string;
    last_seen: string;
    tags: string[];
}

export interface MITRETechnique {
    technique_id: string;
    name: string;
    description: string;
    tactic: string;
    url: string;
}

export interface ThreatPrediction {
    target: string;
    predicted_threats: string[];
    confidence_score: number;
    risk_level: ThreatLevel;
    recommended_actions: string[];
    time_horizon: string;
}

export interface ThreatAnalysis {
    target: string;
    indicators: ThreatIndicator[];
    techniques: MITRETechnique[];
    predictions: ThreatPrediction[];
    overall_risk_score: number;
    attack_vectors: string[];
}

// --- Compliance Guardian ---

export type ComplianceStatus =
    | 'compliant'
    | 'partially_compliant'
    | 'non_compliant'
    | 'not_applicable';

export interface ComplianceCheck {
    requirement_id: string;
    status: ComplianceStatus;
    score: number;
    evidence: string[];
    violations: string[];
    remediation_steps: string[];
    checked_at: string;
}

export interface ComplianceAssessment {
    target: string;
    framework: string;
    checks: ComplianceCheck[];
    overall_score: number;
    overall_status: ComplianceStatus;
    assessment_date: string;
}

// --- Wargame Executor ---

export interface WargameScenario {
    id: string;
    name: string;
    description: string;
    difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
    scenario_type: 'red_team' | 'purple_team' | 'tabletop' | 'breach_simulation';
    tactics: string[];
    techniques: string[];
    estimated_duration_s: number;
}

export interface WargameResult {
    scenario_id: string;
    execution_id: string;
    timestamp: number;
    success: boolean;
    detection_rate: number;
    logs: string[];
    artifacts: Record<string, unknown>;
}

// --- Patch Validator ML ---

export interface PatchRisk {
    risk_score: number;
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    confidence: number;
    flags: string[];
    recommendation: 'Approve' | 'Manual Review' | 'Reject';
}

// --- CyberSec Basic ---

export interface PortResult {
    port: number;
    state: 'open' | 'closed' | 'filtered';
    service: string;
    banner?: string;
}

export interface ReconResult {
    target: string;
    timestamp: number;
    open_ports: PortResult[];
    http_headers: Record<string, string>;
    security_issues: string[];
    tool_outputs: Record<string, unknown>;
}

// =============================================================================
// TYPE HELPERS
// =============================================================================

/** Union type for all possible tool results */
export type ToolResult =
    | EthicalDecision
    | OSINTResult
    | ThreatAnalysis
    | ComplianceAssessment
    | WargameScenario[]
    | WargameResult
    | PatchRisk
    | ReconResult;

/** Typed execute response for specific tools */
export type EthicalValidateResponse = MCPToolResponse<EthicalDecision>;
export type OSINTInvestigateResponse = MCPToolResponse<OSINTResult>;
export type ThreatAnalyzeResponse = MCPToolResponse<ThreatAnalysis>;
export type ComplianceAssessResponse = MCPToolResponse<ComplianceAssessment>;
export type WargameListResponse = MCPToolResponse<WargameScenario[]>;
export type WargameRunResponse = MCPToolResponse<WargameResult>;
export type PatchValidateResponse = MCPToolResponse<PatchRisk>;
export type CybersecReconResponse = MCPToolResponse<ReconResult>;
