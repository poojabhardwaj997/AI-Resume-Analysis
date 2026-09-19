import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '../services/supabaseClient';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch application profile from public.profiles table
  const fetchProfile = async (userId) => {
    if (!userId) {
      setProfile(null);
      return;
    }
    try {
      const { data, error: profileErr } = await supabase
        .table('profiles')
        .select('*')
        .eq('id', userId)
        .single();

      if (profileErr) {
        console.warn('[AuthContext] Profile fetch notice:', profileErr.message);
        // Fallback to auth metadata if profile trigger is delayed
        setProfile({
          id: userId,
          full_name: user?.user_metadata?.full_name || '',
          email: user?.email || '',
        });
      } else {
        setProfile(data);
      }
    } catch (err) {
      console.error('[AuthContext] Unexpected profile error:', err);
    }
  };

  useEffect(() => {
    // 1. Get initial session
    supabase.auth.getSession().then(({ data: { session: initSession }, error: sessionErr }) => {
      if (sessionErr) {
        console.error('[AuthContext] Session error:', sessionErr);
      }
      setSession(initSession);
      setUser(initSession?.user ?? null);
      if (initSession?.user) {
        fetchProfile(initSession.user.id);
      }
      setLoading(false);
    });

    // 2. Listen for auth state changes (login, logout, refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, currentSession) => {
      setSession(currentSession);
      const currentUser = currentSession?.user ?? null;
      setUser(currentUser);
      setError(null);

      if (currentUser) {
        await fetchProfile(currentUser.id);
      } else {
        setProfile(null);
      }
      setLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Sign up with Email, Password & Full Name
  const signUp = async ({ email, password, fullName }) => {
    setError(null);
    try {
      const { data, error: authError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });

      if (authError) throw authError;

      // If session immediately returned (email confirm disabled)
      if (data?.user) {
        setUser(data.user);
        await fetchProfile(data.user.id);
      }

      return { data, error: null };
    } catch (err) {
      setError(err.message);
      return { data: null, error: err };
    }
  };

  // Sign In with Email & Password
  const signIn = async ({ email, password }) => {
    setError(null);
    try {
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (authError) throw authError;

      setSession(data.session);
      setUser(data.user);
      if (data.user) {
        await fetchProfile(data.user.id);
      }

      return { data, error: null };
    } catch (err) {
      setError(err.message);
      return { data: null, error: err };
    }
  };

  // Sign Out
  const signOut = async () => {
    try {
      await supabase.auth.signOut();
    } catch (err) {
      console.error('[AuthContext] SignOut error:', err);
    } finally {
      setUser(null);
      setSession(null);
      setProfile(null);
      setError(null);
    }
  };

  // Request password reset email
  const resetPasswordForEmail = async (email) => {
    setError(null);
    try {
      const redirectUrl = `${window.location.origin}/reset-password`;
      const { data, error: resetErr } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: redirectUrl,
      });
      if (resetErr) throw resetErr;
      return { data, error: null };
    } catch (err) {
      setError(err.message);
      return { data: null, error: err };
    }
  };

  // Update password (used on /reset-password or /profile)
  const updatePassword = async (newPassword) => {
    setError(null);
    try {
      const { data, error: updateErr } = await supabase.auth.updateUser({
        password: newPassword,
      });
      if (updateErr) throw updateErr;
      return { data, error: null };
    } catch (err) {
      setError(err.message);
      return { data: null, error: err };
    }
  };

  // Update profile full name
  const updateProfile = async ({ fullName }) => {
    if (!user) return { error: new Error('User not logged in') };
    setError(null);
    try {
      const { error: dbErr } = await supabase
        .table('profiles')
        .update({ full_name: fullName, updated_at: new Date().toISOString() })
        .eq('id', user.id);

      if (dbErr) throw dbErr;

      // Update auth user metadata
      await supabase.auth.updateUser({
        data: { full_name: fullName },
      });

      setProfile((prev) => ({ ...prev, full_name: fullName }));
      return { error: null };
    } catch (err) {
      setError(err.message);
      return { error: err };
    }
  };

  const value = {
    user,
    session,
    profile,
    loading,
    error,
    signUp,
    signIn,
    signOut,
    resetPasswordForEmail,
    updatePassword,
    updateProfile,
    refreshProfile: () => user && fetchProfile(user.id),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
