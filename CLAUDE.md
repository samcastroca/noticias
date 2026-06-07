# CLAUDE.md

## De qué se trata
Sistema que detecta y visualiza en tiempo real las noticias en tendencia de
los principales medios colombianos. La IA es el núcleo, no un adorno: el
sistema "entiende" las noticias en vez de solo listarlas.

## La idea central (el modelo mental que explica todo lo demás)
Cada artículo se convierte en un vector (embedding) que captura su significado.
En ese espacio semántico, las noticias que hablan de lo mismo quedan cerca,
aunque usen palabras distintas. De ahí salen las tres capacidades del sistema:
- AGRUPAR: artículos cercanos = la misma historia (clustering). Esto resuelve
  la deduplicación entre fuentes sin comparar texto.
- TENDENCIA: una región del espacio que se DENSIFICA rápido = un tema del que
  se empezó a hablar mucho. Una tendencia no es una palabra que se repite, es
  una zona que se llena de golpe. La señal es la derivada (velocidad de
  llegada), no el tamaño absoluto.
- ENTENDER: un LLM lee cada grupo y produce un resumen multi-fuente neutral y
  una categoría.
Una sola idea geométrica unifica agrupar, deduplicar y detectar tendencias.

## Por qué las reglas duras son como son
- El espacio de los embeddings tiene muchas dimensiones (~1536). Para MOSTRARLO
  a un humano se proyecta a 3D con UMAP. Pero UMAP deforma distancias y
  densidades A PROPÓSITO para que se vea bien: medir tendencias sobre el 3D
  mide artefactos de la proyección, no la realidad. Por eso el cómputo va en
  alta dimensión y el 3D es SOLO una pantalla.
- El LLM es la parte cara. Llamarlo por artículo multiplica el costo sin
  aportar; por cluster y solo cuando cambia, el costo cae a centavos al día.
- Embeber es baratísimo; el LLM no. Esa asimetría dicta toda la arquitectura.

## Flujo
Fuentes RSS (El Tiempo, El Espectador, El Colombiano, El Universal/El Heraldo)
→ worker ingiere → embebe → agrupa (HDBSCAN, alta dim.) → puntúa tendencia
→ LLM resume/categoriza el cluster → Postgres/pgvector. La API (FastAPI) sirve
al frontend React y empuja cambios por SSE. UMAP corre aparte solo para dar
coordenadas x/y/z al mapa 3D.

## Cómo trabajamos
- Antes de escribir código, presenta el plan de archivos (uno por línea, qué
  hace) y espera OK. Una fase a la vez; no te adelantes a fases futuras.
- Si una decisión contradice este archivo, detente y pregunta.

## Stack
- Backend: FastAPI (async). Worker de ingesta: proceso Python SEPARADO,
  APScheduler para cron. Comparten modelos y acceso a datos; corren aparte.
- Datos: PostgreSQL + pgvector. Redis (caché + pub/sub). Migraciones: Alembic.
- Frontend: React. Mapa 3D: react-three-fiber. Gráficos: Recharts. SSE para
  tiempo real (no WebSockets).
- Todo el contenido de cara al usuario va en ESPAÑOL.

## Reglas que NO se negocian (errores fáciles de cometer)
1. Clustering y scoring de tendencia se calculan SIEMPRE sobre los vectores
   originales en alta dimensión. UMAP es SOLO para coordenadas de display.
   Nunca medir densidad ni agrupar sobre las coordenadas 2D/3D.
2. El LLM se llama por CLUSTER, nunca por artículo. Solo se regenera si el
   cluster cambió de forma relevante; si no, se reusa el resultado cacheado.
   Usar modelo barato (tier nano/flash) y Batch API si está disponible.
3. UMAP se ajusta (fit) poco frecuente y se persiste; a los puntos nuevos
   solo se les aplica transform, para que el mapa no salte entre frames.
4. Los clusters necesitan ID estable entre ciclos (emparejado de centroides).
   HDBSCAN da etiquetas arbitrarias en cada corrida; "el mismo tema" conserva
   su id.
5. El worker nunca debe tumbar la API: una fuente caída o un fallo de red se
   captura y se sigue; no se propaga al proceso de la API.

## Convenciones
- Configurables por variable de entorno: modelo de embeddings, modelo LLM,
  ventana de tendencia (arranca en 1-2h por el volumen bajo de prensa
  colombiana), umbrales de cluster.
- Secretos (API keys) solo por entorno, nunca en el repo.
- Cada función de la pipeline (embeber, agrupar, puntuar, resumir) debe poder
  ejecutarse y probarse de forma aislada.

## Estado actual
Fase: 0 (andamiaje). << actualizar al cerrar cada fase >>