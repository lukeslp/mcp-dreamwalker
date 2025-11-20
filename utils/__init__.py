"""
Common utilities for configuration and error handling.
"""

import os
from typing import Any, Optional
import logging

# Import file utilities for easy access
from .file_utils import (
    format_size,
    format_timestamp,
    calculate_hash,
    get_file_type,
    get_file_info,
    get_directory_info,
    find_files_by_extension,
    get_file_age_days,
    ensure_directory,
    safe_filename
)

# Import progress tracking utilities
from .progress import (
    show_progress_bar,
    TaskInfo,
    ProgressTracker,
    MultiProgressTracker
)

# Import TTS utilities
from .tts import (
    TTSResult,
    check_gtts_available,
    get_available_languages,
    generate_tts,
    play_audio,
    text_to_speech,
    validate_language,
    get_language_name,
    list_common_languages
)

# Import execution safety utilities
from .execution import (
    ExecutionResult,
    SafeExecutor,
    execute_python,
    execute_bash,
    is_command_safe,
    UNSAFE_BASH_TOKENS
)

# Import citation utilities
from .citation import (
    Citation,
    CitationManager,
    write_bibtex,
    write_csv,
    format_apa,
    format_mla,
    format_chicago
)

# Import vision utilities
from .vision import (
    VisionResult,
    VisionClient,
    analyze_image,
    analyze_video,
    generate_filename_from_vision
)

# Import time utilities
from .time_utils import (
    TimeConversion,
    TimeDifference,
    TimeUtilities,
    convert_timezone,
    calculate_difference,
    add_time,
    parse_duration,
    list_timezones,
    validate_timezone
)

# Import multi-search utilities
from .multi_search import (
    SearchQuery,
    SearchResult,
    MultiSearchResult,
    MultiSearchOrchestrator,
    multi_search
)

# Import document parsing utilities
from .document_parsers import (
    ParseResult,
    FileParser,
    parse_file,
    get_supported_extensions,
    is_supported_file,
    get_file_type
)

# Import embedding utilities
from .embeddings import (
    EmbeddingResult,
    SimilarityResult,
    EmbeddingGenerator,
    calculate_similarity,
    find_most_similar,
    embedding_to_bytes,
    bytes_to_embedding,
    generate_embedding,
    generate_batch_embeddings
)

# Text processing helpers
from .text_processing import (
    normalize_whitespace,
    split_into_sentences,
    chunk_text,
    extract_keywords,
    generate_outline,
)

# Data validation helpers
from .data_validation import (
    ValidationError,
    SchemaValidationError,
    ensure_fields,
    validate_choices,
    validate_schema,
    coerce_types,
)

# Retry helpers
from .retry_logic import retry, async_retry, RetryConfig

# Rate limiter helpers
from .rate_limiter import TokenBucket, InMemoryRateLimiter, rate_limit

# Crypto helpers
from .crypto import (
    hash_text,
    generate_hmac,
    verify_hmac,
    generate_random_key,
    derive_key,
    generate_symmetric_key,
    encrypt_text,
    decrypt_text,
    FERNET_AVAILABLE,
)


logger = logging.getLogger(__name__)


def get_env_var(key: str, default: Any = None, required: bool = False) -> Any:
    """
    Get environment variable with optional default and required check.

    Args:
        key: Environment variable name
        default: Default value if not found
        required: If True, raise ValueError if not found

    Returns:
        Environment variable value or default

    Raises:
        ValueError: If required=True and variable not found
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value


def load_config(config_path: str = None) -> dict:
    """
    Load configuration from file or environment.

    Args:
        config_path: Path to config file (JSON or YAML)

    Returns:
        Configuration dictionary
    """
    config = {}

    if config_path and os.path.exists(config_path):
        import json
        with open(config_path, 'r') as f:
            if config_path.endswith('.json'):
                config = json.load(f)
            elif config_path.endswith(('.yaml', '.yml')):
                try:
                    import yaml
                    config = yaml.safe_load(f)
                except ImportError:
                    logger.warning("PyYAML not installed. Install with: pip install pyyaml")

    return config
