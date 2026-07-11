import React, { useEffect, useRef } from 'react'

const JarvisUI = ({ isListening, isConnected, isProcessing, onStartListening, systemInfo }) => {
  const canvasRef = useRef(null)
  
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    const size = 400
    canvas.width = size
    canvas.height = size
    
    let rotation = 0
    let animationFrame
    let pulsePhase = 0
    
    const drawArcReactor = () => {
      ctx.clearRect(0, 0, size, size)
      const center = size / 2
      
      // Outer glow
      const gradient = ctx.createRadialGradient(center, center, 0, center, center, 180)
      gradient.addColorStop(0, isListening ? 'rgba(0, 255, 136, 0.1)' : 'rgba(0, 212, 255, 0.1)')
      gradient.addColorStop(1, 'transparent')
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, size, size)
      
      // Outer ring with segments
      ctx.save()
      ctx.translate(center, center)
      ctx.rotate(rotation)
      
      for (let i = 0; i < 12; i++) {
        const angle = (i / 12) * Math.PI * 2
        ctx.save()
        ctx.rotate(angle)
        
        ctx.beginPath()
        ctx.moveTo(0, -160)
        ctx.lineTo(0, -140)
        ctx.strokeStyle = isListening ? '#00ff88' : '#00d4ff'
        ctx.lineWidth = 3
        ctx.lineCap = 'round'
        ctx.stroke()
        
        ctx.restore()
      }
      
      // Rotating arcs
      for (let ring = 0; ring < 4; ring++) {
        const radius = 130 - ring * 25
        const arcLength = Math.PI * (0.3 + ring * 0.1)
        const startAngle = rotation * (1 + ring * 0.5)
        
        ctx.beginPath()
        ctx.arc(0, 0, radius, startAngle, startAngle + arcLength)
        ctx.strokeStyle = ring % 2 === 0 ? '#00d4ff' : '#0088aa'
        ctx.lineWidth = 2 + ring * 0.5
        ctx.lineCap = 'round'
        ctx.stroke()
      }
      
      ctx.restore()
      
      // Inner hexagon
      ctx.save()
      ctx.translate(center, center)
      ctx.rotate(-rotation * 0.5)
      
      ctx.beginPath()
      for (let i = 0; i < 6; i++) {
        const angle = (i / 6) * Math.PI * 2 - Math.PI / 2
        const x = Math.cos(angle) * 80
        const y = Math.sin(angle) * 80
        if (i === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      }
      ctx.closePath()
      ctx.strokeStyle = isListening ? '#00ff88' : '#00d4ff'
      ctx.lineWidth = 2
      ctx.stroke()
      
      ctx.restore()
      
      // Inner circles with pulse
      const pulseSize = isProcessing ? 45 + Math.sin(pulsePhase) * 5 : 45
      
      ctx.beginPath()
      ctx.arc(center, center, pulseSize, 0, Math.PI * 2)
      ctx.strokeStyle = isListening ? '#00ff88' : isProcessing ? '#ffaa00' : '#00d4ff'
      ctx.lineWidth = 2
      ctx.stroke()
      
      ctx.beginPath()
      ctx.arc(center, center, 30, 0, Math.PI * 2)
      ctx.strokeStyle = isListening ? '#00ff88' : '#00d4ff'
      ctx.lineWidth = 1.5
      ctx.stroke()
      
      // Center core
      const coreGradient = ctx.createRadialGradient(center, center, 0, center, center, 20)
      if (isListening) {
        coreGradient.addColorStop(0, '#00ff88')
        coreGradient.addColorStop(0.5, '#00cc66')
        coreGradient.addColorStop(1, 'rgba(0, 255, 136, 0)')
      } else if (isProcessing) {
        coreGradient.addColorStop(0, '#ffaa00')
        coreGradient.addColorStop(0.5, '#ff8800')
        coreGradient.addColorStop(1, 'rgba(255, 170, 0, 0)')
      } else {
        coreGradient.addColorStop(0, '#00d4ff')
        coreGradient.addColorStop(0.5, '#0088cc')
        coreGradient.addColorStop(1, 'rgba(0, 212, 255, 0)')
      }
      
      ctx.beginPath()
      ctx.arc(center, center, 20, 0, Math.PI * 2)
      ctx.fillStyle = coreGradient
      ctx.fill()
      
      // Data points
      for (let i = 0; i < 8; i++) {
        const angle = (i / 8) * Math.PI * 2 + rotation * 2
        const x = center + Math.cos(angle) * 95
        const y = center + Math.sin(angle) * 95
        
        ctx.beginPath()
        ctx.arc(x, y, 3, 0, Math.PI * 2)
        ctx.fillStyle = isListening ? '#00ff88' : '#00d4ff'
        ctx.fill()
        
        // Connection lines to center
        ctx.beginPath()
        ctx.moveTo(x, y)
        ctx.lineTo(
          center + Math.cos(angle) * 35,
          center + Math.sin(angle) * 35
        )
        ctx.strokeStyle = isListening ? 'rgba(0, 255, 136, 0.3)' : 'rgba(0, 212, 255, 0.3)'
        ctx.lineWidth = 1
        ctx.stroke()
      }
      
      // Scanning line effect
      if (isProcessing) {
        const scanAngle = (Date.now() / 500) % (Math.PI * 2)
        ctx.beginPath()
        ctx.moveTo(center, center)
        ctx.lineTo(
          center + Math.cos(scanAngle) * 150,
          center + Math.sin(scanAngle) * 150
        )
        ctx.strokeStyle = 'rgba(255, 170, 0, 0.5)'
        ctx.lineWidth = 2
        ctx.stroke()
      }
      
      rotation += 0.008
      pulsePhase += 0.1
      animationFrame = requestAnimationFrame(drawArcReactor)
    }
    
    drawArcReactor()
    
    return () => {
      if (animationFrame) cancelAnimationFrame(animationFrame)
    }
  }, [isListening, isConnected, isProcessing])
  
  return (
    <div className="jarvis-ui">
      <div className="arc-reactor-container">
        <canvas ref={canvasRef} className="arc-reactor-canvas" />
        
        <div className="reactor-ring outer"></div>
        <div className="reactor-ring middle"></div>
        <div className="reactor-ring inner"></div>
      </div>
      
      <div className="jarvis-controls">
        <button 
          className={`control-button voice ${isListening ? 'active' : ''}`}
          onClick={onStartListening}
          disabled={!isConnected || isProcessing}
        >
          <div className="button-ring"></div>
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
          </svg>
          <span>{isListening ? 'ESCUCHANDO' : 'MICRÓFONO'}</span>
        </button>
        
        <div className={`status-display ${isConnected ? 'online' : 'offline'}`}>
          <div className="status-pulse"></div>
          <span className="status-text">{isConnected ? 'JARVIS ONLINE' : 'JARVIS OFFLINE'}</span>
        </div>
        
        {isProcessing && (
          <div className="processing-indicator">
            <div className="processing-bar">
              <div className="processing-fill"></div>
            </div>
            <span>PROCESANDO</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default JarvisUI
