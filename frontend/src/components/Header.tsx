import React from 'react';
import { Brain, Activity } from 'lucide-react';
import { HealthResponse } from '../types/api';

interface HeaderProps {
  healthStatus: HealthResponse | null;
}

export const Header: React.FC<HeaderProps> = ({ healthStatus }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500';
      case 'degraded':
        return 'bg-yellow-500';
      case 'unhealthy':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <Brain className="w-8 h-8 text-primary-600" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Intelligent Research Assistant
              </h1>
              <p className="text-sm text-gray-500">
                Multi-agent RAG-powered research system
              </p>
            </div>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center space-x-4">
            {healthStatus && (
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-gray-400" />
                <div className="flex items-center space-x-2">
                  <div
                    className={`w-2 h-2 rounded-full ${getStatusColor(
                      healthStatus.status
                    )}`}
                  />
                  <span className="text-sm text-gray-600 capitalize">
                    {healthStatus.status}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
