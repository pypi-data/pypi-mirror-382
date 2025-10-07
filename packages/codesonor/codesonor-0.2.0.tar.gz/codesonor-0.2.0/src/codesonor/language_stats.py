"""Language statistics analyzer for repositories."""

import os
from collections import defaultdict
from typing import Dict, List


class LanguageAnalyzer:
    """Analyzer for calculating language distribution in repositories."""
    
    # Language extensions mapping
    LANGUAGE_EXTENSIONS = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.rs': 'Rust',
        '.html': 'HTML',
        '.css': 'CSS',
        '.jsx': 'React',
        '.tsx': 'TypeScript React',
        '.vue': 'Vue',
        '.sql': 'SQL',
        '.sh': 'Shell',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.md': 'Markdown',
    }
    
    @classmethod
    def calculate_stats(cls, files: List[Dict]) -> Dict[str, float]:
        """
        Calculate language distribution based on file extensions.
        
        Args:
            files: List of file dictionaries with 'name' and 'size' keys
            
        Returns:
            Dictionary mapping language names to percentage values
        """
        language_sizes = defaultdict(int)
        total_size = 0
        
        for file in files:
            ext = os.path.splitext(file['name'])[1].lower()
            if ext in cls.LANGUAGE_EXTENSIONS:
                language = cls.LANGUAGE_EXTENSIONS[ext]
                size = file['size']
                language_sizes[language] += size
                total_size += size
        
        # Convert to percentages
        language_stats = {}
        for language, size in language_sizes.items():
            if total_size > 0:
                percentage = (size / total_size) * 100
                language_stats[language] = round(percentage, 2)
        
        # Sort by percentage (descending)
        language_stats = dict(sorted(language_stats.items(), key=lambda x: x[1], reverse=True))
        
        return language_stats
    
    @classmethod
    def get_primary_language(cls, files: List[Dict]) -> str:
        """
        Get the primary (most used) language in the repository.
        
        Args:
            files: List of file dictionaries
            
        Returns:
            Name of the primary language or "Unknown"
        """
        stats = cls.calculate_stats(files)
        if stats:
            return list(stats.keys())[0]
        return "Unknown"
    
    @classmethod
    def filter_by_language(cls, files: List[Dict], language: str) -> List[Dict]:
        """
        Filter files by programming language.
        
        Args:
            files: List of file dictionaries
            language: Language name to filter by
            
        Returns:
            Filtered list of files
        """
        # Get all extensions for the specified language
        target_exts = [ext for ext, lang in cls.LANGUAGE_EXTENSIONS.items() if lang == language]
        
        filtered = []
        for file in files:
            ext = os.path.splitext(file['name'])[1].lower()
            if ext in target_exts:
                filtered.append(file)
        
        return filtered
