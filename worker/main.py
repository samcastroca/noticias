import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler

from shared.config import settings
from worker.jobs import ingest_rss

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        ingest_rss,
        "interval",
        seconds=settings.ingest_interval_seconds,
        id="ingest_rss",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Worker iniciado. Intervalo de ingesta: %ds", settings.ingest_interval_seconds
    )

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Worker detenido.")


if __name__ == "__main__":
    main()
