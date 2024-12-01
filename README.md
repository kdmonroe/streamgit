# StreamGit 🌊

StreamGit is a powerful GitHub analytics tool that combines the fluidity of Streamlit with the power of GitHub's API. Visualize and manage your GitHub repositories through two seamless interfaces:

1. An interactive Streamlit dashboard 🌊
2. A powerful command-line interface ⚡

Both interfaces leverage PyGithub to provide real-time insights into your GitHub repositories, activity tracking, and data visualization using Plotly.

![StreamGit Visualizations](/images/demo-viz.png)
![StreamGit Stats](/images/demo-stats.png)

### Prerequisites
- Python 3.9 or higher 
- GitHub Personal Access Token

### Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Update `.env` with your GitHub token:
```env
GITHUB_TOKEN=your_github_token_here
```

> ⚠️ Never commit your actual `.env` file to version control. The `.env.example` file serves as a template only.

### GitHub Token Setup

StreamGit requires a [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) with the following permissions:

1. **repo**: Full control of private repositories
2. **read:user**: Read access to user profile data
3. **user:email**: Access user email addresses (read-only)
4. **delete_repo**: Delete repositories

To set up your token:

1. Visit GitHub Settings > Developer settings > Personal access tokens
2. Click "Generate new token"
3. Select the required scopes listed above
4. Generate and store your token securely

The token is required for both the web app and CLI interfaces, but is never stored permanently.

## Features

- **Stats 📊**: Comprehensive overview of your GitHub repositories
- **Activity 🕒**: Real-time tracking of commits and repository updates
- **Data 📁**: Detailed repository insights with flexible export options
- **Visualize 📈**: Interactive charts powered by Plotly
- **Stars ⭐**: Analysis of your starred repositories
- **Create 🆕**: Streamlined repository creation
- **Delete 🗑️**: Repository management tools

## Interfaces

### 1. StreamGit Dashboard

The [StreamGit Dashboard](https://streamgit.streamlit.app) provides an intuitive, interactive interface for real-time GitHub analytics.

#### Launch the Dashboard
```bash
streamlit run app.py
```

### 2. StreamGit CLI

The CLI provides rapid access to core features through your terminal.

#### Installation
Install from the local directory:
```bash
pip install -e .
```

#### Basic Usage
```bash
streamgit <command> [options]
```

Example Commands:
```bash
# Get repository stats
streamgit stats

# List all repositories
streamgit list

# Create a new repository
streamgit create --name "new-project" --description "A new project" --private

# Export repository data
streamgit export --data-format csv --output repositories.csv

# Generate visualization
streamgit visualize --type language_distribution --output languages.png
```

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/keonmonroe/streamgit.git
cd streamgit
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Use Cases

- **Developers**: Streamline repository management and gain insights
- **Teams**: Track project activity and repository metrics
- **Analysts**: Generate GitHub analytics and visualizations

## Contributing
Feel free to open issues or submit pull requests to help improve StreamGit!

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements
Built with:
- [PyGithub](https://pygithub.readthedocs.io/en/latest/)
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/python/)
