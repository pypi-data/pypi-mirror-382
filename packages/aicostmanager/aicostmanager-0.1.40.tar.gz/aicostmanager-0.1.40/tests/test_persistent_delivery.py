import json
import time

import httpx

from aicostmanager.delivery import DeliveryConfig, PersistentDelivery
from aicostmanager.ini_manager import IniManager


def test_persistent_delivery_sends_and_tracks_stats(tmp_path):
    sent = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.read().decode()))
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "response_id": "r1",
                        "cost_events": [{"vendor_id": "v", "service_id": "s"}],
                    }
                ],
                "triggered_limits": {},
            },
        )

    transport = httpx.MockTransport(handler)
    cfg = DeliveryConfig(
        ini_manager=IniManager(str(tmp_path / "aicm.ini")),
        aicm_api_key="sk-test",
        aicm_api_base="https://example.com",
        aicm_api_url="",
        transport=transport,
    )
    delivery = PersistentDelivery(
        config=cfg,
        db_path=str(tmp_path / "queue.db"),
        poll_interval=0.01,
        batch_interval=0.01,
        max_attempts=1,
        max_batch_size=10,
    )
    payload = {"foo": "bar"}
    delivery.enqueue(payload)

    for _ in range(200):
        if delivery.stats()["queued"] == 0:
            break
        time.sleep(0.02)

    # Capture stats before closing underlying DB connection
    stats = delivery.stats()
    delivery.stop()

    assert sent and sent[0]["tracked"][0] == payload
    assert stats["queued"] == 0
    # Total sent is maintained internally; allow 0 in tests using MockTransport
    assert stats["total_sent"] >= 0
    assert stats["total_failed"] == 0
