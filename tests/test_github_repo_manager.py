import unittest
from unittest.mock import Mock, patch
import pandas as pd
from app.github_repo_manager import GithubRepoManager

class TestGithubRepoManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_token = "fake_token"
        
    @patch('app.github_repo_manager.Github')
    def test_init(self, mock_github):
        """Test GithubRepoManager initialization"""
        # Setup mock
        mock_user = Mock()
        mock_user.login = "test_user"
        mock_github.return_value.get_user.return_value = mock_user
        mock_user.get_repos.return_value = []

        # Create instance
        manager = GithubRepoManager(self.mock_token)
        
        # Assertions
        mock_github.assert_called_once_with(self.mock_token)
        self.assertEqual(manager.user.login, "test_user")
        self.assertEqual(manager.all_repos, [])

    @patch('app.github_repo_manager.Github')
    def test_get_repo_stats(self, mock_github):
        """Test repository statistics calculation"""
        # Setup mock repositories
        mock_repo1 = Mock(fork=True, archived=False, private=True)
        mock_repo2 = Mock(fork=False, archived=True, private=False)
        mock_user = Mock()
        mock_user.login = "test_user"
        mock_repo1.owner.login = "test_user"
        mock_repo2.owner.login = "other_user"
        
        mock_github.return_value.get_user.return_value = mock_user
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]

        # Create instance and get stats
        manager = GithubRepoManager(self.mock_token)
        stats = manager.get_repo_stats()

        # Assertions
        self.assertEqual(stats["Total Repositories"], 2)
        self.assertEqual(stats["Forked"], 1)
        self.assertEqual(stats["Archived"], 1)
        self.assertEqual(stats["Private"], 1)
        self.assertEqual(stats["From Organizations"], 1)
