"""StreamGit CLI - Command Line Interface for GitHub Analytics 🌊

A command-line tool that works in parallel with the StreamGit web application,
providing quick access to GitHub repository analytics and management features.

Features:
- Repository Statistics 📊
- Data Export to CSV/Excel 📁
- Interactive Visualizations 📈
- Star Analysis ⭐
- Repository Management 🆕
- Multiple Token Source Support 🔑

Commands:
  stats       Display statistics for all repositories
  list        List all repositories
  create      Create a new repository
  delete      Delete an existing repository
  export      Export repository data to CSV/Excel
  stars       Export starred repositories to CSV/Excel
  visualize   Generate repository visualizations
  dashboard   Launch the StreamGit dashboard
"""

__version__ = "1.0.0"
__license__ = "MIT"
__status__ = "Production"
__description__ = "StreamGit CLI - A Command Line Interface for GitHub Analytics"
__repository__ = "https://github.com/kdmonroe/streamgit"

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

import plotly.express as px
from dotenv import load_dotenv
from .github_repo_manager import GithubRepoManager

def print_welcome():
    print("""
    🌊 StreamGit CLI
    Easy Github Analytics with PyGithub
    
    Usage: streamgit <command> [options]
    
    Commands:
      stats       Display statistics for all your repositories
      list        List all your repositories
      create      Create a new repository (requires --name)
      delete      Delete an existing repository (requires --name)
      export      Export repository data to CSV/Excel (requires --data-format and --output)
      stars       Export starred repositories to CSV/Excel (requires --data-format and --output)
      visualize   Generate repository visualizations (requires --type and --output)
      dashboard   Launch the StreamGit dashboard

    Examples:
      streamgit stats
      streamgit create --name "new-repo" --description "My new repo" --private
      streamgit export --data-format csv --output repos.csv
      streamgit visualize --type language_distribution --output langs.png
      streamgit stars --data-format xlsx --output starred.xlsx
    
    Use 'streamgit <command> --help' for more information about a command.
    --------------------------------
    """)


def get_default_filename(repo_manager, file_type="repos"):
    """Generate default filename with date and GitHub username
    
    Args:
        repo_manager: GithubRepoManager instance
        file_type: Type of export (repos, starred, etc.)
    Returns:
        str: Formatted filename with date and username
    """
    today = datetime.now().strftime("%Y%m%d")
    username = repo_manager.user.login
    return f"{today}_{file_type}_{username}.csv"


def export_data(repo_manager, format="csv", output=None):
    """Export repository data to file
    
    Args:
        repo_manager: GithubRepoManager instance
        format: Export format (csv by default)
        output: Output filename (generated from date/username if None)
    """
    if output is None:
        output = get_default_filename(repo_manager, "repos")
    
    df = repo_manager.get_repos_dataframe()
    
    if format == "csv":
        df.to_csv(output, index=False)
    elif format == "xlsx":
        print("⚠️ Warning: Excel export is not recommended. Using CSV instead.")
        output = output.replace('.xlsx', '.csv')
        df.to_csv(output, index=False)
        
    print(f"📊 Data exported to {output}")
    return output


def export_stars(repo_manager, use_format="csv", output=None):
    """Export starred repositories to file
    
    Args:
        repo_manager: GithubRepoManager instance
        use_format: Export format (csv by default)
        output: Output filename (generated from date/username if None)
    """
    if output is None:
        output = get_default_filename(repo_manager, "starred_repos")
    
    starred_df = repo_manager.get_starred_repos()
    
    if use_format == "csv":
        starred_df.to_csv(output, index=False)
    elif use_format == "xlsx":
        print("⚠️ Warning: Excel export is not recommended. Using CSV instead.")
        output = output.replace('.xlsx', '.csv')
        starred_df.to_csv(output, index=False)
        
    print(f"⭐ Starred repositories exported to {output}")
    return output


