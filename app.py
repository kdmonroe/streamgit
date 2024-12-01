import streamlit as st
from streamlit_option_menu import option_menu
from github_repo_manager import GithubRepoManager
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from github import GithubException
import kaleido

BRAND = {
    'name': 'StreamGit 🌊',
    'tagline': 'GitHub Analytics with Python & Streamlit',
    'primary': '#FF4B4B',   
    'secondary': '#2188ff', 
    'background': 'linear-gradient(to right, #ff4b4b1a, #2188ff1a)',
    'version': '1.0.0'
}

COLORS = {
    'total': '#4CAF50',     # Green
    'owned': '#2196F3',     # Blue
    'public': '#FDD835',    # yellow
    'private': '#E53935',   # red
    'forked': '#8E24AA',    # purple
    'archived': '#6D4C41'   # brown
}

def load_token_from_env():
    env_path = os.path.join(os.path.dirname(__file__), 'token.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        return os.getenv('GITHUB_TOKEN')
    return None

def get_token_from_user():
    st.warning("GitHub token not found in the environment.")
    token = st.text_input("Please enter your GitHub Personal Access Token:", type="password")
    if token:
        return token
    return None

def create_summary(repo_manager, stats):
    username = repo_manager.user.login
    return f"""
    <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-family: "Source Sans Pro", sans-serif; margin-bottom: 20px;'>
        <h3 style='font-family: "Source Sans Pro", sans-serif; margin-bottom: 15px;'>Successfully authenticated as GitHub user: <span style='color: #1E88E5'>{username}</span></h3>
        
        <div style='font-size: 16px; line-height: 2; font-family: "Source Sans Pro", sans-serif; margin-bottom: 10px;'>
            Found a total of <span style='color:{COLORS["total"]};font-weight:bold;font-size:18px;'>{stats["Total Repositories"]}</span> repositories, 
            of which <span style='color:{COLORS["owned"]};font-weight:bold;font-size:18px;'>{stats[f"Owned by {username}"]}</span> are owned by {username}.
        </div>
        <div style='font-size: 16px; line-height: 2; margin-bottom: 10px; font-family: "Source Sans Pro", sans-serif;'>
            This includes <span style='color:{COLORS["public"]};font-weight:bold;font-size:18px;'>{stats["Public"]}</span> public and 
            <span style='color:{COLORS["private"]};font-weight:bold;font-size:18px;'>{stats["Private"]}</span> private repositories.
        </div>
        <div style='font-size: 16px; line-height: 2; font-family: "Source Sans Pro", sans-serif;'>
            Among these, there are <span style='color:{COLORS["forked"]};font-weight:bold;font-size:18px;'>{stats["Forked"]}</span> forked repositories and 
            <span style='color:{COLORS["archived"]};font-weight:bold;font-size:18px;'>{stats["Archived"]}</span> archived repositories.
        </div>
    </div>
    """

def format_dataframe(df, format_owned):
    def highlight_owned(row):
        if format_owned:
            # Darker background colors for better contrast in dark mode
            color = 'rgba(33, 150, 243, 0.2)' if row['is_owner'] else 'rgba(255, 87, 34, 0.2)'  # Blue vs Orange tints
            text_color = 'white'  # White text for dark mode
            return [f'background-color: {color}; color: {text_color}' for _ in row]
        return ['' for _ in row]
    return df.style.apply(highlight_owned, axis=1)

def format_datetime(dt):
    return dt.strftime("%b %d, %Y %I:%M %p")

def delete_repository(repo_manager):
    st.header("Delete Repository")
    
    # Get list of repositories
    repos = repo_manager.all_repos
    repo_names = [repo.name for repo in repos if repo.permissions.admin]
    
    # Dropdown to select repository
    selected_repo = st.selectbox("Select a repository to delete:", repo_names)
    
    if selected_repo:
        st.warning(f"You are about to delete the repository: {selected_repo}")
        st.write("This action cannot be undone. Please type the repository name to confirm.")
        
        # Text input for confirmation
        confirmation = st.text_input("Type the repository name to confirm deletion:")
        
        if st.button("Delete Repository"):
            if confirmation == selected_repo:
                try:
                    repo_manager.delete_repo(selected_repo)
                    st.success(f"Repository {selected_repo} has been deleted successfully.")
                except GithubException as e:
                    st.error(f"An error occurred while deleting the repository: {str(e)}")
            else:
                st.error("Confirmation does not match the repository name. Deletion aborted.")

def export_to_csv(data, filename):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename_with_date = f"{current_date}_{filename}"
    csv_file = data.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv_file,
        file_name=filename_with_date,
        mime="text/csv"
    )

