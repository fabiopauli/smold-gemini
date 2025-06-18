"""
LSTool for SmolD - Directory listing tool

This tool lists files and directories in a given path.
"""

import os
import fnmatch
from typing import List, Dict, Any, Optional, Set, Tuple

from smolagents import Tool
from .user_input_tool import user_input_tool

# Constants
MAX_FILES = 1000
TRUNCATED_MESSAGE = f"There are more than {MAX_FILES} files in the repository. Use the LS tool (passing a specific path), Bash tool, and other tools to explore nested directories. The first {MAX_FILES} files and directories are included below:\n\n"


class LSTool(Tool):
    """
    Lists files and directories in a given path (immediate contents only, non-recursive).
    """
    
    name = "LS"
    description = "Displays a directory’s contents—files and sub-directories—at the location specified by **path**. The **path** argument must be an absolute path (it cannot be relative). You may optionally supply an **ignore** parameter: an array of glob patterns that should be skipped. If you already know the directories you want to scan, the Glob and Grep tools are generally the better choice."
    inputs = {
        "path": {"type": "string", "description": "The absolute path to the directory to list (must be absolute, not relative)"},
        "ignore": {"type": "array", "description": "List of glob patterns to ignore", "items": {"type": "string"}, "nullable": True}
    }
    output_type = "string"
    
    def forward(self, path: str, ignore: Optional[List[str]] = None) -> str:
        """
        List files and directories in the given path.
        
        Args:
            path: The absolute path to the directory to list
            ignore: Optional list of glob patterns to ignore
            
        Returns:
            A tree-like representation of the directory contents
        """
        # Ensure path is absolute
        if not os.path.isabs(path):
            path = os.path.abspath(path)
            
        # Check if path exists and is a directory
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist"
        if not os.path.isdir(path):
            return f"Error: Path '{path}' is not a directory"
        
        # Safety check for root directory
        normalized_path = os.path.normpath(path)
        if normalized_path == '/' or normalized_path == os.path.sep:
            confirmation = user_input_tool.forward(
                "Warning: You are attempting to list the root directory (/), which may contain a large number of files and could be slow or overwhelming. "
                "This operation might also expose sensitive system information. "
                "Are you sure you want to proceed? (yes/no)"
            )
            if confirmation.lower() not in ['yes', 'y']:
                return "Operation cancelled by user. Root directory listing was not performed."
        
        # Get the list of immediate directory contents
        all_paths = self._list_directory(path, ignore or [])
        
        # Build tree structure from the paths
        tree = self._create_file_tree(all_paths)
        
        # Format the tree as a string
        tree_output = self._print_tree(tree, path)
        
        return tree_output 
        
    def _list_directory(self, initial_path: str, ignore_patterns: List[str]) -> List[str]:
        """
        Lists only the immediate contents of the directory (non-recursive).
        
        Args:
            initial_path: The starting directory path
            ignore_patterns: List of glob patterns to ignore
            
        Returns:
            List of relative paths (directories ending with /)
        """
        results = []
        
        try:
            # Get all entries in the directory
            entries = []
            for item in os.listdir(initial_path):
                item_path = os.path.join(initial_path, item)
                
                # Skip if this path should be filtered
                if self._should_skip(item_path, ignore_patterns):
                    continue
                    
                entries.append(item_path)
            
            # Sort entries alphabetically
            entries.sort()
            
            # Convert to relative paths
            for item_path in entries:
                # Get relative path and normalize separators
                rel_path = os.path.relpath(item_path, initial_path).replace(os.path.sep, '/')
                # Ensure directories end with /
                if os.path.isdir(item_path):
                    if not rel_path.endswith('/'):
                        rel_path += '/'
                results.append(rel_path)
                
        except (PermissionError, FileNotFoundError) as e:
            return [f"Error: Cannot access directory - {str(e)}"]
        
        return results
        
    def _should_skip(self, path: str, ignore_patterns: List[str]) -> bool:
        """
        Determines if a path should be skipped.
        
        Args:
            path: Path to check
            ignore_patterns: List of glob patterns to ignore
            
        Returns:
            True if the path should be skipped, False otherwise
        """
        basename = os.path.basename(path.rstrip(os.path.sep))
        
        # Skip hidden files and directories
        if basename.startswith('.') and basename != '.':
            return True
            
        # Skip __pycache__ directories
        if basename == '__pycache__' or '__pycache__/' in path.replace(os.path.sep, '/'):
            return True
            
        # Skip paths matching ignore patterns
        if any(fnmatch.fnmatch(path, pattern) for pattern in ignore_patterns):
            return True
            
        return False
    
    def _create_file_tree(self, sorted_paths: List[str]) -> List[Dict]:
        """
        Converts a flat list of paths into a simple tree structure (non-recursive listing).
        
        Args:
            sorted_paths: Alphabetically sorted list of relative paths
            
        Returns:
            List of tree nodes representing the immediate directory contents
        """
        root = []
        
        for path in sorted_paths:
            # For non-recursive listing, each path is just a direct child
            name = path.rstrip('/')
            is_directory = path.endswith('/')
            
            node = {
                'name': name,
                'path': path,
                'type': 'directory' if is_directory else 'file'
            }
            
            root.append(node)
        
        return root
    
    def _print_tree(self, tree: List[Dict], root_path: str, level: int = 0, prefix: str = '') -> str:
        """
        Formats a tree structure into a string representation (non-recursive listing).
        
        Args:
            tree: The tree structure to print
            root_path: The absolute path to the root directory
            level: Current indentation level (unused for non-recursive)
            prefix: Prefix string for indentation (unused for non-recursive)
            
        Returns:
            Formatted string representation of the directory contents
        """
        result = ""
        
        # Add absolute path header
        root_path = root_path.rstrip(os.path.sep) + '/'
        result += f"Contents of {root_path}:\n"
        
        if not tree:
            result += "  (empty directory)\n"
            return result
        
        # List files and directories separately for better readability
        directories = [node for node in tree if node['type'] == 'directory']
        files = [node for node in tree if node['type'] == 'file']
        
        # Show directories first
        if directories:
            result += f"\nDirectories ({len(directories)}):\n"
            for node in directories:
                result += f"  📁 {node['name']}/\n"
        
        # Then show files
        if files:
            result += f"\nFiles ({len(files)}):\n"
            for node in files:
                result += f"  📄 {node['name']}\n"
        
        return result


# Export the tool as an instance that can be directly used
ls_tool = LSTool()