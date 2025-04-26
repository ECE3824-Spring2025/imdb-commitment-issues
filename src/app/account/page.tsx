'use client';

import { useEffect, useState } from 'react';
import {
  Container,
  Paper,
  Title,
  Divider,
  Text,
  Box,
  Group,
  Avatar,
  Menu,
  Button
} from '@mantine/core';
import { useRouter } from 'next/navigation';

export default function AccountPage() {
  const router = useRouter();
  const [username, setUsername] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [profileImage, setProfileImage] = useState<string | null>(null);

  useEffect(() => {
    setUsername(localStorage.getItem('username'));
    setEmail(localStorage.getItem('email'));
    setProfileImage(localStorage.getItem('profile_image'));
  }, []);

  const handleSignOut = () => {
    localStorage.clear();
    router.push('/');
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;

    const formData = new FormData();
    formData.append('image', e.target.files[0]);

    const userId = localStorage.getItem('user_id');
    const res = await fetch(`http://localhost:8000/api/upload_profile_image/${userId}`, {
      method: 'POST',
      body: formData
    });

    const data = await res.json();
    if (data.success) {
      setProfileImage(data.profile_image);
      localStorage.setItem('profile_image', data.profile_image);
    }
  };

  return (
    <Box>
      <Box
        px="md"
        py="sm"
        style={{ backgroundColor: '#f1f3f5', borderBottom: '1px solid #dee2e6' }}
      >
        <Group position="apart">
          <Title order={3} style={{ cursor: 'pointer' }} onClick={() => router.push('/')}>
            Commitment Issues
          </Title>

          <Menu shadow="md" width={200}>
            <Menu.Target>
              <Avatar
                src={profileImage ? `http://localhost:8000/${profileImage}` : undefined}
                color="blue"
                radius="xl"
                size="md"
                style={{ cursor: 'pointer' }}
              >
                {!profileImage && (username?.[0]?.toUpperCase() || 'U')}
              </Avatar>
            </Menu.Target>
            <Menu.Dropdown>
              <Menu.Label>Account</Menu.Label>
              <Menu.Item onClick={() => router.push('/account')}>User Info</Menu.Item>
              <Divider />
              <Menu.Item onClick={handleSignOut} color="red">Sign Out</Menu.Item>
            </Menu.Dropdown>
          </Menu>
        </Group>
      </Box>

      <Container size="sm" mt={40}>
        <Paper shadow="xs" p="lg">
          <Title order={3}>User Info</Title>
          <Divider my="sm" />
          <Text><strong>Username:</strong> {username || 'N/A'}</Text>
          <Text><strong>Email:</strong> {email || 'N/A'}</Text>

          <Divider my="md" />

          <Group mt="md" spacing="lg">
            <Avatar
              src={profileImage ? `http://localhost:8000/${profileImage}` : undefined}
              color="blue"
              radius="xl"
              size={64}
            >
              {!profileImage && (username?.[0]?.toUpperCase() || 'U')}
            </Avatar>
            <div>
              <Text><strong>Upload Profile Picture:</strong></Text>
              <input type="file" accept="image/*" onChange={handleUpload} />
            </div>
          </Group>
        </Paper>
      </Container>
    </Box>
  );
}