def get_all_commits(repo_manager, repos):
    all_commits = []
    for repo in repos:
        commits = repo_manager.get_repo_commits(repo)
        for commit in commits:
            all_commits.append({
                'repo': repo.name,
                'message': commit.commit.message,
                'date': commit.commit.author.date,
                'author': commit.commit.author.name,
                'url': commit.html_url
            })
    return pd.DataFrame(all_commits)

def create_repository(repo_manager):
    st.header("Create New Repository")
    
    st.write("""
    This section allows you to create a new GitHub repository directly from the app. 
    You can specify the repository name, description, visibility, and other options. 
    The app uses the GitHub API to create the repository based on your input.
    """)
    
    # Form for repository details
    with st.form("create_repo_form"):
        repo_name = st.text_input("Repository Name", help="Enter the name for your new repository")
        description = st.text_area("Description", help="Provide a brief description of your repository")
        private = st.checkbox("Private Repository", help="Check this if you want the repository to be private")
        auto_init = st.checkbox("Initialize with README", help="Check this to initialize the repository with a README file")
        
        # Optional fields
        with st.expander("Advanced Options"):
            gitignore_template = st.text_input("Gitignore Template", help="Enter the name of a gitignore template (e.g., 'Python', 'Node')")
            license_template = st.text_input("License Template", help="Enter the name of a license template (e.g., 'mit', 'gpl-3.0')")
        
        submitted = st.form_submit_button("Create Repository")
        
    if submitted:
        try:
            new_repo = repo_manager.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=auto_init,
                gitignore_template=gitignore_template if gitignore_template else None,
                license_template=license_template if license_template else None
            )
            st.success(f"Repository '{repo_name}' created successfully! URL: {new_repo.html_url}")
        except GithubException as e:
            st.error(f"An error occurred while creating the repository: {str(e)}")

def initialize_repo_manager():
    token = load_token_from_env()
    if not token:
        token = get_token_from_user()
    
    if not token:
        return None, "GitHub token not provided. Please set up your token."
    
    try:
        repo_manager = GithubRepoManager(token)
        return repo_manager, None
    except Exception as e:
        return None, f"Error initializing GitHub connection: {str(e)}"

