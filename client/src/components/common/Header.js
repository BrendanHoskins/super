import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { AppBar, Toolbar, Button, Box, IconButton, Menu, MenuItem } from '@mui/material';
import { Person as PersonIcon } from '@mui/icons-material';
import { logout } from '../../services/AuthService';
import { useNavigate } from 'react-router-dom';

function Header() {
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();

  const menuItems = [
    { label: 'Messages', path: '/messages' },
    { label: 'Integrations', path: '/integrations' }
  ];

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    handleMenuClose();
    navigate('/login'); // Redirect to login page after logout
  };

  return (
    <AppBar position="fixed" color="primary">
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          component={RouterLink}
          to="/"
          sx={{ mr: 2 }}
        >
          <img src="/favicon.svg" alt="Logo" style={{ height: '32px' }} />
        </IconButton>
        <Box sx={{ flexGrow: 1 }}>
          {menuItems.map((item) => (
            <Button
              key={item.label}
              color="inherit"
              component={RouterLink}
              to={item.path}
              sx={{ mx: 1.5 }}
            >
              {item.label}
            </Button>
          ))}
        </Box>
        <IconButton
          edge="end"
          color="inherit"
          aria-label="account of current user"
          aria-controls={anchorEl ? 'account-menu' : undefined}
          aria-haspopup="true"
          onClick={handleMenuOpen}
        >
          <PersonIcon sx={{ fontSize: '1.25em' }} />
        </IconButton>
        <Menu
          id="account-menu"
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          keepMounted
        >
          <MenuItem onClick={handleLogout}>Logout</MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
