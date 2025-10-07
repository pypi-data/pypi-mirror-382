"""Tests for CodeSonor package"""

import pytest
from codesonor.github_client import GitHubClient
from codesonor.language_stats import LanguageAnalyzer


class TestGitHubClient:
    """Tests for GitHub client functionality"""
    
    def test_parse_url_https(self):
        """Test parsing HTTPS GitHub URLs"""
        client = GitHubClient()
        
        # Test HTTPS URL
        owner, repo = client.parse_url("https://github.com/python/cpython")
        assert owner == "python"
        assert repo == "cpython"
        
        # Test with trailing slash and .git
        owner, repo = client.parse_url("https://github.com/python/cpython.git/")
        assert owner == "python"
        assert repo == "cpython"
    
    def test_parse_url_invalid(self):
        """Test parsing invalid URLs returns None"""
        client = GitHubClient()
        
        # Invalid URLs should return (None, None)
        owner, repo = client.parse_url("https://gitlab.com/user/repo")
        assert owner is None
        assert repo is None
        
        owner, repo = client.parse_url("not-a-url")
        assert owner is None
        assert repo is None


class TestLanguageAnalyzer:
    """Tests for language analysis functionality"""
    
    def test_language_extensions(self):
        """Test language extension mappings"""
        analyzer = LanguageAnalyzer()
        
        # Test various extensions
        assert analyzer.LANGUAGE_EXTENSIONS[".py"] == "Python"
        assert analyzer.LANGUAGE_EXTENSIONS[".js"] == "JavaScript"
        assert analyzer.LANGUAGE_EXTENSIONS[".java"] == "Java"
        assert analyzer.LANGUAGE_EXTENSIONS[".cpp"] == "C++"
    
    def test_calculate_stats(self):
        """Test language statistics calculation"""
        analyzer = LanguageAnalyzer()
        
        files = [
            {"name": "app.py", "path": "src/app.py", "size": 1000},
            {"name": "utils.py", "path": "src/utils.py", "size": 500},
            {"name": "script.js", "path": "static/script.js", "size": 300},
            {"name": "README.md", "path": "README.md", "size": 200},
        ]
        
        stats = analyzer.calculate_stats(files)
        
        assert "Python" in stats
        assert "JavaScript" in stats
        assert "Markdown" in stats
        # Python should be ~75% (1500/2000)
        assert stats["Python"] > 70
        assert stats["Python"] < 80
    
    def test_get_primary_language(self):
        """Test primary language detection"""
        analyzer = LanguageAnalyzer()
        
        files = [
            {"name": "main.py", "size": 1000},
            {"name": "test.py", "size": 500},
            {"name": "index.js", "size": 200},
        ]
        
        primary = analyzer.get_primary_language(files)
        assert primary == "Python"
    
    def test_filter_by_language(self):
        """Test filtering files by language"""
        analyzer = LanguageAnalyzer()
        
        files = [
            {"name": "app.py", "path": "src/app.py"},
            {"name": "utils.py", "path": "src/utils.py"},
            {"name": "script.js", "path": "static/script.js"},
        ]
        
        python_files = analyzer.filter_by_language(files, "Python")
        assert len(python_files) == 2
        assert all(f["name"].endswith(".py") for f in python_files)
        
        js_files = analyzer.filter_by_language(files, "JavaScript")
        assert len(js_files) == 1
        assert js_files[0]["name"] == "script.js"


class TestImports:
    """Test that all modules can be imported"""
    
    def test_import_github_client(self):
        """Test importing GitHubClient"""
        from codesonor import GitHubClient
        assert GitHubClient is not None
    
    def test_import_language_analyzer(self):
        """Test importing LanguageAnalyzer"""
        from codesonor import LanguageAnalyzer
        assert LanguageAnalyzer is not None
    
    def test_import_repository_analyzer(self):
        """Test importing RepositoryAnalyzer"""
        from codesonor import RepositoryAnalyzer
        assert RepositoryAnalyzer is not None
    
    def test_package_version(self):
        """Test that package has version"""
        import codesonor
        assert hasattr(codesonor, "__version__")
        assert codesonor.__version__ == "0.1.0"
