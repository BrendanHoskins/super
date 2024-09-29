import React from 'react';
import { Box } from '@mui/material';
import Header from './Header';
import { Outlet } from 'react-router-dom';

const Layout = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Box component="main" sx={{ flexGrow: 1, pt: 8, px: 3 }}>
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;
