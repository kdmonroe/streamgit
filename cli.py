import os
import argparse
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from github_repo_manager import GithubRepoManager
from pathlib import Path
import sys


def print_welcome():
    print("""
    🌊 StreamGit CLI
    GitHub Analytics with Python & Streamlit
    
    Usage: streamgit <command> [options]
    
    Commands:
      stats       Display statistics for all your repositories
      list        List all your repositories
      create      Create a new repository
      delete      Delete an existing repository
      export      Export repository data to CSV/Excel
      stars       Export starred repositories to CSV/Excel
      visualize   Generate repository visualizations
      dashboard   Launch the StreamGit dashboard

    Examples:
      streamgit stats
      streamgit create --name "new-repo" --description "My new repo" --private
      streamgit export --data-format csv --output repos.csv
      streamgit visualize --type language_distribution --output langs.png
    
    Use 'streamgit <command> --help' for more information about a command.
    --------------------------------
    """)

def export_data(repo_manager, format, output):
    df = repo_manager.get_repos_dataframe()
    if format == 'csv':
        df.to_csv(output, index=False)
    elif format == 'xlsx':
        df.to_excel(output, index=False)
    print(f"📊 Data exported to {output}")

def export_stars(repo_manager, format, output):
    starred_df = repo_manager.get_starred_repos()
    if format == 'csv':
        starred_df.to_csv(output, index=False)
    elif format == 'xlsx':
        starred_df.to_excel(output, index=False)
    print(f"⭐ Starred repositories exported to {output}")

def visualize(repo_manager, type, output, format='png'):
    """
    Generate and save repository visualizations
    Args:
        repo_manager: GithubRepoManager instance
        type: Type of visualization to generate
        output: Output filename (without extension)
        format: Image format (png, jpg, svg, pdf)
    """
    df = repo_manager.get_repos_dataframe()
    
    if type == 'language_distribution':
        lang_counts = df['language'].value_counts()
        fig = px.pie(values=lang_counts.values, names=lang_counts.index, title="Language Distribution")
    elif type == 'stars_vs_forks':
        fig = px.scatter(df, x="stars", y="forks", hover_name="name", 
                        title="Stars vs. Forks",
                        labels={"stars": "Stars", "forks": "Forks"})
    elif type == 'creation_timeline':
        fig = px.histogram(df, x="created_at", 
                          title="Repository Creation Timeline",
                          labels={"created_at": "Creation Date", "count": "Number of Repositories"})
        fig.update_layout(bargap=0.1)
    else:
        print(f"❌ Unknown visualization type: {type}")
        return

    if not output.lower().endswith(f'.{format}'):
        output = f"{output}.{format}"

    try:
        fig.write_image(output, format=format)
        print(f"📈 Visualization saved to {output}")
    except Exception as e:
        print(f"❌ Error saving visualization: {str(e)}")

def load_token_from_env():
    current_dir = Path(__file__).resolve().parent
    env_path = current_dir / 'token.env'
    if env_path.exists():
        load_dotenv(env_path)
        return os.getenv('GITHUB_TOKEN')
    return None

def launch_dashboard():
    """Launch the StreamGit Streamlit dashboard"""
    import streamlit.web.cli as stcli
    import sys
    from pathlib import Path
    
    # Get the path to app.py relative to the installed package
    app_path = Path(__file__).parent / "app.py"
    
    sys.argv = ["streamlit", "run", str(app_path)]
    sys.exit(stcli.main())

def main():
    print_welcome()
    
    token = load_token_from_env()
    if not token:
        print("❌ GitHub token not found. Please set up your token in token.env file.")
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

  # Create a new private repository
  streamgit create --name "new-project" --description "A new project" --private

  # Export repository data to CSV
  streamgit export --data-format csv --output repositories.csv

  # Export starred repositories to Excel
  streamgit stars --data-format xlsx --output starred.xlsx

  # Generate language distribution visualization
  streamgit visualize --type language_distribution --output languages.png

  # Launch the interactive dashboard
  streamgit dashboard
        """
    )
    
    parser.add_argument('action', 
                       choices=['stats', 'list', 'create', 'delete', 'export', 'stars', 'visualize', 'dashboard'],
                       help="""
                       stats: Display repository statistics
                       list: Show all repositories
                       create: Create a new repository
                       delete: Delete an existing repository
                       export: Export repository data
                       stars: Export starred repositories
                       visualize: Generate visualizations
                       dashboard: Launch Streamlit dashboard
                       """)
    
    parser.add_argument('--name', 
                       help="Repository name (required for create/delete actions)")
    parser.add_argument('--description', 
                       help="Repository description (optional for create action)")
    parser.add_argument('--private', 
                       action='store_true', 
                       help="Make repository private (optional for create action)")
    parser.add_argument('--data-format', 
                       choices=['csv', 'xlsx'],
                       help="Export format for data/stars actions (csv or xlsx)")
    parser.add_argument('--image-format',
                       choices=['png', 'jpg', 'svg', 'pdf'],
                       default='png',
                       help="Image format for visualizations (default: png)")
    parser.add_argument('--output', 
                       help="Output file name for export/visualize actions")
    parser.add_argument('--type', 
                       choices=['language_distribution', 'stars_vs_forks', 'creation_timeline'],
                       help="""Visualization type:
                           language_distribution: Pie chart of programming languages
                           stars_vs_forks: Scatter plot comparing stars and forks
                           creation_timeline: Histogram of repository creation dates
                           """)

    args = parser.parse_args()

    repo_manager = GithubRepoManager(token)

    if args.action == 'stats':
        try:
            stats = repo_manager.get_repo_stats()
            for key, value in stats.items():
                print(f"📊 {key}: {value}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error getting stats: {str(e)}")
            sys.exit(1)
    elif args.action == 'list':
        try:
            repos = repo_manager.all_repos
            for repo in repos:
                print(f"📁 {repo.name} - {repo.description}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error listing repositories: {str(e)}")
            sys.exit(1)
    elif args.action == 'create':
        if not args.name:
            print("❌ Repository name is required for create action")
            sys.exit(1)
        try:
            repo = repo_manager.create_repo(args.name, description=args.description, private=args.private)
            print(f"✨ Repository created: {repo.html_url}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error creating repository: {str(e)}")
            sys.exit(1)
    elif args.action == 'delete':
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
    elif args.action == 'export':
        if not args.data_format or not args.output:
            print("❌ Format and output file name are required for export action")
            sys.exit(1)
        try:
            export_data(repo_manager, args.data_format, args.output)
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error exporting data: {str(e)}")
            sys.exit(1)
    elif args.action == 'stars':
        if not args.data_format or not args.output:
            print("❌ Format and output file name are required for stars action")
            sys.exit(1)
        try:
            export_stars(repo_manager, args.data_format, args.output)
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error exporting stars: {str(e)}")
            sys.exit(1)
    elif args.action == 'visualize':
        if not args.type or not args.output:
            print("❌ Visualization type and output file name are required for visualize action")
            sys.exit(1)
        try:
            visualize(repo_manager, args.type, args.output, format=args.image_format)
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error generating visualization: {str(e)}")
            sys.exit(1)
    elif args.action == 'dashboard':
        launch_dashboard()
        # Note: launch_dashboard already includes sys.exit()

if __name__ == "__main__":
    main()