"""
SAP File Modifier - Automatically modify .sap files in Downloads folder
"""

__version__ = "0.1.0"
__license__ = "MIT"

from .modifier import find_and_modify_sap_files, modify_sap_file

__all__ = ["modify_sap_file", "find_and_modify_sap_files"]