def visualize(repo_manager, use_type, output, img_format="png"):
    """
    Generate and save repository visualizations
    Args:
        repo_manager: GithubRepoManager instance
        use_type: Type of visualization to generate
        output: Output filename (without extension)
        img_format: Image format (png, jpg, svg, pdf)
    """
    df = repo_manager.get_repos_dataframe()
    
    try:
        if use_type == "language_distribution":
            lang_counts = df["language"].value_counts()
            fig = px.pie(
                values=lang_counts.values,
                names=lang_counts.index,
                title="Language Distribution",
            )
        elif use_type == "stars_vs_forks":
            fig = px.scatter(
                df,
                x="stars",
                y="forks",
                hover_name="name",
                title="Stars vs. Forks",
                labels={"stars": "Stars", "forks": "Forks"},
            )
        elif use_type == "creation_timeline":
            fig = px.histogram(
                df,
                x="created_at",
                title="Repository Creation Timeline",
                labels={"created_at": "Creation Date", "count": "Number of Repositories"},
            )
            fig.update_layout(bargap=0.1)
        else:
            raise ValueError(f"Unknown visualization type: {use_type}")

        if not output.lower().endswith(f".{img_format}"):
            output = f"{output}.{img_format}"

        fig.write_image(output, format=img_format)
        print(f"📈 Visualization saved to {output}")
        return True
    except Exception as e:
        print(f"❌ Error generating visualization: {str(e)}")
        return False


def load_token_from_env():
    """Load GitHub token from multiple possible sources"""
    # Get current directory (app directory) and project root
    current_dir = Path(__file__).resolve().parent
    root_dir = current_dir.parent

    # Check for token in environment variables
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token

    # Check for token in .streamlit/secrets.toml
    try:
        import streamlit as st

        if "github_token" in st.secrets:
            return st.secrets["github_token"]
    except:
        pass

    # Check for token.env in app directory
    app_token_path = current_dir / "token.env"
    if app_token_path.exists():
        load_dotenv(app_token_path)
        token = os.getenv("GITHUB_TOKEN")
        if token:
            return token

    # Check for token.env in project root
    root_token_path = root_dir / "token.env"
    if root_token_path.exists():
        load_dotenv(root_token_path)
        token = os.getenv("GITHUB_TOKEN")
        if token:
            return token

    # Check for .env in project root
    root_env = root_dir / ".env"
    if root_env.exists():
        load_dotenv(root_env)
        token = os.getenv("GITHUB_TOKEN")
        if token:
            return token

    return None


def launch_dashboard():
    """Launch the StreamGit Streamlit dashboard"""
    import sys
    from pathlib import Path

    import streamlit.web.cli as stcli

    # Get the path to app.py relative to the installed package
    app_path = Path(__file__).parent / "app.py"

    sys.argv = ["streamlit", "run", str(app_path)]
    sys.exit(stcli.main())


