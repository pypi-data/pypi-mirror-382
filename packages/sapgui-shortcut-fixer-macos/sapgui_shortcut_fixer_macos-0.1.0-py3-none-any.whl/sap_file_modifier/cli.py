"""
Command-line interface for sap-file-modifier
"""

import argparse
import logging
import sys
from pathlib import Path
from textwrap import dedent

from .modifier import find_and_modify_sap_files
from .service import (
    get_service_log_path,
    get_service_status,
    install_launchd_service,
    uninstall_launchd_service,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,  # Log to stdout instead of stderr
)
logger = logging.getLogger(__name__)


def cmd_install(args):
    """Install the launchd service"""
    print("🔧 Installing SAP File Modifier service...")
    print()

    success, message = install_launchd_service(
        python_exe=sys.executable,
        enable_backup=args.backup,
    )

    if success:
        print("✅", message)
        print()
        print("📁 The service is now watching your Downloads folder.")
        print(f"📝 Logs: {get_service_log_path()}")
        print()
        print("To check status: sap-modifier status")
    else:
        print("❌", message)
        sys.exit(1)


def cmd_uninstall(args):
    """Uninstall the launchd service"""
    print("🗑️  Uninstalling SAP File Modifier service...")

    success, message = uninstall_launchd_service()

    if success:
        print("✅", message)
    else:
        print("❌", message)
        sys.exit(1)


def cmd_status(args):
    """Show service status"""
    status = get_service_status()

    print("📊 SAP File Modifier Status")
    print("=" * 50)
    print(f"Installed: {'✅ Yes' if status['installed'] else '❌ No'}")
    print(f"Running:   {'✅ Yes' if status['loaded'] else '❌ No'}")
    print(f"Plist:     {status['plist_path']}")
    print(f"Logs:      {status['log_path']}")
    print()

    if status["installed"] and not status["loaded"]:
        print("ℹ️  Service is installed but not loaded.")
        print("   This is normal - it only runs when files are added to Downloads.")
    elif not status["installed"]:
        print("ℹ️  Service is not installed. Run: sap-modifier install")


def cmd_process(args):
    """
    Process SAP files (called internally by launchd).
    This is the command that launchd triggers.
    """
    downloads = Path.home() / "Downloads"

    logger.info("SAP File Modifier triggered by launchd")
    logger.info(f"Scanning {downloads} for .sap files...")

    modified_count = find_and_modify_sap_files(
        directory=downloads, recent_only=True, backup=args.backup
    )

    if modified_count > 0:
        logger.info(f"✅ Modified {modified_count} file(s)")
    else:
        logger.debug("No .sap files to process")


def cmd_test(args):
    """Test the modifier on a specific file"""
    from .modifier import modify_sap_file

    filepath = Path(args.file)

    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    print(f"🔍 Testing on {filepath.name}...")

    if modify_sap_file(filepath, backup=args.backup):
        print(f"✅ Successfully modified {filepath.name}")
    else:
        print("⚠️  No changes needed or error occurred")


def cmd_logs(args):
    """Show recent log entries"""
    log_path = get_service_log_path()

    if not log_path.exists():
        print(f"📝 No logs found at {log_path}")
        print("   (Logs will appear after the service processes files)")
        return

    print(f"📝 Recent logs from {log_path}:")
    print("=" * 50)

    # Show last N lines
    lines = log_path.read_text().splitlines()
    for line in lines[-args.lines :]:
        print(line)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        prog="sap-modifier",
        description="Automatically modify SAP .sap files in Downloads folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
            Examples:
              sap-modifier install          Install the background service
              sap-modifier status           Check if service is running
              sap-modifier test file.sap    Test modification on a file
              sap-modifier logs             View recent logs
              sap-modifier uninstall        Remove the service
        """),
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install launchd service")
    install_parser.add_argument(
        "--backup",
        action="store_true",
        help="Enable automatic backups of modified files",
    )
    install_parser.set_defaults(func=cmd_install)

    # Uninstall command
    uninstall_parser = subparsers.add_parser(
        "uninstall", help="Uninstall launchd service"
    )
    uninstall_parser.set_defaults(func=cmd_uninstall)

    # Status command
    status_parser = subparsers.add_parser("status", help="Show service status")
    status_parser.set_defaults(func=cmd_status)

    # Process command (internal, called by launchd)
    process_parser = subparsers.add_parser("process", help=argparse.SUPPRESS)
    process_parser.add_argument("--backup", action="store_true")
    process_parser.set_defaults(func=cmd_process)

    # Test command
    test_parser = subparsers.add_parser("test", help="Test modification on a file")
    test_parser.add_argument("file", help="Path to .sap file to test")
    test_parser.add_argument(
        "--backup", action="store_true", help="Create a backup before modifying"
    )
    test_parser.set_defaults(func=cmd_test)

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show recent logs")
    logs_parser.add_argument(
        "-n",
        "--lines",
        type=int,
        default=20,
        help="Number of recent lines to show (default: 20)",
    )
    logs_parser.set_defaults(func=cmd_logs)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Run the command
    args.func(args)


if __name__ == "__main__":
    main()
