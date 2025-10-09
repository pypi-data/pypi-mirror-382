"""
Tests for the CLI interface.
"""

import pytest
from pathlib import Path
from unittest.mock import patch
from env_scanner.cli import create_parser, scan_command, list_command


@pytest.fixture
def test_project(tmp_path):
    """Create a test project for CLI testing."""
    (tmp_path / "app.py").write_text("""
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
API_KEY = os.environ['API_KEY']
DEBUG = os.getenv('DEBUG')
""")
    return tmp_path


class TestCLIParser:
    """Test CLI argument parsing."""
    
    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == 'env-scanner'
    
    def test_scan_command_defaults(self):
        """Test scan command with default arguments."""
        parser = create_parser()
        args = parser.parse_args(['scan'])
        
        assert args.command == 'scan'
        assert args.path == '.'
        assert args.output is None
        assert args.no_generate is False
    
    def test_scan_command_with_path(self):
        """Test scan command with custom path."""
        parser = create_parser()
        args = parser.parse_args(['scan', '/path/to/project'])
        
        assert args.command == 'scan'
        assert args.path == '/path/to/project'
    
    def test_scan_command_with_output(self):
        """Test scan command with custom output."""
        parser = create_parser()
        args = parser.parse_args(['scan', '--output', '.env.template'])
        
        assert args.output == '.env.template'
    
    def test_scan_command_with_exclude(self):
        """Test scan command with exclude directories."""
        parser = create_parser()
        args = parser.parse_args(['scan', '--exclude', 'venv,build,dist'])
        
        assert args.exclude == 'venv,build,dist'
    
    def test_scan_command_flags(self):
        """Test scan command with various flags."""
        parser = create_parser()
        
        # Test individual flags
        args = parser.parse_args(['scan', '--no-generate'])
        assert args.no_generate is True
        
        args = parser.parse_args(['scan', '--no-comments'])
        assert args.no_comments is True
        
        args = parser.parse_args(['scan', '--no-grouping'])
        assert args.no_grouping is True
        
        args = parser.parse_args(['scan', '--preview'])
        assert args.preview is True
    
    def test_list_command_defaults(self):
        """Test list command with defaults."""
        parser = create_parser()
        args = parser.parse_args(['list'])
        
        assert args.command == 'list'
        assert args.path == '.'
        assert args.show_locations is False
    
    def test_list_command_with_locations(self):
        """Test list command with show locations."""
        parser = create_parser()
        args = parser.parse_args(['list', '--show-locations'])
        
        assert args.show_locations is True
    
    def test_generate_command(self):
        """Test generate command (alias for scan)."""
        parser = create_parser()
        args = parser.parse_args(['generate'])
        
        assert args.command == 'generate'
    
    def test_version_flag(self):
        """Test version flag."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(['--version'])


class TestScanCommandExecution:
    """Test scan command execution."""
    
    def test_scan_command_basic(self, test_project):
        """Test basic scan command execution."""
        parser = create_parser()
        args = parser.parse_args(['scan', str(test_project), '--no-generate'])
        
        exit_code = scan_command(args)
        
        assert exit_code == 0
    
    def test_scan_command_with_generation(self, test_project):
        """Test scan command with file generation."""
        output_path = test_project / '.env-example'
        
        parser = create_parser()
        args = parser.parse_args([
            'scan',
            str(test_project),
            '--output', str(output_path)
        ])
        
        exit_code = scan_command(args)
        
        assert exit_code == 0
        assert output_path.exists()
        
        # Verify content
        content = output_path.read_text()
        assert 'DATABASE_URL' in content
        assert 'API_KEY' in content
        assert 'DEBUG' in content
    
    def test_scan_empty_project(self, tmp_path):
        """Test scanning empty project."""
        parser = create_parser()
        args = parser.parse_args(['scan', str(tmp_path)])
        
        exit_code = scan_command(args)
        
        assert exit_code == 0
    
    def test_scan_with_custom_exclude(self, tmp_path):
        """Test scan with custom exclude directories."""
        # Create files in different directories
        (tmp_path / "app.py").write_text("""
import os
MAIN_VAR = os.environ.get('MAIN_VAR')
""")
        
        excluded_dir = tmp_path / "excluded"
        excluded_dir.mkdir()
        (excluded_dir / "test.py").write_text("""
