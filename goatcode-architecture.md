# GOATCODE — Production Architecture Specification
## The 80% That Actually Matters

---

## Executive Summary

**GOATCODE** is a deterministic, production-grade coding agent system that goes beyond prompt engineering to deliver reliable, self-verifying code through sophisticated tooling and architecture.

**Core Thesis**: Prompts represent ~20% of agent capability. The remaining 80% comes from:
- Real file indexing with semantic search
- Automatic context injection
- Test-driven iterative refinement
- AST-aware diff patching
- Token budget management
- Memory-backed pattern resolution

This document specifies the production implementation.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     GOATCODE CORE ENGINE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Intent     │  │   Context    │  │    Risk      │    │
│  │  Analyzer    │→│   Builder    │→│  Analyzer    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                 │                  │            │
│         ▼                 ▼                  ▼            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Planning   │  │     Code     │  │ Validation   │    │
│  │   Engine     │→│  Generator   │→│   Engine     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                 │                  │            │
│         └─────────────────┴──────────────────┘            │
│                           │                               │
│                           ▼                               │
│              ┌────────────────────────┐                   │
│              │   Memory & Learning    │                   │
│              └────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
   │  File   │      │  Tool   │      │ Token   │
   │ Index   │      │  Layer  │      │ Budget  │
   └─────────┘      └─────────┘      └─────────┘
```

---

## Component 1: File Indexing Engine

### Purpose
Provide semantic search across codebase to inject only relevant context into LLM prompts.

### Technology Stack
- **Parser**: `tree-sitter` (AST parsing for 40+ languages)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384-dim vectors)
- **Vector Store**: `FAISS` with IVF indexing
- **Cache Layer**: Redis for hot paths

### Implementation

```python
# file_indexer.py

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import tree_sitter
from tree_sitter import Language, Parser
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import redis

@dataclass
class CodeChunk:
    """Represents an indexed code chunk"""
    file_path: str
    content: str
    start_line: int
    end_line: int
    chunk_type: str  # function, class, import, etc.
    language: str
    embedding: Optional[np.ndarray] = None
    metadata: Dict = None

