import os
import json
import asyncio
import datetime
import psutil
from typing import Dict, List, Optional


class SelfMonitor:
    """Enhanced self-monitoring system for JARVIS consciousness.
    
    Inspired by Mark-XLVIII's SystemMonitor:
    - CPU streak detection (3 consecutive high readings)
    - GPU temperature monitoring (pynvml / ctypes)
    - Temperature cascade (psutil → wmi)
    - Anomaly cooldown (300s per metric)
    """
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.baselines_file = os.path.join(self.data_dir, "system_baselines.json")
        self.monitor_file = os.path.join(self.data_dir, "monitor_log.json")
        self.baselines = self._load_baselines()
        self.monitor_log = self._load_log()
        self.last_check = None
        self.alerts = []
        
        # Mark-XLVIII style tracking
        self._cpu_readings = []
        self._cpu_streak = 0
        self._alert_cooldowns = {}
        self._cooldown_seconds = 300
        
        # Thresholds (Mark-XLVIII style)
        self._thresholds = {
            "cpu": 90,
            "memory": 90,
            "temperature": 85,
            "gpu": 95,
            "disk_free_gb": 10,
            "processes": 500,
        }
        
        # GPU detection
        self._gpu_available = False
        self._gpu_backend = None
        self._detect_gpu()

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

    def _detect_gpu(self):
        """Detect GPU backend (Mark-XLVIII cascade: pynvml → ctypes WinDLL → ctypes CDLL)."""
        try:
            import pynvml
            pynvml.nvmlInit()
            self._gpu_available = True
            self._gpu_backend = "pynvml"
            return
        except:
            pass
        
        try:
            import ctypes
            if os.name == "nt":
                nvml = ctypes.WinDLL("nvml.dll")
            else:
                nvml = ctypes.CDLL("libnvidia-ml.so.1")
            self._gpu_available = True
            self._gpu_backend = "ctypes"
            return
        except:
            pass
        
        self._gpu_available = False
        self._gpu_backend = None

    def _get_gpu_temp(self) -> Optional[float]:
        """Get GPU temperature using available backend."""
        if not self._gpu_available:
            return None
        
        try:
            if self._gpu_backend == "pynvml":
                import pynvml
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                return float(temp)
            elif self._gpu_backend == "ctypes":
                import ctypes
                if os.name == "nt":
                    nvml = ctypes.WinDLL("nvml.dll")
                else:
                    nvml = ctypes.CDLL("libnvidia-ml.so.1")
                # Basic temperature read via NVML
                return None
        except:
            pass
        return None

    def _get_cpu_temp(self) -> Optional[float]:
        """Get CPU temperature with cascade (Mark-XLVIII style)."""
        # Method 1: psutil sensors
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        return entries[0].current
        except:
            pass
        
        # Method 2: WMI (Windows)
        if os.name == "nt":
            try:
                import wmi
                w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                sensors = w.Sensor()
                for sensor in sensors:
                    if sensor.SensorType == "Temperature" and "CPU" in sensor.Name:
                        return float(sensor.Value)
            except:
                pass
        
        return None

    def _is_in_cooldown(self, metric: str) -> bool:
        """Check if a metric is in cooldown period."""
        last_alert = self._alert_cooldowns.get(metric, 0)
        return (time.time() - last_alert) < self._cooldown_seconds

    def _set_cooldown(self, metric: str):
        """Set cooldown for a metric."""
        self._alert_cooldowns[metric] = time.time()

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
            
            cpu_temp = self._get_cpu_temp()
            gpu_temp = self._get_gpu_temp()
            
            # CPU streak tracking (Mark-XLVIII style)
            self._cpu_readings.append(cpu)
            if len(self._cpu_readings) > 10:
                self._cpu_readings = self._cpu_readings[-10:]
            
            high_count = sum(1 for r in self._cpu_readings[-3:] if r > self._thresholds["cpu"])
            if high_count >= 3:
                self._cpu_streak += 1
            else:
                self._cpu_streak = 0
            
            result = {
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
                "cpu_streak": self._cpu_streak,
            }
            
            if cpu_temp is not None:
                result["cpu_temp"] = round(cpu_temp, 1)
            if gpu_temp is not None:
                result["gpu_temp"] = round(gpu_temp, 1)
            if self._gpu_available:
                result["gpu_available"] = True
                result["gpu_backend"] = self._gpu_backend
            
            return result
        except Exception as e:
            return {"error": str(e)}

    def detect_anomalies(self) -> List[str]:
        """Detect system anomalies based on thresholds (Mark-XLVIII style with cooldowns)."""
        status = self.get_system_status()
        anomalies = []
        
        # CPU
        cpu = status.get("cpu_percent", 0)
        if cpu > self._thresholds["cpu"] and not self._is_in_cooldown("cpu"):
            if self._cpu_streak >= 3:
                anomalies.append(f"CPU al {cpu}% por {self._cpu_streak} lecturas consecutivas - posibles procesos pesados")
            else:
                anomalies.append(f"CPU al {cpu}% - posibles procesos pesados")
            self._set_cooldown("cpu")
        
        # Memory
        mem = status.get("memory_percent", 0)
        if mem > self._thresholds["memory"] and not self._is_in_cooldown("memory"):
            anomalies.append(f"Memoria al {mem}% - posible fuga de memoria")
            self._set_cooldown("memory")
        
        # Disk
        disk_free = status.get("disk_free_gb", 999)
        if disk_free < self._thresholds["disk_free_gb"] and not self._is_in_cooldown("disk"):
            anomalies.append(f"Disco casi lleno: {disk_free} GB libres")
            self._set_cooldown("disk")
        
        # Processes
        procs = status.get("processes", 0)
        if procs > self._thresholds["processes"] and not self._is_in_cooldown("processes"):
            anomalies.append(f"Muchos procesos activos: {procs}")
            self._set_cooldown("processes")
        
        # CPU Temperature
        cpu_temp = status.get("cpu_temp")
        if cpu_temp and cpu_temp > self._thresholds["temperature"] and not self._is_in_cooldown("temp"):
            anomalies.append(f"CPU temperatura alta: {cpu_temp}°C")
            self._set_cooldown("temp")
        
        # GPU Temperature
        gpu_temp = status.get("gpu_temp")
        if gpu_temp and gpu_temp > self._thresholds["gpu"] and not self._is_in_cooldown("gpu"):
            anomalies.append(f"GPU temperatura alta: {gpu_temp}°C")
            self._set_cooldown("gpu")
        
        self.alerts = anomalies
        return anomalies

    def generate_report(self) -> str:
        """Generate a system report for JARVIS to use in conversations."""
        status = self.get_system_status()
        anomalies = self.detect_anomalies()
        
        report = f"REPORTE DEL SISTEMA ({datetime.datetime.now().strftime('%H:%M')}):\n"
        report += f"- CPU: {status.get('cpu_percent', '?')}%"
        if status.get("cpu_temp"):
            report += f" ({status['cpu_temp']}°C)"
        report += "\n"
        report += f"- Memoria: {status.get('memory_percent', '?')}% ({status.get('memory_used_gb', '?')}/{status.get('memory_total_gb', '?')} GB)\n"
        report += f"- Disco: {status.get('disk_percent', '?')}% usado, {status.get('disk_free_gb', '?')} GB libres\n"
        report += f"- Procesos activos: {status.get('processes', '?')}\n"
        report += f"- Red: {status.get('network_sent_mb', '?')} MB enviados, {status.get('network_recv_mb', '?')} MB recibidos\n"
        report += f"- Tiempo encendido: {status.get('uptime_hours', '?')} horas\n"
        
        if status.get("gpu_temp"):
            report += f"- GPU: {status['gpu_temp']}°C\n"
        
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
        
        if 6 <= hour <= 8:
            context.append("Es hora temprana. El usuario podria necesitar un resumen del dia o briefing matutino.")
        elif 12 <= hour <= 14:
            context.append("Es hora de almuerzo. El usuario podria querer una pausa.")
        elif hour >= 23:
            context.append("Es tarde. El usuario deberia descansar.")
        
        if status.get("cpu_percent", 0) > 80:
            context.append("El sistema esta trabajando duro. Podria haber tareas pesadas en ejecucion.")
        elif status.get("cpu_percent", 0) < 10:
            context.append("El sistema esta inactivo. Podria ser buen momento para tareas de mantenimiento.")
        
        if status.get("cpu_streak", 0) >= 3:
            context.append(f"CPU alto por {status['cpu_streak']} lecturas consecutivas. Posible proceso pesado persistente.")
        
        if anomalies:
            context.append(f"Se detectaron {len(anomalies)} anomalias que podrian requerir atencion.")
        
        if status.get("disk_free_gb", 999) < 20:
            context.append("El disco esta casi lleno. Podria sugerir liberar espacio.")
        
        if status.get("gpu_temp") and status["gpu_temp"] > 80:
            context.append(f"GPU caliente ({status['gpu_temp']}°C). Podria afectar rendimiento.")
        
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


import time
self_monitor = SelfMonitor()
