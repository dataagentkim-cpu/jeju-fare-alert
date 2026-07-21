# systemd에서 실행할 에이전트 서비스 진입점입니다.

import logging
import os
import signal
import threading


def main() -> None:
    logging.basicConfig(
        level=os.getenv("APP_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(message)s",
    )

    stop_event = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop_event.set())
    signal.signal(signal.SIGINT, lambda *_: stop_event.set())

    logging.info("agent service started")
    stop_event.wait()
    logging.info("agent service stopped")


if __name__ == "__main__":
    main()
