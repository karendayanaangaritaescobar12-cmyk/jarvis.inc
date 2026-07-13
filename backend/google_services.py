import os
import json
import datetime
from typing import Optional, Dict, List


class GoogleServices:
    def __init__(self):
        self.credentials_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.credentials_dir, exist_ok=True)
        self.credentials_file = os.path.join(self.credentials_dir, "google_credentials.json")
        self._calendar_service = None
        self._gmail_service = None

    def _get_credentials(self):
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow

            SCOPES = [
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send'
            ]

            creds = None
            if os.path.exists(self.credentials_file):
                creds = Credentials.from_authorized_user_file(self.credentials_file, SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    return None
                with open(self.credentials_file, 'w') as token:
                    token.write(creds.to_json())

            return creds
        except ImportError:
            return None
        except Exception:
            return None

    def is_available(self) -> bool:
        return self._get_credentials() is not None

    async def get_calendar_events(self, days: int = 7) -> str:
        creds = self._get_credentials()
        if not creds:
            return "Google Calendar no configurado. Necesitas: pip install google-api-python-client google-auth-oauthlib"

        try:
            from googleapiclient.discovery import build
            service = build('calendar', 'v3', credentials=creds)

            now = datetime.datetime.utcnow().isoformat() + 'Z'
            end = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + 'Z'

            events_result = service.events().list(
                calendarId='primary', timeMin=now, timeMax=end,
                maxResults=10, singleEvents=True, orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            if not events:
                return f"No hay eventos en los próximos {days} días."

            result = f"📅 Próximos {len(events)} eventos:\n\n"
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'Sin título')
                location = event.get('location', '')
                result += f"• {summary}\n  📆 {start}"
                if location:
                    result += f" 📍 {location}"
                result += "\n"
            return result
        except Exception as e:
            return f"Error accediendo a Google Calendar: {str(e)[:100]}"

    async def create_calendar_event(self, summary: str, start_time: str, end_time: str = None, location: str = "") -> str:
        creds = self._get_credentials()
        if not creds:
            return "Google Calendar no configurado."

        try:
            from googleapiclient.discovery import build
            service = build('calendar', 'v3', credentials=creds)

            event = {
                'summary': summary,
                'location': location,
                'start': {'dateTime': start_time, 'timeZone': 'America/Bogota'},
                'end': {'dateTime': end_time or start_time, 'timeZone': 'America/Bogota'}
            }

            created = service.events().insert(calendarId='primary', body=event).execute()
            return f"✅ Evento creado: {created.get('htmlLink')}"
        except Exception as e:
            return f"Error creando evento: {str(e)[:100]}"

    async def get_gmail_messages(self, max_results: int = 10) -> str:
        creds = self._get_credentials()
        if not creds:
            return "Gmail no configurado. Necesitas: pip install google-api-python-client google-auth-oauthlib"

        try:
            from googleapiclient.discovery import build
            service = build('gmail', 'v1', credentials=creds)

            results = service.users().messages().list(
                userId='me', maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                return "No hay mensajes nuevos."

            result = f"📧 Últimos {len(messages)} mensajes:\n\n"
            for msg in messages:
                msg_data = service.users().messages().get(
                    userId='me', id=msg['id'], format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}
                sender = headers.get('From', 'Desconocido')
                subject = headers.get('Subject', 'Sin asunto')
                snippet = msg_data.get('snippet', '')[:100]

                result += f"• De: {sender}\n  Asunto: {subject}\n  Preview: {snippet}\n\n"
            return result
        except Exception as e:
            return f"Error accediendo a Gmail: {str(e)[:100]}"

    async def send_gmail(self, to: str, subject: str, body: str) -> str:
        creds = self._get_credentials()
        if not creds:
            return "Gmail no configurado."

        try:
            from googleapiclient.discovery import build
            from email.mime.text import MIMEText
            import base64

            service = build('gmail', 'v1', credentials=creds)

            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            sent = service.users().messages().send(
                userId='me', body={'raw': raw}
            ).execute()

            return f"✅ Correo enviado a {to}"
        except Exception as e:
            return f"Error enviando correo: {str(e)[:100]}"


google_services = GoogleServices()
