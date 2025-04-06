"""
File Utilities Module.

Provides utilities for file collection, reading, and document ID management.
"""

import os
from typing import List, Dict, Set, Optional


class FileListCollector:
    """File list collector with filtering capabilities."""
    
    def __init__(self, file_extensions: Optional[List[str]] = None):
        """Initialize a file list collector.
        
        Args:
            file_extensions: List of file extensions to collect (e.g., ['.txt', '.html'])
        """
        self.file_extensions = file_extensions
        
    def collect_files(self, directory: str) -> List[str]:
        """Collect files from a directory.
        
        Args:
            directory: Directory path to collect files from
            
        Returns:
            List of file paths
        """
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
            
        file_list = []
        for root, _, files in os.walk(directory):
            for file in files:
                # Filter by extensions if specified
                if self.file_extensions:
                    if not any(file.endswith(ext) for ext in self.file_extensions):
                        continue
                        
                file_path = os.path.join(root, file)
                file_list.append(file_path)
                
        print(f"Collected {len(file_list)} files from {directory}")
        
        return file_list
        
    def assign_doc_ids(self, file_list: List[str]) -> Dict[str, int]:
        """Assign document IDs to files.
        
        Args:
            file_list: List of file paths
            
        Returns:
            Dictionary mapping file paths to document IDs
        """
        doc_id_mapping = {}
        for i, file_path in enumerate(sorted(file_list), 1):
            doc_id_mapping[file_path] = i
            
        print(f"Assigned IDs to {len(doc_id_mapping)} documents")
        
        return doc_id_mapping


class FileReader:
    """File reader with support for multiple formats."""
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """Read a file and return its contents.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File contents as string
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content
        except UnicodeDecodeError:
            # Fallback to Latin-1 encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
                return content
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """get the file size(bytes)

        Args:
            file_path: file path

        Returns:
            file size, return 0 if file doesn't exist
        """
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0 