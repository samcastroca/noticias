# Noticias Colombia

Detector y visualizador en tiempo real de noticias en tendencia de los principales medios colombianos. La IA es el núcleo: los artículos se convierten en vectores semánticos para agruparlos, detectar tendencias y resumirlos con un LLM.

## Arquitectura

```
RSS feeds → worker (ingesta + embeddings + clustering) → Postgres/pgvector
                                                       ↓
                                              FastAPI (SSE) → React (mapa 3D)
```

- **Postgres + pgvector** — almacena artículos con embeddings y clusters
- **Redis** — caché y pub/sub
- **API** (FastAPI) — sirve datos al frontend por HTTP y SSE
- **Worker** (proceso separado) — ingesta RSS, embebe, agrupa, puntúa tendencias, llama al LLM por cluster

## Levantar en desarrollo

```bash
cp .env.example .env
# editar .env para añadir tu API key de OpenAI
docker-compose up --build
```

Aplicar migraciones (primera vez):

```bash
docker-compose exec api alembic upgrade head
```

Verificar:

```bash
curl http://localhost:8000/health
# → {"status":"ok","version":"0.1.0"}

docker-compose exec redis redis-cli ping
# → PONG
```

## Variables de entorno

Ver [.env.example](.env.example) para la lista completa. Las más importantes:

| Variable | Descripción | Default |
|---|---|---|
| `DATABASE_URL` | Conexión a Postgres | `postgresql+asyncpg://...` |
| `REDIS_URL` | Conexión a Redis | `redis://redis:6379/0` |
| `EMBED_MODEL` | Modelo de embeddings | `text-embedding-3-small` |
| `LLM_MODEL` | Modelo LLM para resúmenes | `gpt-4o-mini` |
| `TREND_WINDOW_HOURS` | Ventana de detección de tendencias | `2` |
| `INGEST_INTERVAL_SECONDS` | Frecuencia de ingesta RSS | `300` |

## Estructura del proyecto

```
shared/      — código compartido entre API y worker (modelos, DB, config)
api/         — servicio FastAPI
worker/      — proceso de ingesta con APScheduler
alembic/     — migraciones de base de datos
requirements/
  base.txt   — dependencias comunes
  api.txt    — dependencias de la API
  worker.txt — dependencias del worker
```

## Estado

**Fase 0** — andamiaje: infraestructura Docker, esquema de BD, esqueleto de API y worker.
