'use client';

import { useState } from 'react';
import { TextInput, PasswordInput, Button, Title, Alert, Anchor } from '@mantine/core';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://3.219.44.117:5001/api';

export default function SignUpPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSignup = async () => {
    setError('');
    try {
      const res = await fetch(`${API_URL}/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, username }),
      });

      const data = await res.json();
      if (data.success) {
        setSuccess(true);
        setTimeout(() => router.push('/signin'), 1000);
      } else {
        setError(data.error || 'Signup failed');
      }
    } catch {
      setError('Server error. Please try again.');
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '50px auto' }}>
      <Title align="center" mb={20}>Sign Up</Title>

      <TextInput
        label="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
      />

      <TextInput
        label="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        mt="sm"
      />

      <PasswordInput
        label="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        mt="sm"
      />

      <Button fullWidth mt="md" onClick={handleSignup}>
        Sign Up
      </Button>

      <div style={{ marginTop: '10px', textAlign: 'center' }}>
        Already have an account?{' '}
        <Anchor onClick={() => router.push('/signin')}>Sign In</Anchor>
      </div>

      {error && <Alert color="red" mt="md">{error}</Alert>}
      {success && <Alert color="green" mt="md">Account created!</Alert>}
    </div>
  );
}
