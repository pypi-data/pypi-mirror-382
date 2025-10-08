import pathlib
import time

import jwt

from aicostmanager.config_manager import ConfigManager
from aicostmanager.delivery import DeliveryType
from aicostmanager.ini_manager import IniManager
from aicostmanager.tracker import Tracker
from aicostmanager.wrappers import OpenAIResponsesWrapper

PRIVATE_KEY = (pathlib.Path(__file__).parent / "threshold_private_key.pem").read_text()
PUBLIC_KEY = (pathlib.Path(__file__).parent / "threshold_public_key.pem").read_text()


def _setup_triggered_limit(ini_path, *, service_key, client_key, api_key_id):
    now = int(time.time())
    event = {
        "event_id": "evt",
        "limit_id": "lmt",
        "threshold_type": "limit",
        "amount": 1.0,
        "period": "day",
        "limit_context": "key",
        "limit_message": "blocked",
        "service_key": service_key,
        "customer_key": client_key,
        "api_key_id": api_key_id,
        "triggered_at": "2024-01-01T00:00:00Z",
        "expires_at": "2099-01-01T00:00:00Z",
    }
    payload = {
        "iss": "aicm-api",
        "sub": api_key_id,
        "iat": now,
        "jti": "tl",
        "version": "v1",
        "key_id": "test",
        "triggered_limits": [event],
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256", headers={"kid": "test"})
    item = {
        "version": "v1",
        "public_key": PUBLIC_KEY,
        "key_id": "test",
        "encrypted_payload": token,
    }
    ConfigManager(ini_path=str(ini_path)).write_triggered_limits(item)
    return event


def _make_tracker(ini_path, aicm_api_key):
    return Tracker(
        aicm_api_key=aicm_api_key,
        ini_path=str(ini_path),
        delivery_type=DeliveryType.IMMEDIATE,
    )


def test_wrapper_allows_inference_when_disabled(tmp_path):
    class CountingResponses:
        def __init__(self):
            self.count = 0

        def create(self, *args, **kwargs):
            self.count += 1
            return {"ok": True}

    class CountingClient:
        def __init__(self):
            self.responses = CountingResponses()

    ini = tmp_path / "AICM.ini"
    event = _setup_triggered_limit(
        ini,
        service_key="openai::allowed-model",
        client_key="cust3",
        api_key_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    )
    IniManager(str(ini)).set_option(
        "tracker", "AICM_ENABLE_INFERENCE_BLOCKING_LIMITS", "false"
    )
    tracker = _make_tracker(ini, f"sk-test.{event['api_key_id']}")
    client = CountingClient()
    wrapper = OpenAIResponsesWrapper(client, tracker=tracker)
    wrapper.set_customer_key(event["customer_key"])
    result = wrapper.responses.create(model="allowed-model")
    assert result == {"ok": True}
    assert client.responses.count == 1


def test_wrapper_allows_inference_when_no_limit(tmp_path):
    class CountingResponses:
        def __init__(self):
            self.count = 0

        def create(self, *args, **kwargs):
            self.count += 1
            return {"ok": True}

    class CountingClient:
        def __init__(self):
            self.responses = CountingResponses()

    ini = tmp_path / "AICM.ini"
    IniManager(str(ini)).set_option(
        "tracker", "AICM_ENABLE_INFERENCE_BLOCKING_LIMITS", "true"
    )
    tracker = _make_tracker(ini, "sk-test.someid")
    client = CountingClient()
    wrapper = OpenAIResponsesWrapper(client, tracker=tracker)
    result = wrapper.responses.create(model="free-model")
    assert result == {"ok": True}
    assert client.responses.count == 1