def save_figure_to_html(fig, filename):
    """Save a Plotly figure as an HTML file that can be opened in a browser"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename_with_date = f"{current_date}_{filename}.html"
    
    # Convert figure to HTML string
    html_str = fig.to_html(include_plotlyjs='cdn', full_html=True)
    
    # Create download button
    st.download_button(
        label=f"Download {filename}",
        data=html_str,
        file_name=filename_with_date,
        mime="text/html"
    )

def main():
    st.markdown(f"""
    <style>
    .stApp {{
        background: {BRAND['background']};
    }}
    .brand-header {{
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        text-align: center;
    }}
    .brand-name {{
        color: {BRAND['primary']};
        font-size: 2.5rem;
        font-weight: bold;
        font-family: "Source Sans Pro", sans-serif;
    }}
    .brand-tagline {{
        color: {BRAND['secondary']};
        font-size: 1.2rem;
        font-family: "Source Sans Pro", sans-serif;
    }}
    </style>
    """, unsafe_allow_html=True)

    repo_manager, error = initialize_repo_manager()
    token_loaded = repo_manager is not None

    # Help information placement and expansion
    if not token_loaded:
        display_help_info(expanded=True)

    if error:
        st.error(error)
        return

    user = repo_manager.user
    
    # Sidebar with user info
    with st.sidebar:
        st.markdown(f"""
            <style>
            .brand-header {{
                text-align: center;
                margin-bottom: 1.5rem;
            }}
            .user-info {{
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 1.5rem;
            }}
            .user-info img {{
                border-radius: 50%;
                margin-bottom: 0.5rem;
            }}
            </style>
            <div class="brand-header">
                <div class="brand-name">{BRAND['name']}</div>
                <div class="brand-tagline">{BRAND['tagline']}</div>
            </div>
            <div class="user-info">
                <img src="{user.avatar_url}" width="100">
                <p>Welcome, <strong>{user.name}</strong>!</p>
            </div>
        """, unsafe_allow_html=True)
        
        selected = option_menu(
            menu_title="Main Menu",
            options=["Stats 📊", "Activity 🕒", "Data 📁", "Visualize 📈", "Stars ⭐", "Create 🆕", "Delete 🗑️"],
            icons=["graph-up", "clock-history", "folder", "bar-chart", "star", "plus-circle", "trash"],
            # menu_icon="cast",
            default_index=0,
        )

    # Main content
    if selected == "Stats 📊":
        st.header("Repository Statistics 📊")
        stats = repo_manager.get_repo_stats()
        
        # First display the summary
        st.components.v1.html(create_summary(repo_manager, stats), height=250)
        
        # Add more spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Create three columns with equal spacing
        col1, col2, col3 = st.columns(3)
        
        metrics = [
            ("Total Repositories", stats["Total Repositories"], COLORS['total']),
            (f"Owned by {repo_manager.user.login}", stats[f"Owned by {repo_manager.user.login}"], COLORS['owned']),
            ("Public", stats["Public"], COLORS['public']),
            ("Private", stats["Private"], COLORS['private']),
            ("Forked", stats["Forked"], COLORS['forked']),
            ("Archived", stats["Archived"], COLORS['archived'])
        ]
        
        # Custom CSS for metric cards
        metric_style = """
            <div style='background-color: white; 
                        padding: 25px; 
                        border-radius: 10px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                        margin: 15px 0;
                        text-align: center;
                        min-height: 120px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;'>
                <p style='color: {}; font-weight: bold; font-size: 16px; margin-bottom: 15px;'>{}</p>
                <h2 style='color: {}; font-size: 36px; margin: 0;'>{}</h2>
            </div>
        """
        
        for i, (key, value, color) in enumerate(metrics):
            if i % 3 == 0:
                col1.markdown(metric_style.format(color, key, color, value), unsafe_allow_html=True)
            elif i % 3 == 1:
                col2.markdown(metric_style.format(color, key, color, value), unsafe_allow_html=True)
            else:
                col3.markdown(metric_style.format(color, key, color, value), unsafe_allow_html=True)

    elif selected == "Activity 🕒":
        st.header("Recent Activity 🕒")
        st.subheader("Recently Active Repositories")
        
        num_recent_repos = st.number_input("Number of recent repositories to fetch", min_value=1, max_value=50, value=10, step=1)
        
        recent_repos = repo_manager.get_recent_repos(num_recent_repos)
        show_all_commits = st.checkbox("Show all recent commits", value=True)
        
        # Filter for owned vs non-owned repos
        filter_owned = st.checkbox("Show only owned repositories", value=False)
        if filter_owned:
            recent_repos = [repo for repo in recent_repos if repo.owner.login == user.login]

        all_commits = []
        
        for i, repo in enumerate(recent_repos, 1):
            st.write(f"{i}. **{repo.name}** - Last updated: {format_datetime(repo.updated_at)}")
            commits = repo_manager.get_repo_commits(repo)
            
            if commits:
                if show_all_commits:
                    for commit in commits:
                        all_commits.append({
                            'repo': repo.name,
                            'message': commit.commit.message,
                            'date': commit.commit.author.date,
                            'author': commit.commit.author.name,
                            'url': commit.html_url
                        })
                else:
                    with st.expander(f"Show commits for {repo.name}"):
                        for commit in commits:
                            st.write(f"- {commit.commit.message} ({format_datetime(commit.commit.author.date)})")
            else:
                st.write("No commits found in this repository.")
        
        if show_all_commits and all_commits:
            st.subheader("All Recent Commits")
            filter_user_commits = st.checkbox("Show only my commits", value=True)
            df_commits = pd.DataFrame(all_commits)
            df_commits['date'] = pd.to_datetime(df_commits['date']).dt.strftime("%b %d, %Y %I:%M %p")
            
            if filter_user_commits:
                user_login = repo_manager.user.login
                user_name = repo_manager.user.name
                st.write(f"Filtering commits by {user_login} (username) and {user_name} (full name)")
                
                # Create summary for owned repos
                owned_repos = df_commits[df_commits['author'].isin([user_login, user_name])]
                owned_summary = f"""
                You have made <span style='color:#4CAF50;font-weight:bold;'>{len(owned_repos)}</span> commits 
                across <span style='color:#4CAF50;font-weight:bold;'>{owned_repos['repo'].nunique()}</span> repositories.
                """
                
                # Create summary for other repos
                other_repos = df_commits[~df_commits['author'].isin([user_login, user_name])]
                other_summary = f"""
                There are <span style='color:#2196F3;font-weight:bold;'>{len(other_repos)}</span> commits 
                by other authors across <span style='color:#2196F3;font-weight:bold;'>{other_repos['repo'].nunique()}</span> repositories.
                """
                
                st.markdown(owned_summary, unsafe_allow_html=True)
                st.markdown(other_summary, unsafe_allow_html=True)
                
                # Display unique authors
                st.write("Unique authors in the dataset:")
                authors = df_commits['author'].unique()
                for author in authors:
                    color = '#4CAF50' if author in [user_login, user_name] else '#2196F3'
                    st.markdown(f"<span style='color:{color};'>{author}</span>", unsafe_allow_html=True)
                
                df_filtered = owned_repos
                st.write(f"Showing {len(df_filtered)} commits for {user_login}/{user_name}")
                if len(df_filtered) == 0:
                    st.warning("No commits found for the current user. This might be due to a mismatch between your GitHub username/name and the commit author name.")
                df_commits = df_filtered
            
            st.dataframe(df_commits, use_container_width=True)
        elif show_all_commits:
            st.write("No commits found in any of the recent repositories.")
        
        # Export All Commits
        st.subheader("Export All Commits")
        if st.button("Prepare Commits for Export"):
            with st.spinner("Fetching all commits... This may take a while."):
                all_commits_df = get_all_commits(repo_manager, recent_repos)
            st.success("Commits fetched successfully!")
            export_to_csv(all_commits_df, f"{repo_manager.user.login}_all_commits.csv")
        
        # Activity Timeline
        activity_data = [{'repo': repo.name, 'date': repo.updated_at} for repo in recent_repos]
        activity_df = pd.DataFrame(activity_data)
        fig = px.scatter(activity_df, x="date", y="repo", title="Recent Repository Activity",
                         labels={"date": "Last Update", "repo": "Repository"},
                         hover_data=["date"])
        fig.update_traces(marker=dict(size=10))
        fig.update_layout(xaxis_title="Last Update", yaxis_title="Repository")
        st.plotly_chart(fig, use_container_width=True)

    elif selected == "Data 📁":
        st.header("Repository Data 📁")
        # Checkbox for formatting owned vs. non-owned repos
        format_owned = st.checkbox("Format Owned vs. Non-Owned", value=True)

        df = repo_manager.get_repos_dataframe()
        
        if format_owned:
            owned_count = df['is_owner'].sum()
            non_owned_count = len(df) - owned_count
            st.markdown(f"""
                <div style='font-size: 1.1em; margin-bottom: 1em;'>
                    You <span style='color: #2196F3; font-weight: bold;'>own {owned_count} repositories</span> 
                    and have access to 
                    <span style='color: #FF5722; font-weight: bold;'>{non_owned_count} repositories owned by others</span>.
                </div>
                """, unsafe_allow_html=True)

        st.dataframe(format_dataframe(df, format_owned), use_container_width=True)
        
        # Add export button for repository data
        export_to_csv(df, f"{repo_manager.user.login}_repository_data.csv")

    elif selected == "Visualize 📈":
        st.header("Visualizations 📈")
        
        st.write("""
        This section provides visual insights into your GitHub repositories using Plotly charts.
        Each visualization can be downloaded as an interactive HTML file that can be opened in your browser.
        """)
        
        df = repo_manager.get_repos_dataframe()
        
        # Language Distribution
        st.subheader("Language Distribution")
        lang_counts = df['language'].value_counts()
        fig_lang = px.pie(values=lang_counts.values, names=lang_counts.index, title="Language Distribution")
        st.plotly_chart(fig_lang, use_container_width=True)
        save_figure_to_html(fig_lang, "language_distribution")
        
        # Stars vs. Forks
        st.subheader("Stars vs. Forks")
        fig_stars = px.scatter(df, x="stars", y="forks", hover_name="name", 
                              title="Stars vs. Forks",
                              labels={"stars": "Stars", "forks": "Forks"})
        st.plotly_chart(fig_stars, use_container_width=True)
        save_figure_to_html(fig_stars, "stars_vs_forks")
        
        # Repository Creation Timeline
        st.subheader("Repository Creation Timeline")
        fig_timeline = px.histogram(df, x="created_at", 
                                   title="Repository Creation Timeline",
                                   labels={"created_at": "Creation Date", "count": "Number of Repositories"})
        fig_timeline.update_layout(bargap=0.1)
        st.plotly_chart(fig_timeline, use_container_width=True)
        save_figure_to_html(fig_timeline, "creation_timeline")
        
        # Additional options for static image export
        st.subheader("Export Options")
        export_format = st.selectbox("Select export format for static images:", 
                                    ["png", "jpg", "svg", "pdf"])
        
        if st.button("Export All Visualizations"):
            try:
                current_date = datetime.now().strftime("%Y-%m-%d")
                for fig, name in [(fig_lang, "language_distribution"), 
                                (fig_stars, "stars_vs_forks"), 
                                (fig_timeline, "creation_timeline")]:
                    img_bytes = fig.to_image(format=export_format)
                    filename = f"{current_date}_{name}.{export_format}"
                    st.download_button(
                        label=f"Download {name}",
                        data=img_bytes,
                        file_name=filename,
                        mime=f"image/{export_format}"
                    )
                st.success("Visualizations prepared for download!")
            except Exception as e:
                st.error(f"Error exporting visualizations: {str(e)}")

    elif selected == "Stars ⭐":
        st.header("Starred Repositories ⭐")
        
        st.write("""
        This section analyzes and visualizes your starred repositories on GitHub. 
        """)
        
        starred_df = repo_manager.get_starred_repos()
        
        # Ensure starred_df is a DataFrame
        if not isinstance(starred_df, pd.DataFrame):
            starred_df = pd.DataFrame(starred_df)

        # Display total number of starred repositories
        st.subheader(f"Total Starred Repositories: {len(starred_df)}")
        
        # Display table of starred repositories
        st.dataframe(starred_df, use_container_width=True)
        
        # Language breakdown pie chart
        lang_counts = starred_df['language'].value_counts()
        fig = px.pie(values=lang_counts.values, names=lang_counts.index, title="Language Distribution of Starred Repositories")
        st.plotly_chart(fig, use_container_width=True)
        
        # Top 10 most starred repositories
        top_10_starred = starred_df.nlargest(10, 'stars')
        fig = go.Figure(data=[go.Bar(x=top_10_starred['name'], y=top_10_starred['stars'])])
        fig.update_layout(title="Top 10 Most Starred Repositories", xaxis_title="Repository", yaxis_title="Stars")
        st.plotly_chart(fig, use_container_width=True)
        
        # Export to CSV
        st.subheader("Export Starred Repositories Data")
        export_to_csv(starred_df, f"{repo_manager.user.login}_starred_repositories.csv")

    elif selected == "Create 🆕":
        create_repository(repo_manager)

    elif selected == "Delete 🗑️":
        delete_repository(repo_manager)

    if token_loaded:
        display_help_info(expanded=False)

    st.sidebar.markdown("""
    ---
    ### About this app
    
    This GitHub Repository Analyzer helps you manage and visualize your GitHub repositories efficiently using [PyGithub](https://pygithub.readthedocs.io/en/latest/) and [Streamlit](https://streamlit.io/). See more at [GitHub Repository Analyzer](https://github.com/keonmonroe/github-repo-analyzer) including CLI usage and potential use cases.
                        
    """)

def display_help_info(expanded):
    with st.expander("❓ Need help?", expanded=expanded):
        st.write("""
        This app allows you to manage and visualize your GitHub repositories efficiently using [PytGithub](https://pygithub.readthedocs.io/en/latest/) and [Streamlit](https://streamlit.io/). 

        To use this app, you need to set up a GitHub Personal Access Token. Here's how:
        1. Go to your GitHub account settings.
        2. Click on "Developer settings" in the left sidebar.
        3. Select "Personal access tokens" and then "Tokens (classic)".
        4. Click "Generate new token" and select "Generate new token (classic)".
        5. Give your token a descriptive name.
        6. Select the following scopes:
           - `repo` (Full control of private repositories)
           - `delete_repo` (Delete repositories)
           - `read:user` (Read all user profile data)
           - `user:email` (Access user email addresses (read-only))
        7. Click "Generate token" at the bottom of the page.
        8. Copy the generated token and store it securely.
        9. Provide the token in the input field below.

        Remember to keep your token secret and never share it publicly!
        """)

if __name__ == "__main__":
    st.set_page_config(
        page_title=f"{BRAND['name']} - GitHub Analytics",
        page_icon="🌊",
        layout="wide"
    )
    main()
