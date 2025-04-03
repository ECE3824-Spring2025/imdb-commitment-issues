'use client';

import { useState } from 'react';
import { TextInput, PasswordInput, Button, Title, Alert, Anchor } from '@mantine/core';
import { useRouter } from 'next/navigation';

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async () => {
    setError('');
    try {
      const res = await fetch('http://localhost:8000/api/signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
  
      const data = await res.json();
      if (data.success) {
        setSuccess(true);
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('username', data.username);
        localStorage.setItem('email', data.email);
        localStorage.setItem('profile_image', data.profile_image || '');
        setTimeout(() => router.push('/'), 1000);
      } else {
        setError(data.error || 'Invalid credentials');
      }
    } catch {
      setError('Server error');
    }
  };
  

  return (
    <div style={{ maxWidth: 400, margin: '50px auto' }}>
      <Title align="center" mb={20}>Sign In</Title>
      <TextInput
        label="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <PasswordInput
        label="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        mt="sm"
      />
      <Button fullWidth mt="md" onClick={handleSubmit}>
        Sign In
      </Button>

      <div style={{ marginTop: '10px', textAlign: 'center' }}>
        Don’t have an account?{' '}
        <Anchor onClick={() => router.push('/signup')}>Sign Up</Anchor>
      </div>

      {error && <Alert color="red" mt="md">{error}</Alert>}
      {success && <Alert color="green" mt="md">Login successful!</Alert>}
    </div>
  );
}
