import React, { useState, useRef, useEffect } from 'react'

const ChatPanel = ({ messages, onSendMessage, isListening, isProcessing }) => {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !isProcessing) {
      onSendMessage(input.trim())
      setInput('')
    }
  }
  
  const quickCommands = [
    { label: 'SISTEMA', icon: '💻', command: 'información del sistema' },
    { label: 'NAVEGADOR', icon: '🌐', command: 'abrir navegador' },
    { label: 'CALC', icon: '🔢', command: 'abrir calculadora' },
    { label: 'ARCHIVOS', icon: '📁', command: 'abrir explorador' },
    { label: 'BLOQUEAR', icon: '🔒', command: 'bloquear pc' },
    { label: 'PROCESOS', icon: '⚡', command: 'mostrar procesos' },
    { label: 'VOLUMEN+', icon: '🔊', command: 'subir volumen' },
    { label: 'VOLUMEN-', icon: '🔉', command: 'bajar volumen' },
  ]
  
  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="header-left">
          <div className="header-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div className="header-text">
            <h2>COMUNICACIÓN</h2>
            <span className="header-subtitle">CANAL ENCRIPTADO</span>
          </div>
        </div>
        <div className="header-status">
          <span className="encryption-badge">AES-256</span>
          <span className="signal-bars">
            <span></span><span></span><span></span><span></span>
          </span>
        </div>
      </div>
      
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-screen">
            <div className="welcome-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            </div>
            <h3>INICIALIZACIÓN COMPLETADA</h3>
            <p>Sistema JARVIS listo para operar</p>
            <div className="welcome-divider"></div>
            <p className="welcome-hint">Escriba un comando o presione el micrófono</p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? (
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              )}
            </div>
            <div className="message-content">
              <div className="message-header">
                <span className="message-role">{msg.role === 'user' ? 'OPERADOR' : 'JARVIS'}</span>
                {msg.timestamp && (
                  <span className="message-time">
                    {new Date(msg.timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                )}
              </div>
              <div className="message-bubble">
                <div className="message-text">
                  {msg.content}
                  {!msg.complete && <span className="typing-cursor">▊</span>}
                </div>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="quick-commands">
        <div className="commands-label">ACCESO RÁPIDO</div>
        <div className="commands-grid">
          {quickCommands.map((cmd, idx) => (
            <button
              key={idx}
              className="quick-command"
              onClick={() => onSendMessage(cmd.command)}
              disabled={isProcessing}
            >
              <span className="cmd-icon">{cmd.icon}</span>
              <span className="cmd-label">{cmd.label}</span>
            </button>
          ))}
        </div>
      </div>
      
      <form className="input-container" onSubmit={handleSubmit}>
        <div className="input-wrapper">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? "Escuchando..." : "Ingrese comando..."}
            className="chat-input"
            disabled={isListening || isProcessing}
          />
          <div className="input-decoration"></div>
        </div>
        <button 
          type="submit" 
          className={`send-button ${isProcessing ? 'processing' : ''}`}
          disabled={!input.trim() || isListening || isProcessing}
        >
          {isProcessing ? (
            <div className="spinner"></div>
          ) : (
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          )}
        </button>
      </form>
    </div>
  )
}

export default ChatPanel
