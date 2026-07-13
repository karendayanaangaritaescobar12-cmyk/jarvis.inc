import os
import psutil
import subprocess
import webbrowser
import platform
import shutil
import json
from typing import Optional
from datetime import datetime


class SystemController:
    def __init__(self):
        self.system = platform.system().lower()
        self.workspace = os.path.join(os.path.dirname(__file__), "..", "workspace")
        os.makedirs(self.workspace, exist_ok=True)

    def get_system_info(self) -> dict:
        return {
            "system": platform.system(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "memory": dict(psutil.virtual_memory()._asdict()),
            "battery": self._get_battery_info(),
            "disk_usage": self.get_disk_info(),
        }

    def _get_battery_info(self) -> Optional[dict]:
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "secs_left": battery.secsleft
                }
        except:
            pass
        return None

    def execute_command(self, command: str) -> str:
        command = command.lower().strip()

        if any(w in command for w in ["abrir navegador", "abre el navegador", "internet"]):
            return self.open_browser()
        elif any(w in command for w in ["abrir calculadora", "calculadora"]):
            return self.open_calculator()
        elif any(w in command for w in ["abrir explorador", "explorador de archivos", "archivos"]):
            return self.open_explorer()
        elif any(w in command for w in ["apagar", "apaga el pc", "shutdown"]):
            return self.shutdown()
        elif any(w in command for w in ["reiniciar", "reinicia el pc", "restart"]):
            return self.restart()
        elif any(w in command for w in ["bloquear", "bloquear pc", "lock"]):
            return self.lock_screen()
        elif any(w in command for w in ["volumen subir", "subir volumen", "mas volumen", "más volumen"]):
            return self.change_volume("up")
        elif any(w in command for w in ["volumen bajar", "bajar volumen", "menos volumen"]):
            return self.change_volume("down")
        elif any(w in command for w in ["mutear", "silenciar", "mute"]):
            return self.mute_volume()
        elif "procesos" in command or "que esta corriendo" in command:
            return self.get_running_processes()
        elif "informacion del sistema" in command or "system info" in command:
            return self.get_system_info_text()

        return None

    def run_powershell(self, script: str, timeout: int = 30) -> str:
        if self.system == "windows":
            try:
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", script],
                    capture_output=True, text=True, timeout=timeout,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                output = result.stdout.strip()
                error = result.stderr.strip()
                if error:
                    return f"Error: {error}" if not output else f"{output}\nError: {error}"
                return output if output else "Comando ejecutado sin salida."
            except subprocess.TimeoutExpired:
                return "Timeout: el comando tardó demasiado."
            except Exception as e:
                return f"Error ejecutando comando: {str(e)}"
        else:
            return self.run_cmd(script, timeout)

    def run_cmd(self, command: str, timeout: int = 30) -> str:
        try:
            flags = subprocess.CREATE_NO_WINDOW if self.system == "windows" else 0
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout,
                creationflags=flags
            )
            output = result.stdout.strip()
            error = result.stderr.strip()
            if error:
                return f"Error: {error}" if not output else f"{output}\nError: {error}"
            return output if output else "Comando ejecutado sin salida."
        except subprocess.TimeoutExpired:
            return "Timeout: el comando tardó demasiado."
        except Exception as e:
            return f"Error ejecutando comando: {str(e)}"

    def create_file(self, path: str, content: str) -> str:
        try:
            if os.path.isabs(path):
                full_path = path
            else:
                full_path = os.path.join(self.workspace, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Archivo creado: {full_path} ({len(content)} caracteres)"
        except Exception as e:
            return f"Error creando archivo: {str(e)}"

    def read_file(self, path: str) -> str:
        try:
            full_path = os.path.join(self.workspace, path)
            if not os.path.exists(full_path):
                full_path = path
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content[:5000] if len(content) > 5000 else content
        except Exception as e:
            return f"Error leyendo archivo: {str(e)}"

    def list_files(self, path: str = ".") -> str:
        try:
            full_path = os.path.join(self.workspace, path)
            if not os.path.exists(full_path):
                full_path = path
            items = []
            for item in os.listdir(full_path):
                full = os.path.join(full_path, item)
                size = os.path.getsize(full) if os.path.isfile(full) else 0
                tipo = "archivo" if os.path.isfile(full) else "carpeta"
                items.append(f"{'[F]' if tipo == 'archivo' else '[D]'} {item} ({size} bytes)")
            return "\n".join(items) if items else "Directorio vacío."
        except Exception as e:
            return f"Error listando archivos: {str(e)}"

    def delete_file(self, path: str) -> str:
        try:
            full_path = os.path.join(self.workspace, path)
            if not os.path.exists(full_path):
                full_path = path
            if os.path.isfile(full_path):
                os.remove(full_path)
                return f"Archivo eliminado: {path}"
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
                return f"Carpeta eliminada: {path}"
            return "No encontrado."
        except Exception as e:
            return f"Error eliminando: {str(e)}"

    def move_file(self, source: str, dest: str) -> str:
        try:
            src = os.path.join(self.workspace, source)
            dst = os.path.join(self.workspace, dest)
            if not os.path.exists(src):
                src = source
            if not os.path.exists(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            return f"Movido: {source} -> {dest}"
        except Exception as e:
            return f"Error moviendo: {str(e)}"

    def copy_file(self, source: str, dest: str) -> str:
        try:
            src = os.path.join(self.workspace, source)
            dst = os.path.join(self.workspace, dest)
            if not os.path.exists(src):
                src = source
            if os.path.isfile(src):
                shutil.copy2(src, dst)
            elif os.path.isdir(src):
                shutil.copytree(src, dst)
            return f"Copiado: {source} -> {dest}"
        except Exception as e:
            return f"Error copiando: {str(e)}"

    def edit_file(self, path: str, old_text: str, new_text: str) -> str:
        try:
            full_path = os.path.join(self.workspace, path)
            if not os.path.exists(full_path):
                full_path = path
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            if old_text not in content:
                return f"Texto no encontrado en {path}"
            count = content.count(old_text)
            new_content = content.replace(old_text, new_text)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return f"Editado {path}: {count} ocurrencia(s) reemplazada(s)"
        except Exception as e:
            return f"Error editando: {str(e)}"

    def append_file(self, path: str, content: str) -> str:
        try:
            full_path = os.path.join(self.workspace, path)
            if not os.path.exists(full_path):
                full_path = path
            with open(full_path, "a", encoding="utf-8") as f:
                f.write(content)
            return f"Contenido agregado a {path}"
        except Exception as e:
            return f"Error agregando: {str(e)}"

    def insert_file(self, path: str, line_num: int, content: str) -> str:
        try:
            full_path = os.path.join(self.workspace, path)
            if not os.path.exists(full_path):
                full_path = path
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if line_num < 0:
                line_num = 0
            elif line_num > len(lines):
                line_num = len(lines)
            lines.insert(line_num, content + "\n")
            with open(full_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return f"Insertado en línea {line_num + 1} de {path}"
        except Exception as e:
            return f"Error insertando: {str(e)}"

    def rename_file(self, old_name: str, new_name: str) -> str:
        try:
            old_path = os.path.join(self.workspace, old_name)
            new_path = os.path.join(self.workspace, new_name)
            if not os.path.exists(old_path):
                old_path = old_name
                new_path = os.path.join(os.path.dirname(old_name), new_name)
            os.rename(old_path, new_path)
            return f"Renombrado: {old_name} -> {new_name}"
        except Exception as e:
            return f"Error renombrando: {str(e)}"

    def file_info(self, path: str) -> str:
        try:
            full_path = os.path.join(self.workspace, path)
            if not os.path.exists(full_path):
                full_path = path
            if not os.path.exists(full_path):
                return f"Archivo no encontrado: {path}"
            stat = os.stat(full_path)
            from datetime import datetime
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S")
            created = datetime.fromtimestamp(stat.st_ctime).strftime("%d/%m/%Y %H:%M:%S")
            size = stat.st_size
            tipo = "Directorio" if os.path.isdir(full_path) else "Archivo"
            ext = os.path.splitext(full_path)[1] if os.path.isfile(full_path) else ""
            return (
                f"Nombre: {os.path.basename(full_path)}\n"
                f"Tipo: {tipo}{(' (' + ext + ')') if ext else ''}\n"
                f"Tamaño: {size:,} bytes ({size/1024:.1f} KB)\n"
                f"Creado: {created}\n"
                f"Modificado: {modified}\n"
                f"Ruta: {full_path}"
            )
        except Exception as e:
            return f"Error: {str(e)}"

    def create_directory(self, path: str) -> str:
        try:
            if os.path.isabs(path):
                full_path = path
            else:
                full_path = os.path.join(self.workspace, path)
            os.makedirs(full_path, exist_ok=True)
            return f"Carpeta creada: {full_path}"
        except Exception as e:
            return f"Error creando carpeta: {str(e)}"

    def tree_view(self, path: str = ".", max_depth: int = 2) -> str:
        try:
            full_path = os.path.join(self.workspace, path)
            if not os.path.exists(full_path):
                full_path = path
            result = [os.path.basename(full_path) + "/"]

            def _tree(dir_path, prefix="", depth=0):
                if depth >= max_depth:
                    return
                entries = sorted(os.listdir(dir_path))
                dirs = [e for e in entries if os.path.isdir(os.path.join(dir_path, e))]
                files = [e for e in entries if os.path.isfile(os.path.join(dir_path, e))]
                for i, d in enumerate(dirs):
                    is_last = (i == len(dirs) - 1) and not files
                    connector = "└── " if is_last else "├── "
                    result.append(f"{prefix}{connector}{d}/")
                    _tree(os.path.join(dir_path, d), prefix + ("    " if is_last else "│   "), depth + 1)
                for i, f in enumerate(files):
                    is_last = i == len(files) - 1
                    connector = "└── " if is_last else "├── "
                    size = os.path.getsize(os.path.join(dir_path, f))
                    result.append(f"{prefix}{connector}{f} ({size:,} bytes)")

            _tree(full_path)
            return "\n".join(result)
        except Exception as e:
            return f"Error: {str(e)}"

    def system_review(self) -> str:
        info = self.get_system_info()
        parts = []
        parts.append("=== REVISIÓN COMPLETA DEL SISTEMA ===\n")
        parts.append(f"Sistema: {info['system']} {info['version']}")
        parts.append(f"Arquitectura: {info['machine']}")
        parts.append(f"Procesador: {info['processor']}")
        parts.append(f"CPU: {info['cpu_percent']}%")
        mem = info['memory']
        parts.append(f"Memoria: {mem['percent']}% ({mem['used']//1024//1024}MB / {mem['total']//1024//1024}MB)")
        bat = info.get('battery')
        if bat:
            parts.append(f"Batería: {bat['percent']}% ({'Cargando' if bat['power_plugged'] else 'Sin carga'})")
        parts.append(f"\n{self.get_disk_info()}")
        parts.append(f"\n{self.get_network_info()}")
        parts.append(f"\n{self.get_uptime()}")
        parts.append(f"\n=== TOP PROCESOS POR CPU ===")
        parts.append(self.get_running_processes())
        return "\n".join(parts)

    def list_installed_programs(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* "
                "| Select-Object DisplayName, DisplayVersion, Publisher "
                "| Where-Object {$_.DisplayName} "
                "| Sort-Object DisplayName "
                "| Format-Table -AutoSize -Property DisplayName, DisplayVersion, Publisher"
            )
            if not result or "Error" in result:
                result = self.run_powershell(
                    "Get-WmiObject -Class Win32_Product | Select-Object Name, Version, Vendor | Sort-Object Name | Format-Table -AutoSize"
                )
            return result if result else "No se pudieron obtener los programas instalados."
        return "Solo disponible en Windows."

    def list_services(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name, DisplayName | Sort-Object Name | Format-Table -AutoSize"
            )
            return result if result else "No se pudieron obtener los servicios."
        return "Solo disponible en Windows."

    def list_startup_programs(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | Format-Table -AutoSize"
            )
            return result if result else "No se encontraron programas de inicio."
        return "Solo disponible en Windows."

    def list_drivers(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-WmiObject Win32_PnPEntity | Where-Object {$_.Status -eq 'OK'} | Select-Object Name, Manufacturer | Sort-Object Name | Select-Object -First 30 | Format-Table -AutoSize"
            )
            return result if result else "No se pudieron obtener los drivers."
        return "Solo disponible en Windows."

    def list_environment_vars(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-ChildItem Env: | Sort-Object Name | Format-Table -AutoSize"
            )
            return result if result else "No se pudieron obtener las variables de entorno."
        return "Solo disponible en Windows."

    def list_scheduled_tasks(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-ScheduledTask | Where-Object {$_.State -ne 'Disabled'} | Select-Object TaskName, TaskPath, State | Sort-Object TaskName | Format-Table -AutoSize"
            )
            return result if result else "No se encontraron tareas programadas."
        return "Solo disponible en Windows."

    def check_disk_health(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus, Size | Format-Table -AutoSize"
            )
            return result if result else "No se pudo verificar el estado de los discos."
        return "Solo disponible en Windows."

    def check_windows_updates(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10 HotFixID, Description, InstalledOn | Format-Table -AutoSize"
            )
            return result if result else "No se pudieron obtener las actualizaciones."
        return "Solo disponible en Windows."

    def get_user_accounts(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-LocalUser | Select-Object Name, Enabled, LastLogon | Format-Table -AutoSize"
            )
            return result if result else "No se pudieron obtener las cuentas de usuario."
        return "Solo disponible en Windows."

    def get_startup_time(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime"
            )
            boot_info = self.run_powershell(
                "Get-CimInstance Win32_OperatingSystem | Select-Object LastBootUpTime, SystemUpTime | Format-List"
            )
            return boot_info if boot_info else self.get_uptime()
        return self.get_uptime()

    def list_environment_paths(self) -> str:
        if self.system == "windows":
            result = self.run_powershell("$env:PATH -split ';'")
            return f"Rutas PATH:\n{result}" if result else "No se obtuvo PATH."
        return "Solo disponible en Windows."

    def get_open_ports(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-NetTCPConnection | Where-Object {$_.State -eq 'Listen'} | Select-Object LocalPort, OwningProcess | Sort-Object LocalPort | Format-Table -AutoSize"
            )
            return result if result else "No se pudieron obtener los puertos abiertos."
        return "Solo disponible en Windows."

    def get_all_drives(self) -> str:
        try:
            partitions = psutil.disk_partitions()
            result = "Unidades de disco:\n"
            for p in partitions:
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    result += (
                        f"\n{p.mountpoint} ({p.fstype}):\n"
                        f"  Total: {usage.total // (1024**3)} GB\n"
                        f"  Usado: {usage.used // (1024**3)} GB ({usage.percent}%)\n"
                        f"  Libre: {usage.free // (1024**3)} GB\n"
                    )
                except:
                    pass
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    def search_file_content(self, text: str, path: str = ".", ext: str = "*") -> str:
        import glob as g
        try:
            search_path = os.path.join(self.workspace, path)
            if not os.path.exists(search_path):
                search_path = path
            pattern = os.path.join(search_path, "**", ext)
            matches = []
            for filepath in g.glob(pattern, recursive=True):
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            for i, line in enumerate(f, 1):
                                if text.lower() in line.lower():
                                    matches.append(f"{os.path.relpath(filepath, search_path)}:{i}: {line.strip()[:100]}")
                                    if len(matches) >= 20:
                                        break
                    except:
                        pass
                if len(matches) >= 20:
                    break
            if not matches:
                return f"No se encontró '{text}' en archivos."
            return f"Coincidencias para '{text}':\n" + "\n".join(matches)
        except Exception as e:
            return f"Error: {str(e)}"
        import glob as g
        try:
            search_path = os.path.join(self.workspace, path)
            if not os.path.exists(search_path):
                search_path = path
            matches = g.glob(os.path.join(search_path, "**", pattern), recursive=True)
            if not matches:
                return f"No se encontraron archivos con patrón: {pattern}"
            result = f"Archivos encontrados ({len(matches)}):\n"
            for m in matches[:20]:
                result += f"- {os.path.relpath(m, search_path)}\n"
            return result.strip()
        except Exception as e:
            return f"Error buscando: {str(e)}"

    def detailed_processes(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-Process | Select-Object ProcessName, Id, CPU, WorkingSet64, Handles | "
                "Sort-Object CPU -Descending | Select-Object -First 20 | "
                "Format-Table -AutoSize -Property @{N='Proceso';E={$_.ProcessName}}, "
                "@{N='PID';E={$_.Id}}, @{N='CPU(s)';E={[math]::Round($_.CPU,1)}}, "
                "@{N='RAM(MB)';E={[math]::Round($_.WorkingSet64/1MB,1)}}, @{N='Handles';E={$_.Handles}}"
            )
            return result if result else "No se pudieron obtener procesos."
        return "Solo disponible en Windows."

    def gpu_info(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion, VideoModeDescription | Format-Table -AutoSize"
            )
            return result if result else "No se detectó GPU."
        return "Solo disponible en Windows."

    def temperature_info(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace 'root/WMI' | "
                "ForEach-Object { $_.CurrentTemperature / 10 - 273.15 } | "
                "Select-Object -First 5 | ForEach-Object { \"{0:N1}°C\" -f $_ }"
            )
            if result and "Error" not in result and result.strip():
                return "Temperaturas:\n" + "\n".join([f"Zona {i+1}: {t}" for i, t in enumerate(result.strip().split("\n"))])
            result2 = self.run_powershell(
                "Get-CimInstance -Namespace root/WMI -ClassName MSAcpi_ThermalZoneTemperature | "
                "Select-Object InstanceName, CurrentTemperature | Format-Table -AutoSize"
            )
            return result2 if result2 else "No se pudieron obtener temperaturas. (Requiere permisos de administrador)"
        return "Solo disponible en Windows."

    def firewall_status(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-NetFirewallProfile | Select-Object Name, Enabled | Format-Table -AutoSize"
            )
            return result if result else "No se pudo obtener estado del firewall."
        return "Solo disponible en Windows."

    def firewall_rules(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-NetFirewallRule | Where-Object {$_.Enabled -eq 'True' -and $_.Direction -eq 'Inbound'} | "
                "Select-Object DisplayName, Action -First 20 | Format-Table -AutoSize"
            )
            return result if result else "No se pudieron obtener reglas del firewall."
        return "Solo disponible en Windows."

    def active_connections(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-NetTCPConnection | Where-Object {$_.State -ne 'Listen'} | "
                "Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess | "
                "Sort-Object LocalPort | Format-Table -AutoSize"
            )
            return result if result else "No hay conexiones activas."
        return "Solo disponible en Windows."

    def system_logs(self, count: int = 15) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                f"Get-EventLog -LogName System -EntryType Error,Warning -Newest {count} | "
                "Select-Object TimeGenerated, Source, Message | Format-Table -AutoSize -Wrap"
            )
            return result if result else "No se encontraron errores en el log del sistema."
        return "Solo disponible en Windows."

    def application_logs(self, count: int = 10) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                f"Get-EventLog -LogName Application -EntryType Error -Newest {count} | "
                "Select-Object TimeGenerated, Source, Message | Format-Table -AutoSize -Wrap"
            )
            return result if result else "No se encontraron errores en logs de aplicaciones."
        return "Solo disponible en Windows."

    def installed_codecs(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows Media Foundation\\Frameworks | "
                "Select-Object * -ExcludeProperty PS* | Format-List"
            )
            return result if result else "No se pudieron obtener los codecs."
        return "Solo disponible en Windows."

    def network_adapters(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | "
                "Select-Object Name, InterfaceDescription, MacAddress, LinkSpeed, Status | Format-Table -AutoSize"
            )
            return result if result else "No se detectaron adaptadores de red activos."
        return "Solo disponible en Windows."

    def wifi_profiles(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "netsh wlan show profiles"
            )
            return result if result else "No se encontraron perfiles WiFi."
        return "Solo disponible en Windows."

    def power_plan(self) -> str:
        if self.system == "windows":
            result = self.run_powershell("powercfg /getactivescheme")
            return result if result else "No se pudo obtener el plan de energía."
        return "Solo disponible en Windows."

    def startup_programs_detailed(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | Format-Table -AutoSize -Wrap"
            )
            return result if result else "No se encontraron programas de inicio."
        return "Solo disponible en Windows."

    def system_info_full(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Get-ComputerInfo | Select-Object CsName, WindowsProductName, WindowsVersion, OsArchitecture, "
                "CsProcessors, CsPhysicalMemory, BiosManufacturer, BiosSMBIOSBIOSVersion, "
                "PowerPlatformRole, TimeZone | Format-List"
            )
            return result if result else "No se pudo obtener información completa."
        return "Solo disponible en Windows."

    def install_package(self, package: str) -> str:
        return self.run_powershell(f"pip install {package}", timeout=60)

    def open_url(self, url: str) -> str:
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Abriendo: {url}"

    def set_wallpaper(self, path: str) -> str:
        if self.system == "windows":
            abs_path = os.path.abspath(path)
            return self.run_powershell(
                f'Add-Type -TypeDefinition \'using System.Runtime.InteropServices; public class Wallpaper {{ [DllImport("user32.dll", CharSet=CharSet.Auto)] public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni); }}\'; '
                f'[Wallpaper]::SystemParametersInfo(0x0014, 0, "{abs_path}", 0x0001)'
            )
        return "Solo disponible en Windows."

    def schedule_task(self, name: str, command: str, time_str: str) -> str:
        if self.system == "windows":
            return self.run_powershell(
                f'schtasks /create /tn "{name}" /tr "{command}" /sc once /st {time_str} /f'
            )
        return "Solo disponible en Windows."

    def get_network_info(self) -> str:
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_io_counters()
            result = f"Enviado: {stats.bytes_sent / 1024 / 1024:.1f} MB\nRecibido: {stats.bytes_recv / 1024 / 1024:.1f} MB\n"
            for name, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family.name == "AF_INET":
                        result += f"\n{name}: {addr.address}"
            return result
        except Exception as e:
            return f"Error de red: {str(e)}"

    def get_disk_info(self) -> str:
        try:
            partitions = psutil.disk_partitions()
            result = ""
            for p in partitions:
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    result += f"{p.mountpoint}: {usage.percent}% ({usage.free // (1024**3)}GB libres)\n"
                except:
                    pass
            return result.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def get_battery(self) -> str:
        try:
            battery = psutil.sensors_battery()
            if battery:
                status = "Cargando" if battery.power_plugged else "Sin carga"
                return f"Batería: {battery.percent}% ({status})"
            return "No se detectó batería."
        except:
            return "No se pudo obtener información de batería."

    def get_uptime(self) -> str:
        try:
            boot = datetime.fromtimestamp(psutil.boot_time())
            delta = datetime.now() - boot
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            return f"Encendido desde: {boot.strftime('%d/%m/%Y %H:%M')} ({hours}h {minutes}m)"
        except Exception as e:
            return f"Error: {str(e)}"

    def open_browser(self) -> str:
        webbrowser.open("https://www.google.com")
        return "Navegador abierto."

    def open_calculator(self) -> str:
        if self.system == "windows":
            subprocess.Popen("calc.exe")
        elif self.system == "linux":
            subprocess.Popen(["gnome-calculator"])
        elif self.system == "darwin":
            subprocess.Popen(["open", "-a", "Calculator"])
        return "Calculadora abierta."

    def open_explorer(self) -> str:
        if self.system == "windows":
            subprocess.Popen("explorer.exe")
        elif self.system == "linux":
            subprocess.Popen(["xdg-open", "."])
        elif self.system == "darwin":
            subprocess.Popen(["open", "."])
        return "Explorador de archivos abierto."

    def shutdown(self) -> str:
        if self.system == "windows":
            os.system("shutdown /s /t 60")
        elif self.system == "linux":
            os.system("sudo shutdown -h +1")
        elif self.system == "darwin":
            os.system("sudo shutdown -h +1")
        return "Apagando en 60 segundos. Cancela con 'shutdown /a'."

    def restart(self) -> str:
        if self.system == "windows":
            os.system("shutdown /r /t 60")
        elif self.system == "linux":
            os.system("sudo shutdown -r +1")
        elif self.system == "darwin":
            os.system("sudo shutdown -r +1")
        return "Reiniciando en 60 segundos."

    def lock_screen(self) -> str:
        if self.system == "windows":
            subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
        elif self.system == "linux":
            subprocess.Popen(["xdg-screensaver", "lock"])
        elif self.system == "darwin":
            subprocess.Popen(["pmset", "displaysleepnow"])
        return "Pantalla bloqueada."

    def change_volume(self, direction: str) -> str:
        if self.system == "windows":
            key = "[char]175" if direction == "up" else "[char]174"
            os.system(f'powershell -c "$obj = New-Object -ComObject WScript.Shell; 1..5 | ForEach-Object {{ $obj.SendKeys({key}) }}"')
        elif self.system == "linux":
            step = "+5%" if direction == "up" else "-5%"
            os.system(f"amixer -D pulse sset Master {step}")
        elif self.system == "darwin":
            step = "4" if direction == "up" else "-4"
            os.system(f"osascript -e 'set volume output volume (output volume of (get volume info) + {step})'")
        return f"Volumen {'subido' if direction == 'up' else 'bajado'}."

    def mute_volume(self) -> str:
        if self.system == "windows":
            os.system('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"')
        elif self.system == "linux":
            os.system("amixer -D pulse sset Master toggle")
        elif self.system == "darwin":
            os.system("osascript -e 'set volume output muted (not (output muted of (get volume info)))'")
        return "Volumen silenciado/activado."

    def get_running_processes(self) -> str:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                info = proc.info
                if info['cpu_percent'] and info['cpu_percent'] > 0:
                    processes.append((info['name'], info['cpu_percent']))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        top = sorted(processes, key=lambda x: x[1], reverse=True)[:10]
        if not top:
            return "No se detectaron procesos con alto uso de CPU."
        result = "Procesos principales:\n"
        for name, cpu in top:
            result += f"- {name}: {cpu}%\n"
        return result.strip()

    def open_spotify(self) -> str:
        paths = [
            os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
            "spotify.exe",
        ]
        for p in paths:
            try:
                subprocess.Popen([p])
                return "Spotify abierto."
            except:
                continue
        return "No encontré Spotify."

    def spotify_search_and_play(self, query: str) -> str:
        if self.system == "windows":
            try:
                subprocess.Popen(["cmd", "/c", "start", "", f"spotify:search:{query}"])
                import time
                time.sleep(2)
                self._send_media_key(0xB3)
                return f"🎵 Buscando y reproduciendo '{query}' en Spotify."
            except:
                pass
        webbrowser.open(f"https://open.spotify.com/search/{query.replace(' ', '%20')}")
        return f"Buscando '{query}' en Spotify (se abrió en navegador)."

    def spotify_play_pause(self) -> str:
        self._send_media_key(0xB3)
        return "Play/Pause enviado."

    def spotify_next(self) -> str:
        self._send_media_key(0xB0)
        return "Siguiente canción."

    def spotify_prev(self) -> str:
        self._send_media_key(0xB1)
        return "Canción anterior."

    def spotify_stop(self) -> str:
        self._send_media_key(0xB2)
        return "Reproducción detenida."

    def spotify_volume_up(self) -> str:
        self._send_media_key(0xAF)
        return "Volumen de medios subido."

    def spotify_volume_down(self) -> str:
        self._send_media_key(0xAE)
        return "Volumen de medios bajado."

    def spotify_mute(self) -> str:
        self._send_media_key(0xAD)
        return "Medios silenciados."

    def spotify_open_artist(self, artist: str) -> str:
        if self.system == "windows":
            try:
                subprocess.Popen(["cmd", "/c", "start", "", f"spotify:search:{artist}"])
                return f"🎵 Buscando '{artist}' en Spotify."
            except:
                pass
        webbrowser.open(f"https://open.spotify.com/search/{artist.replace(' ', '%20')}")
        return f"Buscando '{artist}' en Spotify."

    def spotify_open_playlist(self, playlist: str) -> str:
        if self.system == "windows":
            try:
                subprocess.Popen(["cmd", "/c", "start", "", f"spotify:search:{playlist}"])
                return f"🎵 Buscando playlist '{playlist}' en Spotify."
            except:
                pass
        webbrowser.open(f"https://open.spotify.com/search/{playlist.replace(' ', '%20')}")
        return f"Buscando playlist '{playlist}' en Spotify."

    def _send_media_key(self, key_code: int) -> None:
        if self.system == "windows":
            script = f'''
            Add-Type @"
            using System;
            using System.Runtime.InteropServices;
            public class MediaKeys {{
                [DllImport("user32.dll")]
                public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);
            }}
"@
            [MediaKeys]::keybd_event({key_code}, 0, 0, 0)
            [MediaKeys]::keybd_event({key_code}, 0, 2, 0)
            '''
            try:
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", script],
                    capture_output=True, timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except:
                pass

    def open_vscode(self) -> str:
        paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
            "code",
        ]
        for p in paths:
            try:
                subprocess.Popen([p])
                return "VS Code abierto."
            except:
                continue
        return "No encontré VS Code."

    def open_app(self, app_name: str) -> str:
        common_apps = {
            "word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "terminal": "wt.exe",
            "discord": "Discord.exe",
            "telegram": "Telegram.exe",
            "whatsapp": "WhatsApp.exe",
            "zoom": "Zoom.exe",
            "obs": "obs64.exe",
            "photoshop": "Photoshop.exe",
            "premiere": "Adobe Premiere Pro.exe",
            "blender": "blender.exe",
            "steam": "steam.exe",
            "epic": "EpicGamesLauncher.exe",
            "gimp": "gimp-2.10.exe",
            "vlc": "vlc.exe",
            "foobar": "foobar2000.exe",
        }
        linux_apps = {
            "chrome": "google-chrome",
            "firefox": "firefox",
            "terminal": "gnome-terminal",
            "nautilus": "nautilus",
            "files": "nautilus",
            "calculator": "gnome-calculator",
            "gimp": "gimp",
            "vlc": "vlc",
            "blender": "blender",
            "discord": "discord",
            "telegram": "telegram-desktop",
            "code": "code",
            "vscode": "code",
        }
        mac_apps = {
            "chrome": "Google Chrome",
            "firefox": "Firefox",
            "terminal": "Terminal",
            "finder": "Finder",
            "calculator": "Calculator",
            "gimp": "GIMP",
            "vlc": "VLC",
            "blender": "Blender",
            "discord": "Discord",
            "telegram": "Telegram",
            "code": "Visual Studio Code",
            "vscode": "Visual Studio Code",
        }
        lower = app_name.lower().strip()
        if self.system == "windows":
            if lower in common_apps:
                try:
                    subprocess.Popen([common_apps[lower]])
                    return f"{app_name} abierto."
                except:
                    pass
            try:
                subprocess.Popen([f"{lower}.exe"])
                return f"{app_name} abierto."
            except:
                pass
            try:
                os.startfile(lower)
                return f"{app_name} abierto."
            except:
                pass
        elif self.system == "linux":
            if lower in linux_apps:
                try:
                    subprocess.Popen([linux_apps[lower]])
                    return f"{app_name} abierto."
                except:
                    pass
            try:
                subprocess.Popen([lower])
                return f"{app_name} abierto."
            except:
                pass
            try:
                subprocess.Popen(["xdg-open", lower])
                return f"{app_name} abierto."
            except:
                pass
        elif self.system == "darwin":
            if lower in mac_apps:
                try:
                    subprocess.Popen(["open", "-a", mac_apps[lower]])
                    return f"{app_name} abierto."
                except:
                    pass
            try:
                subprocess.Popen(["open", "-a", lower])
                return f"{app_name} abierto."
            except:
                pass
        return f"No encontré '{app_name}'. ¿Lo tienes instalado?"

    def close_app(self, app_name: str) -> str:
        if self.system == "windows":
            result = self.run_powershell(f"Stop-Process -Name '{app_name.replace('.exe','')}' -Force -ErrorAction SilentlyContinue")
            return f"{app_name} cerrado." if "Error" not in result else f"No pude cerrar {app_name}."
        elif self.system == "linux":
            os.system(f"pkill -f {app_name}")
            return f"{app_name} cerrado."
        elif self.system == "darwin":
            os.system(f"pkill -f {app_name}")
            return f"{app_name} cerrado."
        return f"No pude cerrar {app_name}."

    def minimize_window(self) -> str:
        if self.system == "windows":
            script = '''
            Add-Type @"
            using System;
            using System.Runtime.InteropServices;
            public class WinAPI {
                [DllImport("user32.dll")]
                public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
                [DllImport("user32.dll")]
                public static extern IntPtr GetForegroundWindow();
            }
"@
            $hwnd = [WinAPI]::GetForegroundWindow()
            [WinAPI]::ShowWindow($hwnd, 6)
            '''
            self.run_powershell(script)
        return "Ventana minimizada."

    def maximize_window(self) -> str:
        if self.system == "windows":
            script = '''
            Add-Type @"
            using System;
            using System.Runtime.InteropServices;
            public class WinAPI2 {
                [DllImport("user32.dll")]
                public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
                [DllImport("user32.dll")]
                public static extern IntPtr GetForegroundWindow();
            }
"@
            $hwnd = [WinAPI2]::GetForegroundWindow()
            [WinAPI2]::ShowWindow($hwnd, 3)
            '''
            self.run_powershell(script)
        return "Ventana maximizada."

    def screenshot(self) -> str:
        if self.system == "windows":
            path = os.path.join(self.workspace, "screenshot.png")
            script = f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen | ForEach-Object {{ $bmp = New-Object System.Drawing.Bitmap($_.Bounds.Width, $_.Bounds.Height); $gfx = [System.Drawing.Graphics]::FromImage($bmp); $gfx.CopyFromScreen($_.Bounds.Location, [System.Drawing.Point]::Empty, $_.Bounds.Size); $bmp.Save("{path}") }}'
            result = self.run_powershell(script, timeout=10)
            if os.path.exists(path):
                return f"Screenshot guardado: {path}"
            return f"Error al tomar screenshot: {result}"
        return "Solo disponible en Windows."

    def get_clipboard(self) -> str:
        if self.system == "windows":
            result = self.run_powershell("Get-Clipboard")
            return f"Portapapeles: {result}"
        return "Solo disponible en Windows."

    def set_clipboard(self, text: str) -> str:
        if self.system == "windows":
            escaped = text.replace("'", "''")
            self.run_powershell(f"Set-Clipboard -Value '{escaped}'")
            return "Texto copiado al portapapeles."
        return "Solo disponible en Windows."

    def get_screen_info(self) -> str:
        if self.system == "windows":
            result = self.run_powershell(
                "Add-Type -AssemblyName System.Windows.Forms; "
                "[System.Windows.Forms.Screen]::AllScreens | ForEach-Object { "
                "'Pantalla: ' + $_.DeviceName + ' | ' + $_.Bounds.Width + 'x' + $_.Bounds.Height + ' | Principal: ' + $_.Primary "
                "}"
            )
            return result if result else "No se detectaron pantallas."
        return "Solo disponible en Windows."

    def get_system_info_text(self) -> str:
        info = self.get_system_info()
        bat = info.get('battery')
        bat_str = f"\nBatería: {bat['percent']}%" if bat else ""
        return f"Sistema: {info['system']} {info['version']}\nCPU: {info['cpu_percent']}%\nMemoria: {info['memory']['percent']}%{bat_str}"


system_controller = SystemController()
