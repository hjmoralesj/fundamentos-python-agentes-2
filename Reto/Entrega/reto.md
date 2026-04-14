# Reto
Tu proyecto debe tener como mínimo estos archivos, cada uno con una única responsabilidad clara:

* `agente.py` — clases `PseudoAgente` y `AgenteAdmin`. La regla dura: **al "despertar" a un agente desde la base de datos, debes reconstruir su clase según el rol**. Si en la tabla `agentes` su rol es `"admin"` debes instanciar `AgenteAdmin(...)`; si es otro, `PseudoAgente(...)`. Esto se verifica con `isinstance`. No basta con devolver un diccionario: el objeto de dominio debe volver a existir cuando tu código lo necesite (por ejemplo, al completar una misión y descontar energía, quien decide cómo se descuenta es la clase, no el endpoint). Aquí **no hay SQL ni FastAPI**.
* `db.py` — funciones que hablan con SQLite: Crear tablas, Registrar fila, Consultar agente por nombre, Registrar mensaje, Consultar mensajes por destinatario, Consultar mensajes por remitente y las nuevas funciones para `misiones`. Aquí **no hay FastAPI**.
* `main.py` — la aplicación FastAPI y los endpoints. Importa desde `agente.py` y `db.py`. Aquí **no defines clases de dominio ni queries SQL en crudo**. Deben ser similes a las definidas en `db.py`. 
* `cliente.py` — script que consume tu API creada por HTTP con `requests`. Ejecuta un guion de demostración end-to-end.
* `config.py` *(opcional pero recomendado)* — carga de variables de entorno.

# Tablas 
```sql
CREATE TABLE IF NOT EXISTS agentes (
            nombre TEXT PRIMARY KEY,
            rol TEXT,
            energia INTEGER
        );

CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remitente TEXT,
            destinatario TEXT,
            contenido TEXT,
            timestamp TEXT
        );

CREATE TABLE IF NOT EXISTS misiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    agente_asignado TEXT,
    estado TEXT,                -- 'pendiente' | 'en_curso' | 'completada' | 'fallida'
    energia_requerida INTEGER,
    prioridad TEXT,             -- decisión de ingeniería: por ejemplo 'baja' | 'media' | 'alta'
    deadline_at TEXT,           -- timestamp ISO 8601, ej. 2026-04-14T15:30:00Z
    created_at TEXT,            -- timestamp ISO 8601
    completed_at TEXT,          -- timestamp ISO 8601
    updated_at TEXT,            -- timestamp ISO 8601
    result TEXT
);
```

Notas sobre fechas:

* En SQLite puedes guardar fechas como `TEXT` siempre que uses formato ISO 8601 de forma consistente.
* Para este reto, los campos temporales (`deadline_at`, `created_at`, `completed_at`, `updated_at` y cualquier `timestamp`) deben persistirse como strings ISO 8601.
* Si decides otro almacenamiento temporal, justifícalo en el `README.md`.

# API (main.py)
**Agrega** los siguientes endpoints:

| Método | Ruta | Protegido | Qué hace |
|---|---|---|---|
|`GET`|`/`|No|Verifica que el sistema esté arriba|
|`GET`|`/agentes/{nombre}`|Si|Consulta un agente por nombre|
|`GET`|`/agentes/`|Si|Consulta todos los agentes|
|`POST`|`/agentes/`|Si|Crea un agente|
|`POST`|`/mensajes`|Si|Registra un mensaje|
|`GET`|`/mensajes/{nombre}`|Si|Consulta los mensajes por el nombre del destinatario |
| `POST` | `/misiones/` | Sí | Crea una misión. Si el `agente_asignado` no existe en la tabla `agentes`, responde `404`. |
| `GET` | `/misiones/{id}` | Si | Devuelve la misión o `404`. |
| `GET` | `/agentes/{nombre}/misiones` | No | Lista las misiones asignadas a un agente. |
| `POST` | `/misiones/{id}/completar` | Si | Marca la misión como `"completada"`. **Aquí se usa la clase de S4:** despierta el agente desde la DB, reconstruye la instancia correcta, descuenta `energia_requerida` a través de un método de la clase, y persiste el nuevo estado del agente. 
| `GET` | `/briefing/{nombre}` | No | Devuelve un briefing combinado con datos locales del agente y una API pública externa. |

Convención de rutas:

