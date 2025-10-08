from unittest.mock import patch

import pytest

from weni_datalake_sdk.clients.redshift.message_templates import (
    get_message_templates,
)


@pytest.fixture
def mock_env_metric(monkeypatch):
    monkeypatch.setenv("MESSAGE_TEMPLATES_METRIC_NAME", "test_metric")


@pytest.mark.parametrize(
    "contact_urn,template_uuid,query_params,expected_params",
    [
        ("contact123", None, None, {"contact_urn": "contact123"}),
        (None, "template123", None, {"template_uuid": "template123"}),
        (
            "contact123",
            "template123",
            {"extra": "param"},
            {
                "contact_urn": "contact123",
                "template_uuid": "template123",
                "extra": "param",
            },
        ),
        (None, None, {"extra": "param"}, {"extra": "param"}),
    ],
)
def test_get_message_templates_parameters(
    mock_env_metric, contact_urn, template_uuid, query_params, expected_params
):
    with patch(
        "weni_datalake_sdk.clients.redshift.message_templates.query_dc_api"
    ) as mock_query:
        mock_query.return_value = {"data": "test"}

        result = get_message_templates(
            contact_urn=contact_urn,
            template_uuid=template_uuid,
            query_params=query_params,
        )

        mock_query.assert_called_once_with(
            metric="test_metric", query_params=expected_params
        )
        assert result == {"data": "test"}


def test_get_message_templates_error(mock_env_metric):
    with patch(
        "weni_datalake_sdk.clients.redshift.message_templates.query_dc_api"
    ) as mock_query:
        mock_query.side_effect = Exception("Test error")

        with pytest.raises(Exception) as exc_info:
            get_message_templates()

        assert str(exc_info.value) == "Error querying message templates: Test error"


def test_get_message_templates_no_params(mock_env_metric):
    with patch(
        "weni_datalake_sdk.clients.redshift.message_templates.query_dc_api"
    ) as mock_query:
        mock_query.return_value = {"data": "test"}

        result = get_message_templates()

        mock_query.assert_called_once_with(metric="test_metric", query_params={})
        assert result == {"data": "test"}
