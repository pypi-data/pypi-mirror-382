from unittest import mock

import pytest

from weni_datalake_sdk.clients.redshift.events import (
    clean_quotes,
    get_events,
    get_events_count,
    get_events_count_by_group,
    get_events_silver,
    get_events_silver_count,
    get_events_silver_count_by_group,
)


class TestCleanQuotes:
    def test_clean_quotes_dict(self):
        obj = {"a": '"value"', "b": 2, "c": {"d": '"inner"'}}
        result = clean_quotes(obj)
        assert result == {"a": "value", "b": 2, "c": {"d": "inner"}}

    def test_clean_quotes_list(self):
        obj = ['"foo"', "bar", 1, {"a": '"baz"'}]
        result = clean_quotes(obj)
        assert result == ["foo", "bar", 1, {"a": "baz"}]

    def test_clean_quotes_str_with_quotes(self):
        assert clean_quotes('"quoted"') == "quoted"

    def test_clean_quotes_str_without_quotes(self):
        assert clean_quotes("notquoted") == "notquoted"

    def test_clean_quotes_int(self):
        assert clean_quotes(123) == 123


class TestGetEvents:
    @pytest.fixture
    def mock_env_metric(self, monkeypatch):
        monkeypatch.setenv("EVENTS_METRIC_NAME", "test_metric")

    def test_get_events_success(self, mock_env_metric):
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_response = mock.Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_query.return_value = mock_response

            result = get_events(
                project="test_project",
                date_start="2023-01-01",
                date_end="2023-01-31",
                extra="param",
            )

            mock_query.assert_called_once_with(
                metric="test_metric",
                query_params={
                    "project": "test_project",
                    "date_start": "2023-01-01",
                    "date_end": "2023-01-31",
                    "extra": "param",
                },
            )
            assert result == {"data": "test"}

    def test_get_events_missing_project(self):
        with pytest.raises(Exception) as exc_info:
            get_events(date_start="2023-01-01", date_end="2023-01-31")
        assert str(exc_info.value) == "Project is required"

    def test_get_events_missing_date_start(self):
        with pytest.raises(Exception) as exc_info:
            get_events(project="test_project", date_end="2023-01-31")
        assert str(exc_info.value) == "Date start is required"

    def test_get_events_missing_date_end(self):
        with pytest.raises(Exception) as exc_info:
            get_events(project="test_project", date_start="2023-01-01")
        assert str(exc_info.value) == "Date end is required"

    def test_get_events_api_error(self, mock_env_metric):
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_query.side_effect = Exception("API Error")

            with pytest.raises(Exception) as exc_info:
                get_events(
                    project="test_project",
                    date_start="2023-01-01",
                    date_end="2023-01-31",
                )
            assert "Error querying events: API Error" in str(exc_info.value)


class TestGetEventsCount:
    def test_get_events_count_success(self, monkeypatch):
        monkeypatch.setenv("EVENTS_COUNT_METRIC_NAME", "test_metric_count")
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_response = mock.Mock()
            mock_response.json.return_value = {"data": "counted"}
            mock_query.return_value = mock_response

            result = get_events_count(
                project="test_project",
                date_start="2023-01-01",
                date_end="2023-01-31",
                extra="param",
            )

            mock_query.assert_called_once_with(
                metric="test_metric_count",
                query_params={
                    "project": "test_project",
                    "date_start": "2023-01-01",
                    "date_end": "2023-01-31",
                    "extra": "param",
                },
            )
            assert result == {"data": "counted"}

    def test_get_events_count_missing_project(self):
        with pytest.raises(Exception) as exc_info:
            get_events_count(date_start="2023-01-01", date_end="2023-01-31")
        assert str(exc_info.value) == "Project is required"

    def test_get_events_count_missing_date_start(self):
        with pytest.raises(Exception) as exc_info:
            get_events_count(project="test_project", date_end="2023-01-31")
        assert str(exc_info.value) == "Date start is required"

    def test_get_events_count_missing_date_end(self):
        with pytest.raises(Exception) as exc_info:
            get_events_count(project="test_project", date_start="2023-01-01")
        assert str(exc_info.value) == "Date end is required"

    def test_get_events_count_api_error(self, monkeypatch):
        monkeypatch.setenv("EVENTS_COUNT_METRIC_NAME", "test_metric_count")
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_query.side_effect = Exception("API Error")
            with pytest.raises(Exception) as exc_info:
                get_events_count(
                    project="test_project",
                    date_start="2023-01-01",
                    date_end="2023-01-31",
                )
            assert "Error querying events count: API Error" in str(exc_info.value)


