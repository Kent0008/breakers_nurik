import { useState, useEffect, useRef } from 'react'

function useWebSocket(url) {
  const [messages, setMessages] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(url)
        wsRef.current = ws

        ws.onopen = () => {
          console.log('WebSocket подключен')
          setIsConnected(true)
        }

        ws.onmessage = (event) => {
          setMessages(prev => [...prev, event.data])
        }

        ws.onclose = () => {
          console.log('WebSocket отключен')
          setIsConnected(false)
          // Попытка переподключения через 5 секунд
          setTimeout(connect, 5000)
        }

        ws.onerror = (error) => {
          console.error('WebSocket ошибка:', error)
          setIsConnected(false)
        }
      } catch (error) {
        console.error('Ошибка подключения WebSocket:', error)
        setIsConnected(false)
      }
    }

    connect()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [url])

  const sendMessage = (message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }

  return {
    messages,
    isConnected,
    sendMessage
  }
}

export default useWebSocket 