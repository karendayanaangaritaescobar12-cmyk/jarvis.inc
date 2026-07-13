import os
import json
import asyncio
import datetime
import psutil
from typing import Dict, List, Optional


class SelfMonitor:
    """Background self-monitoring system for JARVIS consciousness."""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.baselines_file = os.path.join(self.data_dir, "system_baselines.json")
        self.monitor_file = os.path.join(self.data_dir, "monitor_log.json")
        self.baselines = self._load_baselines()
        self.monitor_log = self._load_log()
        self.last_check = None
        self.alerts = []

    def _load_baselines(self) -> dict:
        if os.path.exists(self.baselines_file):
            try:
                with open(self.baselines_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {
            "cpu_normal": 50,
            "memory_normal": 70,
            "disk_normal": 80,
            "last_full_scan": None,
            "user_active_hours": [],
            "common_processes": [],
        }

    def _load_log(self) -> list:
        if os.path.exists(self.monitor_file):
            try:
                with open(self.monitor_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save_baselines(self):
        with open(self.baselines_file, "w") as f:
            json.dump(self.baselines, f, ensure_ascii=False, indent=2)

    def _save_log(self):
        self.monitor_log = self.monitor_log[-200:]
        with open(self.monitor_file, "w") as f:
            json.dump(self.monitor_log, f, ensure_ascii=False, indent=2)

    def get_system_status(self) -> Dict:
        """Get current system status for consciousness."""
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            processes = len(psutil.pids())
            
            net = psutil.net_io_counters()
            
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            
            return {
                "cpu_percent": cpu,
                "memory_percent": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 1),
                "memory_total_gb": round(memory.total / (1024**3), 1),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 1),
                "processes": processes,
                "network_sent_mb": round(net.bytes_sent / (1024**2), 1),
                "network_recv_mb": round(net.bytes_recv / (1024**2), 1),
                "uptime_hours": round(uptime.total_seconds() / 3600, 1),
                "timestamp": datetime.datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    def detect_anomalies(self) -> List[str]:
        """Detect system anomalies based on baselines."""
        status = self.get_system_status()
        anomalies = []
        
        if status.get("cpu_percent", 0) > 90:
            anomalies.append(f"CPU al {status['cpu_percent']}% - posibles procesos pesados")
        elif status.get("cpu_percent", 0) > self.baselines.get("cpu_normal", 50) * 1.5:
            anomalies.append(f"CPU inusualmente alto: {status['cpu_percent']}%")
        
        if status.get("memory_percent", 0) > 90:
            anomalies.append(f"Memoria al {status['memory_percent']}% - posible fuga de memoria")
        
        if status.get("disk_free_gb", 999) < 10:
            anomalies.append(f"Disco casi lleno: {status['disk_free_gb']} GB libres")
        
        if status.get("processes", 0) > 500:
            anomalies.append(f"Muchos procesos activos: {status['processes']}")
        
        self.alerts = anomalies
        return anomalies

    def generate_report(self) -> str:
        """Generate a system report for JARVIS to use in conversations."""
        status = self.get_system_status()
        anomalies = self.detect_anomalies()
        
        report = f"REPORTE DEL SISTEMA ({datetime.datetime.now().strftime('%H:%M')}):\n"
        report += f"- CPU: {status.get('cpu_percent', '?')}%\n"
        report += f"- Memoria: {status.get('memory_percent', '?')}% ({status.get('memory_used_gb', '?')}/{status.get('memory_total_gb', '?')} GB)\n"
        report += f"- Disco: {status.get('disk_percent', '?')}% usado, {status.get('disk_free_gb', '?')} GB libres\n"
        report += f"- Procesos activos: {status.get('processes', '?')}\n"
        report += f"- Red: {status.get('network_sent_mb', '?')} MB enviados, {status.get('network_recv_mb', '?')} MB recibidos\n"
        report += f"- Tiempo encendido: {status.get('uptime_hours', '?')} horas\n"
        
        if anomalies:
            report += "\nANOMALIAS DETECTADAS:\n"
            for a in anomalies:
                report += f"  - {a}\n"
        else:
            report += "\nSistema operando en rangos normales.\n"
        
        return report

    def get_anticipation_context(self) -> str:
        """Generate context for JARVIS to anticipate user needs."""
        hour = datetime.datetime.now().hour
        status = self.get_system_status()
        anomalies = self.detect_anomalies()
        
        context = []
        
        if 12 <= hour <= 14:
            context.append("Es hora de almuerzo. El usuario podria querer una pausa.")
        elif hour >= 23:
            context.append("Es tarde. El usuario deberia descansar.")
        elif 6 <= hour <= 8:
            context.append("Temprano. El usuario podria necesitar un resumen del dia.")
        
        if status.get("cpu_percent", 0) > 80:
            context.append("El sistema esta trabajando duro. Podria haber tareas pesadas en ejecucion.")
        elif status.get("cpu_percent", 0) < 10:
            context.append("El sistema esta inactivo. Podria ser buen momento para tareas de mantenimiento.")
        
        if anomalies:
            context.append(f"Se detectaron {len(anomalies)} anomalias que podrian requerir atencion.")
        
        if status.get("disk_free_gb", 999) < 20:
            context.append("El disco esta casi lleno. Podria sugerir liberar espacio.")
        
        return " | ".join(context) if context else "Todo operando normalmente."

    def log_event(self, event_type: str, description: str):
        """Log a system event."""
        entry = {
            "type": event_type,
            "description": description,
            "time": datetime.datetime.now().isoformat(),
        }
        self.monitor_log.append(entry)
        self._save_log()


self_monitor = SelfMonitor()
