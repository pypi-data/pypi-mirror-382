"""
Integration tests for JiraCloudManifestAdapter API selection functionality.
"""
import unittest
from unittest.mock import MagicMock, patch
from types import MappingProxyType

from jf_ingest.config import JiraDownloadConfig
from jf_ingest.constants import Constants
from jf_ingest.data_manifests.jira.adapters.jira_cloud import JiraCloudManifestAdapter


class TestJiraCloudManifestAdapterAPISelection(unittest.TestCase):
    """Test API selection functionality in JiraCloudManifestAdapter."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = JiraDownloadConfig(
            company_slug='test',
            url="https://test.atlassian.net",
            gdpr_active=False,
            feature_flags={},
        )

    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_projects')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_boards')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.get_jira_connection')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.is_jql_enhanced_search_available')
    def test_legacy_api_selection(self, mock_is_available, mock_get_connection, mock_get_boards, mock_get_projects):
        """Test that legacy API is used when JQL Enhanced Search is not available."""
        # Mock API detection to return False (legacy API)
        mock_is_available.return_value = False
        
        # Mock Jira connection
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        
        # Mock initialization methods
        mock_get_boards.return_value = []
        mock_get_projects.return_value = []
        
        # Create adapter
        adapter = JiraCloudManifestAdapter(config=self.config)
        
        # Verify API selection
        self.assertFalse(adapter.use_jql_enhanced_search)
        
        # Verify connection was created with correct parameters
        mock_get_connection.assert_called_once_with(
            config=self.config, use_jql_enhanced_search=False
        )

    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_projects')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_boards')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.get_jira_connection')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.is_jql_enhanced_search_available')
    def test_jql_enhanced_search_api_selection(self, mock_is_available, mock_get_connection, mock_get_boards, mock_get_projects):
        """Test that JQL Enhanced Search API is used when available and enabled."""
        # Enable JQL Enhanced Search via feature flag
        self.config.feature_flags = {
            Constants.JQL_ENHANCED_SEARCH_ENABLED: True
        }
        
        # Mock API detection to return True (JQL Enhanced Search available)
        mock_is_available.return_value = True
        
        # Mock Jira connection
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        
        # Mock initialization methods
        mock_get_boards.return_value = []
        mock_get_projects.return_value = []
        
        # Create adapter
        adapter = JiraCloudManifestAdapter(config=self.config)
        
        # Verify API selection
        self.assertTrue(adapter.use_jql_enhanced_search)
        
        # Verify connection was created with correct parameters
        mock_get_connection.assert_called_once_with(
            config=self.config, use_jql_enhanced_search=True
        )

    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_projects')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_boards')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.get_jira_connection')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.is_jql_enhanced_search_available')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud._get_issue_count_with_jql_enhanced_search')
    def test_get_issues_count_helper_with_jql_enhanced_search(self, mock_enhanced_count, mock_is_available, mock_get_connection, mock_get_boards, mock_get_projects):
        """Test _get_issues_count_helper uses JQL Enhanced Search API when enabled."""
        # Enable JQL Enhanced Search
        mock_is_available.return_value = True
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_enhanced_count.return_value = 42
        
        # Mock initialization methods
        mock_get_boards.return_value = []
        mock_get_projects.return_value = []
        
        # Create adapter with JQL Enhanced Search enabled
        adapter = JiraCloudManifestAdapter(config=self.config)
        adapter.use_jql_enhanced_search = True
        
        # Test _get_issues_count_helper
        result = adapter._get_issues_count_helper("project = TEST")
        
        # Verify correct API was called
        mock_enhanced_count.assert_called_once_with(mock_connection, "project = TEST")
        self.assertEqual(result, 42)

    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_projects')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_boards')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.get_jira_connection')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.is_jql_enhanced_search_available')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.retry_for_status')
    def test_get_issues_count_helper_with_legacy_api(self, mock_retry, mock_is_available, mock_get_connection, mock_get_boards, mock_get_projects):
        """Test _get_issues_count_helper uses legacy API when JQL Enhanced Search is disabled."""
        # Disable JQL Enhanced Search
        mock_is_available.return_value = False
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_retry.return_value = {'total': 24}
        
        # Mock initialization methods
        mock_get_boards.return_value = []
        mock_get_projects.return_value = []
        
        # Create adapter with legacy API
        adapter = JiraCloudManifestAdapter(config=self.config)
        adapter.use_jql_enhanced_search = False
        
        # Test _get_issues_count_helper
        result = adapter._get_issues_count_helper("project = TEST")
        
        # Verify correct API was called
        mock_retry.assert_called_once_with(
            mock_connection._get_json,
            'search',
            {'jql': "project = TEST", 'maxResults': 0}
        )
        self.assertEqual(result, 24)

    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_projects')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_boards')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.get_jira_connection')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.is_jql_enhanced_search_available')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud._post_raw_result_jql_enhanced')
    def test_get_jql_search_with_jql_enhanced_search(self, mock_enhanced_search, mock_is_available, mock_get_connection, mock_get_boards, mock_get_projects):
        """Test _get_jql_search uses JQL Enhanced Search API when enabled."""
        # Enable JQL Enhanced Search
        mock_is_available.return_value = True
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_enhanced_search.return_value = {'issues': [{'id': '123'}]}
        
        # Mock initialization methods
        mock_get_boards.return_value = []
        mock_get_projects.return_value = []
        
        # Create adapter with JQL Enhanced Search enabled
        adapter = JiraCloudManifestAdapter(config=self.config)
        adapter.use_jql_enhanced_search = True
        
        # Test _get_jql_search
        result = adapter._get_jql_search("project = TEST", max_results=1)
        
        # Verify correct API was called
        mock_enhanced_search.assert_called_once_with(
            jira_connection=mock_connection,
            jql_query="project = TEST",
            fields=['*all'],
            expand=[],
            max_results=1,
            next_page_token=None,
        )
        self.assertEqual(result, {'issues': [{'id': '123'}]})

    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_projects')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_boards')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.get_jira_connection')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.is_jql_enhanced_search_available')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.retry_for_status')
    def test_get_jql_search_with_legacy_api(self, mock_retry, mock_is_available, mock_get_connection, mock_get_boards, mock_get_projects):
        """Test _get_jql_search uses legacy API when JQL Enhanced Search is disabled."""
        # Disable JQL Enhanced Search
        mock_is_available.return_value = False
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_retry.return_value = {'issues': [{'id': '456'}], 'total': 1}
        
        # Mock initialization methods
        mock_get_boards.return_value = []
        mock_get_projects.return_value = []
        
        # Create adapter with legacy API
        adapter = JiraCloudManifestAdapter(config=self.config)
        adapter.use_jql_enhanced_search = False
        
        # Test _get_jql_search
        result = adapter._get_jql_search("project = TEST", max_results=1)
        
        # Verify correct API was called
        mock_retry.assert_called_once_with(
            mock_connection._get_json,
            'search',
            {'jql': "project = TEST", 'maxResults': 1}
        )
        self.assertEqual(result, {'issues': [{'id': '456'}], 'total': 1})

    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_projects')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_boards')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.get_jira_connection')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.is_jql_enhanced_search_available')
    def test_get_issues_count_uses_jql_count_method(self, mock_is_available, mock_get_connection, mock_get_boards, mock_get_projects):
        """Test that get_issues_count uses the new _get_issues_count_helper method."""
        # Mock setup
        mock_is_available.return_value = False
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        
        # Mock initialization methods
        mock_get_boards.return_value = []
        mock_get_projects.return_value = []
        
        # Create adapter
        adapter = JiraCloudManifestAdapter(config=self.config)
        
        # Mock the _get_issues_count_helper method
        adapter._get_issues_count_helper = MagicMock(return_value=100)
        
        # Test get_issues_count
        result = adapter.get_issues_count()
        
        # Verify _get_issues_count_helper was called with correct query
        adapter._get_issues_count_helper.assert_called_once()
        call_args = adapter._get_issues_count_helper.call_args[1]
        self.assertIn('updatedDate >', call_args['jql_query'])
        self.assertEqual(result, 100)

    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_projects')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_boards')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.get_jira_connection')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.is_jql_enhanced_search_available')
    def test_get_issues_count_for_project_uses_jql_count_method(self, mock_is_available, mock_get_connection, mock_get_boards, mock_get_projects):
        """Test that get_issues_count_for_project uses the new _get_issues_count_helper method."""
        # Mock setup
        mock_is_available.return_value = False
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        
        # Mock initialization methods
        mock_get_boards.return_value = []
        mock_get_projects.return_value = []
        
        # Create adapter
        adapter = JiraCloudManifestAdapter(config=self.config)
        
        # Mock the _get_issues_count_helper method
        adapter._get_issues_count_helper = MagicMock(return_value=50)
        
        # Test get_issues_count_for_project
        result = adapter.get_issues_count_for_project(project_id=123)
        
        # Verify _get_issues_count_helper was called with correct query
        adapter._get_issues_count_helper.assert_called_once()
        call_args = adapter._get_issues_count_helper.call_args[1]
        self.assertIn('project = 123', call_args['jql_query'])
        self.assertIn('updatedDate >', call_args['jql_query'])
        self.assertEqual(result, 50)

    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_projects')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.JiraCloudManifestAdapter._get_all_boards')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.get_jira_connection')
    @patch('jf_ingest.data_manifests.jira.adapters.jira_cloud.is_jql_enhanced_search_available')
    def test_get_last_updated_for_project_still_uses_jql_search(self, mock_is_available, mock_get_connection, mock_get_boards, mock_get_projects):
        """Test that get_last_updated_for_project still uses _get_jql_search for actual issue data."""
        # Mock setup
        mock_is_available.return_value = False
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        
        # Mock initialization methods
        mock_get_boards.return_value = []
        mock_get_projects.return_value = []
        
        # Create adapter
        adapter = JiraCloudManifestAdapter(config=self.config)
        
        # Mock the _get_jql_search method to return issue data
        adapter._get_jql_search = MagicMock(return_value={
            'issues': [{
                'fields': {
                    'updated': '2023-05-15T14:04:19.376-0400'
                }
            }]
        })
        
        # Test get_last_updated_for_project
        result = adapter.get_last_updated_for_project(project_id=123)
        
        # Verify _get_jql_search was called with correct parameters
        adapter._get_jql_search.assert_called_once_with(
            jql_search="project = 123 ORDER BY updated",
            max_results=1
        )
        # Verify result is a datetime object
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()