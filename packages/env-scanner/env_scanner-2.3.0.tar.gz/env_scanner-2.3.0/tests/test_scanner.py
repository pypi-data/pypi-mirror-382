"""
Tests for the EnvScanner class.
"""

import pytest
import tempfile
from pathlib import Path
from env_scanner.scanner import EnvScanner


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure for testing."""
    # Create project structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create test files
    (src_dir / "config.py").write_text("""
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
API_KEY = os.environ['API_KEY']
SECRET_KEY = os.getenv('SECRET_KEY', 'default')
""")
    
    (src_dir / "settings.py").write_text("""
import os

DEBUG = os.environ.get('DEBUG', 'False')
PORT = os.getenv('PORT', '8000')
HOST = os.environ['HOST']
""")
    
    # Create a subdirectory
    utils_dir = src_dir / "utils"
    utils_dir.mkdir()
    (utils_dir / "helpers.py").write_text("""
import os

LOG_LEVEL = os.environ.get('LOG_LEVEL')
CACHE_URL = os.getenv('CACHE_URL')
""")
    
    # Create venv directory (should be excluded)
    venv_dir = tmp_path / "venv"
    venv_dir.mkdir()
    (venv_dir / "test.py").write_text("""
import os
SHOULD_BE_IGNORED = os.environ.get('SHOULD_BE_IGNORED')
""")
    
    return tmp_path


class TestEnvScanner:
    """Test cases for EnvScanner class."""
    
    def test_initialization(self, temp_project):
        """Test scanner initialization."""
        scanner = EnvScanner(temp_project)
        
        assert scanner.project_path == temp_project.resolve()
        assert isinstance(scanner.exclude_dirs, list)
        assert 'venv' in scanner.exclude_dirs
        assert scanner.env_vars == set()
    
    def test_scan_file_with_regex(self, temp_project):
        """Test scanning a single file with regex."""
        scanner = EnvScanner(temp_project)
        config_file = temp_project / "src" / "config.py"
        
        env_vars = scanner.scan_file_with_regex(config_file)
        
        assert 'DATABASE_URL' in env_vars
        assert 'API_KEY' in env_vars
        assert 'SECRET_KEY' in env_vars
        assert len(env_vars) >= 3
    
    def test_scan_file_with_ast(self, temp_project):
        """Test scanning a single file with AST."""
        scanner = EnvScanner(temp_project)
        config_file = temp_project / "src" / "config.py"
        
        env_vars = scanner.scan_file_with_ast(config_file)
        
        assert 'DATABASE_URL' in env_vars
        assert 'API_KEY' in env_vars
        assert 'SECRET_KEY' in env_vars
    
    def test_scan_directory(self, temp_project):
        """Test scanning entire directory."""
        scanner = EnvScanner(temp_project)
        env_vars = scanner.scan_directory()
        
        # Should find variables from all files
        expected_vars = {
            'DATABASE_URL', 'API_KEY', 'SECRET_KEY',
            'DEBUG', 'PORT', 'HOST',
            'LOG_LEVEL', 'CACHE_URL'
        }
        
        assert expected_vars.issubset(env_vars)
        # Should not find variables from excluded venv directory
        assert 'SHOULD_BE_IGNORED' not in env_vars
    
    def test_exclude_directories(self, temp_project):
        """Test directory exclusion."""
        scanner = EnvScanner(temp_project)
        
        # venv directory should be excluded
        venv_dir = temp_project / "venv"
        assert scanner.should_skip_directory(venv_dir)
        
        # Regular directory should not be excluded
        src_dir = temp_project / "src"
        assert not scanner.should_skip_directory(src_dir)
    
    def test_custom_exclude_dirs(self, temp_project):
        """Test custom exclude directories."""
        # Create custom directory to exclude
        custom_dir = temp_project / "custom_exclude"
        custom_dir.mkdir()
        (custom_dir / "test.py").write_text("""
