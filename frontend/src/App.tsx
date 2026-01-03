import React, { useState, useEffect } from 'react';
import { ChatInterface } from './components/ChatInterface';
import { DocumentUpload } from './components/DocumentUpload';
import { Header } from './components/Header';
import { apiService } from './services/api';
import { HealthResponse } from './types/api';
import { Send, FileText, Activity } from 'lucide-react';

type Tab = 'chat' | 'upload' | 'status';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const [healthStatus, setHealthStatus] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const health = await apiService.getHealth();
      setHealthStatus(health);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus(null);
    } finally {
      setIsLoading(false);
    }
  };

  const tabs = [
    { id: 'chat' as Tab, label: 'Chat', icon: Send },
    { id: 'upload' as Tab, label: 'Documents', icon: FileText },
    { id: 'status' as Tab, label: 'Status', icon: Activity },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header healthStatus={healthStatus} />
      
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center px-1 py-4 border-b-2 font-medium text-sm transition-colors duration-200
                    ${
                      activeTab === tab.id
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        ) : (
          <>
            {activeTab === 'chat' && <ChatInterface />}
            {activeTab === 'upload' && <DocumentUpload onUploadSuccess={checkHealth} />}
            {activeTab === 'status' && (
              <div className="space-y-6">
                <div className="bg-white shadow rounded-lg p-6">
                  <h2 className="text-lg font-medium text-gray-900 mb-4">System Status</h2>
                  {healthStatus ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Overall Status</span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          healthStatus.status === 'healthy' 
                            ? 'bg-green-100 text-green-800'
                            : healthStatus.status === 'degraded'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {healthStatus.status}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Version</span>
                        <span className="text-sm text-gray-500">{healthStatus.version}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Uptime</span>
                        <span className="text-sm text-gray-500">
                          {Math.floor(healthStatus.uptime / 60)}m {Math.floor(healthStatus.uptime % 60)}s
                        </span>
                      </div>
                      <div className="space-y-2">
                        <span className="text-sm font-medium text-gray-700">Components</span>
                        <div className="grid grid-cols-2 gap-2">
                          {Object.entries(healthStatus.components).map(([component, status]) => (
                            <div key={component} className="flex items-center justify-between text-sm">
                              <span className="text-gray-600 capitalize">{component.replace('_', ' ')}</span>
                              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                status === 'healthy' 
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-red-100 text-red-800'
                              }`}>
                                {status}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-500">Unable to fetch health status</p>
                      <button
                        onClick={checkHealth}
                        className="mt-4 btn-primary"
                      >
                        Retry
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
