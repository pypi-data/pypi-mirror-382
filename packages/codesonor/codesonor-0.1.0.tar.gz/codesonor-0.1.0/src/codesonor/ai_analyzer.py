"""AI-powered code analyzer using Gemini API."""

import os
from typing import Optional, List, Dict
import google.generativeai as genai


class AIAnalyzer:
    """AI-powered code analyzer using Google's Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI analyzer.
        
        Args:
            api_key: Gemini API key (optional, will use GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def is_available(self) -> bool:
        """Check if AI analysis is available."""
        return self.model is not None
    
    def generate_summary(self, code: str, filename: str) -> str:
        """
        Generate AI summary for code.
        
        Args:
            code: Source code content
            filename: Name of the file
            
        Returns:
            AI-generated summary or error message
        """
        if not self.is_available():
            return "AI summary not available. Please configure GEMINI_API_KEY."
        
        try:
            prompt = f"""Analyze this code file named '{filename}' and provide:
1. A brief summary (2-3 sentences) of what this code does
2. The main purpose/functionality
3. Key components or classes (if any)

Code:
```
{code[:3000]}
```

Provide a concise, professional summary."""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def analyze_key_files(self, files: List[Dict], github_client) -> List[Dict]:
        """
        Analyze key source code files with AI.
        
        Args:
            files: List of file dictionaries
            github_client: GitHubClient instance to fetch file content
            
        Returns:
            List of analysis results
        """
        if not self.is_available():
            return []
        
        priority_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.go', '.rb']
        
        # Filter and prioritize files
        key_files = []
        for file in files:
            ext = os.path.splitext(file['name'])[1].lower()
            if ext in priority_extensions and file['size'] < 50000:
                name_lower = file['name'].lower()
                if any(keyword in name_lower for keyword in ['main', 'index', 'app', 'server']):
                    key_files.insert(0, file)
                else:
                    key_files.append(file)
        
        # Analyze up to 3 key files
        analyses = []
        for file in key_files[:3]:
            if file.get('download_url'):
                content = github_client.get_file_content(file['download_url'])
                if content:
                    summary = self.generate_summary(content, file['name'])
                    analyses.append({
                        'file': file['path'],
                        'summary': summary
                    })
        
        return analyses
