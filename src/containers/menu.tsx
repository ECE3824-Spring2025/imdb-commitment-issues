'use client';
import React from 'react';
import { Group, Title, Box, Container } from '@mantine/core';
import SortBy from '@/components/discover';
import Format from '@/components/format';
import Filter from '@/components/filter';
import Search from '@/components/search';

interface MenuProps {
  width?: number;
  buttonSpacing?: number; // Add prop for adjustable spacing between buttons
}

export default function NavigationBar({ width, buttonSpacing = 24 }: MenuProps) {
  return (
    <Box mb={24}>
      <Title size={28} mt={15} mb={13} ta="center">Commitment Issues</Title>
      <Container size={width || "xl"} px={3} style={{ margin: '0 auto' }}>
        <Title size={20} mb={16}>Top Movies</Title>

        {/* Navigation Buttons - Side by Side with adjustable spacing */}
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