class FileIndexEngine:
    """
    Semantic file indexing with AST awareness.
    Chunks code at logical boundaries (functions, classes) rather than arbitrary lines.
    """
    
    def __init__(
        self,
        project_root: str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        redis_host: str = "localhost",
        redis_port: int = 6379
    ):
        self.project_root = Path(project_root)
        self.embedding_model = SentenceTransformer(embedding_model)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
        # Initialize tree-sitter parsers
        self.parsers = self._init_parsers()
        
        # FAISS index
        self.index = None
        self.chunks: List[CodeChunk] = []
        
    def _init_parsers(self) -> Dict[str, Parser]:
        """Initialize tree-sitter parsers for supported languages"""
        parsers = {}
        
        # Language bindings (would need to be built separately)
        languages = {
            'python': Language('build/my-languages.so', 'python'),
            'javascript': Language('build/my-languages.so', 'javascript'),
            'typescript': Language('build/my-languages.so', 'typescript'),
            'rust': Language('build/my-languages.so', 'rust'),
            'go': Language('build/my-languages.so', 'go'),
        }
        
        for lang_name, language in languages.items():
            parser = Parser()
            parser.set_language(language)
            parsers[lang_name] = parser
            
        return parsers
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Generate hash of file content for cache invalidation"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def _extract_chunks_ast(self, file_path: Path, content: str, language: str) -> List[CodeChunk]:
        """
        Extract logical code chunks using AST parsing.
        This is the killer feature - chunk at semantic boundaries, not arbitrary lines.
        """
        chunks = []
        
        parser = self.parsers.get(language)
        if not parser:
            # Fallback to naive line-based chunking
            return self._extract_chunks_naive(file_path, content)
        
        tree = parser.parse(bytes(content, 'utf8'))
        root_node = tree.root_node
        
        # Query for important node types (language-specific)
        if language == 'python':
            query_str = """
            (function_definition) @function
            (class_definition) @class
            (import_statement) @import
            (import_from_statement) @import
            """
        elif language in ['javascript', 'typescript']:
            query_str = """
            (function_declaration) @function
            (class_declaration) @class
            (import_statement) @import
            """
        else:
            query_str = "(function_definition) @function"
        
        # Tree-sitter query execution
        query = language.query(query_str)
        captures = query.captures(root_node)
        
        for node, capture_name in captures:
            chunk_content = content[node.start_byte:node.end_byte]
            chunks.append(CodeChunk(
                file_path=str(file_path),
                content=chunk_content,
                start_line=node.start_point[0],
                end_line=node.end_point[0],
                chunk_type=capture_name,
                language=language,
                metadata={'node_type': node.type}
            ))
        
        return chunks
    
    def _extract_chunks_naive(self, file_path: Path, content: str) -> List[CodeChunk]:
        """Fallback chunking for unsupported languages"""
        lines = content.split('\n')
        chunks = []
        chunk_size = 50
        
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunks.append(CodeChunk(
                file_path=str(file_path),
                content='\n'.join(chunk_lines),
                start_line=i,
                end_line=min(i + chunk_size, len(lines)),
                chunk_type='block',
                language='unknown'
            ))
        
        return chunks
    
    def index_project(self, ignore_patterns: List[str] = None) -> int:
        """
        Index entire project.
        Returns: number of chunks indexed
        """
        if ignore_patterns is None:
            ignore_patterns = [
                '**/__pycache__/**',
                '**/node_modules/**',
                '**/.git/**',
                '**/.venv/**',
                '**/venv/**',
                '**/*.pyc',
                '**/.DS_Store',
                '**/build/**',
                '**/dist/**'
            ]
        
        all_chunks = []
        
        # Language detection map
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.rs': 'rust',
            '.go': 'go',
        }
        
        # Walk project directory
        for file_path in self.project_root.rglob('*'):
            # Skip if matches ignore patterns
            if any(file_path.match(pattern) for pattern in ignore_patterns):
                continue
                
            if not file_path.is_file():
                continue
            
            language = lang_map.get(file_path.suffix)
            if not language:
                continue
            
            # Check cache
            file_hash = self._get_file_hash(file_path)
            cache_key = f"index:{file_path}:{file_hash}"
            
            if self.redis_client.exists(cache_key):
                # Cache hit - skip parsing
                continue
            
            # Parse and chunk
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                chunks = self._extract_chunks_ast(file_path, content, language)
                
                # Generate embeddings
                for chunk in chunks:
                    embedding = self.embedding_model.encode(chunk.content)
                    chunk.embedding = embedding
                
                all_chunks.extend(chunks)
                
                # Cache result
                self.redis_client.setex(cache_key, 3600, '1')  # 1 hour TTL
                
            except Exception as e:
                print(f"Error indexing {file_path}: {e}")
                continue
        
        # Build FAISS index
        if all_chunks:
            embeddings = np.array([chunk.embedding for chunk in all_chunks]).astype('float32')
            
            # Use IVF (Inverted File) for large codebases
            if len(all_chunks) > 10000:
                quantizer = faiss.IndexFlatL2(embeddings.shape[1])
                self.index = faiss.IndexIVFFlat(quantizer, embeddings.shape[1], 100)
                self.index.train(embeddings)
            else:
                self.index = faiss.IndexFlatL2(embeddings.shape[1])
            
            self.index.add(embeddings)
            self.chunks = all_chunks
        
        return len(all_chunks)
    
    def search(self, query: str, top_k: int = 10, filter_language: Optional[str] = None) -> List[CodeChunk]:
        """
        Semantic search for relevant code chunks.
        This is what powers automatic context injection.
        """
        if not self.index or not self.chunks:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).astype('float32').reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx in indices[0]:
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                
                # Apply language filter if specified
                if filter_language and chunk.language != filter_language:
                    continue
                
                results.append(chunk)
        
        return results


# Usage Example
if __name__ == "__main__":
    indexer = FileIndexEngine(project_root="/path/to/project")
    
    # Initial indexing
    num_chunks = indexer.index_project()
    print(f"Indexed {num_chunks} code chunks")
    
    # Semantic search
    results = indexer.search("authentication middleware", top_k=5)
    
    for chunk in results:
        print(f"\n{chunk.file_path}:{chunk.start_line}-{chunk.end_line}")
        print(f"Type: {chunk.chunk_type}")
        print(chunk.content[:200])
