import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Button, Box } from '@mui/material'
import { Monitor, Settings } from '@mui/icons-material'

function Navigation() {
  const location = useLocation()

  return (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <Button
        component={Link}
        to="/"
        color="inherit"
        startIcon={<Monitor />}
        variant={location.pathname === '/' ? 'contained' : 'text'}
      >
        Дашборд
      </Button>
      <Button
        component={Link}
        to="/thresholds"
        color="inherit"
        startIcon={<Settings />}
        variant={location.pathname === '/thresholds' ? 'contained' : 'text'}
      >
        Уставки
      </Button>
    </Box>
  )
}

export default Navigation 