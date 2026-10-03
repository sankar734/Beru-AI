import { create } from 'zustand';

export interface Citation {
  id: string;
  title: string;
  snippet: string;
  source_url?: string;
  confidence_score: number;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  mode?: string;
  thought_process?: string;
  citations?: Citation[];
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  mode: string;
  pinned: boolean;
  archived: boolean;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: ChatMessage[];
  selectedMode: string;
  isStreaming: boolean;
  streamingThought: string;
  streamingContent: string;
  isLoading: boolean;
  error: string | null;
  abortController: AbortController | null;

  setSelectedMode: (mode: string) => void;
  fetchConversations: () => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
  createNewConversation: (title?: string, mode?: string) => Promise<string | null>;
  sendMessage: (content: string, stream?: boolean) => Promise<void>;
  stopStreaming: () => void;
  pinConversation: (id: string, pinned: boolean) => Promise<void>;
  renameConversation: (id: string, title: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  branchConversation: (conversationId: string, messageId: string) => Promise<string | null>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  activeConversationId: null,
  messages: [],
  selectedMode: 'AUTO',
  isStreaming: false,
  streamingThought: '',
  streamingContent: '',
  isLoading: false,
  error: null,
  abortController: null,

  setSelectedMode: (mode) => set({ selectedMode: mode }),

  fetchConversations: async () => {
    const token = localStorage.getItem('nova_token');
    try {
      const res = await fetch('/api/v1/chat/conversations', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        set({ conversations: data });
      }
    } catch {
      // Fallback
    }
  },

  selectConversation: async (id: string) => {
    set({ activeConversationId: id, isLoading: true, error: null });
    const token = localStorage.getItem('nova_token');
    try {
      const res = await fetch(`/api/v1/chat/conversations/${id}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        set({
          messages: data.messages || [],
          selectedMode: data.mode || 'AUTO',
          isLoading: false,
        });
      } else {
        set({ isLoading: false, error: 'Could not load conversation' });
      }
    } catch {
      set({ isLoading: false, error: 'Network error loading conversation' });
    }
  },

  createNewConversation: async (title = 'New Conversation', mode = 'AUTO') => {
    const token = localStorage.getItem('nova_token');
    try {
      const res = await fetch('/api/v1/chat/conversations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ title, mode }),
      });
      if (res.ok) {
        const conv = await res.json();
        set((state) => ({
          conversations: [conv, ...state.conversations],
          activeConversationId: conv.id,
          messages: [],
          selectedMode: conv.mode,
        }));
        return conv.id;
      }
    } catch {
      // Fallback local creation
    }
    return null;
  },

  sendMessage: async (content: string, stream = true) => {
    const token = localStorage.getItem('nova_token');
    let convId = get().activeConversationId;

    if (!convId) {
      convId = await get().createNewConversation('New Conversation', get().selectedMode);
      if (!convId) return;
    }

    const userMsg: ChatMessage = {
      id: `local-${Date.now()}`,
      conversation_id: convId,
      role: 'user',
      content,
      mode: get().selectedMode,
      created_at: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, userMsg],
      isStreaming: true,
      streamingThought: '',
      streamingContent: '',
      error: null,
    }));

    const controller = new AbortController();
    set({ abortController: controller });

    try {
      if (!stream) {
        const res = await fetch(`/api/v1/chat/conversations/${convId}/messages?stream=false`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ content, mode: get().selectedMode }),
          signal: controller.signal,
        });
        if (res.ok) {
          const data = await res.json();
          set((state) => ({
            messages: [...state.messages.slice(0, -1), data.user_message, data.assistant_message],
            isStreaming: false,
          }));
          get().fetchConversations();
        }
        return;
      }

      // Streaming with SSE
      const response = await fetch(`/api/v1/chat/conversations/${convId}/messages?stream=true`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ content, mode: get().selectedMode }),
        signal: controller.signal,
      });

      if (!response.body) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let collectedTokens = '';
      let collectedThought = '';
      let citationsList: Citation[] = [];

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const block of lines) {
          const eventLine = block.split('\n').find((l) => l.startsWith('event: '));
          const dataLine = block.split('\n').find((l) => l.startsWith('data: '));

          if (!eventLine || !dataLine) continue;

          const event = eventLine.replace('event: ', '').trim();
          const data = JSON.parse(dataLine.replace('data: ', '').trim());

          if (event === 'thought') {
            collectedThought = data.thought;
            set({ streamingThought: collectedThought });
          } else if (event === 'token') {
            collectedTokens += data.token;
            set({ streamingContent: collectedTokens });
          } else if (event === 'citations') {
            citationsList = data.citations;
          } else if (event === 'done') {
            const assistantMsg: ChatMessage = {
              id: data.message_id || `asst-${Date.now()}`,
              conversation_id: convId,
              role: 'assistant',
              content: collectedTokens,
              thought_process: collectedThought,
              citations: citationsList,
              mode: get().selectedMode,
              created_at: new Date().toISOString(),
            };
            set((state) => ({
              messages: [...state.messages, assistantMsg],
              isStreaming: false,
              streamingContent: '',
              streamingThought: '',
            }));
            get().fetchConversations();
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        set({ error: 'Failed to stream response', isStreaming: false });
      }
    }
  },

  stopStreaming: () => {
    const controller = get().abortController;
    if (controller) {
      controller.abort();
    }
    const convId = get().activeConversationId;
    const partial = get().streamingContent;
    if (partial && convId) {
      const msg: ChatMessage = {
        id: `stopped-${Date.now()}`,
        conversation_id: convId,
        role: 'assistant',
        content: partial + ' *(Stopped by user)*',
        created_at: new Date().toISOString(),
      };
      set((state) => ({
        messages: [...state.messages, msg],
        isStreaming: false,
        streamingContent: '',
        streamingThought: '',
      }));
    } else {
      set({ isStreaming: false });
    }
  },

  pinConversation: async (id: string, pinned: boolean) => {
    const token = localStorage.getItem('nova_token');
    try {
      await fetch(`/api/v1/chat/conversations/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ pinned }),
      });
      get().fetchConversations();
    } catch {}
  },

  renameConversation: async (id: string, title: string) => {
    const token = localStorage.getItem('nova_token');
    try {
      await fetch(`/api/v1/chat/conversations/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ title }),
      });
      get().fetchConversations();
    } catch {}
  },

  deleteConversation: async (id: string) => {
    const token = localStorage.getItem('nova_token');
    try {
      await fetch(`/api/v1/chat/conversations/${id}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      set((state) => ({
        conversations: state.conversations.filter((c) => c.id !== id),
        activeConversationId: state.activeConversationId === id ? null : state.activeConversationId,
        messages: state.activeConversationId === id ? [] : state.messages,
      }));
    } catch {}
  },

  branchConversation: async (conversationId: string, messageId: string) => {
    const token = localStorage.getItem('nova_token');
    try {
      const res = await fetch(`/api/v1/chat/conversations/${conversationId}/branch?from_message_id=${messageId}`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        set((state) => ({
          conversations: [data, ...state.conversations],
          activeConversationId: data.id,
          messages: data.messages || [],
        }));
        return data.id;
      }
    } catch {}
    return null;
  },
}));
