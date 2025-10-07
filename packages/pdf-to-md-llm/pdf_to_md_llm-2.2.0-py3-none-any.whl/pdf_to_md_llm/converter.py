"""
PDF to Markdown conversion functions
"""

import pymupdf  # PyMuPDF
from pathlib import Path
from typing import List, Optional, Dict, Any
from .providers import AIProvider, get_provider, validate_api_key_available
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Default configuration
DEFAULT_PROVIDER = "anthropic"
DEFAULT_MAX_TOKENS = 4000
DEFAULT_PAGES_PER_CHUNK = 5
DEFAULT_VISION_DPI = 150
DEFAULT_VISION_PAGES_PER_CHUNK = 8
DEFAULT_THREADS = 1


def handle_chunk_conversion_error(chunk_index: int, error: Exception, verbose: bool = True) -> str:
    """
    Handle errors during chunk conversion.

    Args:
        chunk_index: The 1-indexed chunk number that failed
        error: The exception that occurred
        verbose: Whether to print error message

    Returns:
        Error markdown comment to insert in output
    """
    if verbose:
        print(f"  Error converting chunk {chunk_index}: {error}")
    return f"\n\n<!-- Error converting chunk {chunk_index}: {error} -->\n\n"


def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """
    Extract text from PDF, returning a list of page texts.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of strings, one per page
    """
    doc = pymupdf.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages.append(text)

    doc.close()
    return pages


def extract_pages_with_vision(
    pdf_path: str,
    dpi: int = DEFAULT_VISION_DPI
) -> List[Dict[str, Any]]:
    """
    Extract both text and images from PDF pages for vision-based processing.

    Args:
        pdf_path: Path to the PDF file
        dpi: DPI for rendering page images (default: 150)

    Returns:
        List of dicts with keys:
            - page_num: Page number (0-indexed)
            - text: Extracted text
            - image_base64: Base64-encoded PNG image of the page
            - has_images: Whether page contains embedded images
            - has_tables: Whether page likely contains tables
    """
    doc = pymupdf.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Extract text
        text = page.get_text()

        # Render page as image
        # Calculate zoom factor for desired DPI (default PDF is 72 DPI)
        zoom = dpi / 72.0
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # Convert to PNG bytes (using PyMuPDF's native method)
        img_bytes = pix.tobytes(output="png")

        # Encode to base64
        image_base64 = base64.b64encode(img_bytes).decode('utf-8')

        # Detect if page has images
        has_images = len(page.get_images()) > 0

        # Heuristic for table detection: check for multiple tab characters or grid-like text
        has_tables = text.count('\t') > 5 or text.count('|') > 5

        pages.append({
            'page_num': page_num,
            'text': text,
            'image_base64': image_base64,
            'has_images': has_images,
            'has_tables': has_tables
        })

    doc.close()
    return pages


def chunk_pages(pages: List[str], pages_per_chunk: int) -> List[str]:
    """
    Combine pages into chunks for processing.

    Args:
        pages: List of page texts
        pages_per_chunk: Number of pages to combine per chunk

    Returns:
        List of combined page chunks
    """
    chunks = []
    for i in range(0, len(pages), pages_per_chunk):
        chunk = "\n\n".join(pages[i:i + pages_per_chunk])
        chunks.append(chunk)
    return chunks


def chunk_vision_pages(
    pages: List[Dict[str, Any]],
    pages_per_chunk: int
) -> List[List[Dict[str, Any]]]:
    """
    Group vision-extracted pages into chunks for processing.

    Args:
        pages: List of page dicts from extract_pages_with_vision
        pages_per_chunk: Number of pages to combine per chunk

    Returns:
        List of page chunks (each chunk is a list of page dicts)
    """
    chunks = []
    for i in range(0, len(pages), pages_per_chunk):
        chunk = pages[i:i + pages_per_chunk]
        chunks.append(chunk)
    return chunks


def convert_chunk_to_markdown(
    provider: AIProvider,
    chunk: str,
    max_tokens: int = DEFAULT_MAX_TOKENS
) -> str:
    """
    Send a chunk of text to AI provider for markdown conversion.

    Args:
        provider: AI provider instance
        chunk: Text chunk to convert
        max_tokens: Maximum tokens for response

    Returns:
        Converted markdown text
    """
    return provider.convert_to_markdown(chunk, max_tokens)


def convert_vision_chunk_to_markdown(
    provider: AIProvider,
    chunk: List[Dict[str, Any]],
    max_tokens: int = DEFAULT_MAX_TOKENS
) -> str:
    """
    Send a chunk of pages with vision data to AI provider for markdown conversion.

    Args:
        provider: AI provider instance
        chunk: List of page dicts with text and image data
        max_tokens: Maximum tokens for response

    Returns:
        Converted markdown text
    """
    return provider.convert_to_markdown_vision(chunk, max_tokens)


