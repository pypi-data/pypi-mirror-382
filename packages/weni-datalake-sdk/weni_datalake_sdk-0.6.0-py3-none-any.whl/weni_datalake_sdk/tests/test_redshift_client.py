from unittest import mock

import pytest

from weni_datalake_sdk.clients.redshift.redshift_client import query_dc_api


@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setenv("REDSHIFT_QUERY_BASE_URL", "https://example.com/api")
    # Also patch the module-level constant which is read at import time
    import weni_datalake_sdk.clients.redshift.redshift_client as rc

    monkeypatch.setattr(
        rc, "REDSHIFT_QUERY_BASE_URL", "https://example.com/api", raising=False
    )


def make_response(status_code=200, json_body=None):
    response = mock.Mock()
    response.status_code = status_code
    response.__str__ = lambda self=response: f"<Response [{status_code}]>"
    if json_body is None:
        json_body = {"ok": True}
    response.json.return_value = json_body
    return response


class TestQueryDcApi:
    def test_success_and_params_encoding(self, setup_env, monkeypatch):
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.redshift_client.get_secrets",
            return_value="token123",
        ) as mock_secrets, mock.patch(
            "weni_datalake_sdk.clients.redshift.redshift_client.requests.request"
        ) as mock_request:
            mock_request.return_value = make_response(200, {"data": 1})

            result = query_dc_api(
                metric="events",
                query_params={
                    "project": "abc",
                    "date_start": "2023-01-01",
                    "date_end": "2023-01-31",
                    "metadata": "a:b:c",  # ensure ':' remains safe in encoding
                },
            )

            assert result.json() == {"data": 1}
            # Verify correct URL, headers, and encoded params
            mock_secrets.assert_called_once()
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert args[1] == "https://example.com/api/events"
            assert kwargs["verify"] is False
            assert kwargs["headers"]["secretsaccesstoken"] == "token123"
            # ':' should not be percent-encoded due to safe=":"
            assert (
                kwargs["params"]
                == "project=abc&date_start=2023-01-01&date_end=2023-01-31&metadata=a:b:c"
            )

    def test_missing_base_url(self, monkeypatch):
        # Ensure env var not set and module constant cleared
        monkeypatch.delenv("REDSHIFT_QUERY_BASE_URL", raising=False)
        import weni_datalake_sdk.clients.redshift.redshift_client as rc

        monkeypatch.setattr(rc, "REDSHIFT_QUERY_BASE_URL", None, raising=False)
        with pytest.raises(EnvironmentError) as exc:
            query_dc_api(metric="m")
        assert "Missing REDSHIFT_QUERY_BASE_URL" in str(exc.value)

    def test_non_200_error(self, setup_env):
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.redshift_client.get_secrets",
            return_value="token123",
        ), mock.patch(
            "weni_datalake_sdk.clients.redshift.redshift_client.requests.request",
            return_value=make_response(500),
        ):
            with pytest.raises(Exception) as exc:
                query_dc_api(metric="m", query_params={"a": 1})
            assert "Could not send message to DC API! Error:" in str(exc.value)
            assert "URL: https://example.com/api/m" in str(exc.value)

    def test_401_refresh_same_token_raises(self, setup_env):
        # First call returns 401, get_secrets returns same token twice
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.redshift_client.get_secrets",
            side_effect=["token123", "token123"],
        ) as mock_secrets, mock.patch(
            "weni_datalake_sdk.clients.redshift.redshift_client.requests.request",
            return_value=make_response(401),
        ):
            with pytest.raises(Exception) as exc:
                query_dc_api(metric="m")
            assert "Token was updated" in str(exc.value)
            assert mock_secrets.call_count == 2

    def test_401_refresh_new_token_retries_success(self, setup_env):
        # First call gets 401, then function should recursively call and succeed
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.redshift_client.get_secrets",
            side_effect=["old", "new", "new"],
        ) as mock_secrets, mock.patch(
            "weni_datalake_sdk.clients.redshift.redshift_client.requests.request",
        ) as mock_request:
            mock_request.side_effect = [
                make_response(401),
                make_response(200, {"ok": True}),
            ]

            result = query_dc_api(metric="m", query_params={"x": "y"})
            assert result.status_code == 200
            assert mock_secrets.call_count == 3
            assert mock_request.call_count == 2
