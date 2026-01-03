// API response types
export interface HealthResponse {
  status: string;
  version: string;
  uptime: number;
  components: Record<string, string>;
}

export interface ChatRequest {
  query: string;
  session_id?: string;
  max_documents?: number;
  include_web_search?: boolean;
  style_preferences?: Record<string, any>;
}

export interface Citation {
  id: number;
  title: string;
  source_type: string;
  relevance_score: number;
  citation_info: Record<string, any>;
  in_text_reference: string;
}

export interface ChatResponse {
  query: string;
  answer: string;
  citations: Citation[];
  metadata: {
    workflow_id: string;
    processing_time: number;
    steps_completed: (string | null)[];
    sources_used: number;
    quality_score: number;
  };
  error?: string;
  success: boolean;
}

export interface IngestionResult {
  filename: string;
  chunks_created: number;
  processing_time: number;
  file_size: number;
  success: boolean;
  error?: string;
}

export interface CollectionStats {
  vector_store_type: string;
  total_documents: number;
  total_chunks: number;
  storage_size?: number;
  last_updated: string;
}

export interface SearchResult {
  content: string;
  metadata: Record<string, any>;
  score: number;
  chunk_id: string;
}

export interface SearchRequest {
  query: string;
  k?: number;
  rerank?: boolean;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_found: number;
  processing_time: number;
}
