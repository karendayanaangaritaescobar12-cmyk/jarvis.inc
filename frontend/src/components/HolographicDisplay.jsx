import React from 'react'

const HolographicDisplay = ({ systemInfo }) => {
  const memoryPercent = systemInfo?.system?.memory?.percent || 0
  const cpuPercent = systemInfo?.system?.cpu_percent || 0
  const batteryInfo = systemInfo?.system?.battery
  
  return (
    <div className="holographic-display">
      <div className="holo-header">
        <span className="holo-title">PANEL DE DIAGNÓSTICO</span>
        <span className="holo-line"></span>
      </div>
      
      <div className="holo-grid">
        <div className="holo-card">
          <div className="holo-card-icon cpu">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="4" y="4" width="16" height="16" rx="2"/>
              <rect x="9" y="9" width="6" height="6"/>
              <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>
            </svg>
          </div>
          <div className="holo-card-content">
            <span className="holo-label">CPU</span>
            <div className="holo-bar">
              <div className="holo-bar-fill" style={{ width: `${cpuPercent}%` }}></div>
            </div>
            <span className="holo-value">{cpuPercent.toFixed(1)}%</span>
          </div>
        </div>
        
        <div className="holo-card">
          <div className="holo-card-icon memory">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="2" y="6" width="20" height="12" rx="2"/>
              <path d="M6 6V4M10 6V4M14 6V4M18 6V4M6 18v2M10 18v2M14 18v2M18 18v2"/>
            </svg>
          </div>
          <div className="holo-card-content">
            <span className="holo-label">MEMORIA</span>
            <div className="holo-bar">
              <div className="holo-bar-fill memory" style={{ width: `${memoryPercent}%` }}></div>
            </div>
            <span className="holo-value">{memoryPercent.toFixed(1)}%</span>
          </div>
        </div>
        
        {batteryInfo && (
          <div className="holo-card">
            <div className="holo-card-icon battery">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="1" y="6" width="18" height="12" rx="2"/>
                <path d="M23 10v4"/>
                <rect x="3" y="8" width={batteryInfo.percent * 0.14} height="8" fill="currentColor"/>
              </svg>
            </div>
            <div className="holo-card-content">
              <span className="holo-label">BATERÍA</span>
              <div className="holo-bar">
                <div className="holo-bar-fill battery" style={{ width: `${batteryInfo.percent}%` }}></div>
              </div>
              <span className="holo-value">{batteryInfo.percent}%</span>
            </div>
          </div>
        )}
        
        <div className="holo-card">
          <div className="holo-card-icon network">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div className="holo-card-content">
            <span className="holo-label">PROVEEDOR</span>
            <span className="holo-value small">{systemInfo?.provider?.toUpperCase() || 'N/A'}</span>
          </div>
        </div>
      </div>
      
      <div className="holo-scan-line"></div>
    </div>
  )
}

export default HolographicDisplay
