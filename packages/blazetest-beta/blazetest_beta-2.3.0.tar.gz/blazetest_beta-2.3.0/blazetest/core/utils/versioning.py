"""
Semantic versioning utilities for Docker image tags and build metadata.

Provides unique, human-readable version identifiers that include:
- Semantic version (e.g., 2.3.0)
- Timestamp for temporal ordering
- Git commit hash for traceability
- Content/dependency hashes for cache invalidation
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
import hashlib

from blazetest import __version__

logger = logging.getLogger(__name__)


def get_git_commit_hash(short: bool = True) -> Optional[str]:
    """
    Get the current git commit hash.

    Args:
        short: If True, return 7-char short hash. If False, return full hash.

    Returns:
        Git commit hash or None if not in a git repository
    """
    try:
        length = 7 if short else 40
        result = subprocess.run(
            ["git", "rev-parse", f"--short={length}" if short else "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug(f"Failed to get git hash: {e}")
    return None


def get_git_branch() -> Optional[str]:
    """
    Get the current git branch name.

    Returns:
        Branch name or None if not in a git repository
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug(f"Failed to get git branch: {e}")
    return None


def get_git_dirty_status() -> bool:
    """
    Check if there are uncommitted changes in the git repository.

    Returns:
        True if there are uncommitted changes, False otherwise
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--quiet"],
            timeout=5,
        )
        # Exit code 1 means there are changes
        return result.returncode != 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def generate_build_timestamp() -> str:
    """
    Generate a compact timestamp for build versioning.

    Format: YYYYMMDD-HHMMSS
    Example: 20251009-143025

    Returns:
        Timestamp string
    """
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def generate_short_timestamp() -> str:
    """
    Generate a very short timestamp (minutes precision).

    Format: YYYYMMDD-HHMM
    Example: 20251009-1430

    Returns:
        Short timestamp string
    """
    return datetime.now().strftime("%Y%m%d-%H%M")


def generate_semantic_version(
    content_hash: str,
    dependencies_hash: str,
    include_timestamp: bool = True,
    include_git: bool = True,
    format_type: str = "full",
) -> str:
    """
    Generate a semantic version string for Docker image tagging.

    Args:
        content_hash: 8-char hash of project content
        dependencies_hash: 8-char hash of dependencies
        include_timestamp: Include timestamp in version
        include_git: Include git commit hash in version
        format_type: Version format - "full", "compact", "minimal"

    Returns:
        Semantic version string

    Examples:
        full: v2.3.0-20251009-1430-abc1234-70d91f8b
        compact: v2.3.0-abc1234-70d91f8b
        minimal: 70d91f8b (just content hash)
    """
    version = __version__

    if format_type == "minimal":
        return content_hash

    parts = [f"v{version}"]

    if include_timestamp and format_type == "full":
        parts.append(generate_short_timestamp())

    if include_git:
        git_hash = get_git_commit_hash(short=True)
        if git_hash:
            # Add 'dirty' suffix if there are uncommitted changes
            if get_git_dirty_status():
                git_hash = f"{git_hash}-dirty"
            parts.append(git_hash)

    # Always include content hash (primary cache key)
    parts.append(content_hash)

    # Optionally include dependencies hash if different from content
    if dependencies_hash and dependencies_hash != content_hash:
        parts.append(f"deps-{dependencies_hash}")

    return "-".join(parts)


def generate_image_tags(
    content_hash: str,
    dependencies_hash: str,
    session_uuid: Optional[str] = None,
    config_format: str = "full",
) -> Dict[str, str]:
    """
    Generate all image tags for a build.

    Args:
        content_hash: Hash of project content
        dependencies_hash: Hash of dependencies
        session_uuid: Optional session UUID for session-specific tags
        config_format: Version format from config

    Returns:
        Dictionary with tag names and values:
        {
            "primary": "v2.3.0-20251009-1430-abc1234-70d91f8b",
            "content": "70d91f8b",
            "cache": "cache",
            "latest": "latest",  # only for main/master branch
            "session": "fdcf79ea",  # only if session_uuid provided
        }
    """
    tags = {}

    # Primary semantic version tag
    tags["primary"] = generate_semantic_version(
        content_hash=content_hash,
        dependencies_hash=dependencies_hash,
        include_timestamp=True,
        include_git=True,
        format_type=config_format,
    )

    # Content-based tag (for exact cache matching)
    tags["content"] = content_hash

    # Cache tag (for layer caching)
    tags["cache"] = "cache"

    # Latest tag (only for main/master branch)
    git_branch = get_git_branch()
    if git_branch in ["main", "master"]:
        tags["latest"] = "latest"

    # Session-specific tag (for concurrent execution isolation)
    if session_uuid:
        tags["session"] = session_uuid

    return tags


def get_version_metadata(
    content_hash: str,
    dependencies_hash: str,
    session_uuid: str,
) -> Dict[str, str]:
    """
    Get comprehensive version metadata for logging and tracking.

    Args:
        content_hash: Hash of project content
        dependencies_hash: Hash of dependencies
        session_uuid: Session UUID

    Returns:
        Dictionary with version metadata
    """
    git_hash = get_git_commit_hash(short=False)
    git_short_hash = get_git_commit_hash(short=True)
    git_branch = get_git_branch()
    is_dirty = get_git_dirty_status()

    return {
        "blazetest_version": __version__,
        "build_timestamp": generate_build_timestamp(),
        "session_uuid": session_uuid,
        "content_hash": content_hash,
        "dependencies_hash": dependencies_hash,
        "git_commit": git_hash,
        "git_commit_short": git_short_hash,
        "git_branch": git_branch,
        "git_dirty": str(is_dirty),
        "semantic_version": generate_semantic_version(
            content_hash=content_hash,
            dependencies_hash=dependencies_hash,
            include_timestamp=True,
            include_git=True,
            format_type="full",
        ),
    }


def format_version_info(metadata: Dict[str, str]) -> str:
    """
    Format version metadata for pretty printing.

    Args:
        metadata: Version metadata dictionary

    Returns:
        Formatted string
    """
    lines = [
        "=" * 70,
        "Build Version Information",
        "=" * 70,
        f"BlazeTest Version: {metadata['blazetest_version']}",
        f"Semantic Version:  {metadata['semantic_version']}",
        f"Build Timestamp:   {metadata['build_timestamp']}",
        f"Session UUID:      {metadata['session_uuid']}",
        "",
        "Content Hashes:",
        f"  Project:         {metadata['content_hash']}",
        f"  Dependencies:    {metadata['dependencies_hash']}",
        "",
    ]

    if metadata.get("git_commit"):
        lines.extend(
            [
                "Git Information:",
                f"  Branch:          {metadata.get('git_branch', 'N/A')}",
                f"  Commit:          {metadata['git_commit']}",
                f"  Short Hash:      {metadata['git_commit_short']}",
                f"  Dirty:           {metadata['git_dirty']}",
                "",
            ]
        )

    lines.append("=" * 70)
    return "\n".join(lines)
