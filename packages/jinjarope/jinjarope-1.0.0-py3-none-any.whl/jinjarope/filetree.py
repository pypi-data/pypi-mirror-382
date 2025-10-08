from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
import re
from re import Pattern
import stat
from typing import TYPE_CHECKING, Any

from jinja2 import filters

from jinjarope import iconfilters, textfilters


if TYPE_CHECKING:
    from collections.abc import Iterator
    import os

    import upath


class SortCriteria(Enum):
    """Enumeration for different sorting criteria."""

    NAME = auto()
    SIZE = auto()
    DATE = auto()
    EXTENSION = auto()


@dataclass
class TreeOptions:
    """Configuration options for directory tree printing."""

    show_hidden: bool = False
    show_size: bool = True
    show_date: bool = False
    show_permissions: bool = False
    show_icons: bool = True
    max_depth: int | None = None
    include_pattern: Pattern[str] | None = None
    exclude_pattern: Pattern[str] | None = None
    allowed_extensions: set[str] | None = None
    hide_empty: bool = True
    sort_criteria: SortCriteria = SortCriteria.NAME
    reverse_sort: bool = False
    date_format: str = "%Y-%m-%d %H:%M:%S"


def _get_path_info(path: upath.UPath) -> dict[str, Any]:
    """Get all relevant information about a path.

    Args:
        path: Path to get information about.

    Returns:
        Dictionary containing information about the path.
    """
    try:
        stats = path.stat()
        return {
            "size": stats.st_size,
            "mtime": stats.st_mtime,
            "mode": stats.st_mode,
            "is_dir": path.is_dir(),
            "name": path.name,
            "extension": path.suffix.lower(),
        }
    except OSError:
        return {
            "size": 0,
            "mtime": 0,
            "mode": 0,
            "is_dir": path.is_dir(),
            "name": path.name,
            "extension": path.suffix.lower(),
        }


class DirectoryTree:
    """A class to generate and print directory tree structure."""

    PIPE = "┃   "
    ELBOW = "┗━━ "
    TEE = "┣━━ "
    DIRECTORY = "📂"

    def __init__(
        self,
        root_path: str | os.PathLike[str],
        options: TreeOptions | None = None,
    ):
        """A class to generate and print directory tree structure.

        Attributes:
            root_path: Root path of the directory tree.
            options: Options for directory tree printing.
        """
        from upathtools import to_upath

        self.root_path = to_upath(root_path)
        self.options = options or TreeOptions()

    def _get_sort_key(self, path: upath.UPath) -> tuple[bool, Any]:
        """Generate sort key based on current sort criteria.

        Args:
            path: Path to get sort key for.

        Returns:
            Tuple containing boolean indicating if path is a directory and
            the sort key based on the selected criteria.
        """
        info = _get_path_info(path)
        criteria_keys = {
            SortCriteria.NAME: lambda: (info["name"].lower(),),
            SortCriteria.SIZE: lambda: (info["size"],),
            SortCriteria.DATE: lambda: (info["mtime"],),
            SortCriteria.EXTENSION: lambda: (info["extension"], info["name"].lower()),
        }
        # Always sort directories first within each category
        return not path.is_dir(), criteria_keys[self.options.sort_criteria]()

    def _should_include(self, path: upath.UPath) -> bool:
        """Check if path should be included based on filters.

        Args:
            path: Path to check.

        Returns:
            True if the path should be included, False otherwise.
        """
        name = path.name

        if not self.options.show_hidden and name.startswith("."):
            return False

        if self.options.include_pattern and not self.options.include_pattern.match(name):
            return False

        if self.options.exclude_pattern and self.options.exclude_pattern.match(name):
            return False

        return not (
            self.options.allowed_extensions
            and (
                path.is_file()
                and path.suffix.lower() not in self.options.allowed_extensions
            )
        )

    def _is_directory_empty_after_filters(
        self,
        directory: upath.UPath,
        depth: int = 0,
    ) -> bool:
        """Recursively check if directory is empty after applying all filters.

        Args:
            directory: Directory to check.
            depth: Current depth of recursion.

        Returns:
            True if directory has no visible contents after filtering,
            False otherwise.
        """
        if self.options.max_depth is not None and depth > self.options.max_depth:
            return True

        try:
            # Get all paths and apply filters
            paths = [p for p in directory.iterdir() if self._should_include(p)]

            # If no paths remain after filtering, directory is considered empty
            if not paths:
                return True

            # For directories, recursively check if they're empty
            for path in paths:
                if path.is_dir():
                    # If a directory is not empty, this directory is not empty
                    if not self._is_directory_empty_after_filters(path, depth + 1):
                        return False
                else:
                    # If we find any visible file, directory is not empty
                    return False
            else:
                # If we only found empty directories, this directory is empty
                return True

        except (PermissionError, OSError):
            # Treat inaccessible directories as empty
            return True

    def _get_tree_entries(
        self, directory: upath.UPath, prefix: str = "", depth: int = 0
    ) -> list[tuple[str, upath.UPath, bool]]:
        """Generate tree entries with proper formatting.

        Args:
            directory: Directory to generate entries for.
            prefix: Prefix string for the entry.
            depth: Current depth of recursion.

        Returns:
            List of tuples containing prefix, path and boolean indicating if it's
            the last entry.
        """
        entries: list[tuple[str, upath.UPath, bool]] = []

        if self.options.max_depth is not None and depth > self.options.max_depth:
            return entries

        try:
            # Get all paths and apply sorting
            paths = sorted(
                directory.iterdir(),
                key=self._get_sort_key,
                reverse=self.options.reverse_sort,
            )
        except (PermissionError, OSError) as e:
            print(f"Error accessing {directory}: {e}")
            return entries

        # Filter paths and check if they're empty (if directories)
        visible_paths: list[upath.UPath] = []
        for path in paths:
            if not self._should_include(path):
                continue

            if (
                path.is_dir()
                and self.options.hide_empty
                and self._is_directory_empty_after_filters(path, depth + 1)
            ):
                continue
            visible_paths.append(path)

        # Process visible paths
        for i, path in enumerate(visible_paths):
            is_last = i == len(visible_paths) - 1
            connector = self.ELBOW if is_last else self.TEE

            entries.append((f"{prefix}{connector}", path, is_last))

            if path.is_dir():
                new_prefix = f"{prefix}{self.PIPE}" if not is_last else f"{prefix}    "
                entries.extend(self._get_tree_entries(path, new_prefix, depth + 1))

        return entries

    def get_tree_text(self) -> str:
        """Generate and return the directory tree as a string."""
        return "\n".join(self.iter_tree_lines())

    def iter_tree_lines(self) -> Iterator[str]:
        """Iterate the directory and yield the formatted lines.

        Included items as well as design is based on the configured options.
        """
        if not self.root_path.exists():
            msg = f"Path does not exist: {self.root_path}"
            raise FileNotFoundError(msg)

        # Check if root directory is empty after filtering
        if self.options.hide_empty and self._is_directory_empty_after_filters(
            self.root_path
        ):
            icon = self.DIRECTORY if self.options.show_icons else ""
            yield f"{icon} {self.root_path.name} (empty)"
            return

        root_icon = self.DIRECTORY if self.options.show_icons else ""
        yield f"{root_icon} {self.root_path.name}"

        for prefix, path, _is_last in self._get_tree_entries(self.root_path):
            info = _get_path_info(path)

            # Prepare icon
            icon = ""
            if self.options.show_icons:
                icon = (
                    self.DIRECTORY
                    if info["is_dir"]
                    else iconfilters.get_path_ascii_icon(path)
                )

            # Prepare additional information
            details: list[str] = []

            if self.options.show_size and not info["is_dir"]:
                details.append(f"{filters.do_filesizeformat(info['size'])}")

            if self.options.show_date:
                s = textfilters.format_timestamp(info["mtime"], self.options.date_format)
                details.append(s)
            if self.options.show_permissions:
                permissions = stat.filemode(info["mode"])
                details.append(permissions)

            details_str = f" ({', '.join(details)})" if details else ""

            yield f"{prefix}{icon} {path.name}{details_str}"


