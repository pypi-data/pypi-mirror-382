import typer
from typing import Optional
from .core.config import DEFAULT_MODEL, DEFAULT_THRESHOLD, DEFAULT_TOPK, DEFAULT_MIN_LINES, SUPPORTED_EXTS
from .core.utils import scan_files
from .core.extractors.base_extractor import extract_functions
from .core.embeddings import EmbeddingEngine
from .core.similarity import SimilarityEngine
from .core.report import generate_reports
from tqdm import tqdm
import os

app = typer.Typer()

@app.command()
def main(
    path: str = typer.Argument(..., help="Project path to analyze"),
    languages: str = typer.Option(",".join(SUPPORTED_EXTS), help="File extensions to analyze (comma separated)"),
    threshold: float = typer.Option(DEFAULT_THRESHOLD, help="Similarity threshold (0-1)"),
    min_lines: int = typer.Option(DEFAULT_MIN_LINES, help="Minimum block size (lines)"),
    top_k: int = typer.Option(DEFAULT_TOPK, help="Top-K neighbors per snippet"),
    report_html: Optional[str] = typer.Option("report.html", help="HTML output path (None to disable)"),
    report_json: Optional[str] = typer.Option(None, help="JSON output path (optional)"),
    model: str = typer.Option(DEFAULT_MODEL, help="Embeddings model"),
    cache_dir: Optional[str] = typer.Option(None, help="Embeddings cache directory (optional)"),
    exclusions_file: Optional[str] = typer.Option(None, help="File with exclusion patterns (one per line)"),
    jobs: int = typer.Option(1, help="Parallelism for embeddings (1 = single-threaded, -1 = auto)"),
    verbose: bool = typer.Option(False, help="Verbose/logs"),
    dry_run: bool = typer.Option(False, help="Only list snippets, without similarity"),
):
    """
    🔍 Detect code duplicates using semantic embeddings
    """
    
    # Set threading environment variables to avoid conflicts
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    
    if not os.path.exists(path):
        typer.echo(f"❌ Error: The path '{path}' does not exist")
        raise typer.Exit(1)
    
    # Auto-detect .codeduplicates-ignore if no exclusions file specified
    if exclusions_file is None and os.path.exists(".codeduplicates-ignore"):
        exclusions_file = ".codeduplicates-ignore"
        if verbose:
            typer.echo("📋 Using .codeduplicates-ignore file")
    
    langs = [ext.strip() for ext in languages.split(",")]
    
    if verbose:
        typer.echo(f"📂 Scanning files in '{path}' for extensions: {langs}")
    
    files = scan_files(path, langs, exclusions_file)
    if not files:
        typer.echo("❌ No files found to analyze")
        return
    
    if verbose:
        typer.echo(f"📄 Found {len(files)} files")

    if verbose:
        typer.echo("🔍 Extracting functions...")
    
    all_functions = extract_functions(files, languages=langs, min_lines=min_lines)
    
    if not all_functions:
        typer.echo("❌ No functions found to analyze")
        return
    
    if verbose:
        typer.echo(f"🎯 Extracted {len(all_functions)} functions")
    
    if dry_run:
        typer.echo("🏃 Dry-run mode: listing found snippets")
        for func in all_functions:
            typer.echo(f"  📄 {func['file']}:{func['lines'][0]}-{func['lines'][1]} ({func['symbol']})")
        return
    
    embedding_engine = EmbeddingEngine(model_name=model, cache_dir=cache_dir, n_jobs=jobs, verbose=verbose)
    if verbose:
        typer.echo("🧠 Generating embeddings...")
    
    embeddings = embedding_engine.encode_snippets(all_functions)
    
    similarity_engine = SimilarityEngine(threshold=threshold, top_k=top_k)
    if verbose:
        typer.echo("🔗 Calculating similarities...")
    
    duplicates = similarity_engine.find_duplicates(embeddings, all_functions)
    
    if verbose:
        typer.echo("📊 Generating reports...")
    
    generate_reports(
        duplicates=duplicates,
        html_out=report_html,
        json_out=report_json
    )
    
    typer.echo(f"✅ Analysis completed:")
    typer.echo(f"   📄 {len(files)} files analyzed")
    typer.echo(f"   🎯 {len(all_functions)} functions extracted")
    typer.echo(f"   🔗 {len(duplicates)} duplicate groups found")
    
    if report_html:
        typer.echo(f"   📊 HTML Report: {report_html}")
        grouped_html = report_html.replace('.html', '_grouped.html')
        typer.echo(f"   📊 Grouped Report: {grouped_html}")
    if report_json:
        typer.echo(f"   📊 JSON Report: {report_json}")

if __name__ == "__main__":
    app()
