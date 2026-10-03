export type UUID = string;

export type UserRole = 'user' | 'admin' | 'guest';

export interface User {
  id: UUID;
  email: string;
  name: string;
  role: UserRole;
  createdAt: string;
  preferences?: Record<string, unknown>;
}

export type ChatMode =
  | 'AUTO'
  | 'QUICK'
  | 'THINK'
  | 'SEARCH'
  | 'RESEARCH'
  | 'CODE'
  | 'LEARN'
  | 'WRITE'
  | 'ANALYZE'
  | 'CREATE'
  | 'AGENT';

export interface Citation {
  id: string;
  sourceUrl?: string;
  title: string;
  snippet: string;
  fileName?: string;
  pageNumber?: number;
  confidenceScore: number;
}

export interface MessageAttachment {
  id: string;
  fileName: string;
  fileSize: number;
  mimeType: string;
  storagePath: string;
  extractedTextPreview?: string;
}

export interface ChatMessage {
  id: UUID;
  conversationId: UUID;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  mode?: ChatMode;
  citations?: Citation[];
  attachments?: MessageAttachment[];
  toolCalls?: ToolCall[];
  thoughtProcess?: string;
  createdAt: string;
}

export interface Conversation {
  id: UUID;
  userId: UUID;
  title: string;
  mode: ChatMode;
  projectId?: UUID;
  pinned: boolean;
  archived: boolean;
  createdAt: string;
  updatedAt: string;
}

export type ToolRisk =
  | 'INFORMATIONAL'
  | 'SAFE_READ'
  | 'REVERSIBLE_WRITE'
  | 'CONSEQUENTIAL'
  | 'PRIVILEGED';

export interface ToolDefinition {
  id: string;
  name: string;
  description: string;
  riskLevel: ToolRisk;
  requiredScope: string;
  parametersSchema: Record<string, unknown>;
}

export interface ToolCall {
  id: string;
  toolId: string;
  parameters: Record<string, unknown>;
  status: 'proposed' | 'awaiting_approval' | 'running' | 'completed' | 'failed' | 'rejected';
  result?: unknown;
  verificationReport?: {
    verified: boolean;
    evidence: string;
  };
}

export type ArtifactType =
  | 'DOCUMENT'
  | 'REPORT'
  | 'CODE'
  | 'WEB_APP'
  | 'DIAGRAM'
  | 'CHART'
  | 'SPREADSHEET'
  | 'PRESENTATION'
  | 'IMAGE';

export interface Artifact {
  id: UUID;
  userId: UUID;
  projectId?: UUID;
  title: string;
  type: ArtifactType;
  content: string;
  language?: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface DesktopDevice {
  id: string;
  name: string;
  os: string;
  version: string;
  connected: boolean;
  lastSeen: string;
  allowedFolders: string[];
  capabilities: string[];
}
