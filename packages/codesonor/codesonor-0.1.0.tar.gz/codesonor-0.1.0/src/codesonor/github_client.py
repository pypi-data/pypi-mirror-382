"""GitHub API client for fetching repository information."""

import os
import requests
from typing import Optional, Dict, List


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub Personal Access Token (optional)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CodeSonor-CLI'
        }
        if self.token and self.token != 'your_github_token_here':
            headers['Authorization'] = f'token {self.token}'
        return headers
    
    def parse_url(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """
        Parse GitHub URL to extract owner and repo name.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo) or (None, None) if invalid
        """
        url = url.rstrip('/').replace('.git', '')
        
        if 'github.com' in url:
            parts = url.split('github.com/')[-1].split('/')
            if len(parts) >= 2:
                return parts[0], parts[1]
        
        return None, None
    
    def get_repository_info(self, owner: str, repo: str) -> Optional[Dict]:
        """
        Fetch repository information from GitHub.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository information dictionary or None if error
        """
        url = f'{self.base_url}/repos/{owner}/{repo}'
        
        try:
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 401:
                raise PermissionError(
                    "GitHub authentication required. Please set GITHUB_TOKEN environment variable. "
                    "Visit https://github.com/settings/tokens to create one with public_repo scope."
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repository info: {e}")
            return None
    
    def fetch_contents(self, owner: str, repo: str, path: str = '') -> Optional[List]:
        """
        Fetch contents of a directory in the repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within repository
            
        Returns:
            List of contents or None if error
        """
        url = f'{self.base_url}/repos/{owner}/{repo}/contents/{path}'
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching contents: {e}")
            return None
    
    def get_all_files(self, owner: str, repo: str, path: str = '', 
                     max_files: int = 500) -> List[Dict]:
        """
        Recursively get all files in the repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Starting path
            max_files: Maximum number of files to fetch
            
        Returns:
            List of file information dictionaries
        """
        files_list = []
        skip_dirs = ['node_modules', '.git', 'dist', 'build', '__pycache__', 'vendor', 'target']
        
        def _fetch_recursive(current_path: str = ''):
            if len(files_list) >= max_files:
                return
            
            contents = self.fetch_contents(owner, repo, current_path)
            if contents is None:
                return
            
            for item in contents:
                if len(files_list) >= max_files:
                    break
                
                if item['type'] == 'file':
                    files_list.append({
                        'name': item['name'],
                        'path': item['path'],
                        'size': item['size'],
                        'download_url': item.get('download_url')
                    })
                elif item['type'] == 'dir' and item['name'] not in skip_dirs:
                    _fetch_recursive(item['path'])
        
        _fetch_recursive(path)
        return files_list
    
    def get_file_content(self, url: str) -> Optional[str]:
        """
        Fetch the content of a file.
        
        Args:
            url: Download URL for the file
            
        Returns:
            File content as string or None if error
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching file content: {e}")
            return None
