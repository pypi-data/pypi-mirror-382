"""
Core SAP file modification logic
"""

import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


def modify_sap_file(filepath: Path, backup: bool = False) -> bool:
    """
    Modify a SAP .sap file by removing the first /M/ from the GuiParm line.

    Args:
        filepath: Path to the .sap file
        backup: Whether to create a backup before modifying

    Returns:
        True if file was modified, False otherwise
    """
    try:
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return False

        if not filepath.suffix.lower() == ".sap":
            logger.warning(f"Not a .sap file: {filepath}")
            return False

        # Read the file
        content = filepath.read_text(encoding="utf-8")

        # Check if GuiParm line exists and has /M/ at the start
        if "GuiParm=" not in content:
            logger.info(f"No GuiParm line found in {filepath.name}")
            return False

        # Pattern to match GuiParm=/M/ and replace with GuiParm=/
        # This will only replace the first /M/ after GuiParm=
        pattern = r"(GuiParm=)/M//"

        if not re.search(pattern, content):
            logger.info(f"No /M/ to remove in {filepath.name}")
            return False

        # Create backup if requested
        if backup:
            backup_path = filepath.with_suffix(".sap.bak")
            backup_path.write_text(content, encoding="utf-8")
            logger.info(f"Backup created: {backup_path}")

        # Perform replacement - remove /M/ from GuiParm=/M//
        modified_content = re.sub(pattern, r"\1/", content, count=1)

        # Write back
        filepath.write_text(modified_content, encoding="utf-8")

        logger.info(f"✅ Modified {filepath.name}")
        return True

    except Exception as e:
        logger.error(f"Error modifying {filepath}: {e}")
        return False


def is_recently_modified(filepath: Path, seconds: int = 10) -> bool:
    """
    Check if a file was modified within the last N seconds.

    Args:
        filepath: Path to check
        seconds: Number of seconds to consider as "recent"

    Returns:
        True if file was modified recently
    """
    try:
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
        age = datetime.now() - mtime
        return age < timedelta(seconds=seconds)
    except Exception:
        return False


def find_and_modify_sap_files(
    directory: Path, recent_only: bool = True, backup: bool = False
) -> int:
    """
    Find and modify all .sap files in a directory.

    Args:
        directory: Directory to search
        recent_only: Only process recently modified files
        backup: Create backups before modifying

    Returns:
        Number of files modified
    """
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return 0

    modified_count = 0

    for sap_file in directory.glob("*.sap"):
        # Skip if we only want recent files and this isn't recent
        if recent_only and not is_recently_modified(sap_file, seconds=10):
            continue

        if modify_sap_file(sap_file, backup=backup):
            modified_count += 1

    return modified_count
