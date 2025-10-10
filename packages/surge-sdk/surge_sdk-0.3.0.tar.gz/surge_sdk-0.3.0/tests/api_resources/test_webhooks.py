# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest
import standardwebhooks

from surge import Surge

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWebhooks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    def test_method_unwrap(self, client: Surge) -> None:
        key = b"secret"
        hook = standardwebhooks.Webhook(key)

        data = """{"account_id":"acct_01japd271aeatb7txrzr2xj8sg","data":{"id":"call_01jjnn7s0zfx5tdcsxjfy93et2","contact":{"id":"ctc_01ja88cboqffhswjx8zbak3ykk","phone_number":"+18015551234","email":"dom@toretto.family","first_name":"Dominic","last_name":"Toretto","metadata":{"car":"1970 Dodge Charger R/T"}},"duration":184,"initiated_at":"2025-03-31T21:01:37Z","status":"completed"},"timestamp":"2024-10-21T23:29:41Z","type":"call.ended"}"""
        msg_id = "1"
        timestamp = datetime.now(tz=timezone.utc)
        sig = hook.sign(msg_id=msg_id, timestamp=timestamp, data=data)
        headers = {
            "webhook-id": msg_id,
            "webhook-timestamp": str(int(timestamp.timestamp())),
            "webhook-signature": sig,
        }

        try:
            _ = client.webhooks.unwrap(data, headers=headers, key=key)
        except standardwebhooks.WebhookVerificationError as e:
            raise AssertionError("Failed to unwrap valid webhook") from e

        bad_headers = [
            {**headers, "webhook-signature": hook.sign(msg_id=msg_id, timestamp=timestamp, data="xxx")},
            {**headers, "webhook-id": "bad"},
            {**headers, "webhook-timestamp": "0"},
        ]
        for bad_header in bad_headers:
            with pytest.raises(standardwebhooks.WebhookVerificationError):
                _ = client.webhooks.unwrap(data, headers=bad_header, key=key)


class TestAsyncWebhooks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    def test_method_unwrap(self, client: Surge) -> None:
        key = b"secret"
        hook = standardwebhooks.Webhook(key)

        data = """{"account_id":"acct_01japd271aeatb7txrzr2xj8sg","data":{"id":"call_01jjnn7s0zfx5tdcsxjfy93et2","contact":{"id":"ctc_01ja88cboqffhswjx8zbak3ykk","phone_number":"+18015551234","email":"dom@toretto.family","first_name":"Dominic","last_name":"Toretto","metadata":{"car":"1970 Dodge Charger R/T"}},"duration":184,"initiated_at":"2025-03-31T21:01:37Z","status":"completed"},"timestamp":"2024-10-21T23:29:41Z","type":"call.ended"}"""
        msg_id = "1"
        timestamp = datetime.now(tz=timezone.utc)
        sig = hook.sign(msg_id=msg_id, timestamp=timestamp, data=data)
        headers = {
            "webhook-id": msg_id,
            "webhook-timestamp": str(int(timestamp.timestamp())),
            "webhook-signature": sig,
        }

        try:
            _ = client.webhooks.unwrap(data, headers=headers, key=key)
        except standardwebhooks.WebhookVerificationError as e:
            raise AssertionError("Failed to unwrap valid webhook") from e

        bad_headers = [
            {**headers, "webhook-signature": hook.sign(msg_id=msg_id, timestamp=timestamp, data="xxx")},
            {**headers, "webhook-id": "bad"},
            {**headers, "webhook-timestamp": "0"},
        ]
        for bad_header in bad_headers:
            with pytest.raises(standardwebhooks.WebhookVerificationError):
                _ = client.webhooks.unwrap(data, headers=bad_header, key=key)