import os
EXCLUDED_VAR = os.environ.get('EXCLUDED_VAR')
""")
        
        parser = create_parser()
        args = parser.parse_args([
            'scan',
            str(tmp_path),
            '--exclude', 'excluded',
            '--output', str(tmp_path / '.env-example')
        ])
        
        exit_code = scan_command(args)
        
        assert exit_code == 0
        
        content = (tmp_path / '.env-example').read_text()
        assert 'MAIN_VAR' in content
        assert 'EXCLUDED_VAR' not in content


class TestListCommandExecution:
    """Test list command execution."""
    
    def test_list_command_basic(self, test_project, capsys):
        """Test basic list command."""
        parser = create_parser()
        args = parser.parse_args(['list', str(test_project)])
        
        exit_code = list_command(args)
        
        assert exit_code == 0
        
        captured = capsys.readouterr()
        assert 'DATABASE_URL' in captured.out
        assert 'API_KEY' in captured.out
        assert 'DEBUG' in captured.out
    
    def test_list_command_with_locations(self, test_project, capsys):
        """Test list command with location information."""
        parser = create_parser()
        args = parser.parse_args(['list', str(test_project), '--show-locations'])
        
        exit_code = list_command(args)
        
        assert exit_code == 0
        
        captured = capsys.readouterr()
        assert 'app.py' in captured.out
    
    def test_list_empty_project(self, tmp_path, capsys):
        """Test list command on empty project."""
        parser = create_parser()
        args = parser.parse_args(['list', str(tmp_path)])
        
        exit_code = list_command(args)
        
        assert exit_code == 0
        
        captured = capsys.readouterr()
        assert 'No environment variables found' in captured.out


class TestCLIOptions:
    """Test various CLI options and combinations."""
    
    def test_no_comments_option(self, test_project):
        """Test --no-comments option."""
        output_path = test_project / '.env-example'
        
        parser = create_parser()
        args = parser.parse_args([
            'scan',
            str(test_project),
            '--output', str(output_path),
            '--no-comments'
        ])
        
        scan_command(args)
        
        content = output_path.read_text()
        # Should have fewer or no comment lines (except header)
        assert 'DATABASE_URL=' in content
    
    def test_no_grouping_option(self, test_project):
        """Test --no-grouping option."""
        output_path = test_project / '.env-example'
        
        parser = create_parser()
        args = parser.parse_args([
            'scan',
            str(test_project),
            '--output', str(output_path),
            '--no-grouping'
        ])
        
        scan_command(args)
        
        content = output_path.read_text()
        assert 'DATABASE_URL=' in content
    
    def test_no_header_option(self, test_project):
        """Test --no-header option."""
        output_path = test_project / '.env-example'
        
        parser = create_parser()
        args = parser.parse_args([
            'scan',
            str(test_project),
            '--output', str(output_path),
            '--no-header'
        ])
        
        scan_command(args)
        
        content = output_path.read_text()
        assert 'Environment Variables Configuration' not in content
        assert 'DATABASE_URL=' in content
    
    def test_combined_options(self, test_project):
        """Test combination of multiple options."""
        output_path = test_project / '.env-example'
        
        parser = create_parser()
        args = parser.parse_args([
            'scan',
            str(test_project),
            '--output', str(output_path),
            '--no-header',
            '--no-comments',
            '--no-grouping'
        ])
        
        scan_command(args)
        
        assert output_path.exists()
        content = output_path.read_text()
        
        # Should still have variables
        assert 'DATABASE_URL=' in content
        assert 'API_KEY=' in content


class TestCLIPreview:
    """Test preview functionality."""
    
    @patch('builtins.input', return_value='n')
    def test_preview_cancel(self, mock_input, test_project):
        """Test preview with cancel."""
        output_path = test_project / '.env-example'
        
        parser = create_parser()
        args = parser.parse_args([
            'scan',
            str(test_project),
            '--output', str(output_path),
            '--preview'
        ])
        
        exit_code = scan_command(args)
        
        assert exit_code == 0
        assert not output_path.exists()  # Should not save
    
    @patch('builtins.input', return_value='y')
    def test_preview_accept(self, mock_input, test_project):
        """Test preview with accept."""
        output_path = test_project / '.env-example'
        
        parser = create_parser()
        args = parser.parse_args([
            'scan',
            str(test_project),
            '--output', str(output_path),
            '--preview'
        ])
        
        exit_code = scan_command(args)
        
        assert exit_code == 0
        assert output_path.exists()  # Should save


