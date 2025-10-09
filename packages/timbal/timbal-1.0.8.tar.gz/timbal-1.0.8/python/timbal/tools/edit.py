"""
Edit tool for making targeted changes to existing files.

Performs exact string replacements in files with diff output.
Supports replacing all occurrences or just the first match.
Supports ~ (home directory) and environment variables in paths.
"""
import difflib
import os
from pathlib import Path

import structlog

from ..core.tool import Tool

logger = structlog.get_logger("timbal.tools.edit")


class Edit(Tool):

    def __init__(self, **kwargs):

        async def _edit(
            path: str,
            old_string: str,
            new_string: str,
            replace_all: bool = False,
            dry_run: bool = False
        ):
            """
            Edit a file by replacing old_string with new_string.

            Args:
                path: Path to the file to edit
                old_string: The exact string to replace
                new_string: The replacement string
                replace_all: If True, replace all occurrences. If False, replace only the first occurrence
                dry_run: If True, preview changes without writing

            Returns:
                Success message with diff of changes made
            """
            path = Path(os.path.expandvars(os.path.expanduser(path))).resolve()

            if not path.exists():
                raise FileNotFoundError(f"File does not exist: {path}")

            if path.is_dir():
                raise ValueError(f"Path is a directory, not a file: {path}")

            # Read original content
            try:
                original_content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                raise ValueError(f"File is not a text file or uses unsupported encoding: {path}")

            # Check if old_string exists in file
            if old_string not in original_content:
                return f"String not found in file: '{old_string}'"

            # Perform replacement
            if replace_all:
                new_content = original_content.replace(old_string, new_string)
                count = original_content.count(old_string)
                replacement_msg = f"Replaced {count} occurrence(s)"
            else:
                new_content = original_content.replace(old_string, new_string, 1)
                replacement_msg = "Replaced first occurrence"

            # Check if replacement actually changed anything
            if original_content == new_content:
                return "No changes made - old_string and new_string are identical"

            # Generate diff
            diff = "\n".join(difflib.unified_diff(
                original_content.splitlines(),
                new_content.splitlines(),
                fromfile=str(path) + " (original)",
                tofile=str(path) + " (edited)",
                lineterm=""
            ))

            if dry_run:
                return f"Preview - would edit {path}:\n{replacement_msg}\n\n{diff}"

            # Write the modified content
            path.write_text(new_content, encoding="utf-8")

            return f"File edited: {path}\n{replacement_msg}\n\nChanges:\n{diff}"

        super().__init__(
            name="edit",
            description="Edit an existing file by replacing old_string with new_string",
            handler=_edit,
            **kwargs
        )
