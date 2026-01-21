
import { z } from 'zod';

// Config Schemas
export const AgentConfigSchema = z.object({
    max_concurrent_tasks: z.number().int().min(1).max(10).default(1),
    log_level: z.enum(['DEBUG', 'INFO', 'WARN', 'ERROR']).default('INFO'),
    timeout_seconds: z.number().int().min(10).default(300)
});

export type AgentConfig = z.infer<typeof AgentConfigSchema>;

export const OSINTConfigSchema = AgentConfigSchema.extend({
    scan_depth: z.enum(['shallow', 'medium', 'deep']).default('medium'),
    port_range: z.tuple([z.number(), z.number()]).default([1, 1000]),
    dns_enumeration: z.boolean().default(true),
    subdomain_bruteforce: z.boolean().default(false)
});

export type OSINTConfig = z.infer<typeof OSINTConfigSchema>;

// Checkpoint Data
export const CheckpointDataSchema = z.object({
    step_index: z.number().int().min(0),
    accumulated_results: z.record(z.string(), z.unknown()),
    memory_snapshot: z.record(z.string(), z.unknown()),
    last_updated: z.string().datetime()
});

export type CheckpointData = z.infer<typeof CheckpointDataSchema>;

// Job Status
export const JobStatusSchema = z.enum([
    'PENDING', 'RUNNING', 'PAUSED', 'COMPLETED', 'FAILED', 'CANCELLED'
]);

export type JobStatus = z.infer<typeof JobStatusSchema>;

export interface Job {
    job_id: string;
    agent_id: string;
    job_type: string;
    status: JobStatus;
    progress: number;
    result_data?: any;
    error_message?: string;
}
