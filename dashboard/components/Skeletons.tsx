import React from 'react';

export function AgentSkeleton() {
    return (
        <div className="animate-pulse flex items-center gap-3 p-2 bg-white/5 rounded-lg">
            {/* Avatar skeleton */}
            <div className="w-10 h-10 bg-gray-700/50 rounded-full" />

            {/* Text skeletons */}
            <div className="flex-1">
                <div className="h-3 bg-gray-700/50 rounded w-20 mb-2" />
                <div className="h-2 bg-gray-700/30 rounded w-14" />
            </div>

            {/* Status skeleton */}
            <div className="w-2 h-2 bg-gray-700/50 rounded-full" />
        </div>
    );
}

export function AgentListSkeleton() {
    return (
        <div className="space-y-2 p-4">
            {Array.from({ length: 6 }).map((_, i) => (
                <AgentSkeleton key={i} />
            ))}
        </div>
    );
}

export function ThreatSkeleton() {
    return (
        <div className="animate-pulse p-3 border-l-2 border-gray-700/50 bg-white/5">
            <div className="flex items-center justify-between mb-2">
                <div className="h-3 bg-gray-700/50 rounded w-16" />
                <div className="h-2 bg-gray-700/30 rounded w-12" />
            </div>
            <div className="h-2 bg-gray-700/30 rounded w-24" />
        </div>
    );
}

export function ThreatFeedSkeleton() {
    return (
        <div className="space-y-2 p-4">
            {Array.from({ length: 4 }).map((_, i) => (
                <ThreatSkeleton key={i} />
            ))}
        </div>
    );
}
