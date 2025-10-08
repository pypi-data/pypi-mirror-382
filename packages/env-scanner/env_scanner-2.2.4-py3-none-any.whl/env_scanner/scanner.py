"""
Environment variable scanner for Python projects.

This module scans Python files to detect environment variable usage patterns.
"""

import ast
import os
import re
from pathlib import Path
from typing import Set, List, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)


class EnvScanner:
    """
    Scanner to detect environment variables used in Python code.
    
    Detects patterns like:
    - os.environ.get('VAR_NAME')
    - os.environ['VAR_NAME']
    - os.getenv('VAR_NAME')
    - And various other patterns
    """
    
    # Common environment variable access patterns
    ENV_PATTERNS = [
        r'os\.environ\.get\(["\']([A-Z_][A-Z0-9_]*)["\']',
        r'os\.environ\[["\']([A-Z_][A-Z0-9_]*)["\']\]',
        r'os\.getenv\(["\']([A-Z_][A-Z0-9_]*)["\']',
        r'environ\.get\(["\']([A-Z_][A-Z0-9_]*)["\']',
        r'environ\[["\']([A-Z_][A-Z0-9_]*)["\']\]',
        r'getenv\(["\']([A-Z_][A-Z0-9_]*)["\']',
    ]
    
    def __init__(
        self,
        project_path: Union[str, Path],
        exclude_dirs: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None
    ):
        """
        Initialize the environment scanner.
        
        Args:
            project_path: Root path of the Python project to scan
            exclude_dirs: List of directory names to exclude (e.g., ['venv', 'node_modules'])
            include_patterns: Additional regex patterns to detect env variables
        """
        self.project_path = Path(project_path).resolve()
        self.exclude_dirs = exclude_dirs or [
            'venv', 'env', '.venv', '.env',
            'node_modules', '__pycache__', '.git',
            'dist', 'build', '*.egg-info', '.tox',
            '.pytest_cache', '.mypy_cache'
        ]
        self.env_vars: Set[str] = set()
        self.var_locations: Dict[str, List[Dict[str, Union[str, int]]]] = {}
        
        # Compile regex patterns
        self.patterns = [re.compile(pattern) for pattern in self.ENV_PATTERNS]
        if include_patterns:
            self.patterns.extend([re.compile(p) for p in include_patterns])
    
    def should_skip_directory(self, directory: Path) -> bool:
        """
        Check if a directory should be skipped during scanning.
        
        Args:
            directory: Directory path to check
            
        Returns:
            True if directory should be skipped
        """
        dir_name = directory.name
        
        # Check exclude patterns
        for exclude_pattern in self.exclude_dirs:
            if exclude_pattern.startswith('*'):
                # Wildcard pattern
                if dir_name.endswith(exclude_pattern[1:]):
                    return True
            else:
                # Exact match
                if dir_name == exclude_pattern or dir_name.startswith('.') and exclude_pattern.startswith('.'):
                    return True
        
        return False
    
    def scan_file_with_regex(self, file_path: Path) -> Set[str]:
        """
        Scan a Python file for environment variables using regex patterns.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Set of environment variable names found
        """
        env_vars = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply all regex patterns
            for pattern in self.patterns:
                matches = pattern.findall(content)
                env_vars.update(matches)
            
            # Track locations for each variable
            if env_vars:
                lines = content.split('\n')
                for var in env_vars:
                    for line_num, line in enumerate(lines, 1):
                        if var in line:
                            if var not in self.var_locations:
                                self.var_locations[var] = []
                            self.var_locations[var].append({
                                'file': str(file_path.relative_to(self.project_path)),
                                'line': line_num,
                                'content': line.strip()
                            })
        
        except Exception as e:
            logger.warning(f"Error scanning file {file_path}: {e}")
        
        return env_vars
    
    def scan_file_with_ast(self, file_path: Path) -> Set[str]:
        """
        Scan a Python file for environment variables using AST parsing.
        
        This method is more accurate but may miss some dynamic patterns.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Set of environment variable names found
        """
        env_vars = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                # os.environ.get('VAR') or os.environ['VAR']
                if isinstance(node, ast.Subscript):
                    if self._is_environ_access(node.value):
                        if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                            env_vars.add(node.slice.value)
                
                # os.environ.get('VAR') or os.getenv('VAR')
                elif isinstance(node, ast.Call):
                    if self._is_environ_get_call(node) or self._is_getenv_call(node):
                        if node.args and isinstance(node.args[0], ast.Constant):
                            if isinstance(node.args[0].value, str):
                                env_vars.add(node.args[0].value)
        
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error parsing {file_path} with AST: {e}")
        
        return env_vars
    
    def _is_environ_access(self, node: ast.AST) -> bool:
        """Check if node represents os.environ access."""
        return (
            isinstance(node, ast.Attribute) and
            node.attr == 'environ' and
            isinstance(node.value, ast.Name) and
            node.value.id == 'os'
        )
    
    def _is_environ_get_call(self, node: ast.Call) -> bool:
        """Check if node represents os.environ.get() call."""
        return (
            isinstance(node.func, ast.Attribute) and
            node.func.attr == 'get' and
            self._is_environ_access(node.func.value)
        )
    
    def _is_getenv_call(self, node: ast.Call) -> bool:
        """Check if node represents os.getenv() call."""
        return (
            isinstance(node.func, ast.Attribute) and
            node.func.attr == 'getenv' and
            isinstance(node.func.value, ast.Name) and
            node.func.value.id == 'os'
        )
    
    def scan_file(self, file_path: Path, use_ast: bool = True) -> Set[str]:
        """
        Scan a single Python file for environment variables.
        
        Args:
            file_path: Path to the Python file
            use_ast: Whether to use AST parsing (more accurate) or regex (more permissive)
            
        Returns:
            Set of environment variable names found
        """
        logger.info(f"Scanning file: {file_path}")
        
        if use_ast:
            # Use AST for more accurate parsing
            ast_vars = self.scan_file_with_ast(file_path)
            # Also use regex to catch edge cases
            regex_vars = self.scan_file_with_regex(file_path)
            return ast_vars | regex_vars
        else:
            return self.scan_file_with_regex(file_path)
    
    def scan_directory(self, use_ast: bool = True) -> Set[str]:
        """
        Recursively scan a directory for Python files and collect environment variables.
        
        Args:
            use_ast: Whether to use AST parsing in addition to regex
            
        Returns:
            Set of all environment variable names found
        """
        logger.info(f"Scanning directory: {self.project_path}")
        
        python_files = []
        
        # Find all Python files
        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)
            
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self.should_skip_directory(root_path / d)]
            
            # Process Python files
            for file in files:
                if file.endswith('.py'):
                    python_files.append(root_path / file)
        
        logger.info(f"Found {len(python_files)} Python files to scan")
        
        # Scan each file
        for file_path in python_files:
            file_vars = self.scan_file(file_path, use_ast=use_ast)
            self.env_vars.update(file_vars)
        
        logger.info(f"Found {len(self.env_vars)} unique environment variables")
        
        return self.env_vars
    
    def get_results(self) -> Dict[str, any]:
        """
        Get detailed scan results.
        
        Returns:
            Dictionary containing environment variables and their locations
        """
        return {
            'variables': sorted(list(self.env_vars)),
            'count': len(self.env_vars),
            'locations': self.var_locations,
            'project_path': str(self.project_path)
        }
    
    def print_summary(self) -> None:
        """Print a summary of the scan results."""
        print(f"\n{'='*60}")
        print(f"Environment Variable Scan Summary")
        print(f"{'='*60}")
        print(f"Project: {self.project_path}")
        print(f"Found {len(self.env_vars)} environment variables:\n")
        
        for var in sorted(self.env_vars):
            print(f"  - {var}")
            if var in self.var_locations:
                locations = self.var_locations[var]
                print(f"    Used in {len(locations)} location(s):")
                for loc in locations[:3]:  # Show first 3 locations
                    print(f"      {loc['file']}:{loc['line']}")
                if len(locations) > 3:
                    print(f"      ... and {len(locations) - 3} more")
        
        print(f"\n{'='*60}\n")


