"""
Filesystem Data Models
Data structures for file and directory information
"""

from dataclasses import dataclass


@dataclass
class FileEntry:
    """Информация о файле или директории"""
    name: str
    path: str
    is_directory: bool
    size: int
    modified_time: str 