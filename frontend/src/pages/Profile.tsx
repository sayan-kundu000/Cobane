import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { useAuth } from '../hooks/useAuth.ts';
import { updateProfile, changePassword } from '../services/auth.ts';
import Card from '../components/ui/Card.tsx';
import { Input } from '../components/common/Input.tsx';
import { Button } from '../components/common/Button.tsx';

export const Profile: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [profileLoading, setProfileLoading] = useState(false);
  const [pwdLoading, setPwdLoading] = useState(false);

  // Forms setup
  const { register: regProfile, handleSubmit: handleProfileSubmit, setValue } = useForm();
  const { register: regPwd, handleSubmit: handlePwdSubmit, reset: resetPwd, watch, formState: { errors } } = useForm();
  
  const newPwdVal = watch('new_password');

  useEffect(() => {
    if (user) {
      const u = user as any;
      setValue('full_name', u.full_name || '');
      setValue('bio', u.bio || '');
    }
  }, [user, setValue]);

  const onProfileSave = async (data: any) => {
    try {
      setProfileLoading(true);
      const res = await updateProfile({
        full_name: data.full_name,
        bio: data.bio
      });
      if (res.success && res.data) {
        toast.success('Biographical profile updated!');
        updateUser({ ...user, ...res.data } as any);
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || err.message || 'Failed to update biography.');
    } finally {
      setProfileLoading(false);
    }
  };

  const onPasswordChange = async (data: any) => {
    try {
      setPwdLoading(true);
      const res = await changePassword({
        old_password: data.old_password,
        new_password: data.new_password
      });
      if (res.success) {
        toast.success('Account credentials successfully rotated!');
        resetPwd();
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || err.message || 'Failed to rotate password.');
    } finally {
      setPwdLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div className="p-6 bg-white dark:bg-gray-800 border border-gray-250 dark:border-gray-700/80 rounded-2xl shadow-sm">
        <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          User Profile
        </h1>
        <p className="text-sm text-gray-550 mt-1">
          Manage your author credentials, bio metadata, and password credentials.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Personal Bio Card */}
        <Card className="space-y-4">
          <div>
            <h3 className="text-sm font-bold text-gray-950 dark:text-white uppercase tracking-wider">
              Biography Details
            </h3>
            <p className="text-xs text-gray-500">Public profile identity details</p>
          </div>

          <form onSubmit={handleProfileSubmit(onProfileSave)} className="space-y-4">
            <Input
              label="Author Full Name"
              type="text"
              placeholder="e.g. John Doe"
              {...regProfile('full_name')}
            />
            <div className="space-y-1">
              <label className="text-xs font-bold uppercase tracking-wider text-gray-450">
                Author Bio Summary
              </label>
              <textarea
                className="w-full p-3 border border-gray-250 dark:border-gray-700 dark:bg-gray-900 rounded-xl text-sm focus:ring-1 focus:ring-primary-500 focus:outline-none dark:text-white"
                rows={3}
                placeholder="Developer bio summary details..."
                {...regProfile('bio')}
              />
            </div>
            <div className="flex justify-end pt-2">
              <Button type="submit" disabled={profileLoading} className="font-semibold px-4 text-xs h-9">
                {profileLoading ? 'Saving...' : 'Update Bio'}
              </Button>
            </div>
          </form>
        </Card>

        {/* Credentials Form Card */}
        <Card className="space-y-4">
          <div>
            <h3 className="text-sm font-bold text-gray-950 dark:text-white uppercase tracking-wider">
              Rotate Password
            </h3>
            <p className="text-xs text-gray-500">Rotate active session key credentials</p>
          </div>

          <form onSubmit={handlePwdSubmit(onPasswordChange)} className="space-y-4">
            <div className="space-y-1">
              <Input
                label="Old Password"
                type="password"
                placeholder="••••••••"
                {...regPwd('old_password', { required: 'Old password is required' })}
              />
              {errors.old_password && (
                <p className="text-xs text-rose-500 font-medium">{errors.old_password.message as string}</p>
              )}
            </div>

            <div className="space-y-1">
              <Input
                label="New Password"
                type="password"
                placeholder="••••••••"
                {...regPwd('new_password', {
                  required: 'New password is required',
                  minLength: { value: 6, message: 'Password must be at least 6 characters' }
                })}
              />
              {errors.new_password && (
                <p className="text-xs text-rose-500 font-medium">{errors.new_password.message as string}</p>
              )}
            </div>

            <div className="space-y-1">
              <Input
                label="Confirm Password"
                type="password"
                placeholder="••••••••"
                {...regPwd('confirm_password', {
                  required: 'Please confirm password',
                  validate: (val) => val === newPwdVal || 'Passwords do not match'
                })}
              />
              {errors.confirm_password && (
                <p className="text-xs text-rose-500 font-medium">{errors.confirm_password.message as string}</p>
              )}
            </div>

            <div className="flex justify-end pt-2">
              <Button type="submit" disabled={pwdLoading} className="font-semibold px-4 text-xs h-9">
                {pwdLoading ? 'Rotating...' : 'Rotate Credentials'}
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
