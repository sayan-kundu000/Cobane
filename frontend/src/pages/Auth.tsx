import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../hooks/useAuth.ts';
import { loginUser, registerUser, forgotPassword, resetPassword } from '../services/auth.ts';
import { Input } from '../components/common/Input.tsx';
import { Button } from '../components/common/Button.tsx';
import Alert from '../components/ui/Alert.tsx';

type AuthMode = 'login' | 'register' | 'forgot' | 'reset';

export const Auth: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [mode, setMode] = useState<AuthMode>('login');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, watch, reset, formState: { errors } } = useForm<any>({
    defaultValues: {
      email: 'admin@cobane.ai',
      password: 'admin123',
    }
  });
  
  const passwordVal = watch('password');

  // Synchronize mode with query parameters (?mode=login)
  useEffect(() => {
    const qMode = searchParams.get('mode');
    if (qMode === 'register' || qMode === 'forgot' || qMode === 'reset') {
      setMode(qMode as AuthMode);
    } else {
      setMode('login');
    }
    setError(null);
    reset({
      email: 'admin@cobane.ai',
      password: 'admin123',
    });
  }, [searchParams, reset]);

  const onSubmit = async (data: any) => {
    setError(null);
    setLoading(true);
    try {
      if (mode === 'login') {
        const res = await loginUser({ email: data.email, password: data.password });
        if (res.success && res.data) {
          login(res.data.access_token, res.data.user);
          toast.success('Successfully logged in!');
          navigate('/');
        } else {
          setError(res.message || 'Login failed.');
        }
      } else if (mode === 'register') {
        const res = await registerUser({
          email: data.email,
          username: data.username,
          password: data.password
        });
        if (res.success) {
          toast.success('Registration successful! Please sign in.');
          navigate('/auth?mode=login');
        } else {
          setError(res.message || 'Registration failed.');
        }
      } else if (mode === 'forgot') {
        const res = await forgotPassword({ email: data.email });
        if (res.success) {
          toast.success('If the account exists, a reset code was generated.');
          reset();
        } else {
          setError(res.message || 'Failed to request password reset.');
        }
      } else if (mode === 'reset') {
        const res = await resetPassword({
          token: data.token,
          new_password: data.password
        });
        if (res.success) {
          toast.success('Password updated successfully! Please login.');
          navigate('/auth?mode=login');
        } else {
          setError(res.message || 'Failed to reset password.');
        }
      }
    } catch (err: any) {
      console.error(err);
      setError(
        err.response?.data?.message ||
        err.message ||
        'An error occurred during authentication processing.'
      );
    } finally {
      setLoading(false);
    }
  };

  const getFormTitle = () => {
    switch (mode) {
      case 'register':
        return 'Create your account';
      case 'forgot':
        return 'Reset your password';
      case 'reset':
        return 'Setup a new password';
      default:
        return 'Sign in to Cobane';
    }
  };

  return (
    <div className="max-w-md w-full mx-auto mt-16 p-8 bg-white border border-gray-250 dark:border-gray-750 dark:bg-gray-800 rounded-2xl shadow-xl space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          {getFormTitle()}
        </h2>
        {mode === 'login' && (
          <p className="text-sm text-gray-500">
            Don't have an account?{' '}
            <button
              onClick={() => navigate('/auth?mode=register')}
              className="text-primary-600 hover:text-primary-700 font-bold outline-none"
            >
              Sign up
            </button>
          </p>
        )}
        {mode === 'register' && (
          <p className="text-sm text-gray-500">
            Already have an account?{' '}
            <button
              onClick={() => navigate('/auth?mode=login')}
              className="text-primary-600 hover:text-primary-700 font-bold outline-none"
            >
              Sign in
            </button>
          </p>
        )}
      </div>

      {error && (
        <Alert variant="danger" title="Authentication Error">
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {mode === 'register' && (
          <div className="space-y-1">
            <Input
              label="Username"
              type="text"
              placeholder="developer"
              {...register('username', {
                required: 'Username is required',
                minLength: { value: 3, message: 'Username must be at least 3 characters' }
              })}
            />
            {errors.username && (
              <p className="text-xs text-rose-500 font-medium">{errors.username.message as string}</p>
            )}
          </div>
        )}

        {(mode === 'login' || mode === 'register' || mode === 'forgot') && (
          <div className="space-y-1">
            <Input
              label="Email Address"
              type="email"
              placeholder="developer@cobane.ai"
              {...register('email', {
                required: 'Email address is required',
                pattern: {
                  value: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
                  message: 'Enter a valid email address'
                }
              })}
            />
            {errors.email && (
              <p className="text-xs text-rose-500 font-medium">{errors.email.message as string}</p>
            )}
          </div>
        )}

        {mode === 'reset' && (
          <div className="space-y-1">
            <Input
              label="Reset Code/Token"
              type="text"
              placeholder="e.g. token_hash"
              {...register('token', { required: 'Reset token is required' })}
            />
            {errors.token && (
              <p className="text-xs text-rose-500 font-medium">{errors.token.message as string}</p>
            )}
          </div>
        )}

        {(mode === 'login' || mode === 'register' || mode === 'reset') && (
          <div className="space-y-1">
            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              {...register('password', {
                required: 'Password is required',
                minLength: { value: 6, message: 'Password must be at least 6 characters' }
              })}
            />
            {errors.password && (
              <p className="text-xs text-rose-500 font-medium">{errors.password.message as string}</p>
            )}
          </div>
        )}

        {mode === 'register' && (
          <div className="space-y-1">
            <Input
              label="Confirm Password"
              type="password"
              placeholder="••••••••"
              {...register('confirmPassword', {
                required: 'Please confirm your password',
                validate: (val) => val === passwordVal || 'Passwords do not match'
              })}
            />
            {errors.confirmPassword && (
              <p className="text-xs text-rose-500 font-medium">{errors.confirmPassword.message as string}</p>
            )}
          </div>
        )}

        {mode === 'login' && (
          <div className="flex justify-end items-center">
            <button
              type="button"
              onClick={() => navigate('/auth?mode=forgot')}
              className="text-xs font-bold text-gray-500 hover:text-primary-600 outline-none"
            >
              Forgot Password?
            </button>
          </div>
        )}

        <Button
          variant="primary"
          type="submit"
          disabled={loading}
          className="w-full h-11 font-bold rounded-full mt-4"
        >
          {loading ? (
            <div className="flex items-center justify-center space-x-2">
              <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Processing...</span>
            </div>
          ) : mode === 'login' ? (
            'Sign In'
          ) : mode === 'register' ? (
            'Create Account'
          ) : mode === 'forgot' ? (
            'Send Reset Link'
          ) : (
            'Update Password'
          )}
        </Button>
      </form>

      {mode !== 'login' && (
        <div className="text-center pt-2">
          <button
            onClick={() => navigate('/auth?mode=login')}
            className="text-xs font-bold text-primary-600 hover:text-primary-700 outline-none"
          >
            ← Return to sign in
          </button>
        </div>
      )}
    </div>
  );
};

export default Auth;