class TestGetEventsCountByGroup:
    def test_get_events_count_by_group_success(self, monkeypatch):
        monkeypatch.setenv("EVENTS_COUNT_BY_GROUP_METRIC_NAME", "test_metric_group")
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_response = mock.Mock()
            mock_response.json.return_value = {"data": "grouped"}
            mock_query.return_value = mock_response

            result = get_events_count_by_group(
                project="test_project",
                date_start="2023-01-01",
                date_end="2023-01-31",
                metadata_key="topic_uuid",
                extra="param",
            )

            mock_query.assert_called_once_with(
                metric="test_metric_group",
                query_params={
                    "project": "test_project",
                    "date_start": "2023-01-01",
                    "date_end": "2023-01-31",
                    "metadata_key": "topic_uuid",
                    "extra": "param",
                },
            )
            assert result == {"data": "grouped"}

    def test_get_events_count_by_group_missing_project(self):
        with pytest.raises(Exception) as exc_info:
            get_events_count_by_group(
                date_start="2023-01-01",
                date_end="2023-01-31",
                metadata_key="topic_uuid",
            )
        assert str(exc_info.value) == "Project is required"

    def test_get_events_count_by_group_missing_date_start(self):
        with pytest.raises(Exception) as exc_info:
            get_events_count_by_group(
                project="test_project", date_end="2023-01-31", metadata_key="topic_uuid"
            )
        assert str(exc_info.value) == "Date start is required"

    def test_get_events_count_by_group_missing_date_end(self):
        with pytest.raises(Exception) as exc_info:
            get_events_count_by_group(
                project="test_project",
                date_start="2023-01-01",
                metadata_key="topic_uuid",
            )
        assert str(exc_info.value) == "Date end is required"

    def test_get_events_count_by_group_missing_metadata_key(self):
        with pytest.raises(Exception) as exc_info:
            get_events_count_by_group(
                project="test_project", date_start="2023-01-01", date_end="2023-01-31"
            )
        assert str(exc_info.value) == "metadata_key is required"

    def test_get_events_count_by_group_api_error(self, monkeypatch):
        monkeypatch.setenv("EVENTS_COUNT_BY_GROUP_METRIC_NAME", "test_metric_group")
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_query.side_effect = Exception("API Error")
            with pytest.raises(Exception) as exc_info:
                get_events_count_by_group(
                    project="test_project",
                    date_start="2023-01-01",
                    date_end="2023-01-31",
                    metadata_key="topic_uuid",
                )
            assert "Error querying events count: API Error" in str(exc_info.value)


