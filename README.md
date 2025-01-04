# StreamGit 🌊

[StreamGit](https://streamgit.up.railway.app) is a powerful GitHub analytics tool that combines the fluidity of Streamlit with the power of GitHub's API. Visualize and manage your GitHub repositories through two seamless interfaces:

1. An interactive Streamlit dashboard. View summary statistics, repository activity, and more.
2. An easy to use command-line interface (with parallel functionality to the dashboard). 


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

To set up your token, follow the instructions linked above.

### Token Configuration

StreamGit supports two methods for providing your GitHub token:

1. **Manual Input (Web App)**
   - Enter your token directly in the web interface
   - Token is stored only in session state and cleared on browser refresh
   - Best for public deployments where users provide their own tokens

2. **Using a Local Secrets File (Local Streamlit App or CLI)**
   ```bash
   mkdir -p .streamlit
   touch .streamlit/secrets.toml
   ```

   Alternatively you could also use a `.env` file, an example of which is provided in the `.env.example` file.

   Add your token to `.streamlit/secrets.toml`:
   ```toml
   github_token = "your-github-token-here"
   ```

   > ⚠️ Never commit `secrets.toml` to version control! Add it to your `.gitignore`

Learn more about Streamlit secrets management in the [official documentation](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management).

This project handles the token securely by storing it in session state and clearing it on browser refresh.

## Why StreamGit?

- **For Developers**: Streamline your repository management and gain insights into your GitHub activity
- **For Teams**: Track project activity and repository metrics at scale
- **For Analysts**: Easily generate GitHub analytics and corresponding Python visualizations easily

### Features

- **Stats 📊**: Comprehensive overview of your GitHub repositories
- **Activity 🕒**: Real-time tracking of commits and repository updates
- **Data 📁**: Detailed repository insights with flexible export options
- **Visualize 📈**: Interactive charts powered by Plotly
- **Stars ⭐**: Analysis of your starred repositories
- **Create 🆕**: Streamlined repository creation
- **Delete 🗑️**: Repository management tools

## Interfaces

### 1. StreamGit Web App

The [StreamGit dashboard](https://streamgit.up.railway.app) provides an intuitive, interactive interface for real-time GitHub analytics. Just plug in your GitHub token to get started.

[![StreamGit Front Page](/images/demo-front-page.png)](https://streamgit.up.railway.app)

### 2. Local Streamlit App

Launch the locally Streamlit app to interact with the dashboard. Develop and test new features here.


#### Launch the Streamlit App
```bash
streamlit run app.py
```

### 3. StreamGit CLI

The CLI provides rapid access to core features through your terminal. Tests are available in the `tests` directory.

#### Installation
Install from the local directory:
```bash
pip install -e .
```

#### Basic Usage
```bash
streamgit <command> [options]
```

Available Commands:
```bash
stats       Display statistics for all your repositories
list        List all your repositories
create      Create a new repository
delete      Delete an existing repository
export      Export repository data to CSV/Excel
stars       Export starred repositories to CSV/Excel
visualize   Generate repository visualizations
dashboard   Launch the StreamGit dashboard
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

# Export starred repositories
streamgit stars --data-format xlsx --output starred.xlsx

# Generate visualizations
streamgit visualize --type language_distribution --output languages.png
streamgit visualize --type stars_vs_forks --output activity.png
streamgit visualize --type creation_timeline --output timeline.png

# Launch the interactive dashboard
streamgit dashboard
```

For detailed help on any command:
```bash
streamgit <command> --help
```

## Development Setup

1. Clone this repo:
```bash
git clone https://github.com/keonmonroe/streamgit.git
cd streamgit
```

2. Using Conda, create and activate the environment:
```bash
conda env create -f environment.yml
conda activate streamgit-env
```

3. Using Pip, install dependencies:
```bash
pip install -r requirements.txt
```

## Contributing
Feel free to open issues or submit pull requests to help improve StreamGit!

## Acknowledgements
Built with:
- [PyGithub](https://pygithub.readthedocs.io/en/latest/)
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/python/)
