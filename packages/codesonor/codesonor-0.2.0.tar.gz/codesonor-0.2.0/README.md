# CodeSonor 🔍

**AI-powered GitHub repository analyzer** - Available as both a CLI tool and web application.

[![PyPI version](https://img.shields.io/pypi/v/codesonor.svg)](https://pypi.org/project/codesonor/)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/codesonor.svg)](https://pypi.org/project/codesonor/)

## 🚀 Quick Start

### CLI Tool (Recommended)
```bash
pip install codesonor
codesonor analyze https://github.com/pallets/flask
```

### Web Application
```bash
git clone https://github.com/farhanmir/CodeSonor.git
cd CodeSonor
pip install -r requirements.txt
python app.py  # Visit http://localhost:5000
```

## Features ✨

- 💾 **Easy Installation** - `pip install codesonor`
- 🖥️ **Dual Interface** - CLI tool or web application
- 📊 **Language Analysis** - Distribution breakdown across 20+ languages
- 🤖 **AI Summaries** - Powered by Google Gemini
- 📈 **Repository Stats** - Stars, forks, file counts, and more
- ⚡ **Fast Analysis** - Smart filtering for quick results
- 🎨 **Beautiful Output** - Rich terminal formatting or Bootstrap UI

## Features ✨

- �️ **Dual Interface** - Use as CLI tool or web application
- 💾 **Easy Installation** - `pip install codesonor` (after publishing)
- �📊 **Language Distribution Analysis** - Visual breakdown of programming languages used
- 🤖 **AI-Powered Code Summaries** - Automatic insights using Google's Gemini API
- 📈 **Repository Statistics** - File counts, stars, forks, and timeline information
- 🎨 **Beautiful Output** - Rich terminal formatting (CLI) or Bootstrap UI (Web)
- ⚡ **Fast Analysis** - Smart filtering and file limits for quick results
- 🔒 **Public Repos** - Analyze any public GitHub repository

## Tech Stack 🛠️

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Requests** - HTTP library for GitHub API
- **Google Generative AI** - Gemini API for code analysis
- **python-dotenv** - Environment variable management

### Frontend
- **HTML5 & CSS3**
- **Bootstrap 5** - Responsive UI framework
- **JavaScript (ES6+)** - Client-side logic
- **Bootstrap Icons** - Icon library

## Installation & Setup 🚀

### CLI Installation

```bash
# Install from PyPI
pip install codesonor

# Set API keys
export GEMINI_API_KEY="your_gemini_api_key"
export GITHUB_TOKEN="your_github_token"

# Use it
codesonor analyze https://github.com/pallets/flask
```

Get API keys:
- **Gemini**: https://makersuite.google.com/app/apikey (Free)
- **GitHub**: https://github.com/settings/tokens (needs `public_repo` scope)

📖 **Full CLI docs**: See [CLI_README.md](CLI_README.md)

---

### Web App Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- A Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- A GitHub Personal Access Token ([Get one here](https://github.com/settings/tokens)) - **Required for API access**

### Step 1: Clone or Download the Repository
```bash
cd CodeSonor
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
1. Copy the example environment file:
   ```bash
   # Windows PowerShell
   Copy-Item .env.example .env

   # macOS/Linux
   cp .env.example .env
   ```

2. Edit the `.env` file and add your API keys:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GITHUB_TOKEN=your_actual_github_token_here
   ```

   **Getting API Keys:**
   - **Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **GitHub Token**: Visit [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
     - Create a token with `public_repo` scope

### Step 5: Run the Application
```bash
python app.py
```

The server will start at `http://localhost:5000`

### Step 6: Open in Browser
Navigate to `http://localhost:5000` in your web browser.

## Usage 📖

### CLI Commands

```bash
# Quick summary (no API keys needed)
codesonor summary https://github.com/owner/repo

# Full analysis with AI
codesonor analyze https://github.com/owner/repo

# Advanced options
codesonor analyze <url> --no-ai              # Skip AI (faster)
codesonor analyze <url> --max-files 200      # Limit files
codesonor analyze <url> --json-output out.json  # Export JSON
```

### Web Interface

1. **Enter Repository URL**: Paste any public GitHub repository URL into the input field
   - Example: `https://github.com/facebook/react`
   - Example: `https://github.com/microsoft/vscode`

2. **Click Analyze**: The application will:
   - Fetch repository information from GitHub API
   - Calculate language distribution
   - Analyze key source files with AI
   - Display comprehensive results

3. **View Results**: The report includes:
   - Repository metadata (name, description, stars, forks)
   - Total file count and creation/update dates
   - Language distribution with visual progress bars
   - AI-generated summaries of key code files
   - File structure overview

## Project Structure 📁

```
CodeSonor/
├── src/codesonor/         # CLI Package
│   ├── __init__.py        # Package exports
│   ├── __main__.py        # CLI entry point
│   ├── cli.py             # Click-based CLI
│   ├── analyzer.py        # Main orchestrator
│   ├── github_client.py   # GitHub API client
│   ├── language_stats.py  # Language analysis
│   └── ai_analyzer.py     # Gemini AI integration
├── static/                # Web App Frontend
│   ├── index.html         # Main HTML page
│   ├── style.css          # Custom styles
│   └── script.js          # JavaScript logic
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_codesonor.py
├── app.py                 # Flask backend server
├── pyproject.toml         # Package configuration
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── CLI_README.md          # CLI documentation
├── PUBLISHING.md          # PyPI publishing guide
└── README.md              # This file
```

## API Endpoints 🔌

### `POST /analyze`
Analyzes a GitHub repository.

**Request Body:**
```json
{
  "url": "https://github.com/owner/repo"
}
```

**Response:**
```json
{
  "repository": {
    "name": "repo-name",
    "owner": "owner-name",
    "description": "Repository description",
    "stars": 1234,
    "forks": 567,
    "url": "https://github.com/owner/repo",
    "created_at": "2020-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "statistics": {
    "total_files": 150,
    "language_distribution": {
      "Python": 60.5,
      "JavaScript": 30.2,
      "HTML": 9.3
    }
  },
  "ai_analysis": [
    {
      "file": "src/main.py",
      "summary": "AI-generated summary..."
    }
  ],
  "file_list": ["file1.py", "file2.js", ...]
}
```

## Configuration ⚙️

### Language Extensions
The application recognizes the following file extensions:
- Python (.py)
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)
- Java (.java)
- C/C++ (.c, .cpp)
- C# (.cs)
- Go (.go)
- Ruby (.rb)
- PHP (.php)
- Swift (.swift)
- Kotlin (.kt)
- Rust (.rs)
- And more...

### AI Analysis
- Analyzes up to 3 key source files per repository
- Prioritizes main, index, app, and server files
- Skips files larger than 50KB to avoid token limits
- Uses first 3000 characters of each file for analysis

## Troubleshooting 🔧

### CLI Issues

**Command not found: `codesonor`**
```bash
# Use python module instead
python -m codesonor --help
```

**Import errors**
```bash
# Reinstall the package
pip install --force-reinstall codesonor
```

### Web App Issues

**"Error fetching repository files"**
- Ensure the repository URL is correct and public
- Check your internet connection
- Verify GitHub API is accessible

**"AI summary not available"**
- Make sure `GEMINI_API_KEY` is set in `.env` file
- Verify your API key is valid and active
- Check if you've exceeded API quota

### API Issues

**Rate Limiting**
- GitHub API has rate limits (60 requests/hour without token)
- Add a `GITHUB_TOKEN` to your `.env` file for higher limits (5000 requests/hour)

## Documentation 📚

- **[CLI_README.md](CLI_README.md)** - Complete CLI documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development & publishing guide
- **[QUICKSTART.md](QUICKSTART.md)** - 5-step web app quickstart

## Contributing 🤝

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and publishing guide.

## License 📄

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- Google Gemini for AI analysis
- GitHub API for repository data
- Bootstrap & Rich for beautiful UIs

---

**Author**: Farhan Mir | [GitHub](https://github.com/farhanmir)