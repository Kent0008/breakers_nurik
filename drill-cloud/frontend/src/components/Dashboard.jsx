import React, { useState, useEffect, useCallback } from 'react'
import {
  Grid,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Alert,
  Chip
} from '@mui/material'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from 'recharts'
import axios from 'axios'
import useWebSocket from '../hooks/useWebSocket'

function Dashboard() {
  const [selectedTags, setSelectedTags] = useState([])
  const [availableTags, setAvailableTags] = useState([])
  const [sensorData, setSensorData] = useState({})
  const [thresholds, setThresholds] = useState({})
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingTags, setLoadingTags] = useState(true)
  const [error, setError] = useState(null)

  const { messages, sendMessage, isConnected } = useWebSocket('/ws/monitoring/')

  // Загрузка доступных тегов
  useEffect(() => {
    const fetchTags = async () => {
      setLoadingTags(true)
      try {
        const response = await axios.get('/api/data/tags/', {
          timeout: 5000 // Таймаут 5 секунд
        })
        const tags = response.data.tags
        setAvailableTags(tags)
        
        // Автоматически выбираем первые 2 тега для производительности
        if (tags.length > 0 && selectedTags.length === 0) {
          setSelectedTags(tags.slice(0, 2))
        }
      } catch (err) {
        console.error('Ошибка загрузки тегов:', err)
        // Если не удалось загрузить теги, используем пустой массив
        setAvailableTags([])
      } finally {
        setLoadingTags(false)
      }
    }
    fetchTags()
  }, [selectedTags.length])

  // Загрузка данных сенсоров с дебаунсингом
  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      if (selectedTags.length === 0) return
      
      setLoading(true)
      try {
        const promises = selectedTags.map(tag =>
          axios.get(`/api/data/?tag=${tag}`)
        )
        const responses = await Promise.all(promises)
        
        const newData = {}
        responses.forEach((response, index) => {
          const rawData = response.data.results.map(item => ({
            timestamp: new Date(item.timestamp).toLocaleTimeString(),
            value: parseFloat(item.value)
          }))
          
          // Ограничиваем количество точек для производительности
          const maxPoints = 100
          const step = Math.max(1, Math.floor(rawData.length / maxPoints))
          newData[selectedTags[index]] = rawData.filter((_, index) => index % step === 0)
        })
        setSensorData(newData)
      } catch (err) {
        setError('Ошибка загрузки данных')
        console.error('Ошибка загрузки данных:', err)
      } finally {
        setLoading(false)
      }
    }, 300) // Дебаунсинг 300мс

    return () => clearTimeout(timeoutId)
  }, [selectedTags])

  // Загрузка уставок
  useEffect(() => {
    const fetchThresholds = async () => {
      try {
        const response = await axios.get('/api/thresholds/')
        const thresholdsMap = {}
        response.data.results.forEach(threshold => {
          thresholdsMap[threshold.tag] = {
            min: threshold.min_value,
            max: threshold.max_value
          }
        })
        setThresholds(thresholdsMap)
      } catch (err) {
        console.error('Ошибка загрузки уставок:', err)
      }
    }
    fetchThresholds()
  }, [])

  // Подписка на WebSocket обновления для выбранных тегов
  useEffect(() => {
    if (isConnected && selectedTags.length > 0) {
      selectedTags.forEach(tag => {
        sendMessage({
          type: 'subscribe_sensor',
          tag: tag
        })
      })
    }
  }, [isConnected, selectedTags, sendMessage])

  // Обработка WebSocket сообщений с ограничением
  useEffect(() => {
    messages.forEach(message => {
      try {
        const data = JSON.parse(message)
        console.log('WebSocket сообщение:', data)
        
        if (data.type === 'connection_established') {
          console.log('WebSocket подключен:', data.message)
        } else if (data.type === 'sensor_update') {
          setSensorData(prev => ({
            ...prev,
            [data.tag]: [...(prev[data.tag] || []), {
              timestamp: new Date(data.data.timestamp).toLocaleTimeString(),
              value: data.data.value
            }].slice(-20) // Ограничиваем до 20 последних точек
          }))
        } else if (data.type === 'incident_alert') {
          setIncidents(prev => [data.incident, ...prev.slice(0, 5)]) // Ограничиваем до 5 инцидентов
        }
      } catch (err) {
        console.error('Ошибка обработки WebSocket сообщения:', err)
      }
    })
  }, [messages])

  const handleTagChange = (event) => {
    const value = event.target.value
    const newTags = typeof value === 'string' ? value.split(',') : value
    
    // Ограничиваем до 3 тегов для производительности
    if (newTags.length <= 3) {
      setSelectedTags(newTags)
    }
  }

  const renderChart = useCallback((tag) => {
    const data = sensorData[tag] || []
    const threshold = thresholds[tag]

    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#2196f3"
            strokeWidth={2}
            dot={false}
            name={tag}
          />
          {threshold?.min && (
            <ReferenceLine
              y={threshold.min}
              stroke="#f44336"
              strokeDasharray="3 3"
              label="Мин"
            />
          )}
          {threshold?.max && (
            <ReferenceLine
              y={threshold.max}
              stroke="#f44336"
              strokeDasharray="3 3"
              label="Макс"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    )
  }, [sensorData, thresholds])

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">
          Мониторинг параметров
        </Typography>
        <Chip
          label={isConnected ? 'WebSocket подключен' : 'WebSocket отключен'}
          color={isConnected ? 'success' : 'error'}
          size="small"
        />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Выберите параметры (макс. 3)</InputLabel>
            <Select
              multiple
              value={selectedTags}
              onChange={handleTagChange}
              label="Выберите параметры (макс. 3)"
              inputProps={{ maxLength: 3 }}
              disabled={loadingTags}
            >
              {loadingTags ? (
                <MenuItem disabled>Загрузка тегов...</MenuItem>
              ) : (
                availableTags.map((tag) => (
                  <MenuItem key={tag} value={tag}>
                    {tag}
                  </MenuItem>
                ))
              )}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
            Выбрано: {selectedTags.length}/3 тегов. Для лучшей производительности рекомендуется выбирать не более 3 тегов одновременно.
          </Typography>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {selectedTags.map((tag) => (
          <Grid item xs={12} md={6} lg={4} key={tag}>
            <Paper sx={{ p: 2, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                {tag}
                <Typography variant="caption" display="block" color="textSecondary">
                  {sensorData[tag]?.length || 0} записей
                </Typography>
              </Typography>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
                  <Typography>Загрузка...</Typography>
                </Box>
              ) : (
                renderChart(tag)
              )}
            </Paper>
          </Grid>
        ))}
      </Grid>

      {incidents.length > 0 && (
        <Paper sx={{ p: 2, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Последние инциденты
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {incidents.map((incident, index) => (
              <Chip
                key={index}
                label={`${incident.tag}: ${incident.value} (${incident.violation_type})`}
                color="error"
                variant="outlined"
                size="small"
              />
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  )
}

export default Dashboard 