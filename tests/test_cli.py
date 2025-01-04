"""StreamGit CLI Test Suite 

This module comprises tests for the StreamGit CLI functionality, including:
- Repository data export 
- Visualization generation 
- File naming conventions 
- Error handling 
- Data format conversions 
"""

import pytest
from unittest.mock import Mock, patch
import pandas as pd
import os
from app.cli import visualize, export_data, export_stars, get_default_filename
from freezegun import freeze_time

class TestCLI:
    """Test suite for StreamGit CLI functionality
    
    Tests cover:
    1. Data Visualization
        - Language distribution
        - Stars vs. forks comparison
        - Repository creation timeline
    2. Data Export
        - Repository data export
        - Starred repositories export
        - Format conversion (xlsx to csv)
    3. File Operations
        - Default filename generation
        - File format handling
        - Path operations
    """

    @pytest.fixture
    def mock_repo_manager(self):
        """Create a mock repo manager with sample data"""
        print("\n🔧 Setting up mock repository manager")
        manager = Mock()
        df = pd.DataFrame({
            'language': ['Python', 'JavaScript', 'Python', 'TypeScript'],
            'name': ['repo1', 'repo2', 'repo3', 'repo4'],
            'stars': [10, 20, 30, 40],
            'forks': [1, 2, 3, 4],
            'created_at': ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01']
        })
        manager.get_repos_dataframe.return_value = df
        return manager

    # === Visualization Tests ===
    @patch('plotly.express.pie')
    def test_visualize_language_distribution(self, mock_px_pie, mock_repo_manager):
        """Test language distribution pie chart visualization"""
        print("\n📊 Testing language distribution visualization")
        mock_fig = Mock()
        mock_px_pie.return_value = mock_fig

        visualize(mock_repo_manager, 'language_distribution', 'test')

        mock_px_pie.assert_called_once()
        args, kwargs = mock_px_pie.call_args
        assert 'values' in kwargs, "Missing 'values' in pie chart kwargs"
        assert 'names' in kwargs, "Missing 'names' in pie chart kwargs"
        assert kwargs['title'] == 'Language Distribution'
        mock_fig.write_image.assert_called_once_with('test.png', format='png')
        print("✅ Language distribution visualization test passed")

    @patch('plotly.express.scatter')
    def test_visualize_stars_vs_forks(self, mock_px_scatter, mock_repo_manager):
        """Test stars vs forks scatter plot visualization"""
        print("\n📈 Testing stars vs forks visualization")
        mock_fig = Mock()
        mock_px_scatter.return_value = mock_fig

        visualize(mock_repo_manager, 'stars_vs_forks', 'test')

        mock_px_scatter.assert_called_once()
        mock_fig.write_image.assert_called_once_with('test.png', format='png')
        print("✅ Stars vs forks visualization test passed")

    @patch('plotly.express.histogram')
    def test_visualize_creation_timeline(self, mock_px_histogram, mock_repo_manager):
        """Test repository creation timeline histogram"""
        print("\n📅 Testing creation timeline visualization")
        mock_fig = Mock()
        mock_px_histogram.return_value = mock_fig

        visualize(mock_repo_manager, 'creation_timeline', 'test')

        mock_px_histogram.assert_called_once()
        mock_fig.write_image.assert_called_once_with('test.png', format='png')
        print("✅ Creation timeline visualization test passed")

    # === File Operation Tests ===
    def test_get_default_filename(self, mock_repo_manager):
        """Test default filename generation with date and username"""
        print("\n📝 Testing default filename generation")
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_repo_manager.user = mock_user
        
        with freeze_time("2025-01-03"):
            filename = get_default_filename(mock_repo_manager, "starred_repos")
            assert filename == "20250103_starred_repos_testuser.csv"
            
            repos_filename = get_default_filename(mock_repo_manager, "repos")
            assert repos_filename == "20250103_repos_testuser.csv"
        print("✅ Default filename generation test passed")

    # === Data Export Tests ===
    def test_export_data(self, mock_repo_manager, tmp_path):
        """Test repository data export functionality"""
        print("\n💾 Testing repository data export")
        # Test default CSV export
        output = export_data(mock_repo_manager)
        assert output.endswith('.csv'), "Default export should be CSV"
        assert os.path.exists(output), "Export file should exist"
        
        # Test explicit CSV path
        csv_path = tmp_path / "test.csv"
        output = export_data(mock_repo_manager, "csv", str(csv_path))
        assert output.endswith('.csv'), "CSV export should have .csv extension"
        assert os.path.exists(output), "CSV file should exist"
        
        # Test xlsx gets converted to csv
        xlsx_path = tmp_path / "test.xlsx"
        output = export_data(mock_repo_manager, "xlsx", str(xlsx_path))
        assert output.endswith('.csv'), "XLSX should be converted to CSV"
        assert not output.endswith('.xlsx'), "XLSX should not be used"
        assert os.path.exists(output), "Converted CSV file should exist"
        print("✅ Repository data export test passed")

    def test_export_stars(self, mock_repo_manager, tmp_path):
        """Test starred repositories export functionality"""
        print("\n⭐ Testing starred repositories export")
        # Setup mock starred repos DataFrame
        starred_df = pd.DataFrame({
            'name': ['starred1', 'starred2'],
            'owner': ['owner1', 'owner2'],
            'stars': [100, 200]
        })
        mock_repo_manager.get_starred_repos.return_value = starred_df
        
        # Test default CSV export
        output = export_stars(mock_repo_manager)
        assert output.endswith('.csv'), "Default export should be CSV"
        assert os.path.exists(output), "Export file should exist"
        
        # Test explicit CSV path
        csv_path = tmp_path / "starred.csv"
        output = export_stars(mock_repo_manager, "csv", str(csv_path))
        assert output.endswith('.csv'), "CSV export should have .csv extension"
        assert os.path.exists(output), "CSV file should exist"
        
        # Test xlsx gets converted to csv
        xlsx_path = tmp_path / "starred.xlsx"
        output = export_stars(mock_repo_manager, "xlsx", str(xlsx_path))
        assert output.endswith('.csv'), "XLSX should be converted to CSV"
        assert not output.endswith('.xlsx'), "XLSX should not be used"
        assert os.path.exists(output), "Converted CSV file should exist"
        print("✅ Starred repositories export test passed")