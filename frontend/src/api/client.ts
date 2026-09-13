/* API client for the Lenny Growth Assistant backend */

import type { AppConfig, IngestionResult, IngestionStatus, Message, Session, SessionDetail } from '../types';

const API_BASE = '/api';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(errorData.detail || errorData.error || `HTTP ${response.status}`);
  }

  // 204 No Content
  if (response.status === 204) return undefined as T;
  return response.json();
}

// --- Sessions ---

export async function createSession(title?: string): Promise<Session> {
  return fetchJSON<Session>(`${API_BASE}/sessions`, {
    method: 'POST',
    body: JSON.stringify({ title: title || 'New Chat' }),
  });
}

export async function listSessions(): Promise<Session[]> {
  return fetchJSON<Session[]>(`${API_BASE}/sessions`);
}

export async function getSession(id: string): Promise<SessionDetail> {
  const data = await fetchJSON(`/api/sessions/${id}`);
  return data as SessionDetail;
}

export async function updateSession(id: string, title: string): Promise<Session> {
  const data = await fetchJSON(`/api/sessions/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  return data as Session;
}

export async function deleteSession(id: string): Promise<void> {
  await fetchJSON(`/api/sessions/${id}`, { method: 'DELETE' });
}

// --- Messages ---

export async function sendMessage(sessionId: string, content: string): Promise<Message> {
  return fetchJSON<Message>(`${API_BASE}/sessions/${sessionId}/messages`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

// --- Ingestion ---

export async function runIngestion(): Promise<IngestionResult> {
  return fetchJSON<IngestionResult>(`${API_BASE}/ingestion/run`, { method: 'POST' });
}

export async function getIngestionStatus(): Promise<IngestionStatus> {
  return fetchJSON<IngestionStatus>(`${API_BASE}/ingestion/status`);
}

// --- Config ---

export async function getConfig(): Promise<AppConfig> {
  return fetchJSON<AppConfig>(`${API_BASE}/config`);
}

// --- Health ---

export async function getHealth() {
  return fetchJSON<{ status: string; database: string; ollama: string; version: string }>('/health');
}
