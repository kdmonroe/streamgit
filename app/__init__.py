"""StreamGit - GitHub Analytics Tool 🌊

A tool that combines Streamlit and PyGithub to provide:
1. Interactive web dashboard
2. Command-line interface
"""

__version__ = "1.0.0"
__author__ = "Keon Monroe"
__license__ = "MIT"

from .github_repo_manager import GithubRepoManager
from .cli import main as cli_main

__all__ = [
    'GithubRepoManager',
    'cli_main',
]