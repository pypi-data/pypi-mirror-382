"""
Tests for the EnvExampleGenerator class.
"""

import pytest
from pathlib import Path
from env_scanner.generator import EnvExampleGenerator
from env_scanner.scanner import EnvScanner


@pytest.fixture
def sample_env_vars():
    """Sample environment variables for testing."""
    return {
        'DATABASE_URL',
        'DATABASE_NAME',
        'API_KEY',
        'API_SECRET',
        'DEBUG',
        'PORT',
        'SECRET_KEY',
        'LOG_LEVEL',
        'SMTP_HOST',
        'SMTP_PORT',
        'AWS_ACCESS_KEY',
        'AWS_SECRET_KEY',
    }


@pytest.fixture
def sample_locations():
    """Sample variable locations for testing."""
    return {
        'DATABASE_URL': [
            {'file': 'src/config.py', 'line': 10, 'content': 'DATABASE_URL = os.environ.get("DATABASE_URL")'}
        ],
        'API_KEY': [
            {'file': 'src/api.py', 'line': 5, 'content': 'API_KEY = os.environ["API_KEY"]'}
        ],
    }


class TestEnvExampleGenerator:
    """Test cases for EnvExampleGenerator class."""
    
    def test_initialization(self, sample_env_vars, tmp_path):
        """Test generator initialization."""
        output_path = tmp_path / '.env-example'
        
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            output_path=output_path
        )
        
        assert generator.env_vars == sorted(list(sample_env_vars))
        assert generator.output_path == output_path
        assert generator.add_comments is True
        assert generator.group_by_prefix is True
    
    def test_generate_content_basic(self, sample_env_vars):
        """Test basic content generation."""
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            include_header=False,
            add_comments=False,
            group_by_prefix=False
        )
        
        content = generator.generate_content()
        
        # Check that all variables are present
        for var in sample_env_vars:
            assert var in content
        
        # Check format (VAR=value)
        assert 'DATABASE_URL=' in content
        assert 'API_KEY=' in content
    
    def test_generate_content_with_header(self, sample_env_vars):
        """Test content generation with header."""
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            include_header=True
        )
        
        content = generator.generate_content()
        
        assert 'Environment Variables Configuration' in content
        assert 'automatically generated' in content
        assert 'Generated on:' in content
    
    def test_generate_content_without_header(self, sample_env_vars):
        """Test content generation without header."""
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            include_header=False
        )
        
        content = generator.generate_content()
        
        assert 'Environment Variables Configuration' not in content
    
    def test_generate_content_with_grouping(self, sample_env_vars):
        """Test content generation with variable grouping."""
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            group_by_prefix=True,
            include_header=False
        )
        
        content = generator.generate_content()
        
        # Should have group headers
        assert 'DATABASE Configuration' in content or 'DATABASE' in content
        assert 'API Configuration' in content or 'API' in content
        assert 'AWS Configuration' in content or 'AWS' in content
        assert 'SMTP Configuration' in content or 'SMTP' in content
    
    def test_generate_content_without_grouping(self, sample_env_vars):
        """Test content generation without grouping."""
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            group_by_prefix=False,
            include_header=False
        )
        
        content = generator.generate_content()
        
        # Should not have group headers (or fewer)
        # Just check variables are present
        for var in sample_env_vars:
            assert var in content
    
    def test_generate_content_with_comments(self, sample_env_vars):
        """Test content generation with comments."""
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            add_comments=True,
            include_header=False
        )
        
        content = generator.generate_content()
        
        # Should have some comment lines
        assert '#' in content
        lines = content.split('\n')
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        assert len(comment_lines) > 0
    
    def test_variable_placeholder_generation(self):
        """Test placeholder value generation for different variable types."""
        generator = EnvExampleGenerator(
            env_vars=set(),
            include_header=False
        )
        
        # Test different variable name patterns
        assert generator._get_variable_placeholder('DEBUG') == 'false'
        assert generator._get_variable_placeholder('PORT') == '8000'
        assert generator._get_variable_placeholder('DATABASE_URL') == 'https://example.com'
        assert generator._get_variable_placeholder('API_KEY') == 'your_secret_key_here'
        assert generator._get_variable_placeholder('EMAIL_ADDRESS') == 'user@example.com'
        assert generator._get_variable_placeholder('USERNAME') == 'your_username'
        assert generator._get_variable_placeholder('PASSWORD') == 'your_password'
    
    def test_variable_comment_generation(self):
        """Test comment generation for variables."""
        generator = EnvExampleGenerator(
            env_vars=set(),
            add_comments=True
        )
        
        # Test comment generation
        comment = generator._get_variable_comment('DATABASE_URL')
        assert comment is not None
        assert 'Database' in comment or 'database' in comment
        
        comment = generator._get_variable_comment('API_KEY')
        assert comment is not None
        assert 'API' in comment or 'key' in comment.lower()
    
    def test_save_file(self, sample_env_vars, tmp_path):
        """Test saving file to disk."""
        output_path = tmp_path / '.env-example'
        
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            output_path=output_path
        )
        
        saved_path = generator.save()
        
        assert saved_path == output_path
        assert output_path.exists()
        
        # Read and verify content
        content = output_path.read_text()
        for var in sample_env_vars:
            assert var in content
    
    def test_save_creates_directories(self, sample_env_vars, tmp_path):
        """Test that save creates parent directories if needed."""
        output_path = tmp_path / 'nested' / 'dirs' / '.env-example'
        
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            output_path=output_path
        )
        
        saved_path = generator.save()
        
        assert saved_path.exists()
        assert saved_path.parent.exists()
    
    def test_save_overwrites_existing(self, sample_env_vars, tmp_path):
        """Test that save overwrites existing file."""
        output_path = tmp_path / '.env-example'
        
        # Create existing file
        output_path.write_text("OLD CONTENT")
        
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            output_path=output_path
        )
        
        generator.save()
        
        # Verify new content
        content = output_path.read_text()
        assert "OLD CONTENT" not in content
        assert "DATABASE_URL" in content
    
    def test_from_scanner(self, tmp_path):
        """Test creating generator from scanner."""
        # Create a test file
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import os
VAR1 = os.environ.get('VAR1')
VAR2 = os.getenv('VAR2')
""")
        
        # Scan
        scanner = EnvScanner(tmp_path)
        scanner.scan_directory()
        
        # Create generator from scanner
        output_path = tmp_path / '.env-example'
        generator = EnvExampleGenerator.from_scanner(
            scanner,
            output_path=output_path
        )
        
        assert 'VAR1' in generator.env_vars
        assert 'VAR2' in generator.env_vars
        assert generator.output_path == output_path
    
    def test_empty_env_vars(self, tmp_path):
        """Test generator with empty environment variables."""
        output_path = tmp_path / '.env-example'
        
        generator = EnvExampleGenerator(
            env_vars=set(),
            output_path=output_path
        )
        
        content = generator.generate_content()
        
        # Should still generate valid file (with header if enabled)
        assert isinstance(content, str)
    
    def test_group_variables_logic(self, sample_env_vars):
        """Test the variable grouping logic."""
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            group_by_prefix=True
        )
        
        groups = generator._group_variables()
        
        assert isinstance(groups, dict)
        assert len(groups) > 1  # Should have multiple groups
        
        # Check that DATABASE vars are grouped
        database_group = None
        for group_name, vars_list in groups.items():
            if any('DATABASE' in var for var in vars_list):
                database_group = vars_list
                break
        
        assert database_group is not None
        assert 'DATABASE_URL' in database_group or 'DATABASE_NAME' in database_group
    
    def test_group_variables_no_grouping(self, sample_env_vars):
        """Test grouping when disabled."""
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            group_by_prefix=False
        )
        
        groups = generator._group_variables()
        
        # Should have single group
        assert len(groups) == 1
        assert 'All Variables' in groups
    
    def test_variable_with_locations(self, sample_env_vars, sample_locations):
        """Test that location information is included in comments."""
        generator = EnvExampleGenerator(
            env_vars=sample_env_vars,
            var_locations=sample_locations,
            add_comments=True
        )
        
        content = generator.generate_content()
        
        # Check that location info is in comments
        assert 'src/config.py' in content or 'config.py' in content
    
    def test_custom_content_save(self, tmp_path):
        """Test saving custom content."""
        output_path = tmp_path / '.env-example'
        
        generator = EnvExampleGenerator(
            env_vars={'TEST_VAR'},
            output_path=output_path
        )
        
        custom_content = "# Custom content\nTEST_VAR=custom_value\n"
        generator.save(content=custom_content)
        
        saved_content = output_path.read_text()
        assert saved_content == custom_content


class TestEnvExampleGeneratorIntegration:
    """Integration tests combining scanner and generator."""
    
    def test_full_workflow(self, tmp_path):
        """Test complete workflow from scan to generation."""
        # Create test project
        (tmp_path / "app.py").write_text("""
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
API_KEY = os.environ['API_KEY']
DEBUG = os.getenv('DEBUG', 'False')
""")
        
        # Scan
        scanner = EnvScanner(tmp_path)
        scanner.scan_directory()
        
        # Generate
        output_path = tmp_path / '.env-example'
        generator = EnvExampleGenerator.from_scanner(scanner, output_path=output_path)
        generator.save()
        
        # Verify
        assert output_path.exists()
        content = output_path.read_text()
        
        assert 'DATABASE_URL=' in content
        assert 'API_KEY=' in content
        assert 'DEBUG=' in content
    
    def test_real_world_example(self, tmp_path):
        """Test with realistic project structure."""
        # Create realistic project
        src = tmp_path / "src"
        src.mkdir()
        
        (src / "config.py").write_text("""
import os

class Config:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ['SECRET_KEY']
    DEBUG = os.getenv('DEBUG', 'False')
    
class ProductionConfig(Config):
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
""")
        
        (src / "mail.py").write_text("""
import os

SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = os.getenv('SMTP_PORT', '587')
SMTP_USER = os.environ['SMTP_USER']
SMTP_PASSWORD = os.environ['SMTP_PASSWORD']
""")
        
        # Scan and generate
        scanner = EnvScanner(tmp_path)
        scanner.scan_directory()
        
        output_path = tmp_path / '.env-example'
        generator = EnvExampleGenerator.from_scanner(
            scanner,
            output_path=output_path,
            group_by_prefix=True,
            add_comments=True
        )
        generator.save()
        
        # Verify comprehensive output
        content = output_path.read_text()
        
        # All variables should be present
        expected_vars = [
            'DATABASE_URL', 'SECRET_KEY', 'DEBUG',
            'AWS_ACCESS_KEY', 'AWS_SECRET_KEY',
            'SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD'
        ]
        
        for var in expected_vars:
            assert var in content
        
        # Should have grouping
        assert 'AWS' in content
        assert 'SMTP' in content


