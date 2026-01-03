import React, { useState, useCallback } from 'react';
import { Upload, FileText, Trash2, Search, BarChart3, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { IngestionResult, CollectionStats, SearchResponse } from '../types/api';

interface DocumentUploadProps {
  onUploadSuccess?: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState<IngestionResult[]>([]);
  const [collectionStats, setCollectionStats] = useState<CollectionStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'search' | 'stats'>('upload');

  const loadCollectionStats = useCallback(async () => {
    try {
      const stats = await apiService.getCollectionStats();
      setCollectionStats(stats);
    } catch (error) {
      console.error('Error loading collection stats:', error);
    }
  }, []);

  React.useEffect(() => {
    loadCollectionStats();
  }, [loadCollectionStats]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    setFiles(prev => [...prev, ...selectedFiles]);
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    setUploadResults([]);

    try {
      const results = await apiService.uploadDocuments(files);
      setUploadResults(results.results || []);
      setFiles([]);
      
      if (onUploadSuccess) {
        onUploadSuccess();
      }
      
      // Reload stats
      await loadCollectionStats();
      
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      const results = await apiService.searchDocuments({
        query: searchQuery,
        k: 10,
        rerank: true
      });
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const handleDeleteCollection = async () => {
    if (!window.confirm('Are you sure you want to delete all documents? This action cannot be undone.')) {
      return;
    }

    try {
      await apiService.deleteCollection();
      await loadCollectionStats();
      setSearchResults(null);
      setUploadResults([]);
    } catch (error) {
      console.error('Delete error:', error);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const tabs = [
    { id: 'upload' as const, label: 'Upload Documents', icon: Upload },
    { id: 'search' as const, label: 'Search Documents', icon: Search },
    { id: 'stats' as const, label: 'Collection Stats', icon: BarChart3 },
  ];

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
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
                <Icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          {/* File Upload Area */}
          <div className="bg-white rounded-lg border-2 border-dashed border-gray-300 p-8 text-center">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <div className="space-y-2">
              <p className="text-lg font-medium text-gray-900">
                Upload Documents
              </p>
              <p className="text-sm text-gray-500">
                Supported formats: PDF, TXT, MD. Maximum file size: 50MB.
              </p>
            </div>
            <input
              type="file"
              multiple
              accept=".pdf,.txt,.md"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="btn-primary cursor-pointer inline-block"
            >
              Select Files
            </label>
          </div>

          {/* Selected Files */}
          {files.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="font-medium text-gray-900 mb-3">Selected Files</h3>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center space-x-3">
                      <FileText className="w-4 h-4 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{file.name}</p>
                        <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
              <button
                onClick={handleUpload}
                disabled={isUploading}
                className="mt-4 btn-primary w-full disabled:opacity-50"
              >
                {isUploading ? 'Uploading...' : `Upload ${files.length} File${files.length > 1 ? 's' : ''}`}
              </button>
            </div>
          )}

          {/* Upload Results */}
          {uploadResults.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="font-medium text-gray-900 mb-3">Upload Results</h3>
              <div className="space-y-2">
                {uploadResults.map((result, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded border ${
                      result.success
                        ? 'bg-green-50 border-green-200'
                        : 'bg-red-50 border-red-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{result.filename}</p>
                        <p className="text-sm text-gray-600">
                          {result.chunks_created} chunks • {result.processing_time.toFixed(2)}s
                        </p>
                      </div>
                      <div className={`w-3 h-3 rounded-full ${
                        result.success ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                    </div>
                    {result.error && (
                      <p className="text-sm text-red-600 mt-2">{result.error}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'search' && (
        <div className="space-y-6">
          {/* Search Interface */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex space-x-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search documents..."
                className="input-field flex-1"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button
                onClick={handleSearch}
                disabled={!searchQuery.trim()}
                className="btn-primary disabled:opacity-50"
              >
                <Search className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Search Results */}
          {searchResults && (
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="font-medium text-gray-900 mb-3">
                Search Results ({searchResults.total_found} found)
              </h3>
              <div className="space-y-4">
                {searchResults.results.map((result, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-sm font-medium text-primary-600">
                        Score: {result.score.toFixed(3)}
                      </span>
                      <span className="text-xs text-gray-500">
                        {result.chunk_id}
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm leading-relaxed">
                      {result.content}
                    </p>
                    {result.metadata && (
                      <div className="mt-2 text-xs text-gray-500">
                        Source: {result.metadata.filename || 'Unknown'}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'stats' && (
        <div className="space-y-6">
          {/* Collection Statistics */}
          {collectionStats && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="font-medium text-gray-900 mb-4">Collection Statistics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Vector Store</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {collectionStats.vector_store_type}
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Total Documents</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {collectionStats.total_documents}
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Total Chunks</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {collectionStats.total_chunks}
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Last Updated</p>
                  <p className="text-sm font-medium text-gray-900">
                    {new Date(collectionStats.last_updated).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Danger Zone */}
          <div className="bg-white rounded-lg border border-red-200 p-6">
            <div className="flex items-center space-x-2 mb-4">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <h3 className="font-medium text-red-900">Danger Zone</h3>
            </div>
            <p className="text-sm text-red-700 mb-4">
              Deleting the collection will permanently remove all documents and embeddings.
              This action cannot be undone.
            </p>
            <button
              onClick={handleDeleteCollection}
              className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Delete All Documents
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
