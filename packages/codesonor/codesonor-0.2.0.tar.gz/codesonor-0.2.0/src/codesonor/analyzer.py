"""Main repository analyzer combining all components."""

from typing import Optional, Dict
from datetime import datetime

from .github_client import GitHubClient
from .language_stats import LanguageAnalyzer
from .ai_analyzer import AIAnalyzer


class RepositoryAnalyzer:
    """Main analyzer for GitHub repositories."""
    
    def __init__(self, github_token: Optional[str] = None, gemini_key: Optional[str] = None):
        """
        Initialize repository analyzer.
        
        Args:
            github_token: GitHub Personal Access Token
            gemini_key: Gemini API key for AI analysis
        """
        self.github = GitHubClient(github_token)
        self.ai = AIAnalyzer(gemini_key)
        self.language_analyzer = LanguageAnalyzer()
    
    def analyze(self, repo_url: str, include_ai: bool = True, max_files: int = 500) -> Dict:
        """
        Analyze a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            include_ai: Whether to include AI analysis
            max_files: Maximum number of files to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        # Parse GitHub URL
        owner, repo = self.github.parse_url(repo_url)
        
        if not owner or not repo:
            raise ValueError(f"Invalid GitHub URL format: {repo_url}")
        
        # Get repository information
        repo_info = self.github.get_repository_info(owner, repo)
        if not repo_info:
            raise RuntimeError(f"Failed to fetch repository information for {owner}/{repo}")
        
        # Get all files
        files = self.github.get_all_files(owner, repo, max_files=max_files)
        
        if not files:
            raise RuntimeError("Could not fetch repository files")
        
        # Calculate language statistics
        language_stats = self.language_analyzer.calculate_stats(files)
        
        # AI analysis (optional)
        ai_analyses = []
        if include_ai and self.ai.is_available():
            ai_analyses = self.ai.analyze_key_files(files, self.github)
        
        # Compile results
        result = {
            'repository': {
                'name': repo_info['name'],
                'owner': repo_info['owner']['login'],
                'description': repo_info.get('description', 'No description available'),
                'stars': repo_info['stargazers_count'],
                'forks': repo_info['forks_count'],
                'url': repo_info['html_url'],
                'created_at': repo_info['created_at'],
                'updated_at': repo_info['updated_at'],
                'primary_language': repo_info.get('language', 'Unknown')
            },
            'statistics': {
                'total_files': len(files),
                'language_distribution': language_stats,
                'primary_language': self.language_analyzer.get_primary_language(files)
            },
            'ai_analysis': ai_analyses if include_ai else [],
            'files': files[:50]  # First 50 files
        }
        
        return result
    
    def get_summary(self, repo_url: str) -> str:
        """
        Get a brief text summary of the repository.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Human-readable summary string
        """
        result = self.analyze(repo_url, include_ai=False)
        
        repo = result['repository']
        stats = result['statistics']
        
        summary_lines = [
            f"\n{'='*60}",
            f"Repository: {repo['name']} by {repo['owner']}",
            f"{'='*60}",
            f"Description: {repo['description']}",
            f"Stars: {repo['stars']:,} | Forks: {repo['forks']:,}",
            f"URL: {repo['url']}",
            f"\nStatistics:",
            f"  Total Files: {stats['total_files']:,}",
            f"  Primary Language: {stats['primary_language']}",
            f"\nLanguage Distribution:"
        ]
        
        for lang, pct in list(stats['language_distribution'].items())[:5]:
            summary_lines.append(f"  {lang:20} {pct:6.2f}%")
        
        summary_lines.append(f"{'='*60}\n")
        
        return '\n'.join(summary_lines)
