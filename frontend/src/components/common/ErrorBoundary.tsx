import { Component, ErrorInfo, ReactNode } from 'react';
import Card from '../ui/Card.tsx';
import { Button } from './Button.tsx';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an unhandled rendering crash:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen items-center justify-center p-6 bg-gray-50 dark:bg-gray-900">
          <Card className="max-w-md w-full text-center p-8 space-y-6">
            <div className="p-4 bg-red-50 dark:bg-red-950/20 text-red-500 rounded-full inline-block">
              <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="space-y-2">
              <h2 className="text-xl font-extrabold text-gray-900 dark:text-white">
                Application Interface Error
              </h2>
              <p className="text-xs text-gray-500 leading-relaxed">
                An unhandled rendering exception occurred inside the client components stack.
              </p>
              {this.state.error && (
                <div className="p-3 bg-gray-100 dark:bg-gray-900 rounded text-left overflow-x-auto text-[10px] font-mono text-rose-500 max-h-36">
                  {this.state.error.toString()}
                </div>
              )}
            </div>
            <Button onClick={this.handleReload} className="w-full font-bold h-10 rounded-xl">
              Reload Interface
            </Button>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
