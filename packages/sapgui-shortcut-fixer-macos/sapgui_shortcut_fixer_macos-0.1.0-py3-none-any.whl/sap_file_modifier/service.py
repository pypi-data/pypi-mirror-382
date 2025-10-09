"""
macOS launchd service management
"""

import subprocess
from pathlib import Path
from typing import Dict, Tuple

PLIST_LABEL = "com.user.sapfilemodifier"
PLIST_FILENAME = f"{PLIST_LABEL}.plist"


def get_plist_path() -> Path:
    """Get the path to the launchd plist file"""
    return Path.home() / "Library" / "LaunchAgents" / PLIST_FILENAME


def get_service_log_path() -> Path:
    """Get the path to the service log file"""
    return Path.home() / "Library" / "Logs" / f"{PLIST_LABEL}.log"


def get_service_error_log_path() -> Path:
    """Get the path to the service error log file"""
    return Path.home() / "Library" / "Logs" / f"{PLIST_LABEL}.error.log"


def create_plist_content(python_exe: str, enable_backup: bool = False) -> dict:
    """
    Create the launchd plist configuration.

    Args:
        python_exe: Full path to Python interpreter
        enable_backup: Whether to enable automatic backups

    Returns:
        Dictionary representing the plist content
    """
    downloads_path = str(Path.home() / "Downloads")
    log_path = str(get_service_log_path())
    error_log_path = str(get_service_error_log_path())

    # Build command arguments using -m (module execution)
    program_args = [python_exe, "-m", "sap_file_modifier.cli", "process"]
    if enable_backup:
        program_args.append("--backup")

    plist_dict = {
        "Label": PLIST_LABEL,
        "ProgramArguments": program_args,
        "WatchPaths": [downloads_path],
        "ThrottleInterval": 3,
        "StandardOutPath": log_path,
        "StandardErrorPath": error_log_path,
        "RunAtLoad": False,
    }

    return plist_dict


def install_launchd_service(
    python_exe: str, enable_backup: bool = False
) -> Tuple[bool, str]:
    """
    Install the launchd service.

    Args:
        python_exe: Full path to Python interpreter
        enable_backup: Whether to enable automatic backups

    Returns:
        Tuple of (success: bool, message: str)
    """
    plist_path = get_plist_path()

    # Check if already installed
    if plist_path.exists():
        # Unload first
        uninstall_launchd_service()

    try:
        # Ensure LaunchAgents directory exists
        plist_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure Logs directory exists
        get_service_log_path().parent.mkdir(parents=True, exist_ok=True)

        # Create plist content
        plist_content = create_plist_content(python_exe, enable_backup)

        # Write plist file (using simple XML format)
        write_plist_file(plist_path, plist_content)

        # Load the service
        result = subprocess.run(
            ["launchctl", "load", str(plist_path)], capture_output=True, text=True
        )

        if result.returncode != 0:
            return False, f"Failed to load service: {result.stderr}"

        return True, f"Service installed successfully at {plist_path}"

    except Exception as e:
        return False, f"Installation failed: {e}"


def uninstall_launchd_service() -> Tuple[bool, str]:
    """
    Uninstall the launchd service.

    Returns:
        Tuple of (success: bool, message: str)
    """
    plist_path = get_plist_path()

    if not plist_path.exists():
        return True, "Service is not installed"

    try:
        # Unload the service (ignore errors if not loaded)
        subprocess.run(
            ["launchctl", "unload", str(plist_path)], capture_output=True, text=True
        )

        # Remove the plist file
        plist_path.unlink()

        return True, "Service uninstalled successfully"

    except Exception as e:
        return False, f"Uninstallation failed: {e}"


def get_service_status() -> Dict[str, any]:
    """
    Get the current status of the service.

    Returns:
        Dictionary with status information
    """
    plist_path = get_plist_path()
    log_path = get_service_log_path()

    status = {
        "installed": plist_path.exists(),
        "plist_path": str(plist_path),
        "log_path": str(log_path),
        "loaded": False,
    }

    if status["installed"]:
        # Check if loaded
        result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        status["loaded"] = PLIST_LABEL in result.stdout

    return status


def write_plist_file(path: Path, content: dict):
    """
    Write a plist file in XML format.

    Args:
        path: Path to write the plist file
        content: Dictionary content to write
    """
    # Simple plist XML generator (avoids external dependencies)
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
        '<plist version="1.0">',
        "<dict>",
    ]

    for key, value in content.items():
        xml_lines.append(f"    <key>{key}</key>")
        xml_lines.append(format_plist_value(value, indent=1))

    xml_lines.append("</dict>")
    xml_lines.append("</plist>")

    path.write_text("\n".join(xml_lines))


def format_plist_value(value, indent: int = 0) -> str:
    """Format a Python value as plist XML"""
    indent_str = "    " * indent

    if isinstance(value, bool):
        return f'{indent_str}<{"true" if value else "false"}/>'
    elif isinstance(value, int):
        return f"{indent_str}<integer>{value}</integer>"
    elif isinstance(value, str):
        return f"{indent_str}<string>{value}</string>"
    elif isinstance(value, list):
        lines = [f"{indent_str}<array>"]
        for item in value:
            lines.append(format_plist_value(item, indent + 1))
        lines.append(f"{indent_str}</array>")
        return "\n".join(lines)
    elif isinstance(value, dict):
        lines = [f"{indent_str}<dict>"]
        for k, v in value.items():
            lines.append(f"{indent_str}    <key>{k}</key>")
            lines.append(format_plist_value(v, indent + 1))
        lines.append(f"{indent_str}</dict>")
        return "\n".join(lines)
    else:
        return f"{indent_str}<string>{str(value)}</string>"
