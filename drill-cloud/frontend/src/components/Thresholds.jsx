import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Alert
} from '@mui/material'
import { Edit, Delete, Add } from '@mui/icons-material'
import axios from 'axios'

function Thresholds() {
  const [thresholds, setThresholds] = useState([])
  const [open, setOpen] = useState(false)
  const [editingThreshold, setEditingThreshold] = useState(null)
  const [formData, setFormData] = useState({
    tag: '',
    min_value: '',
    max_value: ''
  })
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  useEffect(() => {
    fetchThresholds()
  }, [])

  const fetchThresholds = async () => {
    try {
      const response = await axios.get('/api/thresholds/')
      setThresholds(response.data.results)
    } catch (err) {
      setError('Ошибка загрузки уставок')
      console.error('Ошибка загрузки уставок:', err)
    }
  }

  const handleOpen = (threshold = null) => {
    if (threshold) {
      setEditingThreshold(threshold)
      setFormData({
        tag: threshold.tag,
        min_value: threshold.min_value || '',
        max_value: threshold.max_value || ''
      })
    } else {
      setEditingThreshold(null)
      setFormData({
        tag: '',
        min_value: '',
        max_value: ''
      })
    }
    setOpen(true)
  }

  const handleClose = () => {
    setOpen(false)
    setEditingThreshold(null)
    setFormData({
      tag: '',
      min_value: '',
      max_value: ''
    })
    setError(null)
  }

  const handleSubmit = async () => {
    try {
      const data = {
        tag: formData.tag,
        min_value: formData.min_value ? parseFloat(formData.min_value) : null,
        max_value: formData.max_value ? parseFloat(formData.max_value) : null
      }

      if (editingThreshold) {
        await axios.put(`/api/thresholds/${editingThreshold.id}/`, data)
        setSuccess('Уставка обновлена')
      } else {
        await axios.post('/api/thresholds/', data)
        setSuccess('Уставка создана')
      }

      handleClose()
      fetchThresholds()
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка сохранения уставки')
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Вы уверены, что хотите удалить эту уставку?')) {
      try {
        await axios.delete(`/api/thresholds/${id}/`)
        setSuccess('Уставка удалена')
        fetchThresholds()
      } catch (err) {
        setError('Ошибка удаления уставки')
      }
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Управление уставками
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpen()}
        >
          Добавить уставку
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Параметр</TableCell>
              <TableCell align="right">Минимум</TableCell>
              <TableCell align="right">Максимум</TableCell>
              <TableCell align="center">Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {thresholds.map((threshold) => (
              <TableRow key={threshold.id}>
                <TableCell>{threshold.tag}</TableCell>
                <TableCell align="right">
                  {threshold.min_value || '-'}
                </TableCell>
                <TableCell align="right">
                  {threshold.max_value || '-'}
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    color="primary"
                    onClick={() => handleOpen(threshold)}
                  >
                    <Edit />
                  </IconButton>
                  <IconButton
                    color="error"
                    onClick={() => handleDelete(threshold.id)}
                  >
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingThreshold ? 'Редактировать уставку' : 'Добавить уставку'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Параметр"
            fullWidth
            variant="outlined"
            value={formData.tag}
            onChange={(e) => setFormData({ ...formData, tag: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Минимальное значение"
            type="number"
            fullWidth
            variant="outlined"
            value={formData.min_value}
            onChange={(e) => setFormData({ ...formData, min_value: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Максимальное значение"
            type="number"
            fullWidth
            variant="outlined"
            value={formData.max_value}
            onChange={(e) => setFormData({ ...formData, max_value: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Отмена</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingThreshold ? 'Обновить' : 'Создать'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Thresholds 