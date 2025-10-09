from contextlib import contextmanager
import json

import requests_mock

from jf_ingest.jf_jira.downloaders import download_global_components
from tests.jf_jira.utils import (
    _register_jira_uri,
    get_fixture_file_data,
    get_jira_mock_connection,
)


@contextmanager
def _mock_components_endpoint(
    m: requests_mock.Mocker,
    endpoint_base: str,
):
    component_1 = get_fixture_file_data(f"api_responses/components_1.json")
    component_2 = get_fixture_file_data(f"api_responses/components_2.json")
    print(endpoint_base)
    _register_jira_uri(
        m,
        endpoint=f"component?startAt=0&maxResults=50",
        return_value=component_1,
    )
    _register_jira_uri(
        m,
        endpoint=f"component?startAt=50&maxResults=50",
        return_value=component_2,
    )
    yield

def test_download_board_with_project_filtering_smoke_test():
    base_url = "https://test-co.atlassian.net"
    with requests_mock.Mocker() as m:
        jira_conn = get_jira_mock_connection(mocker=m)
        with _mock_components_endpoint(m, base_url):
            components = download_global_components(
                jira_connection=jira_conn,
            )
            
            component_fixture_data = json.loads(get_fixture_file_data(f"api_responses/components_1.json"))['values'] + json.loads(get_fixture_file_data(f"api_responses/components_2.json"))['values']
            assert len(components) == len(
                [c for c in component_fixture_data if 'ari' in c]
            )
