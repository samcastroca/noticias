import logging

logger = logging.getLogger(__name__)


def ingest_rss() -> None:
    """Stub de ingesta RSS — fase 0: solo registra el tick."""
    try:
        logger.info("tick: ingest_rss")
    except Exception:
        logger.exception("Error en ingest_rss")
