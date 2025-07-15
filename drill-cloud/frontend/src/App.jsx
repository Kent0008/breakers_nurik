import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box, AppBar, Toolbar, Typography, Container } from '@mui/material'
import { Monitor, Settings } from '@mui/icons-material'
import Dashboard from './components/Dashboard'
import Thresholds from './components/Thresholds'
import Navigation from './components/Navigation'

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Monitor sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            DRILL Monitoring
          </Typography>
          <Navigation />
        </Toolbar>
      </AppBar>
      
      <Container component="main" sx={{ flexGrow: 1, py: 3 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/thresholds" element={<Thresholds />} />
        </Routes>
      </Container>
    </Box>
  )
}

export default App 