def get_directory_tree(
    root_path: str | os.PathLike[str],
    *,
    show_hidden: bool = False,
    show_size: bool = True,
    show_date: bool = False,
    show_permissions: bool = False,
    show_icons: bool = True,
    max_depth: int | None = None,
    include_pattern: Pattern[str] | None = None,
    exclude_pattern: Pattern[str] | None = None,
    allowed_extensions: set[str] | None = None,
    hide_empty: bool = True,
    sort_criteria: SortCriteria = SortCriteria.NAME,
    reverse_sort: bool = False,
    date_format: str = "%Y-%m-%d %H:%M:%S",
) -> str:
    """Create a DirectoryTree instance with the specified options.

    Args:
        root_path: Root path of the directory tree
        show_hidden: Whether to show hidden files/directories
        show_size: Whether to show file sizes
        show_date: Whether to show modification dates
        show_permissions: Whether to show file permissions
        show_icons: Whether to show icons for files/directories
        max_depth: Maximum depth to traverse (None for unlimited)
        include_pattern: Regex pattern for files/directories to include
        exclude_pattern: Regex pattern for files/directories to exclude
        allowed_extensions: Set of allowed file extensions
        hide_empty: Whether to hide empty directories
        sort_criteria: Criteria for sorting entries
        reverse_sort: Whether to reverse the sort order
        date_format: Format string for dates

    Returns:
        DirectoryTree: Configured DirectoryTree instance

    Example:
        ```python
        tree = create_directory_tree(
            ".",
            show_hidden=True,
            max_depth=3,
            allowed_extensions={".py", ".txt"},
            exclude_pattern=re.compile(r"__pycache__")
        )
        tree.print_tree()
        ```
    """
    options = TreeOptions(
        show_hidden=show_hidden,
        show_size=show_size,
        show_date=show_date,
        show_permissions=show_permissions,
        show_icons=show_icons,
        max_depth=max_depth,
        include_pattern=include_pattern,
        exclude_pattern=exclude_pattern,
        allowed_extensions=allowed_extensions,
        hide_empty=hide_empty,
        sort_criteria=sort_criteria,
        reverse_sort=reverse_sort,
        date_format=date_format,
    )

    return DirectoryTree(root_path, options).get_tree_text()


def main():
    # Example usage with various options
    options = TreeOptions(
        show_hidden=False,
        show_size=True,
        max_depth=4,
        # include_pattern=re.compile(r".*\.py$|.*\.txt$"),  # Only .py and .txt files
        exclude_pattern=re.compile(r"__pycache__"),
        allowed_extensions={".py", ".txt"},
        hide_empty=False,
    )
    tree = DirectoryTree(".", options)
    text = tree.get_tree_text()
    print(text)


if __name__ == "__main__":
    main()
