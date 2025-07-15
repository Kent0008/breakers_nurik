import React, { useState, useEffect } from 'react'
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
  const [selectedTags, setSelectedTags] = useState(['pressure_1'])
  const [availableTags, setAvailableTags] = useState([])
  const [sensorData, setSensorData] = useState({})
  const [thresholds, setThresholds] = useState({})
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const { messages, sendMessage } = useWebSocket('ws://localhost:8000/ws/monitoring/')

  // Загрузка доступных тегов
  useEffect(() => {
    const fetchTags = async () => {
      try {
        const response = await axios.get('/api/data/tags/')
        setAvailableTags(response.data.tags)
      } catch (err) {
        console.error('Ошибка загрузки тегов:', err)
      }
    }
    fetchTags()
  }, [])

  // Загрузка данных сенсоров
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const promises = selectedTags.map(tag =>
          axios.get(`/api/data/?tag=${tag}&range=1h`)
        )
        const responses = await Promise.all(promises)
        
        const newData = {}
        responses.forEach((response, index) => {
          newData[selectedTags[index]] = response.data.results.map(item => ({
            timestamp: new Date(item.timestamp).toLocaleTimeString(),
            value: parseFloat(item.value)
          }))
        })
        setSensorData(newData)
      } catch (err) {
        setError('Ошибка загрузки данных')
        console.error('Ошибка загрузки данных:', err)
      } finally {
        setLoading(false)
      }
    }

    if (selectedTags.length > 0) {
      fetchData()
    }
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

  // Обработка WebSocket сообщений
  useEffect(() => {
    messages.forEach(message => {
      const data = JSON.parse(message)
      
      if (data.type === 'sensor_update') {
        setSensorData(prev => ({
          ...prev,
          [data.tag]: [...(prev[data.tag] || []), {
            timestamp: new Date(data.data.timestamp).toLocaleTimeString(),
            value: data.data.value
          }].slice(-50) // Ограничиваем количество точек
        }))
      } else if (data.type === 'incident_alert') {
        setIncidents(prev => [data.incident, ...prev.slice(0, 9)])
      }
    })
  }, [messages])

  const handleTagChange = (event) => {
    const value = event.target.value
    setSelectedTags(typeof value === 'string' ? value.split(',') : value)
  }

  const renderChart = (tag) => {
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
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Мониторинг параметров
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Выберите параметры</InputLabel>
            <Select
              multiple
              value={selectedTags}
              onChange={handleTagChange}
              label="Выберите параметры"
            >
              {availableTags.map((tag) => (
                <MenuItem key={tag} value={tag}>
                  {tag}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {selectedTags.map((tag) => (
          <Grid item xs={12} md={6} lg={4} key={tag}>
            <Paper sx={{ p: 2, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                {tag}
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