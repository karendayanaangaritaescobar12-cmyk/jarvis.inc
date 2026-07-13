import os
import mimetypes
import base64
import json
import datetime
from typing import Optional, Dict, Any


class FileProcessor:
    """Universal file handler inspired by Mark-XLVIII.
    
    Handles: images, PDFs, DOCX, CSV, JSON, code files, audio, video.
    Type detection → dispatch → AI analysis when needed.
    """
    
    SUPPORTED_TYPES = {
        "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"],
        "document": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt"],
        "spreadsheet": [".csv", ".xlsx", ".xls"],
        "data": [".json", ".xml", ".yaml", ".yml", ".toml"],
        "code": [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".h",
                  ".rs", ".go", ".rb", ".php", ".sql", ".sh", ".bat", ".ps1"],
        "audio": [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"],
        "video": [".mp4", ".avi", ".mkv", ".mov", ".webm", ".wmv"],
        "archive": [".zip", ".rar", ".7z", ".tar", ".gz"],
    }
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)

    def detect_type(self, filepath: str) -> str:
        """Detect file type by extension."""
        ext = os.path.splitext(filepath)[1].lower()
        for file_type, extensions in self.SUPPORTED_TYPES.items():
            if ext in extensions:
                return file_type
        return "unknown"

    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """Get comprehensive file information."""
        if not os.path.exists(filepath):
            return {"error": f"Archivo no encontrado: {filepath}"}
        
        stat = os.stat(filepath)
        size = stat.st_size
        modified = datetime.datetime.fromtimestamp(stat.st_mtime)
        
        return {
            "path": filepath,
            "name": os.path.basename(filepath),
            "extension": os.path.splitext(filepath)[1],
            "type": self.detect_type(filepath),
            "size_bytes": size,
            "size_human": self._human_size(size),
            "modified": modified.isoformat(),
            "is_file": os.path.isfile(filepath),
            "is_dir": os.path.isdir(filepath),
        }

    def _human_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def read_file_content(self, filepath: str) -> str:
        """Read file content based on type."""
        if not os.path.exists(filepath):
            return f"Archivo no encontrado: {filepath}"
        
        file_type = self.detect_type(filepath)
        size = os.path.getsize(filepath)
        
        if size > self.max_file_size:
            return f"Archivo muy grande ({self._human_size(size)}). Maximo: {self._human_size(self.max_file_size)}"
        
        try:
            if file_type == "image":
                return self._read_image(filepath)
            elif file_type == "document":
                return self._read_document(filepath)
            elif file_type == "spreadsheet":
                return self._read_spreadsheet(filepath)
            elif file_type == "data":
                return self._read_data_file(filepath)
            elif file_type == "code":
                return self._read_code_file(filepath)
            elif file_type in ["audio", "video"]:
                return self._read_media_info(filepath)
            else:
                return self._read_text_file(filepath)
        except Exception as e:
            return f"Error leyendo archivo: {str(e)}"

    def _read_image(self, filepath: str) -> str:
        """Read image file and return description for AI analysis."""
        try:
            with open(filepath, "rb") as f:
                img_data = f.read()
            img_b64 = base64.b64encode(img_data).decode()
            ext = os.path.splitext(filepath)[1].lower()
            mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                       ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp"}
            mime = mime_map.get(ext, "image/jpeg")
            
            info = self.get_file_info(filepath)
            return f"""[IMAGEN: {info['name']}]
Tipo: {mime}
Tamano: {info['size_human']}
Base64: {img_b64[:100]}... (truncado para referencia)
Para analizar esta imagen, usa el endpoint /jarvis/screenshot/analyze o descríbela manualmente."""
        except Exception as e:
            return f"Error leyendo imagen: {str(e)}"

    def _read_document(self, filepath: str) -> str:
        """Read document files (PDF, DOCX, TXT)."""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == ".txt" or ext == ".rtf":
            return self._read_text_file(filepath)
        
        if ext == ".pdf":
            try:
                import PyPDF2
                with open(filepath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for i, page in enumerate(reader.pages[:10]):
                        text += f"--- Pagina {i+1} ---\n"
                        text += page.extract_text() + "\n\n"
                    return text if text else "No se pudo extraer texto del PDF."
            except ImportError:
                info = self.get_file_info(filepath)
                return f"PDF detectado ({info['name']}, {info['size_human']}). Instala PyPDF2 para extraer texto."
            except Exception as e:
                return f"Error leyendo PDF: {str(e)}"
        
        if ext in [".docx", ".doc"]:
            try:
                from docx import Document
                doc = Document(filepath)
                text = "\n".join([para.text for para in doc.paragraphs[:50]])
                return text if text else "Documento vacio."
            except ImportError:
                info = self.get_file_info(filepath)
                return f"DOCX detectado ({info['name']}, {info['size_human']}). Instala python-docx para extraer texto."
            except Exception as e:
                return f"Error leyendo DOCX: {str(e)}"
        
        return self._read_text_file(filepath)

    def _read_spreadsheet(self, filepath: str) -> str:
        """Read CSV/Excel files."""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == ".csv":
            try:
                import csv
                with open(filepath, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    rows = []
                    for i, row in enumerate(reader):
                        if i >= 20:
                            break
                        rows.append(", ".join(row))
                    return "\n".join(rows)
            except Exception as e:
                return f"Error leyendo CSV: {str(e)}"
        
        if ext in [".xlsx", ".xls"]:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(filepath, read_only=True)
                sheet = wb.active
                rows = []
                for i, row in enumerate(sheet.iter_rows(values_only=True)):
                    if i >= 20:
                        break
                    rows.append(", ".join([str(c) if c else "" for c in row]))
                return "\n".join(rows)
            except ImportError:
                info = self.get_file_info(filepath)
                return f"Excel detectado ({info['name']}, {info['size_human']}). Instala openpyxl para leer."
            except Exception as e:
                return f"Error leyendo Excel: {str(e)}"
        
        return "Formato no soportado."

    def _read_data_file(self, filepath: str) -> str:
        """Read JSON/YAML/TOML data files."""
        ext = os.path.splitext(filepath)[1].lower()
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            if ext == ".json":
                data = json.loads(content)
                return json.dumps(data, indent=2, ensure_ascii=False)[:5000]
            
            return content[:5000]
        except Exception as e:
            return f"Error leyendo archivo de datos: {str(e)}"

    def _read_code_file(self, filepath: str) -> str:
        """Read source code files with syntax hints."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            ext = os.path.splitext(filepath)[1].lower()
            lang_map = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
                       ".html": "HTML", ".css": "CSS", ".java": "Java",
                       ".cpp": "C++", ".c": "C", ".rs": "Rust", ".go": "Go",
                       ".rb": "Ruby", ".php": "PHP", ".sql": "SQL",
                       ".sh": "Bash", ".bat": "Batch", ".ps1": "PowerShell"}
            lang = lang_map.get(ext, "code")
            
            lines = content.split("\n")
            truncated = len(lines) > 100
            
            result = f"[{lang}] {os.path.basename(filepath)}\n"
            result += f"Lineas: {len(lines)}\n\n"
            result += "\n".join(lines[:100])
            
            if truncated:
                result += f"\n\n... ({len(lines) - 100} lineas mas)"
            
            return result
        except Exception as e:
            return f"Error leyendo codigo: {str(e)}"

    def _read_media_info(self, filepath: str) -> str:
        """Get media file info without reading content."""
        info = self.get_file_info(filepath)
        ext = info["extension"].lower()
        
        result = f"[MEDIA: {info['name']}]\n"
        result += f"Tipo: {info['type']}\n"
        result += f"Tamano: {info['size_human']}\n"
        result += f"Extension: {ext}\n"
        
        if ext in [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"]:
            result += "Tipo: Audio\n"
        elif ext in [".mp4", ".avi", ".mkv", ".mov", ".webm"]:
            result += "Tipo: Video\n"
        
        return result

    def _read_text_file(self, filepath: str) -> str:
        """Read plain text file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            if len(content) > 5000:
                return content[:5000] + f"\n\n... (truncado, {len(content)} caracteres totales)"
            return content
        except UnicodeDecodeError:
            return f"Archivo binario o encoding no soportado: {filepath}"
        except Exception as e:
            return f"Error leyendo archivo: {str(e)}"

    def summarize_for_ai(self, filepath: str) -> str:
        """Generate a summary of the file for AI context."""
        info = self.get_file_info(filepath)
        content = self.read_file_content(filepath)
        
        summary = f"ARCHIVO: {info['name']}\n"
        summary += f"Tipo: {info['type']}\n"
        summary += f"Tamano: {info['size_human']}\n"
        summary += f"Modificado: {info['modified']}\n"
        summary += f"\nContenido:\n{content[:3000]}"
        
        if len(content) > 3000:
            summary += f"\n\n... ({len(content) - 3000} caracteres mas)"
        
        return summary


file_processor = FileProcessor()