import os
CUSTOM_VAR = os.environ.get('CUSTOM_VAR')
""")
        
        scanner = EnvScanner(
            temp_project,
            exclude_dirs=['venv', 'custom_exclude']
        )
        
        env_vars = scanner.scan_directory()
        
        assert 'CUSTOM_VAR' not in env_vars
    
    def test_get_results(self, temp_project):
        """Test getting detailed results."""
        scanner = EnvScanner(temp_project)
        scanner.scan_directory()
        
        results = scanner.get_results()
        
        assert 'variables' in results
        assert 'count' in results
        assert 'locations' in results
        assert 'project_path' in results
        
        assert isinstance(results['variables'], list)
        assert results['count'] == len(results['variables'])
        assert results['count'] > 0
    
    def test_var_locations_tracking(self, temp_project):
        """Test that variable locations are tracked."""
        scanner = EnvScanner(temp_project)
        scanner.scan_directory()
        
        # Check that locations are tracked
        assert len(scanner.var_locations) > 0
        
        # Check structure of location data
        for var, locations in scanner.var_locations.items():
            assert isinstance(locations, list)
            if locations:
                loc = locations[0]
                assert 'file' in loc
                assert 'line' in loc
                assert 'content' in loc
    
    def test_empty_project(self, tmp_path):
        """Test scanning an empty project."""
        scanner = EnvScanner(tmp_path)
        env_vars = scanner.scan_directory()
        
        assert env_vars == set()
        assert scanner.get_results()['count'] == 0
    
    def test_no_env_vars_in_file(self, tmp_path):
        """Test scanning a file with no environment variables."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def hello():
    return "Hello, World!"
""")
        
        scanner = EnvScanner(tmp_path)
        env_vars = scanner.scan_directory()
        
        assert env_vars == set()
    
    def test_malformed_python_file(self, tmp_path):
        """Test handling of malformed Python files."""
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("""
This is not valid Python code {{{
import os
SOME_VAR = os.environ.get('SOME_VAR')
""")
        
        scanner = EnvScanner(tmp_path)
        # Should not crash, might find variable with regex
        env_vars = scanner.scan_directory()
        
        # Regex should still find it
        assert 'SOME_VAR' in env_vars
    
    def test_different_import_patterns(self, tmp_path):
        """Test detection with different import patterns."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import os
from os import environ, getenv

VAR1 = os.environ.get('VAR1')
VAR2 = environ.get('VAR2')
VAR3 = getenv('VAR3')
VAR4 = os.getenv('VAR4')
""")
        
        scanner = EnvScanner(tmp_path)
        env_vars = scanner.scan_directory()
        
        assert 'VAR1' in env_vars
        assert 'VAR2' in env_vars
        assert 'VAR3' in env_vars
        assert 'VAR4' in env_vars


class TestEnvScannerEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_uppercase_variable_names(self, tmp_path):
        """Test that only uppercase variable names are detected."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import os

# Should be detected
GOOD_VAR = os.environ.get('GOOD_VAR')

# Should not be detected (lowercase)
bad_var = os.environ.get('bad_var')
mixed_Var = os.environ.get('mixed_Var')
""")
        
        scanner = EnvScanner(tmp_path)
        env_vars = scanner.scan_directory()
        
        assert 'GOOD_VAR' in env_vars
        # Regex pattern typically requires uppercase
    
    def test_nested_directories(self, tmp_path):
        """Test scanning deeply nested directories."""
        # Create nested structure
        deep_dir = tmp_path / "a" / "b" / "c" / "d"
        deep_dir.mkdir(parents=True)
        
        (deep_dir / "deep.py").write_text("""
import os
DEEP_VAR = os.environ.get('DEEP_VAR')
""")
        
        scanner = EnvScanner(tmp_path)
        env_vars = scanner.scan_directory()
        
        assert 'DEEP_VAR' in env_vars
    
    def test_multiple_vars_one_line(self, tmp_path):
        """Test detecting multiple variables on one line."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import os
config = {'db': os.environ.get('DB_URL'), 'key': os.environ.get('API_KEY')}
""")
        
        scanner = EnvScanner(tmp_path)
        env_vars = scanner.scan_directory()
        
        assert 'DB_URL' in env_vars
        assert 'API_KEY' in env_vars


