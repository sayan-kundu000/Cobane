import React from 'react';
import { Input } from '../components/common/Input.tsx';
import { Button } from '../components/common/Button.tsx';

export const Auth: React.FC = () => {
  return (
    <div className="max-w-md mx-auto mt-20 p-6 bg-white rounded-lg shadow-md dark:bg-gray-800">
      <h2 className="text-2xl font-bold text-center mb-6">Sign In to Cobane</h2>
      <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
        <Input label="Email" type="email" placeholder="name@domain.com" />
        <Input label="Password" type="password" placeholder="••••••••" />
        <Button variant="primary" type="submit" className="w-full">Sign In</Button>
      </form>
    </div>
  );
};
export default Auth;
