import os
import re
import datetime
from typing import Optional, List, Dict


class TaskExecutor:
    def __init__(self):
        self.tasks_dir = os.path.join(os.path.dirname(__file__), "data", "tasks")
        os.makedirs(self.tasks_dir, exist_ok=True)

    async def execute_task(self, description: str, system_controller, ai_provider=None) -> str:
        lower = description.lower()

        if any(w in lower for w in ["organizar", "organiza", "ordenar", "ordena"]):
            return await self._organize_files(description, system_controller)

        if any(w in lower for w in ["script", "script de", "automatizar", "automatiza"]):
            return await self._create_script(description, system_controller, ai_provider)

        if any(w in lower for w in ["backup", "respaldo", "copia de seguridad"]):
            return await self._create_backup(description, system_controller)

        if any(w in lower for w in ["proyecto", "estructura", "crear proyecto"]):
            return await self._create_project(description, system_controller)

        if any(w in lower for w in ["limpiar", "limpia", "cleanup", "liberar espacio"]):
            return await self._cleanup_system(description, system_controller)

        return f"No identifiqué la tarea: '{description}'. Puedo: organizar archivos, crear scripts, backups, proyectos, o limpiar el sistema."

    async def _organize_files(self, description: str, sc) -> str:
        folder_match = re.search(r'(?:carpeta|directorio|folder)\s+(\S+)', description.lower())
        folder = folder_match.group(1) if folder_match else os.path.expanduser("~\\Downloads")

        if not os.path.exists(folder):
            return f"La carpeta {folder} no existe."

        categories = {
            "Imágenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
            "Documentos": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
            "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
            "Música": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
            "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Instaladores": [".exe", ".msi", ".dmg"],
            "Código": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h"],
        }

        created = {}
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1].lower()
                for cat_name, extensions in categories.items():
                    if ext in extensions:
                        cat_dir = os.path.join(folder, cat_name)
                        os.makedirs(cat_dir, exist_ok=True)
                        new_path = os.path.join(cat_dir, filename)
                        if not os.path.exists(new_path):
                            os.rename(filepath, new_path)
                            created[cat_name] = created.get(cat_name, 0) + 1
                        break

        if not created:
            return f"📂 No encontré archivos para organizar en {folder}."

        result = f"📂 Archivos organizados en {folder}:\n"
        for cat, count in created.items():
            result += f"• {cat}: {count} archivos\n"
        return result

    async def _create_script(self, description: str, sc, ai_provider=None) -> str:
        script_dir = os.path.join(os.path.dirname(__file__), "workspace", "scripts")
        os.makedirs(script_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        script_path = os.path.join(script_dir, f"script_{timestamp}.py")

        if ai_provider:
            prompt = f"Crea un script de Python para: {description}. Solo el código, sin explicaciones."
            code = ""
            try:
                async for chunk in ai_provider.generate_with_system(prompt, [{"role": "user", "content": prompt}]):
                    code += chunk
                code = re.sub(r'```python\n?', '', code)
                code = re.sub(r'```\n?$', '', code).strip()
            except:
                code = f"# Script para: {description}\nprint('Script generado')\n# TODO: implementar"
        else:
            code = f"""#!/usr/bin/env python3
# Script: {description}
# Generado: {datetime.datetime.now().isoformat()}

import os
import sys

def main():
    print("Ejecutando: {description}")
    # TODO: implementar lógica

if __name__ == "__main__":
    main()
"""

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        return f"📜 Script creado: {script_path}\n\n{code[:500]}"

    async def _create_backup(self, description: str, sc) -> str:
        import shutil

        folder_match = re.search(r'(?:de|del|carpeta)\s+(.+)', description.lower())
        source = folder_match.group(1).strip() if folder_match else os.path.expanduser("~\\Documents")

        if not os.path.exists(source):
            return f"La carpeta {source} no existe."

        backup_dir = os.path.join(os.path.dirname(__file__), "workspace", "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = os.path.basename(source)
        backup_path = os.path.join(backup_dir, f"{folder_name}_{timestamp}")

        try:
            shutil.copytree(source, backup_path)
            size = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(backup_path) for f in fn)
            return f"💾 Backup creado: {backup_path}\nTamaño: {size // (1024*1024)}MB"
        except Exception as e:
            return f"Error creando backup: {str(e)[:100]}"

    async def _create_project(self, description: str, sc) -> str:
        name_match = re.search(r'(?:proyecto|project)\s+(\S+)', description.lower())
        project_name = name_match.group(1) if name_match else "nuevo_proyecto"

        project_dir = os.path.join(os.path.dirname(__file__), "workspace", "projects", project_name)

        structure = {
            "": ["README.md", ".gitignore"],
            "src": ["__init__.py", "main.py"],
            "tests": ["test_main.py"],
            "docs": [],
        }

        for folder, files in structure.items():
            dir_path = os.path.join(project_dir, folder) if folder else project_dir
            os.makedirs(dir_path, exist_ok=True)
            for filename in files:
                filepath = os.path.join(dir_path, filename)
                if not os.path.exists(filepath):
                    with open(filepath, "w") as f:
                        if filename == "README.md":
                            f.write(f"# {project_name}\n\nProyecto generado por JARVIS.\n")
                        elif filename == ".gitignore":
                            f.write("__pycache__/\n*.pyc\n.env\nvenv/\n")
                        else:
                            f.write("")

        return f"📁 Proyecto creado: {project_dir}\nEstructura:\n• src/\n• tests/\n• docs/\n• README.md"

    async def _cleanup_system(self, description: str, sc) -> str:
        cleaned = 0
        freed = 0

        temp_dirs = [
            os.path.expanduser("~\\AppData\\Local\\Temp"),
            os.path.expanduser("~\\AppData\\Local\\Microsoft\\Windows\\INetCache"),
        ]

        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    try:
                        if os.path.isfile(item_path):
                            size = os.path.getsize(item_path)
                            os.remove(item_path)
                            cleaned += 1
                            freed += size
                    except:
                        pass

        return f"🧹 Limpieza completada:\n• Archivos eliminados: {cleaned}\n• Espacio liberado: {freed // (1024*1024)}MB"


task_executor = TaskExecutor()