def convert_pdf_to_markdown(
    pdf_path: str,
    output_path: Optional[str] = None,
    pages_per_chunk: int = DEFAULT_PAGES_PER_CHUNK,
    provider: str = DEFAULT_PROVIDER,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    verbose: bool = True,
    use_vision: bool = False,
    vision_dpi: int = DEFAULT_VISION_DPI
) -> str:
    """
    Convert a PDF file to markdown using an AI provider.

    Args:
        pdf_path: Path to the PDF file
        output_path: Optional path for output file (defaults to same name with .md)
        pages_per_chunk: Number of pages to process per API call
        provider: AI provider to use ('anthropic' or 'openai')
        api_key: API key for the provider (defaults to provider-specific env var)
        model: Model to use (optional, uses provider defaults if not specified)
        max_tokens: Maximum tokens per API call
        verbose: Print progress messages
        use_vision: Use vision-based processing (images + text)
        vision_dpi: DPI for rendering page images when using vision mode

    Returns:
        Complete markdown document

    Raises:
        ValueError: If API key is not provided and not in environment
    """
    # Validate API key is available before initializing provider
    is_valid, error_message = validate_api_key_available(provider, api_key)
    if not is_valid:
        raise ValueError(error_message)

    # Initialize AI provider
    ai_provider = get_provider(provider, api_key=api_key, model=model)

    if verbose:
        print(f"Processing: {pdf_path}")
        print(f"Using provider: {provider}")
        print(f"Using model: {ai_provider.model}")
        print(f"Vision mode: {'enabled' if use_vision else 'disabled'}")

    # Double-check provider configuration (backup validation)
    if not ai_provider.validate_config():
        provider_upper = provider.upper()
        raise ValueError(
            f"{provider_upper} API key is invalid or not properly configured."
        )

    # Check if vision mode is supported
    if use_vision and not hasattr(ai_provider, 'convert_to_markdown_vision'):
        raise ValueError(f"Vision mode is not supported by {provider} provider")

    # Extract from PDF
    if use_vision:
        if verbose:
            print(f"Extracting text and images from PDF (DPI: {vision_dpi})...")
        vision_pages = extract_pages_with_vision(pdf_path, dpi=vision_dpi)
        if verbose:
            print(f"  Found {len(vision_pages)} pages")
            images_count = sum(1 for p in vision_pages if p['has_images'])
            tables_count = sum(1 for p in vision_pages if p['has_tables'])
            print(f"  Detected {images_count} pages with images, {tables_count} pages with tables")

        # Use vision-specific chunk size if pages_per_chunk wasn't explicitly set
        # Otherwise respect the user's choice
        effective_pages_per_chunk = pages_per_chunk if pages_per_chunk != DEFAULT_PAGES_PER_CHUNK else DEFAULT_VISION_PAGES_PER_CHUNK
        chunks = chunk_vision_pages(vision_pages, effective_pages_per_chunk)
        if verbose:
            print(f"  Created {len(chunks)} chunks ({effective_pages_per_chunk} pages per chunk)")

        # Convert each chunk using vision
        markdown_chunks = []
        for i, chunk in enumerate(chunks, 1):
            if verbose:
                print(f"  Converting chunk {i}/{len(chunks)} (vision mode)...")
            try:
                markdown = convert_vision_chunk_to_markdown(ai_provider, chunk, max_tokens)
                markdown_chunks.append(markdown)
            except Exception as e:
                markdown_chunks.append(handle_chunk_conversion_error(i, e, verbose))
    else:
        # Original text-only mode
        if verbose:
            print("Extracting text from PDF...")
        pages = extract_text_from_pdf(pdf_path)
        if verbose:
            print(f"  Found {len(pages)} pages")

        # Chunk the pages
        chunks = chunk_pages(pages, pages_per_chunk)
        if verbose:
            print(f"  Created {len(chunks)} chunks")

        # Convert each chunk
        markdown_chunks = []
        for i, chunk in enumerate(chunks, 1):
            if verbose:
                print(f"  Converting chunk {i}/{len(chunks)}...")
            try:
                markdown = convert_chunk_to_markdown(ai_provider, chunk, max_tokens)
                markdown_chunks.append(markdown)
            except Exception as e:
                markdown_chunks.append(handle_chunk_conversion_error(i, e, verbose))

    # Combine all chunks
    full_markdown = "\n\n---\n\n".join(markdown_chunks)

    # Add document metadata header
    filename = Path(pdf_path).stem
    header = f"""# {filename}

*Converted from PDF using LLM-assisted conversion*

---

"""
    full_markdown = header + full_markdown

    # Save to file if output path provided
    if output_path is None:
        output_path = str(Path(pdf_path).with_suffix('.md'))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_markdown)

    if verbose:
        print(f"Saved to: {output_path}")

    return full_markdown


