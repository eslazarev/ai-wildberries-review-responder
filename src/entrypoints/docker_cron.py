from __future__ import annotations

import os
import sys
from typing import Any

from apscheduler.schedulers.blocking import BlockingScheduler  # type: ignore[import-untyped]
from apscheduler.triggers.cron import CronTrigger  # type: ignore[import-untyped]

from src.entrypoints.docker_once import run_once
from src.infra.config.settings import Settings
from src.infra.logger import init_logger


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def main() -> None:
    logger: Any = init_logger()

    schedule_cron = os.getenv("SCHEDULE_CRON")
    if schedule_cron and schedule_cron.strip():
        cron = schedule_cron.strip()
    else:
        settings = Settings()
        cron = f"*/{settings.wildberries.check_every_minutes} * * * *"
    timezone_name = os.getenv("SCHEDULE_TZ", "UTC")
    run_on_startup = _env_bool("RUN_ON_STARTUP", True)

    scheduler = BlockingScheduler(timezone=timezone_name)

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
        CronTrigger.from_crontab(cron, timezone=timezone_name),
        id="wb_responder",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    if run_on_startup:
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
