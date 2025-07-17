"""
Semantic Code Search Tool
Uses free sentence transformers for intelligent code search by meaning
"""

import os
import pickle
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

from .base import BaseTool


@dataclass
class CodeChunk:
    """Represents a piece of code with metadata"""
    file_path: str
    start_line: int
    end_line: int
    content: str
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    chunk_type: str = "code"  # code, function, class, comment


class SemanticSearchTool(BaseTool):
    """Tool for semantic search through codebase"""
    
    def __init__(self, workspace_path: str):
        super().__init__("semantic_search", "Семантический поиск по кодовой базе")
        self.workspace_path = Path(workspace_path)
        self.cache_dir = self.workspace_path / ".ai-punk-cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Files to index
        self.code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb'}
        self.doc_extensions = {'.md', '.txt', '.rst', '.org'}
        
        # Model and index
        self.model = None
        self.index = None
        self.chunks = []
        self.is_initialized = False
        
    def _check_dependencies(self):
        """Check if required dependencies are available"""
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(
                "Для семантического поиска нужно установить:\n"
                "pip install sentence-transformers faiss-cpu"
            )
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        if self.model is None:
            self._check_dependencies()
            print("🤖 Загружаю модель для семантического поиска...")
            # Use free, lightweight model optimized for code
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Модель загружена!")
    
    def _get_cache_key(self) -> str:
        """Generate cache key based on codebase content"""
        # Get modification times of all relevant files
        file_times = []
        for ext in self.code_extensions | self.doc_extensions:
            for file_path in self.workspace_path.rglob(f"*{ext}"):
                if self._should_index_file(file_path):
                    file_times.append(f"{file_path}:{file_path.stat().st_mtime}")
        
        # Create hash from all file modification times
        content = "\n".join(sorted(file_times))
        return hashlib.md5(content.encode()).hexdigest()
    
    def _should_index_file(self, file_path: Path) -> bool:
        """Check if file should be indexed"""
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            # But allow .ai-punk-cache
            if '.ai-punk-cache' not in str(file_path):
                return False
        
        # Skip large files (>1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return False
        except:
            return False
            
        # Skip binary files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(100)  # Try to read first 100 chars
        except:
            return False
            
        return True
    
    def _extract_code_chunks(self, file_path: Path) -> List[CodeChunk]:
        """Extract meaningful code chunks from a file"""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            return chunks
        
        rel_path = str(file_path.relative_to(self.workspace_path))
        
        # Simple chunking strategy
        current_chunk = []
        start_line = 1
        
        for i, line in enumerate(lines, 1):
            current_chunk.append(line.rstrip())
            
            # Create chunk on empty line or every 20 lines
            if (not line.strip() and current_chunk) or len(current_chunk) >= 20:
                if current_chunk and any(line.strip() for line in current_chunk):
                    content = '\n'.join(current_chunk)
                    chunks.append(CodeChunk(
                        file_path=rel_path,
                        start_line=start_line,
                        end_line=i,
                        content=content,
                        chunk_type="code"
                    ))
                current_chunk = []
                start_line = i + 1
        
        # Add remaining chunk
        if current_chunk and any(line.strip() for line in current_chunk):
            content = '\n'.join(current_chunk)
            chunks.append(CodeChunk(
                file_path=rel_path,
                start_line=start_line,
                end_line=len(lines),
                content=content,
                chunk_type="code"
            ))
        
        return chunks
    
    def _load_cache(self) -> bool:
        """Load index from cache if available"""
        cache_key = self._get_cache_key()
        cache_file = self.cache_dir / f"semantic_index_{cache_key}.pkl"
        faiss_file = self.cache_dir / f"semantic_index_{cache_key}.faiss"
        
        if cache_file.exists() and faiss_file.exists():
            try:
                print("📦 Загружаю кэшированный индекс...")
                with open(cache_file, 'rb') as f:
                    self.chunks = pickle.load(f)
                
                self.index = faiss.read_index(str(faiss_file))
                print(f"✅ Загружен индекс с {len(self.chunks)} фрагментами кода")
                return True
            except Exception as e:
                print(f"⚠️ Ошибка загрузки кэша: {e}")
                
        return False
    
    def _save_cache(self):
        """Save index to cache"""
        cache_key = self._get_cache_key()
        cache_file = self.cache_dir / f"semantic_index_{cache_key}.pkl"
        faiss_file = self.cache_dir / f"semantic_index_{cache_key}.faiss"
        
        try:
            # Clean old cache files
            for old_file in self.cache_dir.glob("semantic_index_*.pkl"):
                old_file.unlink()
            for old_file in self.cache_dir.glob("semantic_index_*.faiss"):
                old_file.unlink()
            
            # Save new cache
            with open(cache_file, 'wb') as f:
                pickle.dump(self.chunks, f)
            
            faiss.write_index(self.index, str(faiss_file))
            print(f"💾 Индекс сохранен в кэш")
        except Exception as e:
            print(f"⚠️ Ошибка сохранения кэша: {e}")
    
    def index_codebase(self) -> Dict[str, Any]:
        """Index the entire codebase for semantic search"""
        try:
            self._initialize_model()
            
            # Try to load from cache first
            if self._load_cache():
                self.is_initialized = True
                return self._format_success(f"Индекс загружен из кэша: {len(self.chunks)} фрагментов")
            
            print("🔍 Сканирую кодовую базу...")
            
            # Collect all code chunks
            all_chunks = []
            file_count = 0
            
            for ext in self.code_extensions | self.doc_extensions:
                for file_path in self.workspace_path.rglob(f"*{ext}"):
                    if self._should_index_file(file_path):
                        chunks = self._extract_code_chunks(file_path)
                        all_chunks.extend(chunks)
                        file_count += 1
                        
                        if file_count % 10 == 0:
                            print(f"  📁 Обработано файлов: {file_count}")
            
            if not all_chunks:
                return self._format_error("Не найдено файлов для индексации")
            
            print(f"📊 Найдено {len(all_chunks)} фрагментов кода в {file_count} файлах")
            print("🧠 Создаю эмбеддинги...")
            
            # Create embeddings
            texts = [chunk.content for chunk in all_chunks]
            embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
            
            self.chunks = all_chunks
            self.is_initialized = True
            
            # Save to cache
            self._save_cache()
            
            return self._format_success(
                f"Кодовая база проиндексирована: {len(all_chunks)} фрагментов из {file_count} файлов"
            )
            
        except Exception as e:
            return self._format_error(f"Ошибка индексации: {str(e)}")
    
    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search code semantically"""
        try:
            if not self.is_initialized:
                init_result = self.index_codebase()
                if not init_result["success"]:
                    return init_result
            
            # Create query embedding
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding, limit)
            
            # Debug information
            print(f"🔍 Debug: Found {len(scores[0])} results, top scores: {scores[0][:3]}")
            
            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0:  # Убираю порог схожести для тестирования
                    chunk = self.chunks[idx]
                    results.append({
                        "file": chunk.file_path,
                        "lines": f"{chunk.start_line}-{chunk.end_line}",
                        "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                        "score": float(score),
                        "type": chunk.chunk_type
                    })
            
            # Возвращаем результаты на верхнем уровне для совместимости
            result = self._format_success(f"Найдено {len(results)} релевантных фрагментов")
            result["query"] = query
            result["results"] = results
            result["total_found"] = len(results)
            return result
            
        except Exception as e:
            return self._format_error(f"Ошибка поиска: {str(e)}")
    
    def execute(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Execute semantic search"""
        return self.search(query, limit)


def create_semantic_search_tool(workspace_path: str) -> SemanticSearchTool:
    """Factory function to create semantic search tool"""
    return SemanticSearchTool(workspace_path) 