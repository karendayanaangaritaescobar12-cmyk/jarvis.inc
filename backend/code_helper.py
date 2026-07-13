import os
import re
import subprocess
import tempfile
from typing import Optional, Dict, Any


class CodeHelper:
    """Code helper inspired by Mark-XLVIII.
    
    Capabilities:
    - Write code in any language
    - Edit existing code
    - Explain code
    - Run code (with safety limits)
    - Build projects
    - Optimize code
    - Auto-fix errors (3 attempts)
    """
    
    def __init__(self):
        self.workspace = os.path.join(os.path.dirname(__file__), "workspace")
        os.makedirs(self.workspace, exist_ok=True)
        self.supported_languages = {
            "python": {"ext": ".py", "run": "python"},
            "javascript": {"ext": ".js", "run": "node"},
            "typescript": {"ext": ".ts", "run": "ts-node"},
            "html": {"ext": ".html", "run": "browser"},
            "css": {"ext": ".css", "run": "browser"},
            "bash": {"ext": ".sh", "run": "bash"},
            "powershell": {"ext": ".ps1", "run": "powershell"},
            "batch": {"ext": ".bat", "run": "cmd"},
            "java": {"ext": ".java", "run": "javac"},
            "c": {"ext": ".c", "run": "gcc"},
            "cpp": {"ext": ".cpp", "run": "g++"},
            "rust": {"ext": ".rs", "run": "rustc"},
            "go": {"ext": ".go", "run": "go run"},
            "ruby": {"ext": ".rb", "run": "ruby"},
            "php": {"ext": ".php", "run": "php"},
        }

    def detect_language(self, filename: str) -> Optional[str]:
        """Detect language from filename."""
        ext = os.path.splitext(filename)[1].lower()
        for lang, info in self.supported_languages.items():
            if info["ext"] == ext:
                return lang
        return None

    def write_code(self, filename: str, content: str, language: Optional[str] = None) -> str:
        """Write code to a file."""
        if not language:
            language = self.detect_language(filename)
        
        filepath = os.path.join(self.workspace, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            lines = content.split("\n")
            result = f"Codigo escrito en {filepath}\n"
            result += f"Lineas: {len(lines)}\n"
            if language:
                result += f"Lenguaje: {language.title()}\n"
            result += f"\nPara ejecutar: [EXEC: {self._get_run_command(language, filepath)}]"
            
            return result
        except Exception as e:
            return f"Error escribiendo codigo: {str(e)}"

    def edit_code(self, filepath: str, old_code: str, new_code: str) -> str:
        """Edit existing code file."""
        if not os.path.exists(filepath):
            return f"Archivo no encontrado: {filepath}"
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            if old_code not in content:
                return "Texto antiguo no encontrado en el archivo."
            
            new_content = content.replace(old_code, new_code, 1)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            return f"Archivo editado: {filepath}"
        except Exception as e:
            return f"Error editando: {str(e)}"

    def explain_code(self, code: str, language: Optional[str] = None) -> str:
        """Generate explanation prompt for AI."""
        if not language:
            language = "desconocido"
        
        prompt = f"""Explica el siguiente codigo en {language}:
    
```{language}
{code}
```

Proporciona:
1. Que hace el codigo
2. Flujo de ejecucion
3. Funciones/clases importantes
4. Posibles mejoras
5. Errores potenciales"""
        
        return prompt

    def run_code(self, filepath: str, timeout: int = 30) -> str:
        """Run code with safety limits."""
        if not os.path.exists(filepath):
            return f"Archivo no encontrado: {filepath}"
        
        language = self.detect_language(filepath)
        if not language:
            return f"Lenguaje no soportado para ejecucion: {filepath}"
        
        run_cmd = self._get_run_command(language, filepath)
        if not run_cmd:
            return f"No se puede ejecutar {language} automaticamente."
        
        try:
            result = subprocess.run(
                run_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace,
            )
            
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\n[STDERR]\n{result.stderr}"
            
            if not output.strip():
                output = "Ejecucion completada sin salida."
            
            return output[:5000]
        except subprocess.TimeoutExpired:
            return f"Ejecucion timeout ({timeout}s). Posible loop infinito."
        except Exception as e:
            return f"Error ejecutando: {str(e)}"

    def _get_run_command(self, language: Optional[str], filepath: str) -> Optional[str]:
        """Get the command to run a file."""
        if not language or language not in self.supported_languages:
            return None
        
        runner = self.supported_languages[language]["run"]
        
        if language == "html":
            return f"start {filepath}"
        elif language == "css":
            return None
        elif language in ["bash", "powershell", "batch"]:
            return filepath
        else:
            return f"{runner} {filepath}"

    def build_project(self, project_type: str, name: str, location: Optional[str] = None) -> str:
        """Generate a project structure."""
        if not location:
            location = os.path.join(self.workspace, name)
        
        os.makedirs(location, exist_ok=True)
        
        structures = {
            "python": {
                "main.py": "#!/usr/bin/env python3\n\n\ndef main():\n    print('Hello from " + name + "')\n\n\nif __name__ == '__main__':\n    main()\n",
                "requirements.txt": "",
                "README.md": f"# {name}\n\nPython project.\n",
                ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\n",
            },
            "javascript": {
                "index.js": "console.log('Hello from " + name + "');\n",
                "package.json": json.dumps({"name": name, "version": "1.0.0", "main": "index.js"}, indent=2),
                "README.md": f"# {name}\n\nJavaScript project.\n",
                ".gitignore": "node_modules/\n.env\n",
            },
            "html": {
                "index.html": f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>{name}</h1>
    <script src="script.js"></script>
</body>
</html>""",
                "style.css": "body { font-family: sans-serif; margin: 2rem; }\n",
                "script.js": f"console.log('{name} loaded');\n",
            },
        }
        
        structure = structures.get(project_type, structures["python"])
        
        created_files = []
        for filename, content in structure.items():
            filepath = os.path.join(location, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            created_files.append(filename)
        
        return f"Proyecto '{name}' creado en {location}\nArchivos: {', '.join(created_files)}"

    def optimize_code(self, code: str, language: str) -> str:
        """Generate optimization prompt for AI."""
        prompt = """Optimiza el siguiente codigo. Proporciona:
1. Version optimizada
2. Explicacion de cambios
3. Mejoras de rendimiento
4. Mejores practicas aplicadas"""
        return f"{prompt}\n\n```{language}\n{code}\n```"

    def find_and_fix_errors(self, code: str, language: str, error_msg: str) -> str:
        """Generate error fixing prompt for AI."""
        prompt = f"""El siguiente codigo tiene un error. Error reportado: {error_msg}

Proporciona:
1. Causa del error
2. Codigo corregido
3. Explicacion del fix
4. Como prevenirlo en el futuro"""
        return f"{prompt}\n\n```{language}\n{code}\n```"


import json
code_helper = CodeHelper()
