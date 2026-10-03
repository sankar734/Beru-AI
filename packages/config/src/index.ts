export const APP_NAME = 'NOVA X';
export const APP_TAGLINE = 'Think. Search. Research. Create. Code. Learn. Act.';
export const API_VERSION = 'v1';
export const API_BASE_PATH = `/api/${API_VERSION}`;

export const DEFAULT_TIMEOUTS = {
  SEARCH_MS: 10000,
  RESEARCH_MS: 120000,
  CODE_EXECUTION_MS: 5000,
  DESKTOP_ACTION_MS: 15000,
};

export const MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024; // 50MB

export const SUPPORTED_MODES = [
  'AUTO',
  'QUICK',
  'THINK',
  'SEARCH',
  'RESEARCH',
  'CODE',
  'LEARN',
  'WRITE',
  'ANALYZE',
  'CREATE',
  'AGENT',
] as const;

export const RISK_LEVELS = {
  INFORMATIONAL: 0,
  SAFE_READ: 1,
  REVERSIBLE_WRITE: 2,
  CONSEQUENTIAL: 3,
  PRIVILEGED: 4,
} as const;
