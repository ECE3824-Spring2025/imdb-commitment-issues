'use client';

import React, { useEffect, useState } from 'react';
import {
  Group,
  Title,
  Box,
  Container,
  Menu,
  Avatar,
  Button,
  Divider
} from '@mantine/core';
import {
  IconLogout,
  IconSettings,
  IconSun,
  IconMoon,
  IconUser
} from '@tabler/icons-react';
import SortBy from '@/components/discover';
import Format from '@/components/format';
import Filter from '@/components/filter';
import Search from '@/components/search';
import { useRouter } from 'next/navigation';
import { useColorScheme, useLocalStorage } from '@mantine/hooks';

interface MenuProps {
  width?: number;
  buttonSpacing?: number;
}

export default function NavigationBar({ width, buttonSpacing = 24 }: MenuProps) {
  const router = useRouter();
  const preferredColorScheme = useColorScheme();
  const [colorScheme, setColorScheme] = useLocalStorage<'light' | 'dark'>({
    key: 'color-scheme',
    defaultValue: preferredColorScheme || 'light',
  });

  const toggleColorScheme = () => {
    setColorScheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const [username, setUsername] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [profilePic, setProfilePic] = useState<string | null>(null);

  useEffect(() => {
    const storedUsername = localStorage.getItem('username');
    const storedEmail = localStorage.getItem('email');
    const storedProfileImage = localStorage.getItem('profile_image'); // <- FIXED KEY
    console.log('[menu.tsx] Loaded profile_image:', storedProfileImage);

    setUsername(storedUsername);
    setEmail(storedEmail);
    setProfilePic(storedProfileImage); // <- FIXED
  }, []);

  const handleSignOut = () => {
    localStorage.clear();
    setUsername(null);
    setEmail(null);
    setProfilePic(null);
    router.push('/');
  };

  return (
    <Box mb={24}>
      <Box
        px="lg"
        py="md"
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
      >
        <div style={{ width: 100 }} />

        <Title
          size={28}
          style={{ textAlign: 'center', flexGrow: 1, cursor: 'pointer' }}
          onClick={() => router.push('/')}
        >
          Commitment Issues
        </Title>

        {username ? (
          <Menu shadow="md" width={200}>
            <Menu.Target>
              <Avatar
                src={profilePic && profilePic !== 'null' ? `http://localhost:8000/${profilePic}` : undefined}
                radius="xl"
                color="blue"
                style={{ cursor: 'pointer' }}
              >
                {username[0].toUpperCase()}
              </Avatar>
            </Menu.Target>
            <Menu.Dropdown>
              <Menu.Label>Account</Menu.Label>
              <Menu.Item icon={<IconUser size={14} />} onClick={() => router.push('/account')}>
                User Info
              </Menu.Item>
              <Menu.Item
                icon={colorScheme === 'dark' ? <IconSun size={14} /> : <IconMoon size={14} />}
                onClick={toggleColorScheme}
              >
                {colorScheme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </Menu.Item>
              <Divider />
              <Menu.Item icon={<IconLogout size={14} />} color="red" onClick={handleSignOut}>
                Sign Out
              </Menu.Item>
            </Menu.Dropdown>
          </Menu>
        ) : (
          <Group spacing="xs">
            <Button variant="subtle" onClick={() => router.push('/signin')}>
              Sign In
            </Button>
            <Button variant="outline" onClick={() => router.push('/signup')}>
              Sign Up
            </Button>
          </Group>
        )}
      </Box>

      <Container size={width || 'xl'} px={3} style={{ margin: '0 auto' }}>
        <Title size={20} mb={16}>Top Movies</Title>
        <Group spacing={buttonSpacing} align="flex-end" noWrap={false}>
          <Search />
          <Format />
          <SortBy />
          <Filter />
        </Group>
      </Container>
    </Box>
  );
}
