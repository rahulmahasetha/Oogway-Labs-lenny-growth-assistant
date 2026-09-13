/* TypeScript types for the Lenny Growth Assistant */

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface SessionDetail extends Session {
  messages: Message[];
}

export interface SourceCitation {
  id: string;
  title: string;
  source_type: string;
  guest?: string;
  post_url?: string;
  chunk_content?: string;
  speaker?: string;
  start_time?: string;
  similarity?: number;
}

export interface Artifact {
  type: 'markdown' | 'html';
  content: string;
  title?: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceCitation[];
  artifact?: Artifact;
  created_at: string;
}

export interface AppConfig {
  llm_provider: string;
  llm_model: string;
  embedding_model: string;
  rag_top_k: number;
  rag_similarity_threshold: number;
}

export interface IngestionResult {
  sources_processed: number;
  chunks_created: number;
  sources_skipped: number;
  errors: string[];
}

export interface IngestionStatus {
  total_sources: number;
  total_chunks: number;
  podcasts: number;
  newsletters: number;
}

export interface HealthResponse {
  status: string;
  database: string;
  ollama: string;
  version: string;
}
