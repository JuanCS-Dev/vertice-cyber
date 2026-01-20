import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return this.props.fallback || (
                <div className="min-h-screen bg-[#050508] text-white flex items-center justify-center p-8">
                    <div className="max-w-md w-full bg-red-500/10 border border-red-500/50 rounded-lg p-6 backdrop-blur-sm">
                        <h1 className="text-2xl font-bold mb-4 flex items-center gap-2">
                            <span className="text-3xl">⚠️</span> Something went wrong
                        </h1>
                        <p className="text-gray-300 mb-4 font-mono text-sm">
                            {this.state.error?.message || 'An unexpected error occurred'}
                        </p>
                        <button
                            onClick={() => window.location.reload()}
                            className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded transition font-semibold"
                        >
                            Reload Page
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
