import React from 'react';
import { describe, test, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '../context/ThemeContext.tsx';
import { useTheme } from '../hooks/useTheme.ts';

const ThemeTester: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <div>
      <span data-testid="theme-val">{theme}</span>
      <button onClick={toggleTheme}>Toggle</button>
    </div>
  );
};

describe('Custom Context Hooks', () => {
  test('ThemeProvider provides default theme state and toggle behavior', () => {
    render(
      <ThemeProvider>
        <ThemeTester />
      </ThemeProvider>
    );

    const valSpan = screen.getByTestId('theme-val');
    expect(valSpan).toHaveTextContent(/(light|dark)/);

    const initialTheme = valSpan.textContent;
    const expectedToggled = initialTheme === 'light' ? 'dark' : 'light';

    fireEvent.click(screen.getByText('Toggle'));
    expect(valSpan).toHaveTextContent(expectedToggled);
  });
});
