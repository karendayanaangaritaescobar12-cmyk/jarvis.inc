import React, { useState, useEffect, useRef } from 'react'
import JarvisUI from './components/JarvisUI'
import ChatPanel from './components/ChatPanel'
import HolographicDisplay from './components/HolographicDisplay'
import ParticleBackground from './components/ParticleBackground'

function App() {
  const [isListening, setIsListening] = useState(false)
  const [messages, setMessages] = useState([])
  const [systemInfo, setSystemInfo] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())
  const wsRef = useRef(null)

  useEffect(() => {
    connectWebSocket()
    fetchSystemInfo()
    
    const timeInterval = setInterval(() => setCurrentTime(new Date()), 1000)
    const infoInterval = setInterval(fetchSystemInfo, 5000)
    
    return () => {
      if (wsRef.current) wsRef.current.close()
      clearInterval(timeInterval)
      clearInterval(infoInterval)
    }
  }, [])

  const connectWebSocket = () => {
    const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws`)
    
    ws.onopen = () => {
      setIsConnected(true)
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'stream') {
        setIsProcessing(true)
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1]
          if (lastMsg && lastMsg.role === 'assistant' && !lastMsg.complete) {
            return [...prev.slice(0, -1), {
              ...lastMsg,
              content: lastMsg.content + data.content
            }]
          }
          return [...prev, { role: 'assistant', content: data.content, complete: false }]
        })
      } else if (data.type === 'complete') {
        setIsProcessing(false)
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1]
          if (lastMsg && lastMsg.role === 'assistant') {
            return [...prev.slice(0, -1), { ...lastMsg, complete: true }]
          }
          return prev
        })
      } else if (data.type === 'voice_result' && data.text) {
        sendMessage(data.text, true)
      }
    }
    
    ws.onclose = () => {
      setIsConnected(false)
      setTimeout(connectWebSocket, 3000)
    }
    
    wsRef.current = ws
  }

  const fetchSystemInfo = async () => {
    try {
      const res = await fetch('http://localhost:8000/status')
      const data = await res.json()
      setSystemInfo(data)
    } catch (err) {
      console.error('Failed to fetch system info:', err)
    }
  }

  const sendMessage = async (text, voice = false) => {
    const userMessage = { role: 'user', content: text, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
    setIsProcessing(true)
    
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'chat',
        message: text,
        voice: voice
      }))
    }
  }

  const startListening = async () => {
    setIsListening(true)
    try {
      const res = await fetch('http://localhost:8000/voice/listen', { method: 'POST' })
      const data = await res.json()
      if (data.text) {
        sendMessage(data.text, true)
      }
    } catch (err) {
      console.error('Voice error:', err)
    }
    setIsListening(false)
  }

  return (
    <div className="jarvis-container">
      <ParticleBackground />
      
      <div className="main-content">
        <div className="left-panel">
          <div className="top-bar">
            <div className="system-status">
              <span className={`status-indicator ${isConnected ? 'online' : 'offline'}`}></span>
              <span className="status-label">{isConnected ? 'SISTEMA ACTIVO' : 'DESCONECTADO'}</span>
            </div>
            <div className="time-display">
              <span className="time">{currentTime.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
              <span className="date">{currentTime.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
            </div>
          </div>
          
          <JarvisUI 
            isListening={isListening}
            isConnected={isConnected}
            isProcessing={isProcessing}
            onStartListening={startListening}
            systemInfo={systemInfo}
          />
          
          <HolographicDisplay systemInfo={systemInfo} />
        </div>
        
        <ChatPanel 
          messages={messages}
          onSendMessage={sendMessage}
          isListening={isListening}
          isProcessing={isProcessing}
        />
      </div>
    </div>
  )
}

export default App
