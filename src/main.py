# Google Flights 최저가를 조회해 텔레그램으로 알리는 서비스 진입점입니다.

import argparse
import json
import logging
import os
import signal
import threading
from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


SEOUL = ZoneInfo("Asia/Seoul")
RUN_HOURS = (9, 15, 21)
SERPAPI_URL = "https://serpapi.com/search.json"
TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing environment variable: {name}")
    return value


def fetch_lowest_fare(api_key: str) -> dict:
    params = {
        "engine": "google_flights",
        "departure_id": "GMP",
        "arrival_id": "CJU",
        "outbound_date": "2026-09-24",
        "return_date": "2026-09-27",
        "type": "1",
        "travel_class": "1",
        "adults": "4",
        "stops": "1",
        "sort_by": "2",
        "currency": "KRW",
        "hl": "ko",
        "gl": "kr",
        "api_key": api_key,
    }
    with urlopen(f"{SERPAPI_URL}?{urlencode(params)}", timeout=60) as response:
        payload = json.load(response)

    if payload.get("error"):
        raise RuntimeError(payload["error"])

    offers = payload.get("best_flights", []) + payload.get("other_flights", [])
    priced_offers = [offer for offer in offers if isinstance(offer.get("price"), int)]
    if not priced_offers:
        raise RuntimeError("no priced nonstop round-trip offers found")

    cheapest = min(priced_offers, key=lambda offer: offer["price"])
    first_leg = cheapest.get("flights", [{}])[0]
    return {
        "price": cheapest["price"],
        "airline": first_leg.get("airline", "항공사 미상"),
        "departure": first_leg.get("departure_airport", {}).get("time", "시간 미상"),
        "search_url": payload.get("search_metadata", {}).get(
            "google_flights_url", "https://www.google.com/travel/flights"
        ),
    }


def send_telegram(token: str, chat_id: str, text: str) -> None:
    body = urlencode({"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"}).encode()
    request = Request(TELEGRAM_API_URL.format(token=token), data=body, method="POST")
    with urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if not payload.get("ok"):
        raise RuntimeError("Telegram API rejected the message")


def check_and_notify() -> None:
    fare = fetch_lowest_fare(required_env("SERPAPI_API_KEY"))
    checked_at = datetime.now(SEOUL).strftime("%Y-%m-%d %H:%M")
    message = (
        "✈️ 김포–제주 왕복 직항 최저가\n"
        "일정: 2026-09-24 ~ 2026-09-27\n"
        "인원: 성인 4명\n"
        f"가격: {fare['price']:,}원\n"
        f"항공사: {fare['airline']}\n"
        f"출발편: {fare['departure']}\n"
        f"확인: {checked_at} KST\n"
        f"검색 결과: {fare['search_url']}"
    )
    send_telegram(
        required_env("TELEGRAM_BOT_TOKEN"),
        required_env("TELEGRAM_CHAT_ID"),
        message,
    )


def next_run(now: datetime) -> datetime:
    for hour in RUN_HOURS:
        candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if candidate > now:
            return candidate
    return (now + timedelta(days=1)).replace(hour=RUN_HOURS[0], minute=0, second=0, microsecond=0)


def run_scheduler(stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        scheduled_for = next_run(datetime.now(SEOUL))
        delay = (scheduled_for - datetime.now(SEOUL)).total_seconds()
        logging.info("next check scheduled for %s", scheduled_for.isoformat())
        if stop_event.wait(max(delay, 0)):
            break
        try:
            check_and_notify()
        except Exception:
            logging.exception("fare check failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=os.getenv("APP_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(message)s",
    )

    if args.once:
        check_and_notify()
        return

    stop_event = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop_event.set())
    signal.signal(signal.SIGINT, lambda *_: stop_event.set())
    logging.info("jeju fare alert started")
    run_scheduler(stop_event)
    logging.info("jeju fare alert stopped")


if __name__ == "__main__":
    main()