* Usa plural para colecciones (`/agentes/`, `/misiones/`) y un identificador para detalle (`/agentes/{nombre}`, `/misiones/{id}`).
* Mantén esa convención también en el cliente HTTP y en la documentación del proyecto.

# Cliente HTTP de demostración
`cliente.py` debe ejecutar, sin intervención manual, un guion que:

1. Verifica que el servidor está vivo (`GET /`).
2. Crea un agente (`POST /agentes/`) con autenticación.
3. Crea una misión asignada a ese agente (`POST /misiones/`) con autenticación.
4. Completa la misión (`POST /misiones/{id}/completar`) con autenticación.
5. Consulta el briefing del agente (`GET /briefing/{nombre}`) y lo imprime.
6. Envía un mensaje entre agentes y lee la bandeja.

Este guion es la prueba viva de que tu circuito funciona de punta a punta.

# ✅ Validación con Pydantic
Problema: si la API acepta cualquier payload, terminarás guardando datos inválidos o incompletos y los errores aparecerán demasiado tarde.

Qué entregar:

Define modelos Pydantic para las entradas y salidas principales de tu API, al menos para agentes, mensajes, misiones y briefing.
Valida campos obligatorios, tipos y restricciones básicas (por ejemplo: `energia` y `energia_requerida` no negativas, `titulo` no vacío, `estado` dentro de los valores permitidos).
Los campos de fecha expuestos por la API deben representarse como `datetime` o strings ISO 8601 válidos y serializarse de forma consistente.
Los endpoints de FastAPI deben usar esos modelos como `request body` y, cuando tenga sentido, como `response_model`.

# 🔐 Autenticación con API key
Problema: ahora que tu API está expuesta, cualquier persona podría crear agentes fantasma o completar misiones ajenas. La Agencia necesita una llave maestra que sólo conocen sus operadores.

Qué entregar:

Una función (dependencia de FastAPI) que lea un header X-API-KEY de cada request y lo compare contra el valor configurado en tu .env. Si no coincide o no viene: HTTPException(status_code=401, detail="API key inválida").
Aplicar esa dependencia a todos los endpoints de escritura marcados con "Sí" en la tabla de API.
Decisión tuya: si los GET también deben protegerse o no (justifícalo en el README).

# 🗝️ Configuración con variables de entorno
Problema: la API key de tu Agencia y la URL de la API externa no deben estar en el código fuente. Si las subes a GitHub, cualquiera las copia.

Qué entregar:

Un archivo .env (local, no se versiona) con al menos:
AGENCIA_API_KEY=...
EXTERNAL_API_URL=...
Un archivo .env.example (sí se versiona) con las mismas claves pero sin valores reales, para que otra persona sepa qué configurar.
Tu código carga esas variables al arrancar y las usa. No hay strings literales con secretos en el código.
Tu .gitignore incluye .env.

# 🌐 Inteligencia externa (API pública)
Problema: un agente aislado de la realidad no es inteligente. Dale un canal al mundo.

Qué entregar:

El endpoint GET /briefing/{nombre} debe, internamente, hacer requests.get(...) a una API pública sin autenticación que tú elijas. La respuesta del endpoint debe combinar:
Datos locales del agente (de la tabla agentes).
Un campo traído de la API externa (un hecho, un consejo, el clima, una frase, una cotización… lo que tenga sentido con tu narrativa).
Una marca del origen ("fuente_externa": "...").
Manejo de fallos: la API externa puede tardar o estar caída. Define un timeout razonable y un plan de contingencia con try/except. Nunca dejes que tu servidor se cuelgue por culpa de un tercero.

# 🧭 Decisiones de Ingeniería (tu huella en el proyecto)
Hay tres decisiones que no te vamos a dar resueltas. Tómalas, impleméntalas y justifícalas en un README.md del proyecto (mínimo 3 líneas cada una):

Esquema de la tabla misiones. ¿Qué columnas extra agregaste más allá del mínimo? ¿Por qué? (Ej: prioridad, deadline, creado_por, recompensa…). Si mantuviste fechas como `TEXT`, explica por qué ISO 8601 fue suficiente; si no, justifica tu alternativa.
API pública elegida. ¿Cuál escogiste? ¿Por qué encaja con la narrativa de agentes? ¿Qué añade al briefing?
Estrategia de resiliencia. ¿Qué pasa cuando la API externa falla o tarda? ¿Tu agente responde con un mensaje de fallback, omite el campo, o devuelve un error? ¿Por qué?