def batch_convert(
    input_folder: str,
    output_folder: Optional[str] = None,
    pages_per_chunk: int = DEFAULT_PAGES_PER_CHUNK,
    provider: str = DEFAULT_PROVIDER,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    verbose: bool = True,
    use_vision: bool = False,
    vision_dpi: int = DEFAULT_VISION_DPI,
    threads: int = DEFAULT_THREADS
) -> None:
    """
    Convert all PDF files in a folder and its subdirectories to markdown.

    Args:
        input_folder: Folder containing PDF files
        output_folder: Optional output folder (defaults to same as input)
        pages_per_chunk: Number of pages to process per API call
        provider: AI provider to use ('anthropic' or 'openai')
        api_key: API key for the provider (defaults to provider-specific env var)
        model: Model to use (optional, uses provider defaults if not specified)
        max_tokens: Maximum tokens per API call
        verbose: Print progress messages
        use_vision: Use vision-based processing (images + text)
        vision_dpi: DPI for rendering page images when using vision mode
        threads: Number of threads for parallel processing (default: 1)

    Raises:
        ValueError: If API key is not provided and not in environment
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder) if output_folder else input_path

    # Validate API key and initialize provider to get model information
    is_valid, error_message = validate_api_key_available(provider, api_key)
    if not is_valid:
        raise ValueError(error_message)

    # Initialize AI provider to display configuration
    ai_provider = get_provider(provider, api_key=api_key, model=model)

    # Create output folder if needed
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all PDFs recursively
    pdf_files = list(input_path.rglob("*.pdf"))

    if not pdf_files:
        if verbose:
            print(f"No PDF files found in {input_folder}")
        return

    if verbose:
        mode = f"multithreaded ({threads} threads)" if threads > 1 else "single-threaded"
        print(f"Batch Processing Configuration:")
        print(f"  Provider: {provider}")
        print(f"  Model: {ai_provider.model}")
        print(f"  Vision mode: {'enabled' if use_vision else 'disabled'}")
        print(f"  Mode: {mode}")
        print(f"  Files: {len(pdf_files)} PDF files")
        print()

    # Single-threaded execution (original behavior)
    if threads == 1:
        for i, pdf_file in enumerate(pdf_files, 1):
            if verbose:
                print(f"\n[{i}/{len(pdf_files)}]")

            # Preserve subdirectory structure in output
            relative_path = pdf_file.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix('.md')

            # Create subdirectory if needed
            output_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                convert_pdf_to_markdown(
                    str(pdf_file),
                    str(output_file),
                    pages_per_chunk=pages_per_chunk,
                    provider=provider,
                    api_key=api_key,
                    model=model,
                    max_tokens=max_tokens,
                    verbose=verbose,
                    use_vision=use_vision,
                    vision_dpi=vision_dpi
                )
            except Exception as e:
                if verbose:
                    print(f"Failed: {e}")
    else:
        # Multithreaded execution
        completed_count = 0
        progress_lock = threading.Lock()

        def convert_single_file(pdf_file: Path) -> tuple[bool, str]:
            """Convert a single PDF file and return success status and message."""
            nonlocal completed_count

            # Preserve subdirectory structure in output
            relative_path = pdf_file.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix('.md')

            # Create subdirectory if needed
            output_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                # For multithreaded mode, reduce verbosity of individual file processing
                convert_pdf_to_markdown(
                    str(pdf_file),
                    str(output_file),
                    pages_per_chunk=pages_per_chunk,
                    provider=provider,
                    api_key=api_key,
                    model=model,
                    max_tokens=max_tokens,
                    verbose=False,  # Suppress per-file output in multithreaded mode
                    use_vision=use_vision,
                    vision_dpi=vision_dpi
                )

                with progress_lock:
                    completed_count += 1
                    if verbose:
                        print(f"[OK] [{completed_count}/{len(pdf_files)}] {pdf_file.name}")

                return True, str(pdf_file)
            except Exception as e:
                with progress_lock:
                    completed_count += 1
                    if verbose:
                        print(f"[FAILED] [{completed_count}/{len(pdf_files)}] {pdf_file.name}: {e}")

                return False, str(pdf_file)

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Submit all tasks
            future_to_pdf = {
                executor.submit(convert_single_file, pdf_file): pdf_file
                for pdf_file in pdf_files
            }

            # Wait for all tasks to complete
            for future in as_completed(future_to_pdf):
                try:
                    future.result()
                except Exception as e:
                    if verbose:
                        pdf_file = future_to_pdf[future]
                        print(f"Unexpected error processing {pdf_file.name}: {e}")

    if verbose:
        print(f"\nBatch conversion complete!")
        print(f"  Output directory: {output_path}")
