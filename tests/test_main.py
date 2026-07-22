# 가격 선택과 실행 시각 계산을 검증합니다.

import io
import json
import unittest
from datetime import datetime
from unittest.mock import patch

from src.main import SEOUL, fetch_lowest_fare, next_run


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class FareTests(unittest.TestCase):
    @patch("src.main.urlopen")
    def test_fetch_lowest_fare_selects_minimum_price(self, mocked_urlopen):
        mocked_urlopen.side_effect = [
            Response(
                json.dumps(
                    {
                        "search_metadata": {"google_flights_url": "https://example.com/search"},
                        "best_flights": [
                            {
                                "price": 400000,
                                "departure_token": "expensive",
                                "flights": [
                                    {
                                        "airline": "비싼항공",
                                        "departure_airport": {"time": "2026-09-24 09:00"},
                                        "arrival_airport": {"time": "2026-09-24 10:00"},
                                    }
                                ],
                            }
                        ],
                        "other_flights": [
                            {
                                "price": 300000,
                                "departure_token": "cheapest",
                                "flights": [
                                    {
                                        "airline": "저렴항공",
                                        "departure_airport": {"time": "2026-09-24 10:00"},
                                        "arrival_airport": {"time": "2026-09-24 11:00"},
                                    }
                                ],
                            }
                        ],
                    }
                ).encode()
            ),
            Response(
                json.dumps(
                    {
                        "best_flights": [
                            {
                                "price": 300000,
                                "flights": [
                                    {
                                        "airline": "돌아오는항공",
                                        "departure_airport": {"time": "2026-09-27 18:00"},
                                        "arrival_airport": {"time": "2026-09-27 19:00"},
                                    }
                                ],
                            }
                        ]
                    }
                ).encode()
            ),
        ]

        fare = fetch_lowest_fare("test-key")

        self.assertEqual(fare["price"], 300000)
        self.assertEqual(fare["outbound_airline"], "저렴항공")
        self.assertEqual(fare["outbound_departure"], "2026-09-24 10:00")
        self.assertEqual(fare["inbound_airline"], "돌아오는항공")
        self.assertEqual(fare["inbound_departure"], "2026-09-27 18:00")

    def test_next_run_uses_same_day_slot(self):
        now = datetime(2026, 7, 22, 10, 30, tzinfo=SEOUL)
        self.assertEqual(next_run(now), datetime(2026, 7, 22, 15, 0, tzinfo=SEOUL))

    def test_next_run_rolls_to_next_day(self):
        now = datetime(2026, 7, 22, 21, 0, tzinfo=SEOUL)
        self.assertEqual(next_run(now), datetime(2026, 7, 23, 9, 0, tzinfo=SEOUL))


if __name__ == "__main__":
    unittest.main()
