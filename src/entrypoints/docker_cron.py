from __future__ import annotations

import sys
from typing import Any

from apscheduler.schedulers.blocking import BlockingScheduler  # type: ignore[import-untyped]
from apscheduler.triggers.cron import CronTrigger  # type: ignore[import-untyped]

from src.entrypoints.docker_once import run_once
from src.infra.config.settings import Settings
from src.infra.logger import init_logger


def main() -> None:
    logger: Any = init_logger()

    settings = Settings()
    check_every_minutes = settings.wildberries.check_every_minutes
    cron = f"*/{check_every_minutes} * * * *"

    scheduler = BlockingScheduler()

    def job() -> None:
        logger.bind(job="wb_responder").info("cron_job_started")
        try:
            run_once()
        except Exception as exc:
            logger.bind(job="wb_responder", error=str(exc)).exception("cron_job_failed")
        finally:
            logger.bind(job="wb_responder").info("cron_job_finished")

    scheduler.add_job(
        job,
        CronTrigger.from_crontab(cron),
        id="wb_responder",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    logger.bind(job="wb_responder").info("startup_run_started")
    try:
        run_once()
    except Exception as exc:
        logger.bind(job="wb_responder", error=str(exc)).exception("startup_run_failed")
        sys.exit(1)
    else:
        logger.bind(job="wb_responder").info("startup_run_finished")

    scheduler.start()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(1)
