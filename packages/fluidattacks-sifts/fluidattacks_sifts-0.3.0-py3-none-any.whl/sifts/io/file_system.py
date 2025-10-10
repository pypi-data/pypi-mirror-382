import fnmatch
import logging
import os
from pathlib import Path

from sifts.core.types import Language
from sifts.io.file_system_defaults import CONFIG_FILES, EXCLUDE_DIRS, TEST_GLOBS

LOGGER = logging.getLogger(__name__)


def find_parent_project(
    file_path: str | Path,
    base_analysis_dir: Path,
) -> tuple[Path, Language, list[str]] | None:
    file_path = Path(file_path).absolute()
    directory = file_path if file_path.is_dir() else file_path.parent

    current_dir = directory
    while current_dir != current_dir.parent:  # Stop at filesystem root
        if current_dir == base_analysis_dir:
            break

        # Check for config files directly in the current directory
        for config_file_list in CONFIG_FILES.values():
            for config_file in config_file_list:
                if (current_dir / config_file).exists():
                    return next(x for x in find_projects(current_dir) if x[0] == current_dir)

        # Move up to parent directory
        current_dir = current_dir.parent

    return None


def find_projects(root_dir: str | Path) -> list[tuple[Path, Language, list[str]]]:
    project_paths: list[tuple[Path, Language, list[str]]] = []
    root_dir = Path(root_dir)

    # First pass: Find all potential projects
    for root, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pat) for pat in EXCLUDE_DIRS)]
        root_path = Path(root)

        for language, configs in CONFIG_FILES.items():
            if any(config in files for config in configs):
                exclusions = generate_exclusions()
                project_paths.append((root_path, language, exclusions))
                break

    # Second pass: Mark child projects as exclusions in parent projects
    updated_project_paths = []
    for parent_path, parent_lang, parent_exclusions in project_paths:
        # Find all child projects
        child_projects = [
            child_path
            for child_path, _, _ in project_paths
            if child_path != parent_path and child_path.is_relative_to(parent_path)
        ]

        # Add child projects to parent exclusions
        for child_path in child_projects:
            rel_path = child_path.relative_to(parent_path)
            parent_exclusions.append(str(rel_path) + "/")
            parent_exclusions.append(f"**/{rel_path.name}/")

        updated_project_paths.append((parent_path, parent_lang, parent_exclusions))
    if not updated_project_paths:
        LOGGER.warning("No projects found in %s", root_dir)

    return updated_project_paths


def generate_exclusions() -> list[str]:
    final: set[str] = set()
    for patterns in TEST_GLOBS.values():
        final.update(patterns)
    for pat in EXCLUDE_DIRS:
        final.add(pat)
    return sorted(final)


def is_dependency_file(path: Path) -> bool:
    for part in path.parts:
        for pat in EXCLUDE_DIRS:
            if fnmatch.fnmatchcase(part, pat):
                return True

    name = path.name
    return any(fnmatch.fnmatchcase(name, pat) for pat in EXCLUDE_DIRS)


def is_test_file(filename: str | Path, language: Language | None = None) -> bool:
    filename = Path(filename)
    if language and language in TEST_GLOBS:
        for pattern in TEST_GLOBS[language]:
            if fnmatch.fnmatch(filename.name, pattern):
                return True
    else:
        for patterns in TEST_GLOBS.values():
            for pattern in patterns:
                if fnmatch.fnmatch(filename.name, pattern):
                    return True
    return False


def find_files_by_extension(
    working_dir: str | Path,
    extensions: list[str],
    exclusions: list[str | Path] | None = None,
) -> list[Path]:
    working_dir = Path(working_dir)
    results = []
    exclusions = exclusions or []

    # Make sure extensions start with a dot
    formatted_extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]

    # Convert exclusions to Path objects
    exclusion_paths = [Path(excl) for excl in exclusions]

    for root, dirs, files in os.walk(working_dir):
        root_path = Path(root)

        # Skip excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(root_path / d, exclusion_paths)]

        # Find files with matching extensions
        for file in files:
            file_path = root_path / file
            if is_test_file(file_path):
                continue
            file_ext = file_path.suffix

            if file_ext in formatted_extensions and not should_exclude(file_path, exclusion_paths):
                results.append(file_path.absolute())

    return results


def should_exclude(file_path: Path, exclusions: list[Path]) -> bool:
    """
    Check if a file path should be excluded based on exclusion paths.

    Args:
        file_path: The file or directory path to check
        exclusions: List of Path objects to exclude

    Returns:
        True if the path should be excluded, False otherwise

    """
    file_path_resolved = file_path.resolve()

    for exclude in exclusions:
        # Handle glob patterns
        if "*" in str(exclude) or "?" in str(exclude):
            if fnmatch.fnmatch(str(file_path), str(exclude)):
                return True
            continue

        # Handle direct path matches
        exclude_path = Path(exclude).resolve()

        # Exact match
        if file_path_resolved == exclude_path:
            return True

        # Directory exclusion (file is inside excluded directory)
        if exclude_path.is_dir() and any(
            parent == exclude_path for parent in file_path_resolved.parents
        ):
            return True

    return False
