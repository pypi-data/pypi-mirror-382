# CodeSonor 🔍

**AI-Powered GitHub Repository Analyzer** - Analyze any GitHub repository with AI-generated insights, language statistics, and comprehensive code summaries.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Installation

```bash
pip install codesonor
```

## 📋 Prerequisites

You'll need two API keys:

1. **Google Gemini API Key** (Required)
   - Get it free at [Google AI Studio](https://makersuite.google.com/app/apikey)
   
2. **GitHub Personal Access Token** (Required)
   - Create at [GitHub Settings → Developer Settings → Personal Access Tokens](https://github.com/settings/tokens)
   - Needs `public_repo` scope

## ⚙️ Configuration

Set your API keys as environment variables:

### Windows (PowerShell)
```powershell
$env:GEMINI_API_KEY = "your_gemini_api_key_here"
$env:GITHUB_TOKEN = "your_github_token_here"
```

### Linux/MacOS
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
export GITHUB_TOKEN="your_github_token_here"
```

Or create a `.env` file in your working directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here
```

## 📖 Usage

### Full Analysis with AI
```bash
codesonor analyze https://github.com/owner/repo
```

### Quick Summary (No AI)
```bash
codesonor summary https://github.com/owner/repo
```

### Advanced Options
```bash
# Skip AI analysis (faster)
codesonor analyze https://github.com/owner/repo --no-ai

# Limit number of files analyzed
codesonor analyze https://github.com/owner/repo --max-files 200

# Export results as JSON
codesonor analyze https://github.com/owner/repo --json-output results.json
```

## 📊 Example Output

```
╭─────────────────────────────────────────────────╮
│  CodeSonor Analysis: awesome-project            │
╰─────────────────────────────────────────────────╯

Repository Information
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field      ┃ Value                          ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Owner      │ awesome-owner                  │
│ Repository │ awesome-project                │
│ Stars      │ 1,234                          │
│ Forks      │ 567                            │
│ Language   │ Python                         │
└────────────┴────────────────────────────────┘

Language Distribution
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┓
┃ Language   ┃ Files    ┃ %      ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━┩
│ Python     │ 45       │ 78.5%  │
│ JavaScript │ 8        │ 14.0%  │
│ CSS        │ 4        │ 7.0%   │
│ HTML       │ 1        │ 0.5%   │
└────────────┴──────────┴────────┘

🤖 AI-Generated Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This repository implements a modern web application
framework with clean architecture and comprehensive
testing. Key features include...
```

## 🎯 Features

- **🤖 AI Analysis**: Get intelligent insights about repository purpose, architecture, and key features
- **📊 Language Stats**: Detailed breakdown of programming languages used
- **📁 Smart Filtering**: Automatically skips common directories (node_modules, dist, build)
- **⚡ Performance**: File limits and optimizations for fast analysis
- **🎨 Beautiful Output**: Rich terminal formatting with colors and tables
- **💾 Export Options**: Save results as JSON for further processing

## 🛠️ Development

Install with development dependencies:
```bash
pip install codesonor[dev]
```

Run tests:
```bash
pytest
```

## 📦 Web App Version

CodeSonor also comes with a Flask web application. To use it:

```bash
# Install with web dependencies
pip install codesonor[web]

# Clone the repository for web app files
git clone https://github.com/farhanmir/CodeSonor.git
cd CodeSonor

# Run the web server
python app.py
```

Visit `http://localhost:5000` in your browser.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Farhan Mir**

- GitHub: [@farhanmir](https://github.com/farhanmir)

## 🙏 Acknowledgments

- Powered by Google Gemini AI
- Built with Python, Click, and Rich
- GitHub REST API v3

---

**Note**: This tool analyzes public repositories. Ensure you have appropriate permissions before analyzing private repositories.