def main():
    """Main function for the StreamGit CLI"""
    print_welcome()

    token = load_token_from_env()
    if not token:
        print("❌ GitHub token not found. Please ensure one of the following:")
        print("  1. GITHUB_TOKEN environment variable is set")
        print("  2. .streamlit/secrets.toml contains github_token")
        print("  3. token.env file exists in the app directory")
        print("  4. token.env file exists in the project root")
        print("  5. .env file exists in the project root")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="🌊 StreamGit CLI - GitHub Repository Analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get repository statistics
  streamgit stats

  # List all repositories
  streamgit list

  # Create a new repository (--name required)
  streamgit create --name "new-project" --description "A new project" --private

  # Export repository data (--data-format and --output required)
  streamgit export --data-format csv --output repositories.csv

  # Export starred repositories (--data-format and --output required)
  streamgit stars --data-format xlsx --output starred.xlsx

  # Generate visualizations (--type and --output required)
  streamgit visualize --type language_distribution --output languages.png
  streamgit visualize --type stars_vs_forks --output activity.png
  streamgit visualize --type creation_timeline --output timeline.png

  # Launch the interactive dashboard
  streamgit dashboard
        """,
    )

    parser.add_argument(
        "action",
        choices=[
            "stats",
            "list",
            "create",
            "delete",
            "export",
            "stars",
            "visualize",
            "dashboard",
        ],
        help="""
                       stats: Display repository statistics
                       list: Show all repositories
                       create: Create a new repository (requires --name)
                       delete: Delete an existing repository (requires --name)
                       export: Export repository data (requires --data-format and --output)
                       stars: Export starred repositories (requires --data-format and --output)
                       visualize: Generate visualizations (requires --type and --output)
                       dashboard: Launch Streamlit dashboard
                       """,
    )

    parser.add_argument(
        "--name", help="Repository name (required for create/delete actions)"
    )
    parser.add_argument(
        "--description", help="Repository description (optional for create action)"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Make repository private (optional for create action)",
    )
    parser.add_argument(
        "--data-format",
        choices=["csv", "xlsx"],
        help="Export format for data/stars actions (csv or xlsx)",
    )
    parser.add_argument(
        "--image-format",
        choices=["png", "jpg", "svg", "pdf"],
        default="png",
        help="Image format for visualizations (default: png)",
    )
    parser.add_argument(
        "--output", help="Output file name for export/visualize actions"
    )
    parser.add_argument(
        "--type",
        choices=["language_distribution", "stars_vs_forks", "creation_timeline"],
        help="""Visualization type:
                           language_distribution: Pie chart of programming languages
                           stars_vs_forks: Scatter plot comparing stars and forks
                           creation_timeline: Histogram of repository creation dates
                           """,
    )

    args = parser.parse_args()

    repo_manager = GithubRepoManager(token)

    if args.action == "stats":
        try:
            stats = repo_manager.get_repo_stats()
            for key, value in stats.items():
                print(f"📊 {key}: {value}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error getting stats: {str(e)}")
            sys.exit(1)
    elif args.action == "list":
        try:
            repos = repo_manager.all_repos
            total_count = len(repos)
            private_count = len([r for r in repos if r.private])
            public_count = total_count - private_count
            
            print(f"📚 Found {total_count} repositories:")
            print(f"    ├── Public: {public_count} ({public_count/total_count*100:.1f}%)")
            print(f"    └── Private: {private_count} ({private_count/total_count*100:.1f}%)")
            print("\nRepository List:")
            for i, repo in enumerate(repos, 1):
                visibility = "(private)" if repo.private else "(public)"
                print(f"{i}. 📁 {repo.name} - {repo.description} {visibility}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error listing repositories: {str(e)}")
            sys.exit(1)
    elif args.action == "create":
        if not args.name:
            print("❌ Repository name is required for create action")
            sys.exit(1)
        try:
            repo = repo_manager.create_repo(
                args.name, description=args.description, private=args.private
            )
            print(f"✨ Repository created: {repo.html_url}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error creating repository: {str(e)}")
            sys.exit(1)
    elif args.action == "delete":
        if not args.name:
            print("❌ Repository name is required for delete action")
            sys.exit(1)
        try:
            repo_manager.delete_repo(args.name)
            print(f"🗑️ Repository {args.name} deleted")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error deleting repository: {str(e)}")
            sys.exit(1)
    elif args.action == "export":
        if not args.data_format or not args.output:
            print("❌ Format and output file name are required for export action")
            sys.exit(1)
        try:
            export_data(repo_manager, args.data_format, args.output)
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error exporting data: {str(e)}")
            sys.exit(1)
    elif args.action == "stars":
        try:
            export_stars(repo_manager, args.data_format or "csv", args.output)
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error exporting stars: {str(e)}")
            sys.exit(1)
    elif args.action == "visualize":
        if not args.type or not args.output:
            print(
                "❌ Visualization type and output file name are required for visualize action"
            )
            sys.exit(1)
        try:
            visualize(repo_manager, args.type, args.output, img_format=args.image_format)
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error generating visualization: {str(e)}")
            sys.exit(1)
    elif args.action == "dashboard":
        launch_dashboard()
        # Note: launch_dashboard already includes sys.exit()


if __name__ == "__main__":
    main()
