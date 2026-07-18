import '@testing-library/jest-dom';
import { vi } from 'vitest';
import React from 'react';

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock CSS packages causing ES module load errors in worker forks
vi.mock('@asamuzakjp/css-color', () => {
  return {
    default: {},
  };
});
vi.mock('@csstools/css-calc', () => {
  return {
    default: {},
  };
});

// Mock Monaco Editor components
vi.mock('@monaco-editor/react', () => {
  return {
    default: ({ value, onChange }: any) => React.createElement('textarea', {
      'data-testid': 'monaco-mock-editor',
      value,
      onChange: (e: any) => onChange && onChange(e.target.value)
    }),
    Editor: ({ value, onChange }: any) => React.createElement('textarea', {
      'data-testid': 'monaco-mock-editor',
      value,
      onChange: (e: any) => onChange && onChange(e.target.value)
    }),
  };
});
