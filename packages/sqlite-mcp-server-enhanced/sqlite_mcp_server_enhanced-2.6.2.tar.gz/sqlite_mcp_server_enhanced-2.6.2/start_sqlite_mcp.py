#!/usr/bin/env python3
"""
SQLite MCP Server Launcher
Flexible launcher that detects the project environment and sets up the database path appropriately.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_server_sqlite.server import main

def find_project_root():
    """
    Find the project root directory by looking for common project indicators.
    Returns the script's directory if no project root is found.
    """
    # Start from the script's directory instead of CWD to handle MCP execution context
    script_dir = Path(__file__).parent.resolve()
    
    # Look for common project root indicators
    indicators = [
        'pyproject.toml', 'package.json', '.git', 
        'requirements.txt', 'Cargo.toml', 'go.mod',
        'pom.xml', 'build.gradle', 'composer.json'
    ]
    
    # Check script directory and parents (this should find our project root)
    for path in [script_dir] + list(script_dir.parents):
        for indicator in indicators:
            if (path / indicator).exists():
                return path
    
    # Fallback to script directory if no indicators found
    return script_dir

def get_default_db_path():
    """
    Determine the default database path based on the environment.
    Only used when no explicit path is provided.
    Prioritizes: 
    1. ./data/ subdirectory if it exists
    2. Project root
    3. Current directory
    """
    project_root = find_project_root()
    
    # Check for data directory
    data_dir = project_root / "data"
    if data_dir.exists() and data_dir.is_dir():
        return str(data_dir / "database.db")
    
    # Use project root
    return str(project_root / "database.db")

if __name__ == "__main__":
    # Configure logging with reduced noise
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Reduce noise from MCP framework
    logging.getLogger('mcp.server.lowlevel.server').setLevel(logging.WARNING)
    logging.getLogger('mcp').setLevel(logging.WARNING)
    
    logger = logging.getLogger('sqlite_mcp_launcher')
    
    parser = argparse.ArgumentParser(
        description='Start SQLite MCP Server with flexible database path detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Use auto-detected database path
  %(prog)s --db-path ./my-data.db    # Use specific database file
  %(prog)s --db-path :memory:        # Use in-memory database
  %(prog)s --project-root /path/to/project --db-name mydb.db
        """
    )
    
    parser.add_argument(
        '--db-path', 
        type=str, 
        help='Explicit path to the SQLite database file (optional)'
    )
    
    parser.add_argument(
        '--project-root',
        type=str,
        help='Override project root directory detection'
    )
    
    parser.add_argument(
        '--db-name',
        type=str,
        default='sqlite_mcp.db',
        help='Database filename (used with project-root, default: sqlite_mcp.db)'
    )
    
    parser.add_argument(
        '--create-data-dir',
        action='store_true',
        help='Create a data/ subdirectory in project root for the database'
    )
    
    args = parser.parse_args()
    
    # Determine database path
    if args.db_path:
        db_path = args.db_path
        logger.info(f"Using explicit database path: {db_path}")
    elif args.create_data_dir:
        if args.project_root:
            project_root = Path(args.project_root)
        else:
            project_root = find_project_root()
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)
        db_path = str(data_dir / args.db_name)
        logger.debug(f"Created data directory and using: {db_path}")
    else:
        # No database specified - use default database in current directory
        if args.project_root:
            project_root = Path(args.project_root)
        else:
            project_root = find_project_root()
        db_path = str(project_root / args.db_name)
        logger.debug(f"Using default database: {db_path}")
    
    # Ensure parent directory exists
    db_path_obj = Path(db_path)
    if db_path != ":memory:":
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Database location: {db_path_obj.absolute()}")
    
    logger.info(f"SQLite MCP Server ready with database: {db_path}")
    asyncio.run(main(db_path))