class TestGetEventsSilver:
    @pytest.fixture
    def mock_env_metric(self, monkeypatch):
        monkeypatch.setenv("EVENTS_SILVER_METRIC_NAME", "test_metric_silver")

    def test_get_events_silver_success(self, mock_env_metric):
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_response = mock.Mock()
            mock_response.json.return_value = {"data": "silver"}
            mock_query.return_value = mock_response

            result = get_events_silver(
                project="test_project",
                date_start="2023-01-01",
                date_end="2023-01-31",
                table="topics",
                extra="param",
            )

            mock_query.assert_called_once_with(
                metric="test_metric_silver",
                query_params={
                    "project": "test_project",
                    "date_start": "2023-01-01",
                    "date_end": "2023-01-31",
                    "table": "topics",
                    "extra": "param",
                },
            )
            assert result == {"data": "silver"}

    def test_get_events_silver_missing_project(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver(
                date_start="2023-01-01", date_end="2023-01-31", table="topics"
            )
        assert str(exc_info.value) == "Project is required"

    def test_get_events_silver_missing_date_start(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver(
                project="test_project", date_end="2023-01-31", table="topics"
            )
        assert str(exc_info.value) == "Date start is required"

    def test_get_events_silver_missing_date_end(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver(
                project="test_project", date_start="2023-01-01", table="topics"
            )
        assert str(exc_info.value) == "Date end is required"

    def test_get_events_silver_missing_table(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver(
                project="test_project", date_start="2023-01-01", date_end="2023-01-31"
            )
        assert str(exc_info.value) == "Table is required"

    def test_get_events_silver_invalid_table(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver(
                project="test_project",
                date_start="2023-01-01",
                date_end="2023-01-31",
                table="invalid_table",
            )
        assert str(exc_info.value) == "Table is not valid"

    def test_get_events_silver_api_error(self, mock_env_metric):
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_query.side_effect = Exception("API Error")
            with pytest.raises(Exception) as exc_info:
                get_events_silver(
                    project="test_project",
                    date_start="2023-01-01",
                    date_end="2023-01-31",
                    table="topics",
                )
            assert "Error querying events silver: API Error" in str(exc_info.value)


class TestGetEventsSilverCount:
    @pytest.fixture
    def mock_env_metric(self, monkeypatch):
        monkeypatch.setenv(
            "EVENTS_SILVER_COUNT_METRIC_NAME", "test_metric_silver_count"
        )

    def test_get_events_silver_count_success(self, mock_env_metric):
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_response = mock.Mock()
            mock_response.json.return_value = {"data": "silver_count"}
            mock_query.return_value = mock_response

            result = get_events_silver_count(
                project="test_project",
                date_start="2023-01-01",
                date_end="2023-01-31",
                table="topics",
                extra="param",
            )

            mock_query.assert_called_once_with(
                metric="test_metric_silver_count",
                query_params={
                    "project": "test_project",
                    "date_start": "2023-01-01",
                    "date_end": "2023-01-31",
                    "table": "topics",
                    "extra": "param",
                },
            )
            assert result == {"data": "silver_count"}

    def test_get_events_silver_count_missing_project(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver_count(
                date_start="2023-01-01", date_end="2023-01-31", table="topics"
            )
        assert str(exc_info.value) == "Project is required"

    def test_get_events_silver_count_missing_date_start(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver_count(
                project="test_project", date_end="2023-01-31", table="topics"
            )
        assert str(exc_info.value) == "Date start is required"

    def test_get_events_silver_count_missing_date_end(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver_count(
                project="test_project", date_start="2023-01-01", table="topics"
            )
        assert str(exc_info.value) == "Date end is required"

    def test_get_events_silver_count_missing_table(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver_count(
                project="test_project", date_start="2023-01-01", date_end="2023-01-31"
            )
        assert str(exc_info.value) == "Table is required"

    def test_get_events_silver_count_invalid_table(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver_count(
                project="test_project",
                date_start="2023-01-01",
                date_end="2023-01-31",
                table="invalid_table",
            )
        assert str(exc_info.value) == "Table is not valid"

    def test_get_events_silver_count_api_error(self, mock_env_metric):
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_query.side_effect = Exception("API Error")
            with pytest.raises(Exception) as exc_info:
                get_events_silver_count(
                    project="test_project",
                    date_start="2023-01-01",
                    date_end="2023-01-31",
                    table="topics",
                )
            assert "Error querying events silver: API Error" in str(exc_info.value)


class TestGetEventsSilverCountByGroup:
    @pytest.fixture
    def mock_env_metric(self, monkeypatch):
        monkeypatch.setenv(
            "EVENTS_SILVER_COUNT_BY_GROUP_METRIC_NAME",
            "test_metric_silver_count_by_group",
        )

    def test_get_events_silver_count_by_group_success(self, mock_env_metric):
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_response = mock.Mock()
            mock_response.json.return_value = {"data": "silver_group"}
            mock_query.return_value = mock_response

            result = get_events_silver_count_by_group(
                project="test_project",
                date_start="2023-01-01",
                date_end="2023-01-31",
                table="topics",
                metadata_key="topic_uuid",
                extra="param",
            )

            mock_query.assert_called_once_with(
                metric="test_metric_silver_count_by_group",
                query_params={
                    "project": "test_project",
                    "date_start": "2023-01-01",
                    "date_end": "2023-01-31",
                    "table": "topics",
                    "metadata_key": "topic_uuid",
                    "extra": "param",
                },
            )
            assert result == {"data": "silver_group"}

    def test_get_events_silver_count_by_group_missing_project(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver_count_by_group(
                date_start="2023-01-01",
                date_end="2023-01-31",
                table="topics",
                metadata_key="topic_uuid",
            )
        assert str(exc_info.value) == "Project is required"

    def test_get_events_silver_count_by_group_missing_date_start(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver_count_by_group(
                project="test_project",
                date_end="2023-01-31",
                table="topics",
                metadata_key="topic_uuid",
            )
        assert str(exc_info.value) == "Date start is required"

    def test_get_events_silver_count_by_group_missing_date_end(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver_count_by_group(
                project="test_project",
                date_start="2023-01-01",
                table="topics",
                metadata_key="topic_uuid",
            )
        assert str(exc_info.value) == "Date end is required"

    def test_get_events_silver_count_by_group_missing_table(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver_count_by_group(
                project="test_project",
                date_start="2023-01-01",
                date_end="2023-01-31",
                metadata_key="topic_uuid",
            )
        assert str(exc_info.value) == "Table is required"

    def test_get_events_silver_count_by_group_missing_metadata_key(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver_count_by_group(
                project="test_project",
                date_start="2023-01-01",
                date_end="2023-01-31",
                table="topics",
            )
        assert str(exc_info.value) == "metadata_key is required"

    def test_get_events_silver_count_by_group_invalid_table(self):
        with pytest.raises(Exception) as exc_info:
            get_events_silver_count_by_group(
                project="test_project",
                date_start="2023-01-01",
                date_end="2023-01-31",
                table="invalid_table",
                metadata_key="topic_uuid",
            )
        assert str(exc_info.value) == "Table is not valid"

    def test_get_events_silver_count_by_group_api_error(self, mock_env_metric):
        with mock.patch(
            "weni_datalake_sdk.clients.redshift.events.query_dc_api"
        ) as mock_query:
            mock_query.side_effect = Exception("API Error")
            with pytest.raises(Exception) as exc_info:
                get_events_silver_count_by_group(
                    project="test_project",
                    date_start="2023-01-01",
                    date_end="2023-01-31",
                    table="topics",
                    metadata_key="topic_uuid",
                )
            assert "Error querying events count: API Error" in str(exc_info.value)
