# J.A.R.V.I.S. - Just A Rather Very Intelligent System

Asistente personal inspirado en JARVIS de Iron Man.

## Instalación

### Backend (Python)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configura tus API keys
python main.py
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

## Configuración

1. Copia `.env.example` a `.env` en la carpeta `backend`
2. Configura tu proveedor de IA (Groq es gratis):
   - **Groq**: Obtén API key gratis en https://console.groq.com
   - **OpenAI**: Necesitas API key de OpenAI
   - **Ollama**: Instala localmente desde https://ollama.ai

## Funcionalidades

- Chat por voz y texto
- Control del sistema (abrir apps, volumen, apagar, etc.)
- Múltiples proveedores de IA
- Interfaz holográfica tipo Iron Man
- Respuestas en tiempo real (streaming)

## Comandos de voz/texto

- "Abrir navegador"
- "Abrir calculadora"
- "Bloquear pc"
- "Subir/bajar volumen"
- "Información del sistema"
- "Mostrar procesos"
- "Apagar/Reiniciar pc"
