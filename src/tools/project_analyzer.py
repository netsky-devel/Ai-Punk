"""
Project Analyzer Tool
Automatically analyzes and understands project structure and purpose
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from .base import BaseTool
from .semantic_search import SemanticSearchTool


class ProjectAnalyzer(BaseTool):
    """Tool for analyzing and understanding project structure"""
    
    def __init__(self, workspace_path: str):
        super().__init__("project_analyzer", "Анализ структуры и назначения проекта")
        self.workspace_path = Path(workspace_path)
        self.semantic_search = SemanticSearchTool(workspace_path)
        
    def _find_main_files(self) -> List[Path]:
        """Find main project files (README, main.py, package.json, etc.)"""
        important_files = []
        
        # Documentation files
        for pattern in ['README*', 'readme*', 'README.*', 'readme.*']:
            important_files.extend(self.workspace_path.glob(pattern))
            
        # Main entry points
        entry_patterns = [
            'main.py', 'app.py', 'index.py', '__init__.py',
            'package.json', 'setup.py', 'pyproject.toml',
            'Cargo.toml', 'go.mod', 'pom.xml'
        ]
        
        for pattern in entry_patterns:
            file_path = self.workspace_path / pattern
            if file_path.exists():
                important_files.append(file_path)
                
        return important_files
    
    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze file and directory structure"""
        structure = {
            "total_files": 0,
            "code_files": 0,
            "directories": 0,
            "languages": set(),
            "frameworks": set(),
            "main_directories": []
        }
        
        # Language detection patterns
        lang_patterns = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.cs': 'C#'
        }
        
        # Framework detection patterns
        framework_files = {
            'package.json': ['Node.js'],
            'requirements.txt': ['Python'],
            'Pipfile': ['Python', 'Pipenv'],
            'Cargo.toml': ['Rust'],
            'go.mod': ['Go'],
            'pom.xml': ['Java', 'Maven'],
            'build.gradle': ['Java', 'Gradle'],
        }
        
        for item in self.workspace_path.rglob('*'):
            if item.is_file():
                structure["total_files"] += 1
                
                # Language detection
                suffix = item.suffix.lower()
                if suffix in lang_patterns:
                    structure["languages"].add(lang_patterns[suffix])
                    structure["code_files"] += 1
                
                # Framework detection
                if item.name in framework_files:
                    structure["frameworks"].update(framework_files[item.name])
                    
            elif item.is_dir() and not any(part.startswith('.') for part in item.parts):
                structure["directories"] += 1
                
                # Main directories (immediate subdirs of root)
                if item.parent == self.workspace_path:
                    structure["main_directories"].append(item.name)
        
        return structure
    
    def _read_file_safely(self, file_path: Path, max_lines: int = 50) -> str:
        """Read file content safely with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > max_lines:
                    content = ''.join(lines[:max_lines]) + f"\n... (файл содержит ещё {len(lines) - max_lines} строк)"
                else:
                    content = ''.join(lines)
                return content
        except Exception as e:
            return f"Ошибка чтения файла: {e}"
    
    def _extract_project_info(self) -> Dict[str, Any]:
        """Extract project information from main files"""
        info = {
            "name": self.workspace_path.name,
            "description": "",
            "purpose": "",
            "technologies": [],
            "entry_points": [],
            "documentation": ""
        }
        
        main_files = self._find_main_files()
        
        for file_path in main_files:
            content = self._read_file_safely(file_path)
            filename = file_path.name.lower()
            
            # README analysis
            if 'readme' in filename:
                info["documentation"] = content
                # Extract description from first few lines
                lines = content.split('\n')
                for line in lines[:10]:
                    if line.strip() and not line.startswith('#'):
                        if len(line) > 20 and not info["description"]:
                            info["description"] = line.strip()
                            break
            
            # Package.json analysis
            elif filename == 'package.json':
                try:
                    import json
                    data = json.loads(content)
                    info["name"] = data.get("name", info["name"])
                    info["description"] = data.get("description", info["description"])
                    if "scripts" in data:
                        info["entry_points"].extend(data["scripts"].keys())
                except:
                    pass
            
            # Python setup files
            elif filename in ['setup.py', 'pyproject.toml']:
                if 'name' in content and not info["description"]:
                    # Try to extract description from setup.py
                    desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
                    if desc_match:
                        info["description"] = desc_match.group(1)
        
        return info
    
    def analyze_project(self) -> Dict[str, Any]:
        """Perform comprehensive project analysis"""
        try:
            print("🔍 Анализирую структуру проекта...")
            
            # Basic structure analysis
            structure = self._analyze_file_structure()
            
            # Project information extraction
            project_info = self._extract_project_info()
            
            # Initialize semantic search (this will index the codebase)
            print("🧠 Создаю семантический индекс кодовой базы...")
            semantic_result = self.semantic_search.index_codebase()
            
            # Combine results
            analysis = {
                "project_info": project_info,
                "structure": {
                    "total_files": structure["total_files"],
                    "code_files": structure["code_files"],
                    "directories": structure["directories"],
                    "languages": list(structure["languages"]),
                    "frameworks": list(structure["frameworks"]),
                    "main_directories": structure["main_directories"]
                },
                "semantic_index": semantic_result,
                "summary": self._generate_summary(project_info, structure)
            }
            
            return self._format_success("Проект проанализирован успешно", analysis)
            
        except Exception as e:
            return self._format_error(f"Ошибка анализа проекта: {str(e)}")
    
    def _generate_summary(self, project_info: Dict, structure: Dict) -> str:
        """Generate human-readable project summary"""
        summary_parts = []
        
        # Project name and description
        name = project_info.get("name", "Неизвестный проект")
        desc = project_info.get("description", "")
        summary_parts.append(f"📋 Проект: {name}")
        if desc:
            summary_parts.append(f"📝 Описание: {desc}")
        
        # Languages and technologies
        if structure["languages"]:
            langs = ", ".join(structure["languages"])
            summary_parts.append(f"💻 Языки программирования: {langs}")
        
        if structure["frameworks"]:
            frameworks = ", ".join(structure["frameworks"])
            summary_parts.append(f"🔧 Технологии: {frameworks}")
        
        # Structure info
        summary_parts.append(f"📊 Структура: {structure['code_files']} файлов кода, {structure['directories']} директорий")
        
        if structure["main_directories"]:
            dirs = ", ".join(structure["main_directories"])
            summary_parts.append(f"📁 Основные директории: {dirs}")
        
        return "\n".join(summary_parts)
    
    def execute(self) -> Dict[str, Any]:
        """Execute project analysis"""
        return self.analyze_project()


def create_project_analyzer(workspace_path: str) -> ProjectAnalyzer:
    """Factory function to create project analyzer"""
    return ProjectAnalyzer(workspace_path) 