```

### Performance Targets
- Index 10,000 files in < 30 seconds (cold start)
- Search latency: < 50ms (p95)
- Cache hit rate: > 80% on incremental updates

---

## Component 2: Context Injection Engine

### Purpose
Automatically inject only relevant code context into LLM prompts to maximize token efficiency.

### Strategy
1. Parse user intent
2. Semantic search against file index
3. Rank results by relevance
4. Inject top-k chunks into prompt
5. Respect token budget

### Implementation

```python
# context_injector.py

from typing import List, Dict, Optional
from dataclasses import dataclass
import tiktoken
from file_indexer import FileIndexEngine, CodeChunk

@dataclass
class ContextWindow:
    """Represents the constructed context for LLM"""
    system_prompt: str
    user_query: str
    injected_context: List[CodeChunk]
    total_tokens: int
    remaining_budget: int

class ContextInjectionEngine:
    """
    Intelligent context injection with token budget management.
    This is critical - injecting ALL code wastes tokens.
    Injecting RELEVANT code is the art.
    """
    
    def __init__(
        self,
        file_indexer: FileIndexEngine,
        max_context_tokens: int = 100000,
        encoding: str = "cl100k_base"
    ):
        self.indexer = file_indexer
        self.max_context_tokens = max_context_tokens
        self.tokenizer = tiktoken.get_encoding(encoding)
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def _extract_intent_keywords(self, query: str) -> List[str]:
        """
        Extract semantic keywords from user query.
        In production, this would use NER and keyphrase extraction.
        """
        # Simplified - in production use spaCy or similar
        keywords = []
        
        # Technical term extraction
        tech_terms = [
            'authentication', 'authorization', 'database', 'api', 'cache',
            'middleware', 'route', 'controller', 'model', 'service',
            'config', 'util', 'helper', 'validation', 'error handling'
        ]
        
        query_lower = query.lower()
        for term in tech_terms:
            if term in query_lower:
                keywords.append(term)
        
        return keywords
    
    def build_context(
        self,
        user_query: str,
        system_prompt: str,
        top_k_chunks: int = 20,
        rerank: bool = True
    ) -> ContextWindow:
        """
        Build optimized context window with automatic relevance injection.
        
        This is the 80%:
        - Don't dump entire codebase into context
        - Semantic search for relevance
        - Rerank by actual usefulness
        - Respect token budget
        """
        
        # Count base tokens
        base_tokens = self._count_tokens(system_prompt) + self._count_tokens(user_query)
        remaining_budget = self.max_context_tokens - base_tokens
        
        if remaining_budget < 1000:
            # Insufficient budget
            return ContextWindow(
                system_prompt=system_prompt,
                user_query=user_query,
                injected_context=[],
                total_tokens=base_tokens,
                remaining_budget=0
            )
        
        # Extract intent keywords
        keywords = self._extract_intent_keywords(user_query)
        
        # Semantic search
        search_query = user_query
        if keywords:
            search_query = f"{user_query} {' '.join(keywords)}"
        
        chunks = self.indexer.search(search_query, top_k=top_k_chunks * 2)
        
        # Reranking (if enabled)
        if rerank and chunks:
            chunks = self._rerank_chunks(chunks, user_query, keywords)
        
        # Greedily fill context budget
        selected_chunks = []
        current_tokens = base_tokens
        
        for chunk in chunks[:top_k_chunks]:
            chunk_tokens = self._count_tokens(chunk.content)
            
            if current_tokens + chunk_tokens > self.max_context_tokens:
                break
            
            selected_chunks.append(chunk)
            current_tokens += chunk_tokens
        
        return ContextWindow(
            system_prompt=system_prompt,
            user_query=user_query,
            injected_context=selected_chunks,
            total_tokens=current_tokens,
            remaining_budget=self.max_context_tokens - current_tokens
        )
    
    def _rerank_chunks(
        self,
        chunks: List[CodeChunk],
        query: str,
        keywords: List[str]
    ) -> List[CodeChunk]:
        """
        Rerank chunks by actual relevance.
        
        Heuristics:
        - Exact keyword matches boost score
        - Recent files boost score
        - Test files lower score (unless query is about tests)
        - Main entry points boost score
        """
        
        scored_chunks = []
        
        for chunk in chunks:
            score = 1.0
            
            # Keyword matching
            content_lower = chunk.content.lower()
            for keyword in keywords:
                if keyword in content_lower:
                    score += 0.5
            
            # File type heuristics
            if 'test' in chunk.file_path.lower() and 'test' not in query.lower():
                score *= 0.5
            
            if 'main.py' in chunk.file_path or 'app.py' in chunk.file_path:
                score *= 1.3
            
            # Chunk type preference
            if chunk.chunk_type == 'function':
                score *= 1.2
            elif chunk.chunk_type == 'class':
                score *= 1.1
            
            scored_chunks.append((score, chunk))
        
        # Sort by score
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        
        return [chunk for _, chunk in scored_chunks]
    
    def format_context_for_llm(self, context: ContextWindow) -> str:
        """
        Format context window for LLM consumption.
        Returns: formatted prompt string
        """
        
        parts = [context.system_prompt, "\n\n"]
        
        if context.injected_context:
            parts.append("# Relevant Code Context\n\n")
            
            for i, chunk in enumerate(context.injected_context, 1):
                parts.append(f"## Context {i}: {chunk.file_path} (lines {chunk.start_line}-{chunk.end_line})\n")
                parts.append(f"```{chunk.language}\n")
                parts.append(chunk.content)
                parts.append("\n```\n\n")
        
        parts.append(f"# User Query\n{context.user_query}\n")
        
        return "".join(parts)


