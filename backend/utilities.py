import os
import json
import math
import random
import datetime
import webbrowser
import subprocess
import platform
import psutil
import requests
from typing import Optional, Dict, Any, List
from collections import defaultdict


class Utilities:
    def __init__(self):
        self.reminders: List[Dict] = []
        self.notes: List[Dict] = []
        self.timer_start: Optional[float] = None
        self._data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        self._reminders_file = os.path.join(self._data_dir, "reminders.json")
        self._notes_file = os.path.join(self._data_dir, "notes.json")
        if os.path.exists(self._reminders_file):
            try:
                with open(self._reminders_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for r in data:
                        r["time"] = datetime.datetime.fromisoformat(r["time"])
                    self.reminders = data
            except Exception:
                pass
        if os.path.exists(self._notes_file):
            try:
                with open(self._notes_file, "r", encoding="utf-8") as f:
                    self.notes = json.load(f)
            except Exception:
                pass
        self.jokes = [
            # Ciencia
            "¿Por qué el electrón es tan pesado? Porque tiene masa.",
            "¿Qué le dijo un átomo a otro? 'Creo que me perdí un electrón'. '¿Estás seguro?' '¡Positivo!'",
            "¿Por qué los biólogos no confían en los átomos? Porque todo lo inventan.",
            "Un fotón entra a un hotel. El recepcionista le pregunta: '¿Necesita help con el equipaje?' El fotón responde: 'No, gracias, viajo a la velocidad de la luz.'",
            "¿Qué dijo Schrödinger al entrar al bar? 'Y no al mismo tiempo.'",
            "La gravedad es la forma más honesta de atraer a la gente.",
            "¿Por qué el neutrón es el mejor invitado de la fiesta? Porque no cobra entrada.",
            # Historia
            "Cleopatra vivió más cerca en el tiempo de la invención del iPhone que de la construcción de las pirámides.",
            "Los vikingos llegaron a América 500 años antes que Colón. Claro, no tenían Instagram para presumirlo.",
            "Napoleón no era bajo. Media 1.70m, que era promedio para su época. Los ingleses lo inventaron.",
            "Los romanos usaban orina como enjuague bucal. Ahora entiendes por qué sus gladiadores eran tan agresivos.",
            "En la Edad Media, los gatos eran considerados brujas. Hoy son los reyes de internet. Evolución.",
            # Deportes
            "¿Por qué el futbolista fue al banco? Porque quería cuestiones deInterest.",
            "¿Cuál es el deporte más peligroso? El ajedrez. Porque el peón puede llegar a ser rey y el rey puede morir.",
            "El golf es el único deporte donde golpear la pelota y dejarla quieta es un buen resultado.",
            "¿Por qué los corredores son malos en las citas? Porque siempre llegan con los tiempos.",
            "El.Boxing es el único deporte donde te pagan por pegar y recibir. En mi trabajo es al revés.",
            # Cocina
            "¿Qué le dijo una cebolla a otra? 'No me mires que estoy llorando por otra.'",
            "El café es como el código: sin él, nada funciona.",
            "¿Por qué el tomate se puso rojo? Porque vio la ensalada sin ropa.",
            "Un chef le dice a otro: '¿Este plato está crudo?' El otro responde: 'No, está natural.'",
            "La pizza es la única persona que puede unir a toda una familia. A menos que tengas alergia al gluten.",
            # Películas/TV
            "¿Qué le dijo Batman a Robin antes de subirse al batmóvil? 'Entra en el coche.'",
            "En una galaxia muy lejana... esperan, esto es el universo. Aquí todo está lejano.",
            "Indiana Jones es el único arqueólogo que destruye más historias de las que descubre.",
            "¿Por qué Thanos tenía razón? Porque el semáforo siempre está en rojo cuando llegas tarde.",
            "Harry Potter podía hacer magia, pero no pudo arreglar el wifi de los Dursley.",
            # Animales
            "¿Por qué los flamingos son rosa? Porque comen gambas. Yo como pizza y soy del color de la pizza.",
            "Un pingüino entra a una tienda y le dice al vendedor: 'Tenía un hermano pez'. El vendedor: '¿Y qué hacía?' El pingüino: 'Nada.'",
            "Los gatos creen que son dioses. Y los perros creen que nosotros somos dioses. Alguien se equivoca.",
            "¿Por qué los elefantes no usan computadora? Porque le tienen miedo al ratón.",
            "La vida es como un gato: siempre cae de pie.",
            # Vida cotidiana
            "Mi despertador y yo tenemos una relación tóxica: él me despierta y yo lo apago violentamente.",
            "El lunes es el día más largo del año. Los demás son los demás.",
            "El Wi-Fi es como el amor: no lo ves, pero lo sientes cuando se va.",
            "¿Qué tiene en común el fin de semana y el chocolate? Los dos desaparecen demasiado rápido.",
            "El gym es el único lugar donde ir al baño es parte del entrenamiento.",
            # Ciencia ficción
            "Si los aliens nos visitaran, lo primero que harían sería preguntar: '¿Dónde está el wifi?'",
            "La inteligencia artificial es como la magia: si la explicas, se llama programación.",
            "Los robots no sueñan con ovejas eléctricas. Sueñan con procesadores eléctricos.",
            "Viajar a la Speed of Light es posible. Solo necesitas una cantidad infinita de energía. ¿No tienes?",
            # Matemáticas
            "¿Por qué el 6 le tiene miedo al 7? Porque el 7 8 9 (siete comió nueve).",
            "Un matemático entra a un bar y dice: 'Quiero una cerveza multiplicada por cero.' El barman: '¿Nada?'",
            "Los números irracionales son como los humanos: nunca terminan y no tienen sentido.",
            "¿Cuánto es 1+1? Depende. En binario es 10. En amor es 3.",
            "La geometría es el único lugar donde puedes tener un ángulo muerto y un triángulo recto al mismo tiempo.",
        ]
        self.facts = [
            # Ciencia
            "El sol pierde 4 millones de toneladas de masa cada segundo. Afortunadamente, tiene suficiente para otros 5 mil millones de años.",
            "Tu cuerpo tiene más bacterias que células humanas. Eres literalmente un ecosistema ambulante.",
            "El agua caliente se congela más rápido que la fría. Esto se llama el efecto Mpemba.",
            "Los rayos no caen dos veces en el mismo lugar. ¡Falso! Caen repetidamente en edificios altos y torres.",
            "Un relámpago dura menos de un segundo, pero alcanza los 30,000°C. Es 5 veces más caliente que el sol.",
            "El cerebro humano puede procesar información a 432 km/h. Más rápido que un Ferrari.",
            "Si pudiéras plegar un papel 42 veces, llegaría a la Luna. Aunque tu impresora se queje.",
            "El cuerpo humano tiene 206 huesos al nacer, pero solo 206 de adulto. Algunos se fusionan.",
            "La luz del sol tarda 8 minutos en llegar a la Tierra. Es la única vez que el sol llega tarde.",
            "Los delfines se duermen con un ojo abierto. Son los vigilantes del océano.",
            # Historia
            "La Gran Muralla China NO se ve desde el espacio. Es un mito. Pero sí desde avión.",
            "Cleopatra vivió más cerca de la Luna landing que de la construcción de las pirámides.",
            "Los vikingos tenían un ritual: ducharse todos los domingos. Eran más limpios que muchos europeos.",
            "En la antigua Roma, las cenizas de los gladiadores se usaban como cosmético. Belleza desde el infierno.",
            "El imperio romano duró más de 1,000 años. Tu teléfono dura 2 años.",
            "Los samuráis eran también poetas. Guerreros de día, escritores de noche.",
            "En 1932, Australia declaró la guerra a los emúes. Y perdió.",
            "Los egipcios inventaron el calendario, el reloj de sol, y el horno. Todo en una civilización sin internet.",
            "La peste negra mató a 1/3 de Europa. Pero también subió los salarios de los sobrevivientes.",
            "Napoleón era alérgico a los gatos. Irónico para un hombre que conquistó media Europa.",
            # Espacio
            "En Venus llueve ácido sulfúrico. El peor día de lluvia de la historia.",
            "Un día en Mercurio dura 59 días terrestres. Imagínate el lunes así.",
            "Júpiter tiene 79 lunas conocidas. Tiene más acompañantes que tú en WhatsApp.",
            "El universo tiene 13.8 mil millones de años. Pero aún no ha descubierto TikTok.",
            "Si pudieras volar a la velocidad de la luz, tardarías 100,000 años en cruzar la Vía Láctea.",
            "Marte tiene un volcán del tamaño de Francia. Se llama Olympus Mons.",
            "Saturno flotaría en agua si tuvieras una bañera lo suficientemente grande.",
            "En la Estación Espacial International, los astronautas ven 16 amaneceres al día.",
            "La temperatura en Plutón es de -230°C. Ni tu ex tenía el corazón tan frío.",
            "Neptuno tiene los vientos más rápidos del sistema solar: 2,100 km/h.",
            # Cuerpo humano
            "El estómago produce una nueva capa de mucosa cada 3-4 días. Se digiere a sí mismo y se regenera.",
            "Los huesos son más fuertes que el acero. Un hueso de la pierna puede soportar 1,000 kg.",
            "El corazón late 100,000 veces al día. Es el working class hero del cuerpo.",
            "Tienes 600 músculos en el cuerpo. La mayoría los usas para ignorar alarmas.",
            "El ojo humano puede distinguir 10 millones de colores. Pero sigues eligiendo calcetines que no combinan.",
            "Tu nariz puede recordar 50,000 olores. Tu ex huele a traición, lo recuerdas perfectamente.",
            "La lengua es el músculo más fuerte del cuerpo por su tamaño. Especialmente para decir tonterías.",
            "El cerebro consume 20% de la energía del cuerpo. Piensa más, come más.",
            # Naturaleza
            "Las medusas existen desde 500 millones de años. Sobrevivieron sin cerebro. Inspírate.",
            "Un rayo puede alcanzar los 30,000°C. Es 5 veces más caliente que la superficie del sol.",
            "Las abejas pueden reconocer rostros humanos. Te están vigilando.",
            "Los pulpos tienen 3 corazones y sangre azul. Son los alienígenas de la Tierra.",
            "El bambú puede crecer 91 cm en un día. Es la planta más impaciente del mundo.",
            "Los flamencos nacen blancos y se vuelven rosa por la comida. Es como Instagram pero natural.",
            "Un tiburón ha existido más tiempo que los árboles. Los tiburones son más antiguos que los bosques.",
            "Las nutrias de mar se tompan de la mano para no perderse. Es lo más tierno del océano.",
            "Los koalas tienen huellas dactilares casi idénticas a las humanas. Crimen perfecto.",
            "Los árboles se comunican por el suelo a través de hongos. Tienen su propio internet.",
            # Tecnología
            "El nombre 'WiFi' no significa 'Wireless Fidelity'. Es simplemente un nombre comercial.",
            "El primer mouse de computadora fue inventado en 1964 y estaba hecho de madera.",
            "Java fue originalmente llamado 'Oak' por su creador. Se cambió porque ya existía un lenguaje llamado Oak.",
            "El email fue inventado antes que la World Wide Web. La gente ya mandaba correos cuando la web nació.",
            "El primer dominio registrado fue symbolics.com, el 15 de marzo de 1985.",
            "Python fue nombrado por el grupo de comedia Monty Python, no por la serpiente.",
            "El 90% de los datos del mundo se crearon en los últimos 2 años. Los datos son como el pelo: crecen rápido.",
            "El primer iPhone se vendió en 2007. Tenía 0.3 megapíxeles. Tu lavadora tiene mejor cámara.",
            "Un solo GPS puede medir tu posición con 1 metro de precisión. Tu novia puede medir tu mentira con más precisión.",
            "El internet pesa lo mismo que un gramo de fresa. Aunque tú cargas más.",
            # Curiosidades generales
            "La miel no caduca. Han encontrado miel en tumbas egipcias de 3,000 años que aún era comestible.",
            "Los牛乳 (leche) de burra se usa en cosméticos de lujo. Más cara que tu futuro.",
            "En Japón hay más de 50,000 especies de arañas. Todas son más valientes que tu ex.",
            "El chocolate negro contiene más antioxidantes que las fresas. Ahora tienes excusa para comer chocolate.",
            "Un cohete de SpaceX cuesta 62 millones de dólares. Tu deuda del.student loan es más barata.",
            "Los pingüinos proponen a sus parejas con una piedra. El más romántico del reino animal.",
            "El cerebro humano genera suficiente electricidad para encender una bombilla de 25W. Eres literalmente brillante.",
            "Los pulpos tienen sangre azul porque usan cobre en vez de hierro. Son como superheroes acuáticos.",
            "El plátano es técnicamente una baya, pero la fresa no. La naturaleza no tiene sentido.",
            "El 80% del espacio submarino no ha sido explorado. Sabemos más de Marte que de nuestro océano.",
        ]
        self.quotes = [
            # Tecnología
            "La tecnología es mejor cuando une a la gente. - Matt Mullenweg",
            "No temo a las computadoras. Lo que me falta son las horas. - Ada Lovelace",
            "La mejor manera de predecir el futuro es inventarlo. - Alan Kay",
            "La innovación es lo que distingue a un líder de un seguidor. - Steve Jobs",
            "El software es como el sexo: es mejor cuando es gratuito. - Linus Torvalds",
            # Filosofía
            "El futuro pertenece a quienes creen en la belleza de sus sueños. - Eleanor Roosevelt",
            "La simplicidad es la sofisticación suprema. - Leonardo da Vinci",
            "El mejor momento para plantar un árbol fue hace 20 años. El segundo mejor momento es ahora.",
            "No he fracasado. He encontrado 10,000 formas que no funcionan. - Thomas Edison",
            "La vida es lo que pasa mientras estás ocupado haciendo otros planes. - John Lennon",
            # Ciencia
            "La ciencia no es solo una disciplina de razón, sino también de amor y pasión. - Carl Sagan",
            "Si no puedes explicarlo simple, no lo entiendes bien. - Albert Einstein",
            "El más grande error es no cometer ninguno. - Albert Einstein",
            "La imaginación es más importante que el conocimiento. - Albert Einstein",
            "Todo lo que podemos ver es solo una gota en el océano de lo que podemos saber. - Albert Einstein",
            # Éxito
            "El éxito es ir de fracaso en fracaso sin perder el entusiasmo. - Winston Churchill",
            "No sueñes con el éxito, trabaja para conseguirlo. - Estée Lauder",
            "El único modo de hacer un gran trabajo es amar lo que haces. - Steve Jobs",
            "La disciplina es el puente entre tus metas y tus logros. - Jim Rohn",
            "No esperes oportunidades, créalas. - Chris Grosser",
            # Amor a la vida
            "La vida es 10% lo que te pasa y 90% cómo reaccionas. - Charles R. Swindoll",
            "Ser feliz no significa que todo sea perfecto, sino que decidiste ver más allá de las imperfecciones.",
            "La mejor venganza es una vida bien vivida. - Frank Sinatra",
            "No mires atrás. No estabas yendo en esa dirección.",
            "La felicidad no es algo hecho. Viene de tus propias acciones. - Dalai Lama",
            # Humor
            "La vida es corta. Sonríe mientras todavía tienes dientes.",
            "No soy vago. Estoy en modo de ahorro de energía.",
            "Mi motivación no funciona así. Necesito un deadlines o pizza.",
            "Dime que eres programador sin decirme que eres programador: funciona en mi máquina.",
            "La vida es como un bicicleta: si no equilibras, te caes.",
            # Motivación
            "El que tiene un porqué para vivir puede soportar casi cualquier cómo. - Friedrich Nietzsche",
            "La perfección no es alcanzable, pero si perseguimos la perfección podemos alcanzar la excelencia. - Vince Lombardi",
            "El único lugar donde el éxito viene antes del trabajo es en el diccionario. - Vidal Sassoon",
            "La mente que se abre a una nueva idea jamás volverá a su tamaño original. - Albert Einstein",
            "No se puede cruzar un abismo en dos pequeños saltos. - David Lloyd George",
        ]

    def _save_reminders(self):
        os.makedirs(self._data_dir, exist_ok=True)
        data = []
        for r in self.reminders:
            entry = dict(r)
            entry["time"] = entry["time"].isoformat()
            data.append(entry)
        with open(self._reminders_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _save_notes(self):
        os.makedirs(self._data_dir, exist_ok=True)
        with open(self._notes_file, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

    def get_weather(self, city: str = "Madrid") -> str:
        try:
            url = f"https://wttr.in/{city}?format=j1&lang=es"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            current = data["current_condition"][0]
            temp = current["temp_C"]
            desc = current["lang_es"][0]["value"]
            humidity = current["humidity"]
            wind = current["windspeedKmph"]
            feels = current["FeelsLikeC"]
            return (
                f"Clima en {city}:\n"
                f"Temperatura: {temp}°C (sensación {feels}°C)\n"
                f"Condición: {desc}\n"
                f"Humedad: {humidity}%\n"
                f"Viento: {wind} km/h"
            )
        except Exception:
            return "No pude obtener el clima. Verifica tu conexión."

    def calculate(self, expression: str) -> str:
        try:
            safe_expr = expression.replace("x", "*").replace("X", "*").replace("÷", "/")
            safe_expr = safe_expr.replace("^", "**")
            allowed = set("0123456789+-*/.()**% ")
            if not all(c in allowed for c in safe_expr):
                return "Expresión no válida"
            result = eval(safe_expr)
            return f"Resultado: {result}"
        except Exception as e:
            return f"Error en el cálculo: {str(e)}"

    def convert(self, value: float, from_unit: str, to_unit: str) -> str:
        conversions = {
            ("km", "mi"): 0.621371,
            ("mi", "km"): 1.60934,
            ("kg", "lb"): 2.20462,
            ("lb", "kg"): 0.453592,
            ("m", "ft"): 3.28084,
            ("ft", "m"): 0.3048,
            ("cm", "in"): 0.393701,
            ("in", "cm"): 2.54,
            ("l", "gal"): 0.264172,
            ("gal", "l"): 3.78541,
            ("c", "f"): lambda x: x * 9/5 + 32,
            ("f", "c"): lambda x: (x - 32) * 5/9,
        }
        key = (from_unit.lower(), to_unit.lower())
        if key in conversions:
            factor = conversions[key]
            if callable(factor):
                result = factor(value)
            else:
                result = value * factor
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        return f"Conversión no soportada: {from_unit} → {to_unit}"

    def add_reminder(self, text: str, minutes: int = 5) -> str:
        import threading
        reminder = {
            "text": text,
            "time": datetime.datetime.now() + datetime.timedelta(minutes=minutes),
            "id": len(self.reminders) + 1
        }
        self.reminders.append(reminder)
        self._save_reminders()
        return f"Recordatorio #{reminder['id']} configurado para {minutes} minutos: {text}"

    def get_reminders(self) -> str:
        if not self.reminders:
            return "No hay recordatorios activos."
        now = datetime.datetime.now()
        active = [r for r in self.reminders if r["time"] > now]
        if not active:
            return "No hay recordatorios pendientes."
        result = "Recordatorios activos:\n"
        for r in active:
            remaining = (r["time"] - now).seconds // 60
            result += f"#{r['id']}: {r['text']} (en {remaining} min)\n"
        return result.strip()

    def add_note(self, text: str) -> str:
        note = {
            "text": text,
            "time": datetime.datetime.now().strftime("%H:%M"),
            "id": len(self.notes) + 1
        }
        self.notes.append(note)
        self._save_notes()
        return f"Nota #{note['id']} guardada: {text}"

    def get_notes(self) -> str:
        if not self.notes:
            return "No hay notas guardadas."
        result = "Notas:\n"
        for n in self.notes[-10:]:
            result += f"#{n['id']} [{n['time']}]: {n['text']}\n"
        return result.strip()

    def get_joke(self) -> str:
        return random.choice(self.jokes)

    def get_fact(self) -> str:
        return random.choice(self.facts)

    def get_quote(self) -> str:
        return random.choice(self.quotes)

    def get_disk_info(self) -> str:
        parts = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                total_gb = usage.total / (1024**3)
                used_gb = usage.used / (1024**3)
                free_gb = usage.free / (1024**3)
                pct = usage.percent
                parts.append(f"Disco {part.mountpoint}: {used_gb:.1f}/{total_gb:.1f} GB ({pct}%) - Libre: {free_gb:.1f} GB")
            except:
                pass
        return "Almacenamiento:\n" + "\n".join(parts) if parts else "No se detectaron discos."

    def get_network_info(self) -> str:
        try:
            net = psutil.net_io_counters()
            sent = net.bytes_sent / (1024**2)
            recv = net.bytes_recv / (1024**2)
            return f"Red:\nEnviado: {sent:.1f} MB\nRecibido: {recv:.1f} MB"
        except:
            return "No se pudo obtener info de red."

    def get_uptime(self) -> str:
        boot = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        return f"Tiempo encendido: {uptime.days}d {hours}h {minutes}m"

    def open_app(self, app_name: str) -> str:
        apps = {
            "notepad": "notepad.exe",
            "bloc de notas": "notepad.exe",
            "paint": "mspaint.exe",
            "terminal": "cmd.exe",
            "powershell": "powershell.exe",
            "task manager": "taskmgr.exe",
            "administrador de tareas": "taskmgr.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "spotify": "spotify.exe",
            "discord": "discord.exe",
            "vscode": "code.exe",
            "visual studio code": "code.exe",
        }
        for key, exe in apps.items():
            if key in app_name.lower():
                try:
                    subprocess.Popen(exe)
                    return f"Abriendo {key}..."
                except:
                    return f"No pude abrir {key}"
        return f"No encontré la aplicación: {app_name}"

    def search_web(self, query: str) -> str:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Buscando en Google: {query}"

    def get_battery(self) -> str:
        try:
            bat = psutil.sensors_battery()
            if bat:
                status = "Cargando" if bat.power_plugged else "Usando batería"
                return f"Batería: {bat.percent}% - {status}"
        except:
            pass
        return "No se detectó batería (posiblemente un escritorio)."

    def get_ip(self) -> str:
        try:
            resp = requests.get("https://api.ipify.org", timeout=3)
            return f"IP Pública: {resp.text}"
        except:
            return "No se pudo obtener la IP pública."

    def generate_password(self, length: int = 16) -> str:
        import string
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(length))
        return f"Contraseña generada: {password}"

    def tell_time(self) -> str:
        now = datetime.datetime.now()
        return f"Son las {now.strftime('%H:%M')} del {now.strftime('%d/%m/%Y')}"

    def random_number(self, min_val: int = 1, max_val: int = 100) -> str:
        result = random.randint(min_val, max_val)
        return f"Número aleatorio entre {min_val} y {max_val}: {result}"

    def dice_roll(self, sides: int = 6) -> str:
        result = random.randint(1, sides)
        return f"Dado de {sides} caras: {result}"

    def get_whois(self, domain: str) -> str:
        try:
            resp = requests.get(f"https://api.hackertarget.com/whois/?q={domain}", timeout=5)
            lines = resp.text.strip().split('\n')[:10]
            return f"WHOIS {domain}:\n" + "\n".join(lines)
        except:
            return "No se pudo obtener información WHOIS."

utilities = Utilities()
