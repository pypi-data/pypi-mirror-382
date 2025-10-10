# Code Duplicates CLI — Version 3

Multi-language code duplicate detector using **semantic embeddings**, **Tree-Sitter parsing**, **parallelism**, 
**minimum size filtering**, **configurable exclusions**, and **HTML reports with syntax highlighting** and **JSON output**.

## ✨ Features
- **Multi-language support**: `py, js, ts, tsx, jsx, go, rs (rust), c, cpp, java` (extensible)
- **AST extraction** with `tree-sitter-languages` (functions, methods, classes)
- **Semantic embeddings** with `SentenceTransformers` (default: `sentence-transformers/all-mpnet-base-v2`)
- **Fast similarity search** with `faiss` (Inner Product + L2 normalization)
- **Parallel processing** for snippet extraction and embedding generation
- **Smart caching** of embeddings by file content hash
- **Configurable exclusions** for folders and files (node_modules, .git, etc.)
- **Minimum block size filtering** (by lines)
- **Rich HTML reports** with **Pygments syntax highlighting** + **JSON export**
- **Configurable similarity threshold** and top-k results per snippet
- **Verbose mode** and **dry-run** capabilities

## 🚀 Installation
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

> **Note**: `tree-sitter-languages` includes pre-compiled grammars; no manual compilation required.

## 📖 Usage

### Basic Usage
```bash
# Simple scan with defaults
python cli.py ./path/to/project

# Scan current directory
python cli.py .
```

### Advanced Usage
```bash
python cli.py ./path/to/project \
  --languages py,ts,tsx,js,go \
  --threshold 0.85 \
  --min-lines 5 \
  --top-k 10 \
  --report-html reports/duplicates.html \
  --report-json reports/duplicates.json \
  --model sentence-transformers/all-mpnet-base-v2 \
  --cache-dir .cache_embeddings \
  --exclusions-file .codeduplicates-ignore \
  --verbose
```

### Command Line Options
```bash
Options:
  --languages TEXT        Comma-separated list of file extensions (default: py,js,ts,tsx,jsx,go,rs,c,cpp,java)
  --threshold FLOAT       Similarity threshold (0.0-1.0, default: 0.85)
  --min-lines INTEGER     Minimum lines per code block (default: 3)
  --top-k INTEGER         Max similar snippets per block (default: 5)
  --report-html PATH      HTML report output path
  --report-json PATH      JSON report output path
  --model TEXT            Embedding model name (default: sentence-transformers/all-mpnet-base-v2)
  --cache-dir PATH        Directory for embedding cache
  --exclusions-file PATH  Custom exclusions file (default: .codeduplicates-ignore)
  --verbose              Enable verbose output
  --dry-run              Show what would be processed without running
  --help                 Show this message and exit
```

## 🚫 Exclusions
The CLI includes default exclusions for common folders like `node_modules`, `.git`, `__pycache__`, etc.

Create a custom exclusions file:
```bash
# .codeduplicates-ignore
node_modules
.git
dist
build
*.min.js
my-generated-folder
test-data
venv
.venv
__pycache__
.pytest_cache
coverage
.coverage
```

Supports glob patterns (`*`, `?`, `[]`) and comments with `#`.

## 📊 Examples

### Language-Specific Scans
```bash
# Scan TypeScript/JavaScript with high threshold
python cli.py . --languages ts,tsx,js --threshold 0.92 --report-html reports/js-duplicates.html

# Python and Go only, minimum 5 lines, top-3 results
python cli.py src --languages py,go --min-lines 5 --top-k 3 --report-json reports/py-go-duplicates.json

# Rust projects with custom exclusions
python cli.py . --languages rs --exclusions-file rust-exclusions.txt --verbose
```

### Performance Optimization
```bash
# Large codebase with caching
python cli.py . --cache-dir .embeddings-cache --min-lines 10 --threshold 0.80

# Quick scan with dry-run
python cli.py . --dry-run --verbose
```

## 🏗️ Project Structure
```
code-duplicates-cli-v3/
├── cli.py                    # Main CLI entry point
├── core/
│   ├── config.py            # Configuration constants
│   ├── utils.py             # Utility functions
│   ├── embeddings.py        # Embedding generation engine
│   ├── similarity.py        # Similarity calculation engine
│   ├── report.py            # HTML/JSON report generation
│   └── extractors/
│       ├── base_extractor.py    # Base extractor interface
│       ├── parser_manager.py    # Tree-sitter parser management
│       ├── code_extractor.py    # AST-based code extraction
│       ├── regex_extractor.py   # Regex-based extraction
│       └── simple_extractor.py  # Simple text extraction
├── ARCHITECTURE.md          # Detailed architecture documentation
├── MODEL_ANALYSIS.md        # Embedding model analysis
└── requirements.txt         # Python dependencies
```

## 🎯 Model Information

### Current Default Model
- **Model**: `sentence-transformers/all-mpnet-base-v2`
- **Type**: Semantic similarity model based on MPNet
- **Dimensions**: 768
- **Strengths**: Better semantic understanding, fewer false positives
- **Use Case**: General-purpose semantic similarity with good code understanding

### Alternative Models
```bash
# Code-specific models
python cli.py . --model microsoft/codebert-base
python cli.py . --model microsoft/graphcodebert-base

# Faster alternatives
python cli.py . --model sentence-transformers/all-MiniLM-L6-v2
python cli.py . --model sentence-transformers/paraphrase-MiniLM-L6-v2
```

## ⚡ Performance Tips

### For Large Repositories
- **Use caching**: `--cache-dir .embeddings-cache` to avoid recomputing embeddings
- **Increase minimum lines**: `--min-lines 10` to reduce noise from trivial blocks
- **Adjust threshold**: `--threshold 0.80` for broader matches, `0.90+` for strict matches
- **Limit top-k**: `--top-k 3` for faster processing

### Memory Optimization
- **Smaller models**: Use `all-MiniLM-L6-v2` for faster inference
- **Batch processing**: The tool automatically handles large codebases efficiently
- **Exclusions**: Use comprehensive exclusion files to skip irrelevant directories

## 🐛 Troubleshooting

### Common Issues
1. **High false positives**: Increase `--threshold` to 0.90 or higher
2. **Missing duplicates**: Decrease `--threshold` to 0.70-0.80
3. **Too many results**: Increase `--min-lines` or use stricter exclusions
4. **Slow performance**: Use `--cache-dir` and consider a smaller model

### Debug Mode
```bash
# Verbose output for debugging
python cli.py . --verbose --dry-run

# Test specific file types
python cli.py test-project --languages py --verbose
```

## 📄 Output Formats

### HTML Report
- **Syntax highlighting** with Pygments
- **Side-by-side comparison** of duplicate code blocks
- **Similarity scores** and file locations
- **Interactive navigation** between duplicates

### JSON Report
- **Structured data** for programmatic processing
- **Complete metadata** including file paths, line numbers, similarity scores
- **Easy integration** with CI/CD pipelines and other tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.
