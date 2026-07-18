import { describe, test, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../components/common/Button.tsx';
import { Card } from '../components/ui/Card.tsx';

describe('UI Common Components', () => {
  test('renders Button with text content', () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });

  test('button click triggers onClick callback', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    fireEvent.click(screen.getByText('Click Me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('renders Card with children content', () => {
    render(
      <Card>
        <span data-testid="card-child">Nested Card Child</span>
      </Card>
    );
    expect(screen.getByTestId('card-child')).toBeInTheDocument();
    expect(screen.getByText('Nested Card Child')).toBeInTheDocument();
  });
});