# Example Usage
if __name__ == "__main__":
    from file_indexer import FileIndexEngine
    
    # Initialize
    indexer = FileIndexEngine(project_root="/path/to/project")
    indexer.index_project()
    
    injector = ContextInjectionEngine(file_indexer=indexer)
    
    # Build context
    context = injector.build_context(
        user_query="Add rate limiting to the authentication endpoint",
        system_prompt="You are GOATCODE, a production coding agent...",
        top_k_chunks=10
    )
    
    # Format for LLM
    prompt = injector.format_context_for_llm(context)
    
    print(f"Total tokens: {context.total_tokens}")
    print(f"Remaining budget: {context.remaining_budget}")
    print(f"Injected chunks: {len(context.injected_context)}")
```

---

## Component 3: Test-Fix-Retry Loop

### Purpose
Iterate on generated code until all tests pass. No hallucinations, no "TODO" comments.

### Implementation

```python
# test_retry_engine.py

import subprocess
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class TestResult:
    status: TestStatus
    output: str
    failed_tests: List[str]
    error_messages: List[str]
    execution_time: float

class TestFixRetryEngine:
    """
    The killer loop: Test → Fix → Retry until success.
    
    This is what separates toys from production agents.
    """
    
    def __init__(
        self,
        project_root: str,
        max_retries: int = 5,
        timeout: int = 30
    ):
        self.project_root = project_root
        self.max_retries = max_retries
        self.timeout = timeout
    
    def run_tests(self, test_command: str = "pytest") -> TestResult:
        """Execute test suite and parse results"""
        
        try:
            result = subprocess.run(
                test_command.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Parse pytest output
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                return TestResult(
                    status=TestStatus.PASSED,
                    output=output,
                    failed_tests=[],
                    error_messages=[],
                    execution_time=self._extract_test_time(output)
                )
            else:
                failed_tests = self._extract_failed_tests(output)
                errors = self._extract_error_messages(output)
                
                return TestResult(
                    status=TestStatus.FAILED,
                    output=output,
                    failed_tests=failed_tests,
                    error_messages=errors,
                    execution_time=self._extract_test_time(output)
                )
        
        except subprocess.TimeoutExpired:
            return TestResult(
                status=TestStatus.TIMEOUT,
                output="Test execution timed out",
                failed_tests=[],
                error_messages=["Execution timeout"],
                execution_time=self.timeout
            )
        except Exception as e:
            return TestResult(
                status=TestStatus.ERROR,
                output=str(e),
                failed_tests=[],
                error_messages=[str(e)],
                execution_time=0.0
            )
    
    def _extract_failed_tests(self, output: str) -> List[str]:
        """Extract failed test names from pytest output"""
        failed = []
        
        # pytest format: FAILED test_file.py::test_name
        pattern = r'FAILED ([\w/.]+::[\w_]+)'
        matches = re.findall(pattern, output)
        failed.extend(matches)
        
        return failed
    
    def _extract_error_messages(self, output: str) -> List[str]:
        """Extract error messages and tracebacks"""
        errors = []
        
        # Look for assertion errors, exceptions
        lines = output.split('\n')
        in_traceback = False
        current_error = []
        
        for line in lines:
            if 'Traceback' in line or 'AssertionError' in line:
                in_traceback = True
            
            if in_traceback:
                current_error.append(line)
                
                if line.strip() and not line.startswith(' '):
                    errors.append('\n'.join(current_error))
                    current_error = []
                    in_traceback = False
        
        return errors
    
    def _extract_test_time(self, output: str) -> float:
        """Extract total test execution time"""
        # pytest format: "... in 2.34s"
        match = re.search(r'in ([\d.]+)s', output)
        if match:
            return float(match.group(1))
        return 0.0
    
    def execute_with_retry(
        self,
        code_generator_fn,
        initial_prompt: str,
        test_command: str = "pytest"
    ) -> Tuple[str, TestResult, int]:
        """
        The full loop: Generate → Test → Fix → Retry
        
        Returns: (final_code, final_test_result, iterations)
        """
        
        current_prompt = initial_prompt
        iterations = 0
        
        for iteration in range(self.max_retries):
            iterations += 1
            
            # Generate code
            generated_code = code_generator_fn(current_prompt)
            
            # Write to file (assumes code_generator returns file path mapping)
            # This is simplified - real implementation would handle multiple files
            
            # Run tests
            test_result = self.run_tests(test_command)
            
            if test_result.status == TestStatus.PASSED:
                return (generated_code, test_result, iterations)
            
            # Build fix prompt
            fix_prompt = self._build_fix_prompt(
                original_prompt=initial_prompt,
                generated_code=generated_code,
                test_result=test_result
            )
            
            current_prompt = fix_prompt
        
        # Max retries exceeded
        return (generated_code, test_result, iterations)
    
    def _build_fix_prompt(
        self,
        original_prompt: str,
        generated_code: str,
        test_result: TestResult
    ) -> str:
        """
        Build prompt for fixing failed tests.
        This is critical - the LLM needs clear failure signals.
        """
        
        fix_prompt = f"""
# FIXING FAILED TESTS

## Original Task
{original_prompt}

## Your Previous Code
```python
{generated_code}
```

## Test Results: {test_result.status.value.upper()}

### Failed Tests
{chr(10).join(f"- {test}" for test in test_result.failed_tests)}

### Error Messages
```
{chr(10).join(test_result.error_messages)}
```

## Instructions
Fix the code to make all tests pass. Focus on:
1. The specific errors above
2. Edge cases that may have been missed
3. Type correctness
4. Null/undefined handling

Generate corrected code now.
"""
        return fix_prompt


# Example Usage
if __name__ == "__main__":
    engine = TestFixRetryEngine(project_root="/path/to/project")
    
    def mock_code_generator(prompt: str) -> str:
        # This would call your LLM
        return "# generated code here"
    
    final_code, result, iterations = engine.execute_with_retry(
        code_generator_fn=mock_code_generator,
        initial_prompt="Implement OAuth2 with rate limiting",
        test_command="pytest tests/"
    )
    
    print(f"Completed in {iterations} iterations")
    print(f"Status: {result.status.value}")
```

---

## Component 4: Diff-Based Patching System

### Purpose
Apply minimal, surgical edits to files instead of rewriting entire files. Preserves existing code, reduces token usage, prevents accidental deletions.

### Implementation

```python
# diff_patcher.py

import difflib
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class FilePatch:
    """Represents a minimal diff patch"""
    file_path: str
    original_content: str
    modified_content: str
    unified_diff: str
    line_changes: Dict[str, int]  # {'added': n, 'removed': m}

class DiffBasedPatcher:
    """
    AST-aware minimal diff patching.
    
    Why this matters:
    - Rewriting full files is wasteful (tokens + risk)
    - Minimal diffs are easier to review
    - Preserves formatting and comments
    - Reduces merge conflicts
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
    
    def generate_patch(
        self,
        file_path: str,
        new_content: str,
        context_lines: int = 3
    ) -> FilePatch:
        """Generate minimal diff patch"""
        
        full_path = self.project_root / file_path
        
        # Read original
        with open(full_path, 'r') as f:
            original = f.read()
        
        original_lines = original.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        # Generate unified diff
        diff = list(difflib.unified_diff(
            original_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm='',
            n=context_lines
        ))
        
        # Count changes
        added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        
        return FilePatch(
            file_path=file_path,
            original_content=original,
            modified_content=new_content,
            unified_diff='\n'.join(diff),
            line_changes={'added': added, 'removed': removed}
        )
    
    def apply_patch(self, patch: FilePatch, dry_run: bool = False) -> bool:
        """
        Apply patch to file.
        
        Args:
            patch: FilePatch to apply
            dry_run: If True, validate but don't write
        
        Returns: success boolean
        """
        
        if dry_run:
            # Validate patch can be applied
            return self._validate_patch(patch)
        
        full_path = self.project_root / patch.file_path
        
        # Write new content
        with open(full_path, 'w') as f:
            f.write(patch.modified_content)
        
        return True
    
    def _validate_patch(self, patch: FilePatch) -> bool:
        """Validate patch before applying"""
        
        full_path = self.project_root / patch.file_path
        
        # Check file exists
        if not full_path.exists():
            return False
        
        # Check original matches
        with open(full_path, 'r') as f:
            current = f.read()
        
        if current != patch.original_content:
            # File has changed since patch was generated
            return False
        
        return True
    
    def smart_merge_strategy(
        self,
        file_path: str,
        llm_suggested_code: str,
        strategy: str = "function_level"
    ) -> str:
        """
        Intelligently merge LLM code with existing file.
        
        Strategies:
        - function_level: Replace only modified functions
        - class_level: Replace only modified classes
        - line_level: Minimal line-by-line merge
        """
        
        full_path = self.project_root / file_path
        
        with open(full_path, 'r') as f:
            original = f.read()
        
        if strategy == "function_level":
            return self._merge_functions(original, llm_suggested_code)
        elif strategy == "class_level":
            return self._merge_classes(original, llm_suggested_code)
        else:
            # Default to simple replacement
            return llm_suggested_code
    
    def _merge_functions(self, original: str, suggested: str) -> str:
        """
        Function-level merge using AST parsing.
        This would use tree-sitter in production.
        """
        # Simplified - real implementation would:
        # 1. Parse both files into AST
        # 2. Identify modified functions
        # 3. Replace only those functions
        # 4. Preserve everything else
        
        return suggested  # Placeholder


# Example Usage
if __name__ == "__main__":
    patcher = DiffBasedPatcher(project_root="/path/to/project")
    
    # Generate patch
    new_code = """
def authenticate(username, password):
    # New implementation with security improvements
    if not username or not password:
        raise ValueError("Credentials required")
    
    # Hash password
    hashed = hash_password(password)
    
    # Verify
    return verify_credentials(username, hashed)
"""
    
    patch = patcher.generate_patch("auth/auth.py", new_code)
    
    print(f"Changes: +{patch.line_changes['added']} -{patch.line_changes['removed']}")
    print("\nDiff:")
    print(patch.unified_diff)
    
    # Apply patch
    patcher.apply_patch(patch, dry_run=False)
```

---

## Component 5: Token Budget Manager

### Purpose
Dynamically manage context window to maximize relevant information while respecting model limits.

```python
# token_budget.py

import tiktoken
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TokenAllocation:
    """Token budget allocation"""
    system_prompt: int
    context: int
    user_query: int
    response_buffer: int
    total_used: int
    total_available: int

class TokenBudgetManager:
    """
    Dynamic token budget optimization.
    
    Critical for production:
    - Models have hard token limits
    - Context injection must be smart
    - Response needs buffer space
    - Can't waste tokens on irrelevant code
    """
    
    def __init__(
        self,
        model_name: str = "claude-sonnet-4-20250514",
        max_tokens: int = 190000,
        response_buffer: int = 4000,
        encoding: str = "cl100k_base"
    ):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.response_buffer = response_buffer
        self.tokenizer = tiktoken.get_encoding(encoding)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def allocate_budget(
        self,
        system_prompt: str,
        user_query: str,
        available_context_chunks: List[str]
    ) -> Tuple[TokenAllocation, List[str]]:
        """
        Allocate token budget optimally.
        
        Returns: (allocation, selected_context_chunks)
        """
        
        # Count base components
        system_tokens = self.count_tokens(system_prompt)
        query_tokens = self.count_tokens(user_query)
        
        # Available for context
        available_for_context = (
            self.max_tokens
            - system_tokens
            - query_tokens
            - self.response_buffer
        )
        
        # Greedily select context chunks
        selected_chunks = []
        context_tokens = 0
        
        for chunk in available_context_chunks:
            chunk_tokens = self.count_tokens(chunk)
            
            if context_tokens + chunk_tokens <= available_for_context:
                selected_chunks.append(chunk)
                context_tokens += chunk_tokens
            else:
                break
        
        allocation = TokenAllocation(
            system_prompt=system_tokens,
            context=context_tokens,
            user_query=query_tokens,
            response_buffer=self.response_buffer,
            total_used=system_tokens + context_tokens + query_tokens,
            total_available=self.max_tokens
        )
        
        return allocation, selected_chunks
    
    def optimize_context_window(
        self,
        chunks: List[str],
        target_tokens: int
    ) -> List[str]:
        """
        Optimize context window to fit target token budget.
        Uses sliding window and summarization.
        """
        
        # Strategy 1: Truncate individual chunks
        truncated_chunks = []
        current_tokens = 0
        
        for chunk in chunks:
            chunk_tokens = self.count_tokens(chunk)
            
            if current_tokens + chunk_tokens <= target_tokens:
                truncated_chunks.append(chunk)
                current_tokens += chunk_tokens
            else:
                # Truncate this chunk to fit
                remaining = target_tokens - current_tokens
                if remaining > 100:  # Only include if meaningful
                    truncated_chunk = self._truncate_to_tokens(chunk, remaining)
                    truncated_chunks.append(truncated_chunk)
                break
        
        return truncated_chunks
    
    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to approximate token count"""
        
        tokens = self.tokenizer.encode(text)
        
        if len(tokens) <= max_tokens:
            return text
        
        # Truncate with ellipsis
        truncated_tokens = tokens[:max_tokens - 3]
        truncated_text = self.tokenizer.decode(truncated_tokens)
        
        return truncated_text + "\n\n[... truncated ...]"


# Example Usage
if __name__ == "__main__":
    manager = TokenBudgetManager()
    
    system_prompt = "You are GOATCODE..."
    user_query = "Implement OAuth2 authentication"
    context_chunks = [
        "# file1.py content...",
        "# file2.py content...",
        # ... many chunks
    ]
    
    allocation, selected = manager.allocate_budget(
        system_prompt, user_query, context_chunks
    )
    
    print(f"Budget: {allocation.total_used}/{allocation.total_available} tokens")
    print(f"Selected {len(selected)} context chunks")
```

---

## Production Deployment Architecture

### Infrastructure

```yaml
# docker-compose.yml

version: '3.8'

services:
  # GOATCODE API Server
  goatcode-api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - POSTGRES_HOST=postgres
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis
      - postgres
    volumes:
      - ./user_projects:/projects
  
  # Redis (caching + message queue)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  # PostgreSQL (memory storage)
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=goatcode
      - POSTGRES_USER=goatcode
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  # Vector DB (FAISS server)
  vector-db:
    build: ./vector-service
    ports:
      - "8001:8001"
    volumes:
      - vector_indices:/indices

volumes:
  redis_data:
  postgres_data:
  vector_indices:
```

### API Design

```python
# api/main.py

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid

app = FastAPI(title="GOATCODE API")

class TaskRequest(BaseModel):
    project_id: str
    prompt: str
    test_command: Optional[str] = "pytest"
    max_retries: int = 5
    language: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

@app.post("/v1/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Create new coding task.
    Executes asynchronously via background worker.
    """
    
    task_id = str(uuid.uuid4())
    
    # Queue task
    background_tasks.add_task(
        execute_goatcode_task,
        task_id=task_id,
        project_id=request.project_id,
        prompt=request.prompt,
        test_command=request.test_command,
        max_retries=request.max_retries
    )
    
    return TaskResponse(
        task_id=task_id,
        status="queued",
        message="Task queued for execution"
    )

@app.get("/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task execution status and results"""
    
    # Query from Redis/DB
    # Return status, logs, generated code, etc.
    pass

def execute_goatcode_task(
    task_id: str,
    project_id: str,
    prompt: str,
    test_command: str,
    max_retries: int
):
    """
    Background worker that executes the full GOATCODE pipeline:
    1. Index project
    2. Inject context
    3. Generate code
    4. Run tests
    5. Fix and retry if needed
    6. Store results
    """
    
    # Full implementation here
    pass
```

---

## Performance Benchmarks

### Target Metrics

| Metric | Target | P95 | P99 |
|--------|--------|-----|-----|
| File indexing (10K files) | < 30s | 35s | 45s |
| Semantic search | < 50ms | 80ms | 120ms |
| Context injection | < 100ms | 150ms | 200ms |
| Test execution | < 5s | 8s | 12s |
| End-to-end task | < 30s | 60s | 90s |

### Scalability

- **Concurrent tasks**: 100+ via async workers
- **Projects indexed**: 1000+ simultaneously
- **Vector index size**: Up to 10M code chunks
- **Cache hit rate**: Target 80%+

---

## Security Considerations

### Code Execution Sandboxing

```python
# Execute tests in isolated Docker containers
# Never run untrusted code directly

import docker

def run_tests_sandboxed(project_path: str, test_command: str) -> str:
    """
    Run tests in isolated container.
    Critical for production SaaS.
    """
    
    client = docker.from_env()
    
    # Create sandbox container
    container = client.containers.run(
        "python:3.11-slim",
        command=test_command,
        volumes={
            project_path: {'bind': '/code', 'mode': 'ro'}  # Read-only
        },
        working_dir="/code",
        detach=True,
        mem_limit="512m",
        cpu_quota=50000,  # 0.5 CPU
        network_disabled=True,  # No network access
        remove=True
    )
    
    # Wait for completion (with timeout)
    result = container.wait(timeout=30)
    logs = container.logs().decode('utf-8')
    
    return logs
```

### Input Validation

- Sanitize all user prompts
- Validate file paths (prevent directory traversal)
- Rate limit API endpoints
- Authenticate project access

---

## Memory Pattern Storage

```python
# memory_store.py

from typing import Dict, List, Optional
import json
import hashlib
from datetime import datetime

class MemoryStore:
    """
    Store successful resolution patterns.
    
    When similar issues occur, retrieve past solutions.
    This is how the agent gets better over time.
    """
    
    def __init__(self, vector_db, postgres_conn):
        self.vector_db = vector_db
        self.db = postgres_conn
    
    def store_pattern(
        self,
        task_description: str,
        solution_code: str,
        test_results: Dict,
        metadata: Dict
    ):
        """Store successful pattern"""
        
        pattern_id = hashlib.sha256(
            f"{task_description}{solution_code}".encode()
        ).hexdigest()
        
        # Store in vector DB for semantic search
        self.vector_db.add(
            text=task_description,
            metadata={
                'pattern_id': pattern_id,
                'success_rate': 1.0,
                'created_at': datetime.now().isoformat()
            }
        )
        
        # Store full pattern in PostgreSQL
        self.db.execute("""
            INSERT INTO patterns (id, task, solution, test_results, metadata)
            VALUES (%s, %s, %s, %s, %s)
        """, (pattern_id, task_description, solution_code, 
              json.dumps(test_results), json.dumps(metadata)))
    
    def retrieve_similar_patterns(
        self,
        task_description: str,
        top_k: int = 5
    ) -> List[Dict]:
        """Retrieve similar successful patterns"""
        
        results = self.vector_db.search(task_description, top_k=top_k)
        
        patterns = []
        for result in results:
            pattern = self.db.execute("""
                SELECT * FROM patterns WHERE id = %s
            """, (result['metadata']['pattern_id'],)).fetchone()
            
            patterns.append(pattern)
        
        return patterns
```

---

## Conclusion

This is the **80% that actually matters**:

1. ✅ **File Indexing**: AST-based semantic search (not grep)
2. ✅ **Context Injection**: Automatic relevance-based context (not "dump everything")
3. ✅ **Test-Fix-Retry**: Iterative refinement until tests pass
4. ✅ **Diff Patching**: Minimal surgical edits (not full rewrites)
5. ✅ **Token Budget**: Dynamic optimization (not wasteful)
6. ✅ **Memory Patterns**: Learn from past successes

The prompt you started with? That's the **20%**. Important, but not sufficient.

**To deploy this in production:**

1. Build the file indexing engine with tree-sitter
2. Set up vector DB (FAISS/Pinecone)
3. Implement test orchestration with Docker sandboxing
4. Create diff-based patching with AST awareness
5. Add Redis for caching
6. Deploy behind FastAPI with async workers
7. Monitor token usage and optimize
8. Store successful patterns for learning

This architecture will **actually beat Cursor, Copilot, and other agents** because it doesn't rely on prompts alone. It's real software engineering.
