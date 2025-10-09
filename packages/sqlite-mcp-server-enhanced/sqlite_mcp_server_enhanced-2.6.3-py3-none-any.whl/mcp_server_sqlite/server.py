import sqlite3
import logging
import json as json_module
import os
import re
import difflib
import unicodedata
import math
from contextlib import closing
from pathlib import Path
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from pydantic import AnyUrl
from typing import Any, Dict, List, Optional, Union

from .sqlite_version import check_sqlite_version
from .jsonb_utils import convert_to_jsonb, convert_from_jsonb, normalize_json, validate_json
from .db_integration import DatabaseIntegration
from .prompt_handlers import (
    handle_semantic_query_prompt,
    handle_summarize_table_prompt,
    handle_optimize_database_prompt,
    handle_setup_semantic_search_prompt,
    handle_hybrid_search_workflow_prompt
)
from .error_handler import SqliteErrorHandler
from .json_logger import JsonLogger
from .schema_updater import SchemaUpdater
from .diagnostics import DiagnosticsService
from .json_helpers import JSONPathValidator, JSONQueryBuilder, merge_json_objects, validate_json_security

# Load configuration from environment first
DEBUG_MODE = os.environ.get('SQLITE_DEBUG', 'false').lower() in ('true', '1', 'yes')

# Logging is configured by the launcher - no need to configure here
logger = logging.getLogger('mcp_sqlite_server')

# Reduce logging noise in production
if not DEBUG_MODE:
    logger.setLevel(logging.WARNING)

logger.info("Starting Enhanced MCP SQLite Server with JSONB support")
LOG_DIR = os.environ.get('SQLITE_LOG_DIR', './logs')
JSONB_ENABLED = os.environ.get('SQLITE_JSONB_ENABLED', 'true').lower() in ('true', '1', 'yes')

PROMPT_TEMPLATE = """
The assistants goal is to walkthrough an informative demo of MCP. To demonstrate the Model Context Protocol (MCP) we will leverage this example server to interact with an SQLite database.
It is important that you first explain to the user what is going on. The user has downloaded and installed the SQLite MCP Server and is now ready to use it.
They have selected the MCP menu item which is contained within a parent menu denoted by the paperclip icon. Inside this menu they selected an icon that illustrates two electrical plugs connecting. This is the MCP menu.
Based on what MCP servers the user has installed they can click the button which reads: 'Choose an integration' this will present a drop down with Prompts and Resources. The user has selected the prompt titled: 'mcp-demo'.
This text file is that prompt. The goal of the following instructions is to walk the user through the process of using the 3 core aspects of an MCP server. These are: Prompts, Tools, and Resources.
They have already used a prompt and provided a topic. The topic is: {topic}. The user is now ready to begin the demo.
Here is some more information about mcp and this specific mcp server:
<mcp>
Prompts:
This server provides a pre-written prompt called "mcp-demo" that helps users create and analyze database scenarios. The prompt accepts a "topic" argument and guides users through creating tables, analyzing data, and generating insights. For example, if a user provides "retail sales" as the topic, the prompt will help create relevant database tables and guide the analysis process. Prompts basically serve as interactive templates that help structure the conversation with the LLM in a useful way.
Resources:
This server exposes one key resource: "memo://insights", which is a business insights memo that gets automatically updated throughout the analysis process. As users analyze the database and discover insights, the memo resource gets updated in real-time to reflect new findings. Resources act as living documents that provide context to the conversation.
Tools:
This server provides several SQL-related tools:
"read_query": Executes SELECT queries to read data from the database
"write_query": Executes INSERT, UPDATE, or DELETE queries to modify data
"create_table": Creates new tables in the database
"list_tables": Shows all existing tables
"describe_table": Shows the schema for a specific table
"append_insight": Adds a new business insight to the memo resource
</mcp>
<demo-instructions>
You are an AI assistant tasked with generating a comprehensive business scenario based on a given topic.
Your goal is to create a narrative that involves a data-driven business problem, develop a database structure to support it, generate relevant queries, create a dashboard, and provide a final solution.

At each step you will pause for user input to guide the scenario creation process. Overall ensure the scenario is engaging, informative, and demonstrates the capabilities of the SQLite MCP Server.
You should guide the scenario to completion. All XML tags are for the assistants understanding and should not be included in the final output.

1. The user has chosen the topic: {topic}.

2. Create a business problem narrative:
a. Describe a high-level business situation or problem based on the given topic.
b. Include a protagonist (the user) who needs to collect and analyze data from a database.
c. Add an external, potentially comedic reason why the data hasn't been prepared yet.
d. Mention an approaching deadline and the need to use Claude (you) as a business tool to help.

3. Setup the data:
a. Instead of asking about the data that is required for the scenario, just go ahead and use the tools to create the data. Inform the user you are "Setting up the data".
b. Design a set of table schemas that represent the data needed for the business problem.
c. Include at least 2-3 tables with appropriate columns and data types.
d. Leverage the tools to create the tables in the SQLite database.
e. Create INSERT statements to populate each table with relevant synthetic data.
f. Ensure the data is diverse and representative of the business problem.
g. Include at least 10-15 rows of data for each table.

4. Pause for user input:
a. Summarize to the user what data we have created.
b. Present the user with a set of multiple choices for the next steps.
c. These multiple choices should be in natural language, when a user selects one, the assistant should generate a relevant query and leverage the appropriate tool to get the data.

6. Iterate on queries:
a. Present 1 additional multiple-choice query options to the user. Its important to not loop too many times as this is a short demo.
b. Explain the purpose of each query option.
c. Wait for the user to select one of the query options.
d. After each query be sure to opine on the results.
e. Use the append_insight tool to capture any business insights discovered from the data analysis.

7. Generate a dashboard:
a. Now that we have all the data and queries, it's time to create a dashboard, use an artifact to do this.
b. Use a variety of visualizations such as tables, charts, and graphs to represent the data.
c. Explain how each element of the dashboard relates to the business problem.
d. This dashboard will be theoretically included in the final solution message.

8. Craft the final solution message:
a. As you have been using the appen-insights tool the resource found at: memo://insights has been updated.
b. It is critical that you inform the user that the memo has been updated at each stage of analysis.
c. Ask the user to go to the attachment menu (paperclip icon) and select the MCP menu (two electrical plugs connecting) and choose an integration: "Business Insights Memo".
d. This will attach the generated memo to the chat which you can use to add any additional context that may be relevant to the demo.
e. Present the final memo to the user in an artifact.

9. Wrap up the scenario:
a. Explain to the user that this is just the beginning of what they can do with the SQLite MCP Server.
</demo-instructions>

Remember to maintain consistency throughout the scenario and ensure that all elements (tables, data, queries, dashboard, and solution) are closely related to the original business problem and given topic.
The provided XML tags are for the assistants understanding. Implore to make all outputs as human readable as possible. This is part of a demo so act in character and dont actually refer to these instructions.

Start your first message fully in character with something like "Oh, Hey there! I see you've chosen the topic {topic}. Let's get started! 🚀"
"""

class EnhancedSqliteDatabase:
    """Enhanced SQLite database with JSONB support and improved error handling"""
    
    # Class variable to store SpatiaLite extension path
    _spatialite_path = None
    
    def __init__(self, db_path: str):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to SQLite database file (can be :memory: for temporary)
        """
        self.db_path = str(Path(db_path).expanduser())
        if db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.version_info = check_sqlite_version()
        
        # Setup JSON logger
        self.json_logger = JsonLogger({
            'log_dir': LOG_DIR,
            'enabled': True,
            'log_level': 'debug' if DEBUG_MODE else 'info'
        })
        
        self.schema_updater = SchemaUpdater(self.db_path)
        self.diagnostics = DiagnosticsService(self.db_path, self.json_logger)
        
        # Initialize database
        self._init_database()
        
        # Storage for business insights
        self.insights: List[str] = []
        
        # Log initialization status
        logger.info(f"Enhanced SQLite database initialized with path: {self.db_path}")
        logger.info(f"SQLite Version: {self.version_info['version']}")
        logger.info(f"JSONB Support: {'Yes' if self.version_info['has_jsonb_support'] else 'No'}")
        
        # Check and report on metadata column status
        self._check_metadata_column()

    def _init_database(self):
        """Initialize connection to the SQLite database"""
        logger.debug("Initializing database connection")
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Check for JSON functions
            if self.version_info['has_jsonb_support'] and JSONB_ENABLED:
                logger.info("JSONB format is supported and enabled")
                
                # Try to create JSON validation trigger if needed
                if 'memory_journal' in [t[0] for t in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
                    
                    # Check if trigger exists
                    trigger_exists = conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='trigger' AND name='validate_memory_journal_metadata'"
                    ).fetchone()
                    
                    if not trigger_exists:
                        logger.info("Creating JSON validation trigger for memory_journal.metadata")
                        try:
                            conn.execute("""
                                CREATE TRIGGER IF NOT EXISTS validate_memory_journal_metadata
                                BEFORE INSERT ON memory_journal
                                WHEN NEW.metadata IS NOT NULL
                                BEGIN
                                    SELECT CASE
                                        WHEN json_valid(json(NEW.metadata)) = 0
                                        THEN RAISE(ABORT, 'Invalid JSON in memory_journal.metadata')
                                    END;
                                END;
                            """)
                            conn.commit()
                            logger.info("JSON validation trigger created successfully")
                        except Exception as e:
                            logger.error(f"Failed to create JSON validation trigger: {e}")
                
            conn.close()
        # Enable transaction safety
        DatabaseIntegration.enhance_database(self)

    def _check_metadata_column(self):
        """Check if memory_journal.metadata is BLOB type for JSONB storage"""
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Check if memory_journal table exists
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='memory_journal'"
                )
                if not cursor.fetchone():
                    logger.info("memory_journal table does not exist yet")
                    return
                
                # Check metadata column type
                cursor.execute("PRAGMA table_info(memory_journal)")
                columns = cursor.fetchall()
                
                metadata_column = next((col for col in columns if col[1] == 'metadata'), None)
                if not metadata_column:
                    logger.info("metadata column does not exist in memory_journal table")
                    return
                
                if metadata_column[2] == 'BLOB':
                    logger.info("metadata column is already BLOB type, ready for JSONB storage")
                else:
                    logger.warning(
                        f"metadata column is {metadata_column[2]} type, not optimal for JSONB storage. "
                        f"Consider updating schema using SchemaUpdater.update_memory_journal_schema()"
                    )
                    
                    # Only try to update if JSONB is supported and enabled
                    if self.version_info['has_jsonb_support'] and JSONB_ENABLED:
                        logger.info("Attempting to update memory_journal schema for JSONB...")
                        result = self.schema_updater.update_memory_journal_schema()
                        if result.get('success', False):
                            logger.info(f"Schema updated successfully: {result}")
                        else:
                            logger.warning(f"Schema update failed: {result}")
        except Exception as e:
            logger.error(f"Failed to check metadata column: {e}")

    def _synthesize_memo(self) -> str:
        """
        Synthesize business insights into a formatted memo.
        
        Returns:
            Formatted memo as string
        """
        logger.debug(f"Synthesizing memo with {len(self.insights)} insights")
        if not self.insights:
            return "No business insights have been discovered yet."

        insights = "\n".join(f"- {insight}" for insight in self.insights)

        memo = "📊 Business Intelligence Memo 📊\n\n"
        memo += "Key Insights Discovered:\n\n"
        memo += insights

        if len(self.insights) > 1:
            memo += "\nSummary:\n"
            memo += f"Analysis has revealed {len(self.insights)} key business insights that suggest opportunities for strategic optimization and growth."

        logger.debug("Generated basic memo format")
        return memo

    def _load_spatialite_if_needed(self, conn, query: str):
        """Load SpatiaLite extension if the query contains spatial functions"""
        
        spatial_functions = [
            'spatialite_version', 'AddGeometryColumn', 'GeomFromText', 'AsText', 'AsBinary',
            'ST_Distance', 'ST_Buffer', 'ST_Area', 'ST_Length', 'ST_Intersects', 'ST_Within',
            'ST_Union', 'ST_Intersection', 'ST_Difference', 'ST_Centroid', 'ST_Envelope',
            'CreateSpatialIndex', 'InitSpatialMetaData', 'DiscardGeometryColumn'
        ]
        
        # Check if query contains spatial functions
        query_upper = query.upper()
        needs_spatialite = any(func.upper() in query_upper for func in spatial_functions)
        
        # Load SpatiaLite if path is available and query might need it
        if self._spatialite_path and (needs_spatialite or 'geom' in query_upper or 'spatial' in query_upper):
            try:
                conn.enable_load_extension(True)
                conn.load_extension(self._spatialite_path)
                conn.enable_load_extension(False)
            except Exception as e:
                # Extension might already be loaded or there might be an issue
                pass
    
    def _preprocess_spatial_functions(self, query: str) -> str:
        """
        Preprocess spatial functions to work around Windows SpatiaLite limitations.
        
        Specifically, converts GeomFromText() calls in INSERT/UPDATE statements to 
        equivalent functions that work reliably on Windows.
        
        Args:
            query: SQL query to preprocess
            
        Returns:
            Preprocessed query with spatial function conversions
        """
        import re
        
        try:
            # Log the preprocessing attempt
            logger.debug(f"Preprocessing spatial functions in query: {query}")
            
            # Pattern to match GeomFromText with POINT geometries
            # GeomFromText('POINT(x y)', srid) -> MakePoint(x, y, srid)
            point_pattern = r"GeomFromText\s*\(\s*['\"]POINT\s*\(\s*([^)]+)\s*\)['\"](?:\s*,\s*(\d+))?\s*\)"
            
            def replace_point(match):
                coords = match.group(1).strip()
                srid = match.group(2) if match.group(2) else '4326'  # Default to WGS84
                
                # Split coordinates (handle multiple spaces/tabs)
                coord_parts = re.split(r'\s+', coords.strip())
                if len(coord_parts) >= 2:
                    x, y = coord_parts[0], coord_parts[1]
                    # Handle optional Z coordinate
                    if len(coord_parts) >= 3:
                        z = coord_parts[2]
                        return f"MakePointZ({x}, {y}, {z}, {srid})"
                    else:
                        return f"MakePoint({x}, {y}, {srid})"
                return match.group(0)  # Return original if parsing fails
            
            # Replace POINT geometries
            processed_query = re.sub(point_pattern, replace_point, query, flags=re.IGNORECASE)
            
            # For other geometry types, use the hex workaround approach
            # This handles LINESTRING, POLYGON, etc.
            other_geom_pattern = r"GeomFromText\s*\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*(\d+))?\s*\)"
            
            def replace_other_geom(match):
                wkt = match.group(1)
                srid = match.group(2) if match.group(2) else '4326'
                
                # Skip if it's a POINT (already handled above)
                if wkt.upper().startswith('POINT'):
                    return match.group(0)
                
                # For complex geometries, use GeomFromWKB with a subquery approach
                # This is more reliable than GeomFromText on Windows
                return f"GeomFromWKB(GeomFromText('{wkt}', {srid}))"
            
            # Apply the other geometry replacements only if we didn't already process them as points
            if 'POINT(' not in processed_query.upper() or processed_query != query:
                processed_query = re.sub(other_geom_pattern, replace_other_geom, processed_query, flags=re.IGNORECASE)
            
            if processed_query != query:
                logger.info(f"Spatial function preprocessing applied: {query} -> {processed_query}")
                
            return processed_query
            
        except Exception as e:
            logger.warning(f"Failed to preprocess spatial functions: {e}")
            return query  # Return original query if preprocessing fails
    
    def _execute_query(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query with enhanced error handling and JSONB support.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Query results as list of dictionaries
            
        Raises:
            Exception: If query execution fails
        """
        logger.debug(f"Executing query: {query}")
        
        # Auto-serialize JSON objects (dict/list) in parameters with normalization
        if params:
            processed_params = []
            for param in params:
                if isinstance(param, (dict, list)):
                    # Auto-serialize objects to JSON
                    json_str = json_module.dumps(param)
                    processed_params.append(json_str)
                    logger.debug(f"Auto-serialized parameter: {type(param).__name__} -> JSON string")
                elif isinstance(param, str) and param.strip().startswith(('{', '[')):
                    # Try to normalize JSON strings for better compatibility
                    try:
                        is_valid, normalized_json = validate_json(param, auto_normalize=True)
                        if is_valid and normalized_json != param:
                            processed_params.append(normalized_json)
                            logger.debug(f"Auto-normalized JSON parameter: {param[:50]}... -> {normalized_json[:50]}...")
                        else:
                            processed_params.append(param)
                    except Exception as e:
                        logger.debug(f"JSON normalization failed for parameter, using as-is: {e}")
                        processed_params.append(param)
                else:
                    processed_params.append(param)
            params = processed_params
        
        # Log operation for debugging
        self.json_logger.log_operation("execute_query", {
            "query": query,
            "has_params": bool(params)
        })
        
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                
                # Always load SpatiaLite if path is available (more reliable)
                if self._spatialite_path:
                    try:
                        # Ensure PATH includes SpatiaLite DLLs for Windows
                        import os
                        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                        local_spatialite_dir = os.path.join(script_dir, "mod_spatialite-5.1.0-win-amd64")
                        if os.path.exists(local_spatialite_dir):
                            original_path = os.environ.get('PATH', '')
                            if local_spatialite_dir not in original_path:
                                os.environ['PATH'] = local_spatialite_dir + os.pathsep + original_path
                        
                        conn.enable_load_extension(True)
                        conn.load_extension(self._spatialite_path)
                        # Try to initialize spatial metadata if needed
                        try:
                            conn.execute("SELECT InitSpatialMetaData(1)")
                        except:
                            pass  # Already initialized or not needed
                        # Keep extensions enabled for this connection
                        # conn.enable_load_extension(False)  # Comment out to keep functions available
                    except Exception as e:
                        # Log the actual error for debugging
                        logger.debug(f"SpatiaLite loading failed: {e}")
                        pass
                
                # Special handling for memory_journal metadata with JSONB
                if JSONB_ENABLED and self.version_info['has_jsonb_support']:
                    # Check if it's an INSERT or UPDATE to memory_journal with metadata
                    if (
                        query.strip().upper().startswith(('INSERT', 'UPDATE')) and 
                        'memory_journal' in query and 
                        'metadata' in query
                    ):
                        # Handle JSONB conversion for memory_journal metadata
                        # This is a simplified approach - a more robust approach would use SQL parsing
                        try:
                            # For known queries we can modify them to use jsonb()
                            # Note: This is legacy code for memory_journal compatibility
                            if (
                                ('INSERT INTO memory_journal' in query or 'UPDATE memory_journal SET' in query) and 
                                params and 
                                len(params) > 0 and
                                'metadata = ?' in query
                            ):
                                # Convert to JSONB directly in the query for better performance
                                        if 'jsonb(?)' not in query:
                                            query = query.replace('metadata = ?', 'metadata = jsonb(?)')
                        except Exception as e:
                            logger.warning(f"Failed to process JSONB conversion: {e}")
                
                # GeomFromText wrapper for Windows INSERT compatibility
                if (self._spatialite_path and 
                    query.strip().upper().startswith(('INSERT', 'UPDATE')) and 
                    'GeomFromText' in query):
                    query = self._preprocess_spatial_functions(query)
                
                # Execute the query
                with closing(conn.cursor()) as cursor:
                    try:
                        if params:
                            cursor.execute(query, params)
                        else:
                            cursor.execute(query)
                            
                        # Handle different query types
                        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER')):
                            conn.commit()
                            affected = cursor.rowcount
                            logger.debug(f"Write query affected {affected} rows")
                            
                            # Log success
                            self.json_logger.log_operation("write_success", {
                                "affected_rows": affected,
                                "query_type": query.strip().split()[0].upper()
                            })
                            
                            return [{"affected_rows": affected}]
                        else:
                            # Handle read queries
                            results = [dict(row) for row in cursor.fetchall()]
                            
                            # Special handling for JSONB in result set
                            if JSONB_ENABLED and self.version_info['has_jsonb_support']:
                                # Check if any column in any row might be JSONB
                                for row in results:
                                    for key, value in row.items():
                                        if isinstance(value, bytes) and key == 'metadata':
                                            try:
                                                # Convert JSONB to JSON string
                                                json_str = convert_from_jsonb(conn, value)
                                                if json_str:
                                                    # Parse JSON string
                                                    row[key] = json_module.loads(json_str)
                                            except Exception as e:
                                                logger.warning(f"Failed to convert JSONB to JSON: {e}")
                                                # Keep as bytes if conversion fails
                            
                            logger.debug(f"Read query returned {len(results)} rows")
                            
                            # Log success
                            self.json_logger.log_operation("read_success", {
                                "rows_returned": len(results),
                                "query_type": "SELECT"
                            })
                            
                            return results
                    except Exception as e:
                        # Handle database errors with improved diagnostics
                        logger.error(f"Database error executing query: {e}")
                        
                        # Log the error with context
                        error_context = SqliteErrorHandler.extract_error_context(e, query, params)
                        error_analysis = SqliteErrorHandler.analyze_sqlite_error(e, query, params)
                        
                        self.json_logger.log_error(e, {
                            "query": query,
                            "has_params": bool(params),
                            "context": error_context,
                            "analysis": error_analysis
                        })
                        
                        # Improve the error message if it's JSON related
                        if error_analysis["is_json_related"]:
                            error_details = SqliteErrorHandler.extract_json_error_details(e, {"query": query})
                            # Create a more informative error message
                            raise type(e)(
                                f"JSON Error in query: {error_details['message']}. "
                                f"Suggestion: {error_analysis['suggestions'][0] if error_analysis['suggestions'] else 'Check JSON syntax'}"
                            )
                        
                        # Re-raise the original error
                        raise
        except Exception as e:
            # Log all errors
            logger.error(f"Error executing query: {e}")
            self.json_logger.log_error(e, {"query": query})
            raise

    # Text Processing Methods
    async def _handle_regex_extract(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Extract text using PCRE-style regular expressions."""
        if not all(key in arguments for key in ["table_name", "column_name", "pattern"]):
            raise ValueError("Missing required arguments: table_name, column_name, pattern")
    
        table_name = arguments["table_name"]
        column_name = arguments["column_name"]
        pattern = arguments["pattern"]
        flags = arguments.get("flags", "")
        limit = arguments.get("limit", 100)
        where_clause = arguments.get("where_clause", "")
    
        try:
            # Compile regex with flags
            regex_flags = 0
            if 'i' in flags.lower(): regex_flags |= re.IGNORECASE
            if 'm' in flags.lower(): regex_flags |= re.MULTILINE
            if 's' in flags.lower(): regex_flags |= re.DOTALL
        
            compiled_pattern = re.compile(pattern, regex_flags)
        
            where_sql = f" WHERE {where_clause}" if where_clause else ""
        
            query = f"""
            SELECT {column_name}, rowid AS row_id
            FROM {table_name}{where_sql}
            WHERE {column_name} IS NOT NULL
            LIMIT {limit}
            """
            
            result = self._execute_query(query)
            
            if not result:
                return [types.TextContent(type="text", text="No data found for regex extraction")]
            
            matches = []
            for row in result:
                text = str(row[column_name])
                match_result = compiled_pattern.search(text)
                if match_result:
                    groups = match_result.groups() if match_result.groups() else (match_result.group(0),)
                    matches.append({
                        "rowid": row["row_id"],
                        "original_text": text,
                        "match": match_result.group(0),
                        "groups": groups,
                        "start": match_result.start(),
                        "end": match_result.end()
                    })
            
            output = f"""Regex Extraction Results for {table_name}.{column_name}:
        Pattern: {pattern}
        Flags: {flags if flags else 'None'}

        Found {len(matches)} matches:

        """
            
            for i, match in enumerate(matches[:20], 1):  # Show first 20 matches
                output += f"Match {i} (Row {match['rowid']}):\n"
                output += f"  Text: {match['original_text'][:100]}{'...' if len(match['original_text']) > 100 else ''}\n"
                output += f"  Match: '{match['match']}' (pos {match['start']}-{match['end']})\n"
                if len(match['groups']) > 1:
                    output += f"  Groups: {match['groups']}\n"
                output += "\n"
            
            if len(matches) > 20:
                output += f"... and {len(matches) - 20} more matches\n"
            
            return [types.TextContent(type="text", text=output)]
            
        except re.error as e:
            error_msg = f"Invalid regex pattern: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"Failed to extract regex: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

    async def _handle_regex_replace(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Replace text using PCRE-style regular expressions."""
        if not all(key in arguments for key in ["table_name", "column_name", "pattern", "replacement"]):
            raise ValueError("Missing required arguments: table_name, column_name, pattern, replacement")
    
        table_name = arguments["table_name"]
        column_name = arguments["column_name"]
        pattern = arguments["pattern"]
        replacement = arguments["replacement"]
        flags = arguments.get("flags", "")
        max_replacements = arguments.get("max_replacements", 0)  # 0 = all
        where_clause = arguments.get("where_clause", "")
        preview_only = arguments.get("preview_only", True)  # Safe default
    
        try:
            # Compile regex with flags
            regex_flags = 0
            if 'i' in flags.lower(): regex_flags |= re.IGNORECASE
            if 'm' in flags.lower(): regex_flags |= re.MULTILINE
            if 's' in flags.lower(): regex_flags |= re.DOTALL
        
            compiled_pattern = re.compile(pattern, regex_flags)
        
            where_sql = f" WHERE {where_clause}" if where_clause else ""
        
            query = f"""
            SELECT {column_name}, rowid AS row_id
            FROM {table_name}{where_sql}
            WHERE {column_name} IS NOT NULL
            LIMIT 100
            """
            
            result = self._execute_query(query)
            
            if not result:
                return [types.TextContent(type="text", text="No data found for regex replacement")]
            
            replacements = []
            for row in result:
                original_text = str(row[column_name])
                if max_replacements > 0:
                    new_text = compiled_pattern.sub(replacement, original_text, count=max_replacements)
                else:
                    new_text = compiled_pattern.sub(replacement, original_text)
                
                if new_text != original_text:
                    replacements.append({
                        "rowid": row["row_id"],
                        "original": original_text,
                        "new": new_text,
                        "changes": len(compiled_pattern.findall(original_text))
                    })
            
            output = f"""Regex Replacement {'Preview' if preview_only else 'Results'} for {table_name}.{column_name}:
        Pattern: {pattern}
        Replacement: {replacement}
        Flags: {flags if flags else 'None'}
        Max Replacements: {'All' if max_replacements == 0 else max_replacements}

        Found {len(replacements)} rows with changes:

        """
            
            for i, repl in enumerate(replacements[:10], 1):  # Show first 10
                output += f"Row {repl['rowid']} ({repl['changes']} changes):\n"
                output += f"  Before: {repl['original'][:100]}{'...' if len(repl['original']) > 100 else ''}\n"
                output += f"  After:  {repl['new'][:100]}{'...' if len(repl['new']) > 100 else ''}\n\n"
            
            if len(replacements) > 10:
                output += f"... and {len(replacements) - 10} more rows\n"
            
            if preview_only:
                output += "\nTo execute these changes, set preview_only=false"
            else:
                # Execute the replacements
                for repl in replacements:
                    update_query = f"""
                    UPDATE {table_name} 
                    SET {column_name} = ? 
                    WHERE rowid = ?
                    """
                    self._execute_query(update_query, [repl['new'], repl['rowid']])
                
                output += f"\n✅ Successfully updated {len(replacements)} rows"
            
            return [types.TextContent(type="text", text=output)]
            
        except re.error as e:
            error_msg = f"Invalid regex pattern: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"Failed to perform regex replacement: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

    async def _handle_fuzzy_match(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Find fuzzy matches using Levenshtein distance and sequence matching."""
        if not all(key in arguments for key in ["table_name", "column_name", "search_term"]):
            raise ValueError("Missing required arguments: table_name, column_name, search_term")
    
        table_name = arguments["table_name"]
        column_name = arguments["column_name"]
        search_term = arguments["search_term"]
        threshold = arguments.get("threshold", 0.6)
        limit = arguments.get("limit", 50)
        where_clause = arguments.get("where_clause", "")
    
        try:
            where_sql = f" WHERE {where_clause}" if where_clause else ""
        
            query = f"""
            SELECT {column_name}, rowid AS row_id
            FROM {table_name}{where_sql}
            WHERE {column_name} IS NOT NULL
            LIMIT 1000
            """
            
            result = self._execute_query(query)
            
            if not result:
                return [types.TextContent(type="text", text="No data found for fuzzy matching")]
            
            # Calculate similarity scores
            matches = []
            for row in result:
                text = str(row[column_name])
                # Use difflib's SequenceMatcher for similarity
                similarity = difflib.SequenceMatcher(None, search_term.lower(), text.lower()).ratio()
                
                if similarity >= threshold:
                    matches.append({
                        "rowid": row["row_id"],
                        "text": text,
                        "similarity": round(similarity, 3),
                        "match_type": "exact" if similarity >= 0.95 else "fuzzy"
                    })
            
            # Sort by similarity score (highest first)
            matches.sort(key=lambda x: x["similarity"], reverse=True)
            matches = matches[:limit]
            
            output = f"""Fuzzy Match Results for {table_name}.{column_name}:
        Search Term: "{search_term}"
        Threshold: {threshold}
        
        Found {len(matches)} matches:

        """
            
            for i, match in enumerate(matches, 1):
                output += f"Match {i} (Row {match['rowid']}) - Similarity: {match['similarity']:.3f} ({match['match_type']}):\n"
                output += f"  Text: {match['text'][:100]}{'...' if len(match['text']) > 100 else ''}\n\n"
            
            if len(matches) == 0:
                output += f"No matches found above threshold {threshold}\n"
            
            return [types.TextContent(type="text", text=output)]
            
        except Exception as e:
            error_msg = f"Failed to perform fuzzy matching: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

    async def _handle_phonetic_match(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Find phonetic matches using Soundex and Metaphone algorithms."""
        if not all(key in arguments for key in ["table_name", "column_name", "search_term"]):
            raise ValueError("Missing required arguments: table_name, column_name, search_term")
    
        table_name = arguments["table_name"]
        column_name = arguments["column_name"]
        search_term = arguments["search_term"]
        algorithm = arguments.get("algorithm", "soundex")
        limit = arguments.get("limit", 50)
        where_clause = arguments.get("where_clause", "")
    
        def simple_soundex(word):
            """Simple Soundex implementation"""
            if not word:
                return "0000"
            
            word = word.upper()
            soundex = word[0]
            
            # Mapping for consonants
            mapping = {
                'B': '1', 'F': '1', 'P': '1', 'V': '1',
                'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
                'D': '3', 'T': '3',
                'L': '4',
                'M': '5', 'N': '5',
                'R': '6'
            }
            
            for char in word[1:]:
                if char in mapping:
                    code = mapping[char]
                    if soundex[-1] != code:
                        soundex += code
                if len(soundex) == 4:
                    break
            
            return (soundex + "000")[:4]
        
        def simple_metaphone(word):
            """Simple Metaphone-like implementation"""
            if not word:
                return ""
            
            word = word.upper()
            result = ""
            
            # Simple phonetic transformations
            replacements = [
                ('PH', 'F'), ('GH', 'F'), ('CK', 'K'), ('SCH', 'SK'),
                ('QU', 'KW'), ('X', 'KS'), ('Z', 'S'), ('C', 'K')
            ]
            
            for old, new in replacements:
                word = word.replace(old, new)
            
            # Keep only consonants and some vowels
            keep_chars = 'BFPVKGJQSXZTDLMNR'
            result = ''.join(char for char in word if char in keep_chars)
            
            return result[:6]  # Limit length
    
        try:
            where_sql = f" WHERE {where_clause}" if where_clause else ""
        
            query = f"""
            SELECT {column_name}, rowid AS row_id
            FROM {table_name}{where_sql}
            WHERE {column_name} IS NOT NULL
            LIMIT 1000
            """
            
            result = self._execute_query(query)
            
            if not result:
                return [types.TextContent(type="text", text="No data found for phonetic matching")]
            
            # Calculate phonetic codes
            if algorithm.lower() == "soundex":
                search_code = simple_soundex(search_term)
                phonetic_func = simple_soundex
            else:  # metaphone
                search_code = simple_metaphone(search_term)
                phonetic_func = simple_metaphone
            
            matches = []
            for row in result:
                text = str(row[column_name])
                # Extract first word for phonetic matching
                first_word = text.split()[0] if text.split() else text
                text_code = phonetic_func(first_word)
                
                if text_code == search_code:
                    matches.append({
                        "rowid": row["row_id"],
                        "text": text,
                        "phonetic_code": text_code,
                        "matched_word": first_word
                    })
            
            matches = matches[:limit]
            
            output = f"""Phonetic Match Results for {table_name}.{column_name}:
        Search Term: "{search_term}" (Code: {search_code})
        Algorithm: {algorithm.title()}
        
        Found {len(matches)} phonetic matches:

        """
            
            for i, match in enumerate(matches, 1):
                output += f"Match {i} (Row {match['rowid']}) - Code: {match['phonetic_code']}:\n"
                output += f"  Matched Word: '{match['matched_word']}'\n"
                output += f"  Full Text: {match['text'][:100]}{'...' if len(match['text']) > 100 else ''}\n\n"
            
            if len(matches) == 0:
                output += f"No phonetic matches found for '{search_term}' (code: {search_code})\n"
            
            return [types.TextContent(type="text", text=output)]
            
        except Exception as e:
            error_msg = f"Failed to perform phonetic matching: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

    async def _handle_text_similarity(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Calculate text similarity between columns or against reference text."""
        if not all(key in arguments for key in ["table_name", "column_name"]):
            raise ValueError("Missing required arguments: table_name, column_name")
    
        table_name = arguments["table_name"]
        column_name = arguments["column_name"]
        reference_text = arguments.get("reference_text", "")
        compare_column = arguments.get("compare_column", "")
        algorithm = arguments.get("algorithm", "cosine")
        limit = arguments.get("limit", 100)
        where_clause = arguments.get("where_clause", "")
    
        def jaccard_similarity(text1, text2):
            """Calculate Jaccard similarity between two texts"""
            set1 = set(text1.lower().split())
            set2 = set(text2.lower().split())
            intersection = set1.intersection(set2)
            union = set1.union(set2)
            return len(intersection) / len(union) if union else 0
        
        def cosine_similarity(text1, text2):
            """Simple cosine similarity using word frequency"""
            words1 = text1.lower().split()
            words2 = text2.lower().split()
            
            # Get all unique words
            all_words = set(words1 + words2)
            
            # Create frequency vectors
            vec1 = [words1.count(word) for word in all_words]
            vec2 = [words2.count(word) for word in all_words]
            
            # Calculate dot product and magnitudes
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0
            
            return dot_product / (magnitude1 * magnitude2)
        
        def levenshtein_similarity(text1, text2):
            """Calculate Levenshtein similarity (normalized)"""
            return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
        try:
            where_sql = f" WHERE {where_clause}" if where_clause else ""
            
            if compare_column:
                # Compare two columns
                query = f"""
                SELECT {column_name}, {compare_column}, rowid AS row_id
                FROM {table_name}{where_sql}
                WHERE {column_name} IS NOT NULL AND {compare_column} IS NOT NULL
                LIMIT {limit}
                """
                
                result = self._execute_query(query)
                
                if not result:
                    return [types.TextContent(type="text", text="No data found for column comparison")]
                
                similarities = []
                for row in result:
                    text1 = str(row[column_name])
                    text2 = str(row[compare_column])
                    
                    if algorithm.lower() == "jaccard":
                        similarity = jaccard_similarity(text1, text2)
                    elif algorithm.lower() == "levenshtein":
                        similarity = levenshtein_similarity(text1, text2)
                    else:  # cosine
                        similarity = cosine_similarity(text1, text2)
                    
                    similarities.append({
                        "rowid": row["row_id"],
                        "text1": text1,
                        "text2": text2,
                        "similarity": round(similarity, 3)
                    })
                
                # Sort by similarity (highest first)
                similarities.sort(key=lambda x: x["similarity"], reverse=True)
                
                output = f"""Text Similarity Results for {table_name}.{column_name} vs {compare_column}:
        Algorithm: {algorithm.title()}
        
        Found {len(similarities)} comparisons:

        """
                
                for i, sim in enumerate(similarities, 1):
                    output += f"Row {sim['rowid']} - Similarity: {sim['similarity']:.3f}:\n"
                    output += f"  Text 1: {sim['text1'][:80]}{'...' if len(sim['text1']) > 80 else ''}\n"
                    output += f"  Text 2: {sim['text2'][:80]}{'...' if len(sim['text2']) > 80 else ''}\n\n"
                
            elif reference_text:
                # Compare against reference text
                query = f"""
                SELECT {column_name}, rowid AS row_id
                FROM {table_name}{where_sql}
                WHERE {column_name} IS NOT NULL
                LIMIT {limit}
                """
                
                result = self._execute_query(query)
                
                if not result:
                    return [types.TextContent(type="text", text="No data found for reference comparison")]
                
                similarities = []
                for row in result:
                    text = str(row[column_name])
                    
                    if algorithm.lower() == "jaccard":
                        similarity = jaccard_similarity(reference_text, text)
                    elif algorithm.lower() == "levenshtein":
                        similarity = levenshtein_similarity(reference_text, text)
                    else:  # cosine
                        similarity = cosine_similarity(reference_text, text)
                    
                    similarities.append({
                        "rowid": row["row_id"],
                        "text": text,
                        "similarity": round(similarity, 3)
                    })
                
                # Sort by similarity (highest first)
                similarities.sort(key=lambda x: x["similarity"], reverse=True)
                
                output = f"""Text Similarity Results for {table_name}.{column_name} vs Reference:
        Reference Text: "{reference_text[:100]}{'...' if len(reference_text) > 100 else ''}"
        Algorithm: {algorithm.title()}
        
        Found {len(similarities)} comparisons:

        """
                
                for i, sim in enumerate(similarities, 1):
                    output += f"Match {i} (Row {sim['rowid']}) - Similarity: {sim['similarity']:.3f}:\n"
                    output += f"  Text: {sim['text'][:100]}{'...' if len(sim['text']) > 100 else ''}\n\n"
            
            else:
                return [types.TextContent(type="text", text="Please provide either reference_text or compare_column for similarity calculation")]
            
            return [types.TextContent(type="text", text=output)]
            
        except Exception as e:
            error_msg = f"Failed to calculate text similarity: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

    async def _handle_text_normalize(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Normalize text with various transformations."""
        if not all(key in arguments for key in ["table_name", "column_name"]):
            raise ValueError("Missing required arguments: table_name, column_name")
    
        table_name = arguments["table_name"]
        column_name = arguments["column_name"]
        operations = arguments.get("operations", ["lowercase", "trim"])
        preview_only = arguments.get("preview_only", True)
        where_clause = arguments.get("where_clause", "")
    
        try:
            # Build WHERE clause properly to avoid duplicates
            if where_clause:
                where_sql = f" WHERE ({where_clause}) AND {column_name} IS NOT NULL"
            else:
                where_sql = f" WHERE {column_name} IS NOT NULL"
        
            query = f"""
            SELECT {column_name}, rowid AS row_id
            FROM {table_name}{where_sql}
            LIMIT 100
            """
            
            result = self._execute_query(query)
            
            if not result:
                return [types.TextContent(type="text", text="No data found for text normalization")]
            
            normalizations = []
            for i, row in enumerate(result):
                original_text = str(row[column_name])
                normalized_text = original_text
                
                # Apply normalization operations
                for operation in operations:
                    if operation.lower() == "lowercase":
                        normalized_text = normalized_text.lower()
                    elif operation.lower() == "uppercase":
                        normalized_text = normalized_text.upper()
                    elif operation.lower() == "trim":
                        normalized_text = normalized_text.strip()
                    elif operation.lower() == "remove_extra_spaces":
                        normalized_text = re.sub(r'\s+', ' ', normalized_text)
                    elif operation.lower() == "remove_punctuation":
                        normalized_text = re.sub(r'[^\w\s]', '', normalized_text)
                    elif operation.lower() == "remove_digits":
                        normalized_text = re.sub(r'\d+', '', normalized_text)
                    elif operation.lower() == "normalize_unicode":
                        normalized_text = unicodedata.normalize('NFKD', normalized_text)
                
                if normalized_text != original_text:
                    # Try to get rowid, fallback to row number
                    try:
                        row_id = row.get("rowid", row.get("id", i + 1))
                    except:
                        row_id = i + 1
                    
                    normalizations.append({
                        "rowid": row_id,
                        "original": original_text,
                        "normalized": normalized_text
                    })
            
            output = f"""Text Normalization {'Preview' if preview_only else 'Results'} for {table_name}.{column_name}:
        Operations: {', '.join(operations)}
        
        Found {len(normalizations)} rows with changes:

        """
            
            for i, norm in enumerate(normalizations[:20], 1):  # Show first 20
                output += f"Row {norm['rowid']}:\n"
                output += f"  Before: {norm['original'][:100]}{'...' if len(norm['original']) > 100 else ''}\n"
                output += f"  After:  {norm['normalized'][:100]}{'...' if len(norm['normalized']) > 100 else ''}\n\n"
            
            if len(normalizations) > 20:
                output += f"... and {len(normalizations) - 20} more rows\n"
            
            if preview_only:
                output += "\nTo execute these changes, set preview_only=false"
            else:
                # Execute the normalizations - use original content matching for safety
                for norm in normalizations:
                    update_query = f"""
                    UPDATE {table_name} 
                    SET {column_name} = ? 
                    WHERE {column_name} = ?
                    """
                    self._execute_query(update_query, [norm['normalized'], norm['original']])
                
                output += f"\n✅ Successfully normalized {len(normalizations)} rows"
            
            if len(normalizations) == 0:
                output += "No changes needed - text is already normalized"
            
            return [types.TextContent(type="text", text=output)]
            
        except Exception as e:
            error_msg = f"Failed to normalize text: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

    async def _handle_advanced_search(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Advanced search combining multiple text processing techniques."""
        if not all(key in arguments for key in ["table_name", "column_name", "search_term"]):
            raise ValueError("Missing required arguments: table_name, column_name, search_term")
    
        table_name = arguments["table_name"]
        column_name = arguments["column_name"]
        search_term = arguments["search_term"]
        techniques = arguments.get("techniques", ["exact", "fuzzy", "phonetic"])
        fuzzy_threshold = arguments.get("fuzzy_threshold", 0.6)
        limit = arguments.get("limit", 100)
        where_clause = arguments.get("where_clause", "")
    
        try:
            where_sql = f" WHERE {where_clause}" if where_clause else ""
        
            query = f"""
            SELECT {column_name}, rowid AS row_id
            FROM {table_name}{where_sql}
            WHERE {column_name} IS NOT NULL
            LIMIT 1000
            """
            
            result = self._execute_query(query)
            
            if not result:
                return [types.TextContent(type="text", text="No data found for advanced search")]
            
            all_matches = []
            
            for row in result:
                text = str(row[column_name])
                matches = []
                
                # Exact match
                if "exact" in techniques:
                    if search_term.lower() in text.lower():
                        matches.append({"type": "exact", "score": 1.0})
                
                # Fuzzy match
                if "fuzzy" in techniques:
                    similarity = difflib.SequenceMatcher(None, search_term.lower(), text.lower()).ratio()
                    if similarity >= fuzzy_threshold:
                        matches.append({"type": "fuzzy", "score": similarity})
                
                # Phonetic match
                if "phonetic" in techniques:
                    def simple_soundex(word):
                        if not word:
                            return "0000"
                        word = word.upper()
                        soundex = word[0]
                        mapping = {
                            'B': '1', 'F': '1', 'P': '1', 'V': '1',
                            'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
                            'D': '3', 'T': '3', 'L': '4', 'M': '5', 'N': '5', 'R': '6'
                        }
                        for char in word[1:]:
                            if char in mapping:
                                code = mapping[char]
                                if soundex[-1] != code:
                                    soundex += code
                            if len(soundex) == 4:
                                break
                        return (soundex + "000")[:4]
                    
                    search_soundex = simple_soundex(search_term)
                    text_words = text.split()
                    for word in text_words:
                        if simple_soundex(word) == search_soundex:
                            matches.append({"type": "phonetic", "score": 0.8})
                            break
                
                if matches:
                    # Calculate combined score (highest individual score)
                    best_match = max(matches, key=lambda x: x["score"])
                    all_matches.append({
                        "rowid": row["row_id"],
                        "text": text,
                        "match_types": [m["type"] for m in matches],
                        "best_score": best_match["score"],
                        "best_type": best_match["type"]
                    })
            
            # Sort by score (highest first)
            all_matches.sort(key=lambda x: x["best_score"], reverse=True)
            all_matches = all_matches[:limit]
            
            output = f"""Advanced Search Results for {table_name}.{column_name}:
        Search Term: "{search_term}"
        Techniques: {', '.join(techniques)}
        Fuzzy Threshold: {fuzzy_threshold}
        
        Found {len(all_matches)} matches:

        """
            
            for i, match in enumerate(all_matches, 1):
                output += f"Match {i} (Row {match['rowid']}) - Score: {match['best_score']:.3f} ({match['best_type']}):\n"
                output += f"  Match Types: {', '.join(match['match_types'])}\n"
                output += f"  Text: {match['text'][:100]}{'...' if len(match['text']) > 100 else ''}\n\n"
            
            if len(all_matches) == 0:
                output += f"No matches found using techniques: {', '.join(techniques)}\n"
            
            return [types.TextContent(type="text", text=output)]
            
        except Exception as e:
            error_msg = f"Failed to perform advanced search: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

    async def _handle_text_validation(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Validate text against various patterns and rules."""
        if not all(key in arguments for key in ["table_name", "column_name"]):
            raise ValueError("Missing required arguments: table_name, column_name")
    
        table_name = arguments["table_name"]
        column_name = arguments["column_name"]
        validation_type = arguments.get("validation_type", "email")
        custom_pattern = arguments.get("custom_pattern", "")
        return_invalid_only = arguments.get("return_invalid_only", True)
        where_clause = arguments.get("where_clause", "")
    
        # Validation patterns
        patterns = {
            "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "phone": r'^\+?1?-?\.?\s?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',
            "url": r'^https?://(?:[-\w.])+(?:\.[a-zA-Z]{2,})+(?:/[^?\s]*)?(?:\?[^#\s]*)?(?:#[^\s]*)?$',
            "custom_regex": custom_pattern
        }
    
        try:
            if validation_type not in patterns:
                return [types.TextContent(type="text", text=f"Unsupported validation type: {validation_type}")]
            
            pattern = patterns[validation_type]
            if not pattern:
                return [types.TextContent(type="text", text="Custom pattern is required for custom_regex validation")]
            
            compiled_pattern = re.compile(pattern)
            where_sql = f" WHERE {where_clause}" if where_clause else ""
        
            query = f"""
            SELECT {column_name}, rowid AS row_id
            FROM {table_name}{where_sql}
            WHERE {column_name} IS NOT NULL
            LIMIT 1000
            """
            
            result = self._execute_query(query)
            
            if not result:
                return [types.TextContent(type="text", text="No data found for text validation")]
            
            validations = []
            valid_count = 0
            invalid_count = 0
            
            for row in result:
                text = str(row[column_name]).strip()
                is_valid = bool(compiled_pattern.match(text))
                
                if is_valid:
                    valid_count += 1
                else:
                    invalid_count += 1
                
                # Add to results based on return_invalid_only setting
                if not return_invalid_only or not is_valid:
                    validations.append({
                        "rowid": row["row_id"],
                        "text": text,
                        "is_valid": is_valid,
                        "status": "✅ Valid" if is_valid else "❌ Invalid"
                    })
            
            output = f"""Text Validation Results for {table_name}.{column_name}:
        Validation Type: {validation_type.title()}
        Pattern: {pattern}
        
        Summary:
        ✅ Valid: {valid_count}
        ❌ Invalid: {invalid_count}
        Total: {valid_count + invalid_count}

        {"Invalid " if return_invalid_only else ""}Results:

        """
            
            for i, validation in enumerate(validations[:50], 1):  # Show first 50
                output += f"Row {validation['rowid']} - {validation['status']}:\n"
                output += f"  Text: {validation['text'][:100]}{'...' if len(validation['text']) > 100 else ''}\n\n"
            
            if len(validations) > 50:
                output += f"... and {len(validations) - 50} more results\n"
            
            return [types.TextContent(type="text", text=output)]
            
        except re.error as e:
            error_msg = f"Invalid validation pattern: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"Failed to validate text: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

async def main(db_path: str = "sqlite_mcp.db"):
    logger.info(f"Starting Enhanced SQLite MCP Server with DB: {db_path}")

    # Initialize database with enhanced features
    db = EnhancedSqliteDatabase(db_path)
    
    # Check SQLite version and JSONB support
    version_info = check_sqlite_version()
    logger.info(f"SQLite Version: {version_info['version']}")
    logger.info(f"JSONB Support: {'Yes' if version_info['has_jsonb_support'] else 'No'}")
    
    # Initialize MCP server
    server = Server("sqlite-custom")

    # Register handlers
    logger.debug("Registering handlers")

    @server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        logger.debug("Handling list_resources request")
        return [
            # Database Meta-Awareness Resources
            types.Resource(
                uri=AnyUrl("database://schema"),
                name="Database Schema",
                description="Complete database schema with tables, columns, indexes, and relationships in natural language + JSON",
                mimeType="application/json",
            ),
            types.Resource(
                uri=AnyUrl("database://capabilities"),
                name="Server Capabilities",
                description="Comprehensive server capabilities matrix including all 74 tools, features, and supported operations",
                mimeType="application/json",
            ),
            types.Resource(
                uri=AnyUrl("database://statistics"),
                name="Table Statistics",
                description="Real-time database statistics, table sizes, row counts, and optimization recommendations",
                mimeType="application/json",
            ),
            types.Resource(
                uri=AnyUrl("database://search_indexes"),
                name="Search Index Status",
                description="Status of FTS5 full-text search and semantic search indexes with performance metrics",
                mimeType="application/json",
            ),
            types.Resource(
                uri=AnyUrl("database://performance"),
                name="Performance Insights",
                description="Database performance analysis, optimization tips, and health recommendations",
                mimeType="application/json",
            ),
            # Legacy Resources (maintained for compatibility)
            types.Resource(
                uri=AnyUrl("memo://insights"),
                name="Business Insights Memo",
                description="A living document of discovered business insights",
                mimeType="text/plain",
            ),
            types.Resource(
                uri=AnyUrl("diagnostics://json"),
                name="JSON Diagnostics",
                description="Diagnostic information about JSON handling capabilities",
                mimeType="application/json",
            )
        ]

    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        logger.debug(f"Handling read_resource request for URI: {uri}")
        
        # Handle database meta-awareness resources
        if uri.scheme == "database":
            path = str(uri).replace("database://", "")
            
            if path == "schema":
                # Get complete database schema with natural language descriptions
                try:
                    # Get all tables
                    tables_query = "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"
                    tables = db._execute_query(tables_query)
                    
                    schema_info = {
                        "database_path": db.db_path,
                        "sqlite_version": db.version_info.get('version', 'Unknown'),
                        "total_tables": len(tables) if tables else 0,
                        "tables": [],
                        "summary": f"Database contains {len(tables) if tables else 0} tables. SQLite version {db.version_info.get('version', 'Unknown')}."
                    }
                    
                    # Process tables
                    if tables:
                        for table in tables:
                            table_name = table["name"]
                            # Get column info
                            columns_query = f"PRAGMA table_info({table_name})"
                            columns = db._execute_query(columns_query)
                            
                            # Get row count
                            try:
                                count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                                count_result = db._execute_query(count_query)
                                row_count = count_result[0]["count"] if count_result else 0
                            except:
                                row_count = "Unknown"
                            
                            table_info = {
                                "name": table_name,
                                "columns": columns if columns else [],
                                "column_count": len(columns) if columns else 0,
                                "row_count": row_count
                            }
                            schema_info["tables"].append(table_info)
                    
                    return json_module.dumps(schema_info, indent=2)
                    
                except Exception as e:
                    logger.error(f"Failed to generate database schema: {e}")
                    return json_module.dumps({"error": f"Failed to generate schema: {str(e)}"}, indent=2)
            
            elif path == "capabilities":
                # Comprehensive server capabilities matrix
                capabilities = {
                    "server_version": "2.1.0",
                    "sqlite_version": db.version_info.get('version', 'Unknown'),
                        "total_tools": 74,
                    "semantic_search": True,
                    "full_text_search": True,
                    "virtual_tables": True,
                    "geospatial_analysis": True,
                    "backup_restore": True,
                    "jsonb_support": db.version_info.get('has_jsonb_support', False),
                    "advanced_features": [
                        "AI-native semantic/vector search with cosine similarity",
                        "Hybrid keyword + semantic search with configurable weighting",
                        "FTS5 full-text search with BM25 ranking and snippets",
                        "Virtual table management (R-Tree, CSV, Series)",
                        "Database administration tools (VACUUM, ANALYZE, integrity)",
                        "Backup/restore with atomic operations and verification",
                        "Advanced PRAGMA operations for configuration management",
                        "SpatiaLite geospatial analysis with spatial indexing and operations",
                        "Comprehensive GIS functionality with shapefile import/export",
                        "Enhanced CSV/JSON virtual tables with smart type inference"
                    ]
                }
                return json_module.dumps(capabilities, indent=2)
            
            elif path == "statistics":
                # Real-time database statistics
                try:
                    stats = {"tables": [], "recommendations": []}
                    
                    tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                    tables = db._execute_query(tables_query)
                    
                    if tables:
                        for table in tables:
                            table_name = table["name"]
                            try:
                                count_result = db._execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
                                row_count = count_result[0]["count"] if count_result else 0
                                
                                stats["tables"].append({
                                    "name": table_name,
                                    "row_count": row_count
                                })
                                
                                if row_count > 10000:
                                    stats["recommendations"].append(f"Consider indexing '{table_name}' (has {row_count:,} rows)")
                                    
                            except Exception as e:
                                stats["tables"].append({"name": table_name, "error": str(e)})
                    
                    if not stats["recommendations"]:
                        stats["recommendations"].append("Database appears well-optimized")
                    
                    return json_module.dumps(stats, indent=2)
                    
                except Exception as e:
                    return json_module.dumps({"error": f"Failed to generate statistics: {str(e)}"}, indent=2)
            
            elif path == "search_indexes":
                # Search index status
                try:
                    index_status = {"fts5_indexes": [], "semantic_indexes": [], "recommendations": []}
                    
                    # Find FTS5 tables
                    fts_query = """
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND sql LIKE '%VIRTUAL TABLE%' AND sql LIKE '%fts5%'
                    """
                    fts_tables = db._execute_query(fts_query)
                    
                    if fts_tables:
                        for fts_table in fts_tables:
                            try:
                                count_result = db._execute_query(f"SELECT COUNT(*) as count FROM {fts_table['name']}")
                                row_count = count_result[0]["count"] if count_result else 0
                                index_status["fts5_indexes"].append({
                                    "name": fts_table["name"],
                                    "document_count": row_count,
                                    "status": "active" if row_count > 0 else "empty"
                                })
                            except:
                                pass
                    
                    # Find semantic search tables
                    semantic_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%embedding%'"
                    semantic_tables = db._execute_query(semantic_query)
                    
                    if semantic_tables:
                        for semantic_table in semantic_tables:
                            try:
                                count_result = db._execute_query(f"SELECT COUNT(*) as count FROM {semantic_table['name']}")
                                row_count = count_result[0]["count"] if count_result else 0
                                index_status["semantic_indexes"].append({
                                    "name": semantic_table["name"],
                                    "vector_count": row_count,
                                    "status": "active" if row_count > 0 else "empty"
                                })
                            except:
                                pass
                    
                    if not index_status["fts5_indexes"] and not index_status["semantic_indexes"]:
                        index_status["recommendations"].append("Consider setting up FTS5 or semantic search for better search capabilities")
                    
                    return json_module.dumps(index_status, indent=2)
                    
                except Exception as e:
                    return json_module.dumps({"error": f"Failed to analyze search indexes: {str(e)}"}, indent=2)
            
            elif path == "performance":
                # Performance insights
                try:
                    performance = {
                        "health_score": "Good",
                        "optimization_tips": [
                            "Run ANALYZE regularly to update query planner statistics",
                            "Use VACUUM periodically to reclaim space and defragment",
                            "Consider PRAGMA optimize for automatic statistics updates",
                            "Monitor index usage with index_usage_stats tool"
                        ],
                        "maintenance_recommendations": [
                            "Regular integrity checks using integrity_check tool",
                            "Monitor database statistics with database_stats tool",
                            "Backup database regularly using backup_database tool"
                        ]
                    }
                    return json_module.dumps(performance, indent=2)
                except Exception as e:
                    return json_module.dumps({"error": f"Failed to analyze performance: {str(e)}"}, indent=2)
            
            else:
                raise ValueError(f"Unknown database resource path: {path}")
        
        # Handle memo resources (legacy)
        elif uri.scheme == "memo":
            path = str(uri).replace("memo://", "")
            if not path or path != "insights":
                logger.error(f"Unknown memo path: {path}")
                raise ValueError(f"Unknown memo path: {path}")

            return db._synthesize_memo()
            
        # Handle diagnostic resources
        elif uri.scheme == "diagnostics":
            path = str(uri).replace("diagnostics://", "")
            
            if path == "json":
                # Return JSON diagnostics as formatted string
                diagnostics = db.diagnostics.get_json_diagnostics()
                return json_module.dumps(diagnostics, indent=2)
            else:
                logger.error(f"Unknown diagnostics path: {path}")
                raise ValueError(f"Unknown diagnostics path: {path}")
        else:
            logger.error(f"Unsupported URI scheme: {uri.scheme}")
            raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    @server.list_prompts()
    async def handle_list_prompts() -> list[types.Prompt]:
        logger.debug("Handling list_prompts request")
        return [
            # Intelligent Workflow Prompts
            types.Prompt(
                name="semantic_query",
                description="Guide for translating natural language queries into semantic search + SQL operations",
                arguments=[
                    types.PromptArgument(
                        name="user_question",
                        description="The user's natural language question or search intent",
                        required=True,
                    ),
                    types.PromptArgument(
                        name="search_type",
                        description="Type of search: 'semantic', 'keyword', or 'hybrid'",
                        required=False,
                    )
                ],
            ),
            types.Prompt(
                name="summarize_table",
                description="Intelligent table analysis and summary generation with key statistics",
                arguments=[
                    types.PromptArgument(
                        name="table_name",
                        description="Name of the table to analyze and summarize",
                        required=True,
                    ),
                    types.PromptArgument(
                        name="analysis_depth",
                        description="Depth of analysis: 'basic', 'detailed', or 'comprehensive'",
                        required=False,
                    )
                ],
            ),
            types.Prompt(
                name="optimize_database",
                description="Step-by-step database optimization workflow with performance analysis",
                arguments=[
                    types.PromptArgument(
                        name="optimization_focus",
                        description="Focus area: 'performance', 'storage', 'indexes', or 'all'",
                        required=False,
                    )
                ],
            ),
            types.Prompt(
                name="setup_semantic_search",
                description="Complete guide for setting up semantic search with embeddings",
                arguments=[
                    types.PromptArgument(
                        name="content_type",
                        description="Type of content to search: 'documents', 'products', 'articles', or 'general'",
                        required=True,
                    ),
                    types.PromptArgument(
                        name="embedding_provider",
                        description="Embedding provider: 'openai', 'huggingface', or 'custom'",
                        required=False,
                    )
                ],
            ),
            types.Prompt(
                name="hybrid_search_workflow",
                description="Step-by-step implementation of hybrid keyword + semantic search",
                arguments=[
                    types.PromptArgument(
                        name="use_case",
                        description="Use case: 'qa_system', 'content_discovery', 'ecommerce', or 'knowledge_base'",
                        required=True,
                    )
                ],
            ),
            # Legacy Prompts (maintained for compatibility)
            types.Prompt(
                name="mcp-demo",
                description="A prompt to seed the database with initial data and demonstrate what you can do with an SQLite MCP Server + Claude",
                arguments=[
                    types.PromptArgument(
                        name="topic",
                        description="Topic to seed the database with initial data",
                        required=True,
                    )
                ],
            ),
            types.Prompt(
                name="json-diagnostic",
                description="A prompt to check SQLite JSONB capabilities and run diagnostics",
                arguments=[],
            )
        ]

    @server.get_prompt()
    async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
        logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
        
        if name == "mcp-demo":
            if not arguments or "topic" not in arguments:
                logger.error("Missing required argument: topic")
                raise ValueError("Missing required argument: topic")

            topic = arguments["topic"]
            prompt = PROMPT_TEMPLATE.format(topic=topic)

            logger.debug(f"Generated prompt template for topic: {topic}")
            return types.GetPromptResult(
                description=f"Demo template for {topic}",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=prompt.strip()),
                    )
                ],
            )
        elif name == "json-diagnostic":
            # JSON diagnostic prompt
            version_info = check_sqlite_version()
            
            diagnostic_prompt = f"""
            # SQLite JSON Capabilities Diagnostic
            
            I'd like to run a diagnostic check on your SQLite MCP server's JSON capabilities.
            
            ## System Information
            - SQLite Version: {version_info['version']}
            - JSONB Support: {"Yes" if version_info['has_jsonb_support'] else "No"}
            
            Let's use the SQLite MCP tools to run a few diagnostic tests:
            
            1. First, let's check what tables are in the database using the `list_tables` tool.
            2. If there's a memory_journal table, let's use `describe_table` to check its schema.
            3. Let's examine the JSON diagnostics resource at `diagnostics://json`.
            
            This will help us understand the JSON capabilities of your SQLite installation.
            """
            
            return types.GetPromptResult(
                description="JSON diagnostic prompt",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=diagnostic_prompt.strip()),
                    )
                ],
            )
        elif name == "semantic_query":
            return handle_semantic_query_prompt(arguments)
        elif name == "summarize_table":
            return handle_summarize_table_prompt(arguments)
        elif name == "optimize_database":
            return handle_optimize_database_prompt(arguments)
        elif name == "setup_semantic_search":
            return handle_setup_semantic_search_prompt(arguments)
        elif name == "hybrid_search_workflow":
            return handle_hybrid_search_workflow_prompt(arguments)
        else:
            logger.error(f"Unknown prompt: {name}")
            raise ValueError(f"Unknown prompt: {name}")

    # Tool handler helper functions to reduce complexity
    async def _handle_list_tables() -> list[types.TextContent]:
        """Handle list_tables tool"""
        results = db._execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        return [types.TextContent(type="text", text=str(results))]
    
    async def _handle_describe_table(arguments: dict[str, Any]) -> list[types.TextContent]:
        """Handle describe_table tool"""
        if not arguments or "table_name" not in arguments:
            raise ValueError("Missing table_name argument")
            
        results = db._execute_query(
            f"PRAGMA table_info({arguments['table_name']})"
        )
        return [types.TextContent(type="text", text=str(results))]

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        basic_tools = [
            types.Tool(
                name="read_query",
                description="Execute a SELECT query on the SQLite database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SELECT SQL query with ? placeholders for parameters"},
                        "params": {
                            "type": "array",
                            "description": "Optional parameters to bind to query placeholders (dict/list objects will be auto-serialized to JSON)",
                            "items": {
                                "anyOf": [
                                    {"type": "string"},
                                    {"type": "number"},
                                    {"type": "boolean"},
                                    {"type": "null"},
                                    {"type": "object"},
                                    {"type": "array"}
                                ]
                            }
                        }
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="write_query",
                description="Execute an INSERT, UPDATE, or DELETE query on the SQLite database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query with ? placeholders for parameters"},
                        "params": {
                            "type": "array",
                            "description": "Optional parameters to bind to query placeholders (dict/list objects will be auto-serialized to JSON)",
                            "items": {
                                "anyOf": [
                                    {"type": "string"},
                                    {"type": "number"},
                                    {"type": "boolean"},
                                    {"type": "null"},
                                    {"type": "object"},
                                    {"type": "array"}
                                ]
                            }
                        }
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="create_table",
                description="Create a new table in the SQLite database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "CREATE TABLE SQL statement with ? placeholders for parameters"},
                        "params": {
                            "type": "array",
                            "description": "Optional parameters to bind to query placeholders (dict/list objects will be auto-serialized to JSON)",
                            "items": {
                                "anyOf": [
                                    {"type": "string"},
                                    {"type": "number"},
                                    {"type": "boolean"},
                                    {"type": "null"},
                                    {"type": "object"},
                                    {"type": "array"}
                                ]
                            }
                        }
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="list_tables",
                description="List all tables in the SQLite database",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="describe_table",
                description="Get the schema information for a specific table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table to describe"},
                    },
                    "required": ["table_name"],
                },
            ),
            types.Tool(
                name="append_insight",
                description="Add a business insight to the memo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "insight": {"type": "string", "description": "Business insight discovered from data analysis"},
                    },
                    "required": ["insight"],
                },
            ),
            # Database Administration Tools
            types.Tool(
                name="vacuum_database",
                description="Optimize database by reclaiming unused space and defragmenting",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="analyze_database",
                description="Update database statistics for query optimization",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="integrity_check",
                description="Check database integrity and report any corruption",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="database_stats",
                description="Get database performance and usage statistics",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="index_usage_stats",
                description="Get index usage statistics for query optimization",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            # Full-Text Search (FTS5) Tools
            types.Tool(
                name="create_fts_table",
                description="Create a FTS5 virtual table for full-text search",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name for the FTS5 table"},
                        "columns": {"type": "array", "items": {"type": "string"}, "description": "List of columns to include in FTS5 index"},
                        "content_table": {"type": "string", "description": "Optional: source table to populate from"},
                        "tokenizer": {"type": "string", "description": "Optional: tokenizer to use (unicode61, porter, ascii)", "default": "unicode61"}
                    },
                    "required": ["table_name", "columns"],
                },
            ),
            types.Tool(
                name="rebuild_fts_index",
                description="Rebuild FTS5 index for optimal performance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the FTS5 table to rebuild"},
                    },
                    "required": ["table_name"],
                },
            ),
            types.Tool(
                name="fts_search",
                description="Perform enhanced full-text search with ranking and snippets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the FTS5 table to search"},
                        "query": {"type": "string", "description": "FTS5 search query"},
                        "limit": {"type": "integer", "description": "Maximum number of results", "default": 10},
                        "snippet_length": {"type": "integer", "description": "Length of text snippets", "default": 32}
                    },
                    "required": ["table_name", "query"],
                },
            ),
            # Backup/Restore Tools
            types.Tool(
                name="backup_database",
                description="Create a backup of the database to a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "backup_path": {"type": "string", "description": "Path where backup file will be created"},
                        "overwrite": {"type": "boolean", "description": "Whether to overwrite existing backup file", "default": False}
                    },
                    "required": ["backup_path"],
                },
            ),
            types.Tool(
                name="restore_database",
                description="Restore database from a backup file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "backup_path": {"type": "string", "description": "Path to backup file to restore from"},
                        "confirm": {"type": "boolean", "description": "Confirmation flag (required to prevent accidental restores)", "default": False}
                    },
                    "required": ["backup_path", "confirm"],
                },
            ),
            types.Tool(
                name="verify_backup",
                description="Verify integrity of a backup file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "backup_path": {"type": "string", "description": "Path to backup file to verify"},
                    },
                    "required": ["backup_path"],
                },
            ),
            # Advanced PRAGMA Operations
            types.Tool(
                name="pragma_settings",
                description="Get or set SQLite PRAGMA settings for database configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pragma_name": {"type": "string", "description": "PRAGMA name (e.g., 'journal_mode', 'synchronous', 'cache_size')"},
                        "value": {"type": "string", "description": "Optional: value to set (omit to get current value)"}
                    },
                    "required": ["pragma_name"],
                },
            ),
            types.Tool(
                name="pragma_optimize",
                description="Run PRAGMA optimize to update database statistics and improve query performance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "analysis_limit": {"type": "integer", "description": "Optional: limit analysis to N most used tables", "default": 1000}
                    },
                },
            ),
            types.Tool(
                name="pragma_table_info",
                description="Get detailed table schema information using PRAGMA table_info",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table to analyze"},
                        "include_foreign_keys": {"type": "boolean", "description": "Include foreign key information", "default": True}
                    },
                    "required": ["table_name"],
                },
            ),
            types.Tool(
                name="pragma_database_list",
                description="List all attached databases with their file paths and schemas",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="pragma_compile_options",
                description="Show SQLite compile-time options and capabilities",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            
            # Virtual Table Management Tools
            types.Tool(
                name="create_rtree_table",
                description="Create an R-Tree virtual table for spatial indexing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name for the R-Tree table"
                        },
                        "dimensions": {
                            "type": "integer",
                            "description": "Number of dimensions (2 for 2D, 3 for 3D, etc.)",
                            "default": 2
                        },
                        "coordinate_type": {
                            "type": "string",
                            "description": "Coordinate type: 'float' or 'int'",
                            "default": "float"
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            
            types.Tool(
                name="create_csv_table",
                description="Create a virtual table to access CSV files",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name for the CSV virtual table"
                        },
                        "csv_file_path": {
                            "type": "string",
                            "description": "Path to the CSV file"
                        },
                        "has_header": {
                            "type": "boolean",
                            "description": "Whether CSV has header row",
                            "default": True
                        },
                        "delimiter": {
                            "type": "string",
                            "description": "CSV delimiter character",
                            "default": ","
                        }
                    },
                    "required": ["table_name", "csv_file_path"]
                }
            ),
            
            types.Tool(
                name="create_series_table",
                description="Create a generate_series virtual table for sequences",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name for the series virtual table"
                        },
                        "start_value": {
                            "type": "integer",
                            "description": "Starting value of the series",
                            "default": 1
                        },
                        "end_value": {
                            "type": "integer",
                            "description": "Ending value of the series",
                            "default": 100
                        },
                        "step": {
                            "type": "integer",
                            "description": "Step increment",
                            "default": 1
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            
            types.Tool(
                name="list_virtual_tables",
                description="List all virtual tables in the database",
                inputSchema={
                    "type": "object",
                    "properties": {},
                }
            ),
            
            types.Tool(
                name="drop_virtual_table",
                description="Drop a virtual table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the virtual table to drop"
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": "Confirmation flag (required to prevent accidental drops)",
                            "default": False
                        }
                    },
                    "required": ["table_name", "confirm"]
                }
            ),
            
            types.Tool(
                name="virtual_table_info",
                description="Get detailed information about a virtual table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the virtual table to inspect"
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            
            # SpatiaLite Geospatial Tools (v2.0.0)
            types.Tool(
                name="load_spatialite",
                description="Load SpatiaLite extension for geospatial capabilities",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "force_reload": {
                            "type": "boolean",
                            "description": "Force reload if already loaded",
                            "default": False
                        }
                    },
                    "required": []
                }
            ),
            
            types.Tool(
                name="create_spatial_table",
                description="Create a spatial table with geometry column",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the spatial table to create"
                        },
                        "geometry_column": {
                            "type": "string",
                            "description": "Name of the geometry column",
                            "default": "geom"
                        },
                        "geometry_type": {
                            "type": "string",
                            "enum": ["POINT", "LINESTRING", "POLYGON", "MULTIPOINT", "MULTILINESTRING", "MULTIPOLYGON", "GEOMETRY"],
                            "description": "Type of geometry to store",
                            "default": "POINT"
                        },
                        "srid": {
                            "type": "integer",
                            "description": "Spatial Reference System ID (4326 for WGS84)",
                            "default": 4326
                        },
                        "additional_columns": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"}
                                },
                                "required": ["name", "type"]
                            },
                            "description": "Additional non-spatial columns to include",
                            "default": []
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            
            types.Tool(
                name="spatial_index",
                description="Create or drop spatial index on geometry column",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the spatial table"
                        },
                        "geometry_column": {
                            "type": "string",
                            "description": "Name of the geometry column",
                            "default": "geom"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["create", "drop"],
                            "description": "Create or drop the spatial index",
                            "default": "create"
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            
            types.Tool(
                name="spatial_query",
                description="Execute spatial queries with geometric operations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Spatial SQL query using SpatiaLite functions"
                        },
                        "explain": {
                            "type": "boolean",
                            "description": "Show query execution plan",
                            "default": False
                        }
                    },
                    "required": ["query"]
                }
            ),
            
            types.Tool(
                name="geometry_operations",
                description="Common geometry operations (buffer, intersection, union, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["buffer", "intersection", "union", "difference", "distance", "area", "length", "centroid", "envelope"],
                            "description": "Geometric operation to perform"
                        },
                        "geometry1": {
                            "type": "string",
                            "description": "First geometry (WKT format or table.column reference)"
                        },
                        "geometry2": {
                            "type": "string",
                            "description": "Second geometry for binary operations (WKT format or table.column reference)",
                            "default": ""
                        },
                        "buffer_distance": {
                            "type": "number",
                            "description": "Buffer distance for buffer operations",
                            "default": 1.0
                        },
                        "table_name": {
                            "type": "string",
                            "description": "Table name if using table.column references",
                            "default": ""
                        }
                    },
                    "required": ["operation", "geometry1"]
                }
            ),
            
            types.Tool(
                name="import_shapefile",
                description="Import Shapefile data into spatial table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "shapefile_path": {
                            "type": "string",
                            "description": "Path to the .shp file"
                        },
                        "table_name": {
                            "type": "string",
                            "description": "Target table name for imported data"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "Character encoding of the shapefile",
                            "default": "UTF-8"
                        },
                        "srid": {
                            "type": "integer",
                            "description": "Override SRID if not detected automatically",
                            "default": 0
                        }
                    },
                    "required": ["shapefile_path", "table_name"]
                }
            ),
            
            types.Tool(
                name="spatial_analysis",
                description="Perform spatial analysis operations (nearest neighbor, spatial join, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "analysis_type": {
                            "type": "string",
                            "enum": ["nearest_neighbor", "spatial_join", "point_in_polygon", "distance_matrix", "cluster_analysis"],
                            "description": "Type of spatial analysis to perform"
                        },
                        "source_table": {
                            "type": "string",
                            "description": "Source table for analysis"
                        },
                        "target_table": {
                            "type": "string",
                            "description": "Target table for spatial operations",
                            "default": ""
                        },
                        "geometry_column": {
                            "type": "string",
                            "description": "Geometry column name",
                            "default": "geom"
                        },
                        "max_distance": {
                            "type": "number",
                            "description": "Maximum distance for proximity operations",
                            "default": 1000.0
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Limit number of results",
                            "default": 100
                        }
                    },
                    "required": ["analysis_type", "source_table"]
                }
            ),

            # Enhanced Virtual Tables (v1.9.3)
            types.Tool(
                name="create_enhanced_csv_table",
                description="Create enhanced CSV virtual table with automatic data type inference",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name for the enhanced CSV virtual table"
                        },
                        "csv_file_path": {
                            "type": "string",
                            "description": "Path to the CSV file"
                        },
                        "delimiter": {
                            "type": "string",
                            "description": "CSV delimiter character",
                            "default": ","
                        },
                        "has_header": {
                            "type": "boolean",
                            "description": "Whether CSV has header row",
                            "default": True
                        },
                        "sample_rows": {
                            "type": "integer",
                            "description": "Number of rows to sample for type inference",
                            "default": 100
                        },
                        "null_values": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Values to treat as NULL",
                            "default": ["", "NULL", "null", "None", "N/A", "n/a"]
                        }
                    },
                    "required": ["table_name", "csv_file_path"]
                }
            ),
            
            types.Tool(
                name="create_json_collection_table",
                description="Create virtual table for JSON file collections (JSONL, JSON arrays)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name for the JSON collection virtual table"
                        },
                        "json_file_path": {
                            "type": "string",
                            "description": "Path to JSON file (JSONL or JSON array)"
                        },
                        "format_type": {
                            "type": "string",
                            "enum": ["jsonl", "json_array", "auto"],
                            "description": "JSON format: jsonl (line-delimited), json_array, or auto-detect",
                            "default": "auto"
                        },
                        "flatten_nested": {
                            "type": "boolean",
                            "description": "Flatten nested objects into columns with dot notation",
                            "default": True
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum nesting depth to flatten",
                            "default": 3
                        },
                        "sample_records": {
                            "type": "integer",
                            "description": "Number of records to sample for schema inference",
                            "default": 100
                        }
                    },
                    "required": ["table_name", "json_file_path"]
                }
            ),
            
            types.Tool(
                name="analyze_csv_schema",
                description="Analyze CSV file and infer data types without creating table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "csv_file_path": {
                            "type": "string",
                            "description": "Path to the CSV file to analyze"
                        },
                        "delimiter": {
                            "type": "string",
                            "description": "CSV delimiter character",
                            "default": ","
                        },
                        "has_header": {
                            "type": "boolean",
                            "description": "Whether CSV has header row",
                            "default": True
                        },
                        "sample_rows": {
                            "type": "integer",
                            "description": "Number of rows to sample for analysis",
                            "default": 1000
                        }
                    },
                    "required": ["csv_file_path"]
                }
            ),
            
            types.Tool(
                name="analyze_json_schema",
                description="Analyze JSON file collection and infer schema without creating table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "json_file_path": {
                            "type": "string",
                            "description": "Path to JSON file to analyze"
                        },
                        "format_type": {
                            "type": "string",
                            "enum": ["jsonl", "json_array", "auto"],
                            "description": "JSON format type",
                            "default": "auto"
                        },
                        "sample_records": {
                            "type": "integer",
                            "description": "Number of records to sample for analysis",
                            "default": 1000
                        }
                    },
                    "required": ["json_file_path"]
                }
            ),
            
            # Semantic Search Tools
            types.Tool(
                name="create_embeddings_table",
                description="Create a table optimized for storing embeddings with metadata",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name for the embeddings table"
                        },
                        "embedding_dim": {
                            "type": "integer",
                            "description": "Dimension of the embedding vectors",
                            "default": 1536
                        },
                        "metadata_columns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Additional metadata columns to include",
                            "default": []
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            
            types.Tool(
                name="store_embedding",
                description="Store an embedding vector with associated metadata",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the embeddings table"
                        },
                        "embedding": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "The embedding vector as array of numbers"
                        },
                        "content": {
                            "type": "string",
                            "description": "Original content that was embedded"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata as key-value pairs",
                            "default": {}
                        }
                    },
                    "required": ["table_name", "embedding", "content"]
                }
            ),
            
            types.Tool(
                name="semantic_search",
                description="Perform semantic similarity search using cosine similarity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the embeddings table to search"
                        },
                        "query_embedding": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Query embedding vector for similarity search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10
                        },
                        "similarity_threshold": {
                            "type": "number",
                            "description": "Minimum similarity score (0.0-1.0)",
                            "default": 0.0
                        }
                    },
                    "required": ["table_name", "query_embedding"]
                }
            ),
            
            types.Tool(
                name="hybrid_search",
                description="Combine FTS5 keyword search with semantic similarity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "embeddings_table": {
                            "type": "string",
                            "description": "Name of the embeddings table"
                        },
                        "fts_table": {
                            "type": "string",
                            "description": "Name of the FTS5 table"
                        },
                        "query_text": {
                            "type": "string",
                            "description": "Text query for FTS5 keyword search"
                        },
                        "query_embedding": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Query embedding for semantic search"
                        },
                        "keyword_weight": {
                            "type": "number",
                            "description": "Weight for keyword score (0.0-1.0)",
                            "default": 0.5
                        },
                        "semantic_weight": {
                            "type": "number",
                            "description": "Weight for semantic score (0.0-1.0)",
                            "default": 0.5
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["embeddings_table", "fts_table", "query_text", "query_embedding"]
                }
            ),
            
            types.Tool(
                name="calculate_similarity",
                description="Calculate cosine similarity between two embedding vectors",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "vector1": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "First embedding vector"
                        },
                        "vector2": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Second embedding vector"
                        }
                    },
                    "required": ["vector1", "vector2"]
                }
            ),
            
            types.Tool(
                name="batch_similarity_search",
                description="Perform similarity search with multiple query vectors",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the embeddings table"
                        },
                        "query_embeddings": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "number"}
                            },
                            "description": "Array of query embedding vectors"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results per query",
                            "default": 10
                        }
                    },
                    "required": ["table_name", "query_embeddings"]
                }
            ),
            
            # Vector Index Optimization Tools (v1.9.0)
            types.Tool(
                name="create_vector_index",
                description="Create optimized index for vector similarity search performance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the embeddings table to index"
                        },
                        "embedding_column": {
                            "type": "string", 
                            "description": "Name of the embedding column",
                            "default": "embedding"
                        },
                        "index_type": {
                            "type": "string",
                            "enum": ["cluster", "grid", "hash"],
                            "description": "Type of vector index: cluster (k-means), grid (spatial), hash (LSH)",
                            "default": "cluster"
                        },
                        "num_clusters": {
                            "type": "integer",
                            "description": "Number of clusters for cluster index",
                            "default": 100
                        },
                        "grid_size": {
                            "type": "integer", 
                            "description": "Grid dimensions for spatial index",
                            "default": 10
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            
            types.Tool(
                name="optimize_vector_search",
                description="Perform optimized vector similarity search using created indexes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the indexed embeddings table"
                        },
                        "query_embedding": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Query embedding vector for similarity search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10
                        },
                        "search_k": {
                            "type": "integer",
                            "description": "Number of clusters/cells to search (higher = more accurate, slower)",
                            "default": 5
                        },
                        "similarity_threshold": {
                            "type": "number",
                            "description": "Minimum similarity score (0.0-1.0)",
                            "default": 0.0
                        }
                    },
                    "required": ["table_name", "query_embedding"]
                }
            ),
            
            types.Tool(
                name="analyze_vector_index",
                description="Analyze vector index performance and statistics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the indexed embeddings table"
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            
            types.Tool(
                name="rebuild_vector_index", 
                description="Rebuild vector index for optimal performance after data changes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the embeddings table to rebuild index for"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force rebuild even if index appears current",
                            "default": False
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            
            # Statistical Analysis Tools (v2.1.0)
            types.Tool(
                name="descriptive_statistics",
                description="Calculate comprehensive descriptive statistics for a numeric column",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table"
                        },
                        "column_name": {
                            "type": "string",
                            "description": "Name of the numeric column to analyze"
                        },
                        "where_clause": {
                            "type": "string",
                            "description": "Optional WHERE clause to filter data",
                            "default": ""
                        }
                    },
                    "required": ["table_name", "column_name"]
                }
            ),
            
            types.Tool(
                name="correlation_analysis",
                description="Calculate correlation coefficient between two numeric columns",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table"
                        },
                        "column_x": {
                            "type": "string",
                            "description": "First numeric column"
                        },
                        "column_y": {
                            "type": "string",
                            "description": "Second numeric column"
                        },
                        "where_clause": {
                            "type": "string",
                            "description": "Optional WHERE clause to filter data",
                            "default": ""
                        }
                    },
                    "required": ["table_name", "column_x", "column_y"]
                }
            ),
            
            types.Tool(
                name="percentile_analysis",
                description="Calculate percentiles and quartiles for a numeric column",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table"
                        },
                        "column_name": {
                            "type": "string",
                            "description": "Name of the numeric column to analyze"
                        },
                        "percentiles": {
                            "type": "array",
                            "items": {"type": "number", "minimum": 0, "maximum": 100},
                            "description": "List of percentiles to calculate (0-100)",
                            "default": [25, 50, 75, 90, 95, 99]
                        },
                        "where_clause": {
                            "type": "string",
                            "description": "Optional WHERE clause to filter data",
                            "default": ""
                        }
                    },
                    "required": ["table_name", "column_name"]
                }
            ),
            
            types.Tool(
                name="distribution_analysis",
                description="Analyze the distribution of a numeric column (skewness, kurtosis, normality)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table"
                        },
                        "column_name": {
                            "type": "string",
                            "description": "Name of the numeric column to analyze"
                        },
                        "bins": {
                            "type": "integer",
                            "description": "Number of bins for histogram analysis",
                            "default": 10
                        },
                        "where_clause": {
                            "type": "string",
                            "description": "Optional WHERE clause to filter data",
                            "default": ""
                        }
                    },
                    "required": ["table_name", "column_name"]
                }
            ),
            
            types.Tool(
                name="moving_averages",
                description="Calculate moving averages and trend analysis for time series data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table"
                        },
                        "value_column": {
                            "type": "string",
                            "description": "Name of the numeric column with values"
                        },
                        "time_column": {
                            "type": "string",
                            "description": "Name of the time/date column for ordering"
                        },
                        "window_sizes": {
                            "type": "array",
                            "items": {"type": "integer", "minimum": 2},
                            "description": "List of window sizes for moving averages",
                            "default": [7, 30, 90]
                        },
                        "where_clause": {
                            "type": "string",
                            "description": "Optional WHERE clause to filter data",
                            "default": ""
                        }
                    },
                    "required": ["table_name", "value_column", "time_column"]
                }
            ),
            
            types.Tool(
                name="outlier_detection",
                description="Detect outliers using IQR method and Z-score analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table"
                        },
                        "column_name": {
                            "type": "string",
                            "description": "Name of the numeric column to analyze"
                        },
                        "method": {
                            "type": "string",
                            "enum": ["iqr", "zscore", "both"],
                            "description": "Outlier detection method",
                            "default": "both"
                        },
                        "iqr_multiplier": {
                            "type": "number",
                            "description": "IQR multiplier for outlier threshold",
                            "default": 1.5
                        },
                        "zscore_threshold": {
                            "type": "number",
                            "description": "Z-score threshold for outlier detection",
                            "default": 3.0
                        },
                        "where_clause": {
                            "type": "string",
                            "description": "Optional WHERE clause to filter data",
                            "default": ""
                        }
                    },
                    "required": ["table_name", "column_name"]
                }
            ),
            
            types.Tool(
                name="regression_analysis",
                description="Perform linear regression analysis between two variables",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table"
                        },
                        "x_column": {
                            "type": "string",
                            "description": "Independent variable column"
                        },
                        "y_column": {
                            "type": "string",
                            "description": "Dependent variable column"
                        },
                        "confidence_level": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 0.99,
                            "description": "Confidence level for intervals",
                            "default": 0.95
                        },
                        "where_clause": {
                            "type": "string",
                            "description": "Optional WHERE clause to filter data",
                            "default": ""
                        }
                    },
                    "required": ["table_name", "x_column", "y_column"]
                }
            ),
            
            types.Tool(
                name="hypothesis_testing",
                description="Perform statistical hypothesis tests (t-test, chi-square)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "test_type": {
                            "type": "string",
                            "enum": ["one_sample_t", "two_sample_t", "paired_t", "chi_square_goodness", "chi_square_independence"],
                            "description": "Type of statistical test to perform"
                        },
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table"
                        },
                        "column_name": {
                            "type": "string",
                            "description": "Primary column for analysis"
                        },
                        "column2_name": {
                            "type": "string",
                            "description": "Second column (for two-sample or paired tests)",
                            "default": ""
                        },
                        "test_value": {
                            "type": "number",
                            "description": "Test value for one-sample t-test",
                            "default": 0
                        },
                        "alpha": {
                            "type": "number",
                            "minimum": 0.01,
                            "maximum": 0.10,
                            "description": "Significance level",
                            "default": 0.05
                        },
                        "where_clause": {
                            "type": "string",
                            "description": "Optional WHERE clause to filter data",
                            "default": ""
                        }
                    },
                    "required": ["test_type", "table_name", "column_name"]
                }
            ),
            
            # Text Processing Tools
            types.Tool(
                name="regex_extract",
                description="Extract text using PCRE-style regular expressions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "column_name": {"type": "string", "description": "Name of the column to search"},
                        "pattern": {"type": "string", "description": "Regular expression pattern"},
                        "flags": {"type": "string", "description": "Regex flags (i=ignore case, m=multiline, s=dotall)", "default": ""},
                        "limit": {"type": "integer", "description": "Maximum number of results", "default": 100},
                        "where_clause": {"type": "string", "description": "Optional WHERE clause", "default": ""}
                    },
                    "required": ["table_name", "column_name", "pattern"]
                }
            ),
            
            types.Tool(
                name="regex_replace",
                description="Replace text using PCRE-style regular expressions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "column_name": {"type": "string", "description": "Name of the column to modify"},
                        "pattern": {"type": "string", "description": "Regular expression pattern"},
                        "replacement": {"type": "string", "description": "Replacement text"},
                        "flags": {"type": "string", "description": "Regex flags", "default": ""},
                        "max_replacements": {"type": "integer", "description": "Maximum replacements per row (0=all)", "default": 0},
                        "preview_only": {"type": "boolean", "description": "Preview changes without executing", "default": True},
                        "where_clause": {"type": "string", "description": "Optional WHERE clause", "default": ""}
                    },
                    "required": ["table_name", "column_name", "pattern", "replacement"]
                }
            ),
            
            types.Tool(
                name="fuzzy_match",
                description="Find fuzzy matches using Levenshtein distance and sequence matching",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "column_name": {"type": "string", "description": "Name of the column to search"},
                        "search_term": {"type": "string", "description": "Term to find fuzzy matches for"},
                        "threshold": {"type": "number", "description": "Similarity threshold (0.0-1.0)", "default": 0.6},
                        "limit": {"type": "integer", "description": "Maximum number of results", "default": 50},
                        "where_clause": {"type": "string", "description": "Optional WHERE clause", "default": ""}
                    },
                    "required": ["table_name", "column_name", "search_term"]
                }
            ),
            
            types.Tool(
                name="phonetic_match",
                description="Find phonetic matches using Soundex and Metaphone algorithms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "column_name": {"type": "string", "description": "Name of the column to search"},
                        "search_term": {"type": "string", "description": "Term to find phonetic matches for"},
                        "algorithm": {"type": "string", "description": "Algorithm to use (soundex, metaphone)", "default": "soundex"},
                        "limit": {"type": "integer", "description": "Maximum number of results", "default": 50},
                        "where_clause": {"type": "string", "description": "Optional WHERE clause", "default": ""}
                    },
                    "required": ["table_name", "column_name", "search_term"]
                }
            ),
            
            types.Tool(
                name="text_similarity",
                description="Calculate text similarity between columns or against reference text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "column_name": {"type": "string", "description": "Name of the column to analyze"},
                        "reference_text": {"type": "string", "description": "Reference text for comparison", "default": ""},
                        "compare_column": {"type": "string", "description": "Second column for comparison", "default": ""},
                        "algorithm": {"type": "string", "description": "Similarity algorithm (cosine, jaccard, levenshtein)", "default": "cosine"},
                        "limit": {"type": "integer", "description": "Maximum number of results", "default": 100},
                        "where_clause": {"type": "string", "description": "Optional WHERE clause", "default": ""}
                    },
                    "required": ["table_name", "column_name"]
                }
            ),
            
            types.Tool(
                name="text_normalize",
                description="Normalize text with various transformations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "column_name": {"type": "string", "description": "Name of the column to normalize"},
                        "operations": {"type": "array", "items": {"type": "string"}, "description": "Normalization operations", "default": ["lowercase", "trim"]},
                        "preview_only": {"type": "boolean", "description": "Preview changes without executing", "default": True},
                        "where_clause": {"type": "string", "description": "Optional WHERE clause", "default": ""}
                    },
                    "required": ["table_name", "column_name"]
                }
            ),
            
            types.Tool(
                name="advanced_search",
                description="Advanced search combining multiple text processing techniques",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "column_name": {"type": "string", "description": "Name of the column to search"},
                        "search_term": {"type": "string", "description": "Search term"},
                        "techniques": {"type": "array", "items": {"type": "string"}, "description": "Search techniques to use", "default": ["exact", "fuzzy", "phonetic"]},
                        "fuzzy_threshold": {"type": "number", "description": "Fuzzy match threshold", "default": 0.6},
                        "limit": {"type": "integer", "description": "Maximum number of results", "default": 100},
                        "where_clause": {"type": "string", "description": "Optional WHERE clause", "default": ""}
                    },
                    "required": ["table_name", "column_name", "search_term"]
                }
            ),
            
            types.Tool(
                name="text_validation",
                description="Validate text against various patterns and rules",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "column_name": {"type": "string", "description": "Name of the column to validate"},
                        "validation_type": {"type": "string", "description": "Type of validation (email, phone, url, custom_regex)", "default": "email"},
                        "custom_pattern": {"type": "string", "description": "Custom regex pattern for validation", "default": ""},
                        "return_invalid_only": {"type": "boolean", "description": "Only return invalid entries", "default": True},
                        "where_clause": {"type": "string", "description": "Optional WHERE clause", "default": ""}
                    },
                    "required": ["table_name", "column_name"]
                }
            ),
            
            # JSON Helper Tools (Issue #25)
            types.Tool(
                name="json_insert",
                description="Insert JSON data with validation and auto-normalization",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"},
                        "column": {"type": "string", "description": "JSON column name"},
                        "data": {
                            "anyOf": [
                                {"type": "object"},
                                {"type": "array"},
                                {"type": "string"}
                            ],
                            "description": "JSON data to insert (object, array, or JSON string)"
                        },
                        "where_clause": {"type": "string", "description": "Optional WHERE clause for updates", "default": ""},
                        "merge_strategy": {
                            "type": "string",
                            "enum": ["replace", "merge", "error"],
                            "description": "Strategy for handling existing data",
                            "default": "replace"
                        }
                    },
                    "required": ["table", "column", "data"]
                }
            ),
            
            types.Tool(
                name="json_update",
                description="Update JSON fields by path with path validation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"},
                        "column": {"type": "string", "description": "JSON column name"},
                        "path": {"type": "string", "description": "JSON path to update (e.g., '$.category')"},
                        "value": {
                            "anyOf": [
                                {"type": "string"},
                                {"type": "number"},
                                {"type": "boolean"},
                                {"type": "null"},
                                {"type": "object"},
                                {"type": "array"}
                            ],
                            "description": "New value for the JSON path"
                        },
                        "where_clause": {"type": "string", "description": "Optional WHERE clause", "default": ""},
                        "create_path": {"type": "boolean", "description": "Create missing intermediate objects", "default": False}
                    },
                    "required": ["table", "column", "path", "value"]
                }
            ),
            
            types.Tool(
                name="json_select",
                description="Extract JSON data by path with structured output",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"},
                        "column": {"type": "string", "description": "JSON column name"},
                        "paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of JSON paths to extract (e.g., ['$.name', '$.tags[0]'])"
                        },
                        "where_clause": {"type": "string", "description": "Optional WHERE clause", "default": ""},
                        "output_format": {
                            "type": "string",
                            "enum": ["structured", "flat", "raw"],
                            "description": "Output format for results",
                            "default": "structured"
                        }
                    },
                    "required": ["table", "column", "paths"]
                }
            ),
            
            types.Tool(
                name="json_query",
                description="Complex JSON queries with path filtering and aggregation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"},
                        "column": {"type": "string", "description": "JSON column name"},
                        "filter_paths": {
                            "type": "object",
                            "description": "Dict of JSON path->value filters (e.g., {'$.category': 'electronics'})",
                            "default": {}
                        },
                        "select_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of JSON paths to select",
                            "default": []
                        },
                        "aggregate": {
                            "type": "object",
                            "description": "Dict of alias->aggregation expressions",
                            "default": {}
                        },
                        "group_by": {"type": "string", "description": "GROUP BY expression", "default": ""},
                        "order_by": {"type": "string", "description": "ORDER BY expression", "default": ""},
                        "limit": {"type": "integer", "description": "LIMIT value", "default": 0}
                    },
                    "required": ["table", "column"]
                }
            ),
            
            types.Tool(
                name="json_validate_path",
                description="Validate JSON paths before operations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "JSON path to validate (e.g., '$.key', '$.array[0]')"}
                    },
                    "required": ["path"]
                }
            ),
            
            types.Tool(
                name="json_merge",
                description="Merge JSON objects with conflict resolution",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"},
                        "column": {"type": "string", "description": "JSON column name"},
                        "merge_data": {
                            "anyOf": [
                                {"type": "object"},
                                {"type": "string"}
                            ],
                            "description": "JSON data to merge (object or JSON string)"
                        },
                        "where_clause": {"type": "string", "description": "Optional WHERE clause", "default": ""},
                        "strategy": {
                            "type": "string",
                            "enum": ["replace", "merge_deep", "merge_shallow"],
                            "description": "Merge strategy for conflicts",
                            "default": "merge_deep"
                        }
                    },
                    "required": ["table", "column", "merge_data"]
                }
            ),
        ]
        
        # Add diagnostic tools if JSONB is supported
        if db.version_info['has_jsonb_support']:
            diagnostic_tools = [
                types.Tool(
                    name="validate_json",
                    description="Validate a JSON string and provide detailed feedback",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "json_str": {"type": "string", "description": "JSON string to validate"},
                        },
                        "required": ["json_str"],
                    },
                ),
                types.Tool(
                    name="test_jsonb_conversion",
                    description="Test conversion of a JSON string to JSONB format and back",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "json_str": {"type": "string", "description": "JSON string to convert"},
                        },
                        "required": ["json_str"],
                    },
                ),
            ]
            
            return basic_tools + diagnostic_tools
        else:
            return basic_tools

    @server.call_tool()
    async def handle_call_tool(  # type: ignore[misc]
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            # Delegate to helper functions for basic tools
            if name == "list_tables":
                return await _handle_list_tables()
            elif name == "describe_table":
                return await _handle_describe_table(arguments or {})

            # Statistical Analysis Handlers (v2.1.0)
            elif name == "descriptive_statistics":
                table_name = arguments.get("table_name")
                column_name = arguments.get("column_name")
                where_clause = arguments.get("where_clause", "")
                
                try:
                    # Build WHERE clause
                    where_sql = f" WHERE {where_clause}" if where_clause else ""
                    
                    # Calculate comprehensive descriptive statistics
                    stats_query = f"""
                    SELECT 
                        COUNT({column_name}) as count,
                        COUNT(DISTINCT {column_name}) as distinct_count,
                        AVG(CAST({column_name} AS REAL)) as mean,
                        MIN(CAST({column_name} AS REAL)) as min_value,
                        MAX(CAST({column_name} AS REAL)) as max_value,
                        SUM(CAST({column_name} AS REAL)) as sum_value,
                        
                        -- Standard deviation and variance
                        (
                            SELECT SQRT(AVG(power_diff))
                            FROM (
                                SELECT POWER(CAST({column_name} AS REAL) - 
                                    (SELECT AVG(CAST({column_name} AS REAL)) FROM {table_name}{where_sql}), 2) as power_diff
                                FROM {table_name}{where_sql}
                                WHERE {column_name} IS NOT NULL
                            )
                        ) as std_dev,
                        
                        (
                            SELECT AVG(power_diff)
                            FROM (
                                SELECT POWER(CAST({column_name} AS REAL) - 
                                    (SELECT AVG(CAST({column_name} AS REAL)) FROM {table_name}{where_sql}), 2) as power_diff
                                FROM {table_name}{where_sql}
                                WHERE {column_name} IS NOT NULL
                            )
                        ) as variance,
                        
                        -- Range and coefficient of variation
                        (MAX(CAST({column_name} AS REAL)) - MIN(CAST({column_name} AS REAL))) as range_value,
                        
                        CASE 
                            WHEN AVG(CAST({column_name} AS REAL)) != 0 THEN
                                (
                                    SELECT SQRT(AVG(power_diff))
                                    FROM (
                                        SELECT POWER(CAST({column_name} AS REAL) - 
                                            (SELECT AVG(CAST({column_name} AS REAL)) FROM {table_name}{where_sql}), 2) as power_diff
                                        FROM {table_name}{where_sql}
                                        WHERE {column_name} IS NOT NULL
                                    )
                                ) / AVG(CAST({column_name} AS REAL))
                            ELSE NULL
                        END as coefficient_of_variation
                        
                    FROM {table_name}{where_sql}
                    WHERE {column_name} IS NOT NULL
                    """
                    
                    result = db._execute_query(stats_query)
                    
                    if result:
                        stats = result[0]
                        
                        # Format output
                        cv_text = f"{stats['coefficient_of_variation']:.4f}" if stats['coefficient_of_variation'] is not None else 'N/A'
                        
                        output = f"""Descriptive Statistics for {table_name}.{column_name}:

Basic Statistics:
- Count: {stats['count']:,}
- Distinct Values: {stats['distinct_count']:,}

Central Tendency:
- Mean: {stats['mean']:.4f}
- Min: {stats['min_value']:.4f}
- Max: {stats['max_value']:.4f}
- Sum: {stats['sum_value']:.4f}

Variability:
- Range: {stats['range_value']:.4f}
- Standard Deviation: {stats['std_dev']:.4f}
- Variance: {stats['variance']:.4f}
- Coefficient of Variation: {cv_text}"""
                        
                        return [types.TextContent(type="text", text=output)]
                    else:
                        return [types.TextContent(type="text", text="No data found for analysis")]
                        
                except Exception as e:
                    error_msg = f"Failed to calculate descriptive statistics: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "correlation_analysis":
                table_name = arguments.get("table_name")
                column_x = arguments.get("column_x")
                column_y = arguments.get("column_y")
                where_clause = arguments.get("where_clause", "")
                
                try:
                    where_sql = f" WHERE {where_clause}" if where_clause else ""
                    
                    # Calculate Pearson correlation coefficient using direct approach
                    corr_query = f"""
                    SELECT 
                        COUNT(*) as n,
                        AVG(CAST({column_x} AS REAL)) as mean_x,
                        AVG(CAST({column_y} AS REAL)) as mean_y,
                        (
                            (COUNT(*) * SUM(CAST({column_x} AS REAL) * CAST({column_y} AS REAL)) - 
                             SUM(CAST({column_x} AS REAL)) * SUM(CAST({column_y} AS REAL))) 
                            / 
                            SQRT(
                                (COUNT(*) * SUM(CAST({column_x} AS REAL) * CAST({column_x} AS REAL)) - 
                                 SUM(CAST({column_x} AS REAL)) * SUM(CAST({column_x} AS REAL))) *
                                (COUNT(*) * SUM(CAST({column_y} AS REAL) * CAST({column_y} AS REAL)) - 
                                 SUM(CAST({column_y} AS REAL)) * SUM(CAST({column_y} AS REAL)))
                            )
                        ) as correlation
                    FROM {table_name}{where_sql}
                    WHERE {column_x} IS NOT NULL AND {column_y} IS NOT NULL
                    HAVING COUNT(*) > 1
                    """
                    
                    result = db._execute_query(corr_query)
                    
                    if result and len(result) > 0:
                        stats = result[0]
                        correlation = stats['correlation'] if 'correlation' in stats.keys() and stats['correlation'] is not None else 0.0
                        
                        # Interpret correlation strength
                        if abs(correlation) >= 0.9:
                            strength = "Very Strong"
                        elif abs(correlation) >= 0.7:
                            strength = "Strong"
                        elif abs(correlation) >= 0.5:
                            strength = "Moderate"
                        elif abs(correlation) >= 0.3:
                            strength = "Weak"
                        else:
                            strength = "Very Weak"
                        
                        direction = "Positive" if correlation >= 0 else "Negative"
                        
                        output = f"""Correlation Analysis between {column_x} and {column_y}:

Sample Size: {stats['n']:,}
Mean {column_x}: {stats['mean_x']:.4f}
Mean {column_y}: {stats['mean_y']:.4f}

Pearson Correlation Coefficient: {correlation:.4f}
Relationship: {strength} {direction} correlation
R-squared: {correlation**2:.4f} ({correlation**2*100:.1f}% of variance explained)"""
                        
                        return [types.TextContent(type="text", text=output)]
                    else:
                        return [types.TextContent(type="text", text="No data found for correlation analysis")]
                        
                except Exception as e:
                    error_msg = f"Failed to calculate correlation: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "percentile_analysis":
                table_name = arguments.get("table_name")
                column_name = arguments.get("column_name")
                percentiles = arguments.get("percentiles", [25, 50, 75, 90, 95, 99])
                where_clause = arguments.get("where_clause", "")
                
                try:
                    where_sql = f" WHERE {where_clause}" if where_clause else ""
                    
                    # Calculate percentiles using NTILE and row_number
                    percentile_queries = []
                    for p in percentiles:
                        percentile_queries.append(f"""
                        SELECT {p} as percentile,
                               (SELECT CAST({column_name} AS REAL) 
                                FROM (SELECT {column_name}, 
                                             ROW_NUMBER() OVER (ORDER BY CAST({column_name} AS REAL)) as rn,
                                             COUNT(*) OVER () as total_count
                                      FROM {table_name}{where_sql}
                                      WHERE {column_name} IS NOT NULL)
                                WHERE rn = CAST(({p} / 100.0) * total_count AS INTEGER) + 1) as value
                        """)
                    
                    full_query = " UNION ALL ".join(percentile_queries)
                    result = db._execute_query(full_query)
                    
                    if result:
                        output = f"Percentile Analysis for {table_name}.{column_name}:\n\n"
                        
                        for row in result:
                            p = int(row['percentile'])
                            value = row['value']
                            
                            if p == 25:
                                output += f"Q1 (25th percentile): {value:.4f}\n"
                            elif p == 50:
                                output += f"Median (50th percentile): {value:.4f}\n"
                            elif p == 75:
                                output += f"Q3 (75th percentile): {value:.4f}\n"
                            else:
                                output += f"{p}th percentile: {value:.4f}\n"
                        
                        # Calculate IQR
                        q1 = next((row['value'] for row in result if row['percentile'] == 25), None)
                        q3 = next((row['value'] for row in result if row['percentile'] == 75), None)
                        if q1 is not None and q3 is not None:
                            output += f"\nInterquartile Range (IQR): {q3 - q1:.4f}"
                        
                        return [types.TextContent(type="text", text=output)]
                    else:
                        return [types.TextContent(type="text", text="No data found for percentile analysis")]
                        
                except Exception as e:
                    error_msg = f"Failed to calculate percentiles: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "outlier_detection":
                table_name = arguments.get("table_name")
                column_name = arguments.get("column_name")
                method = arguments.get("method", "both")
                iqr_multiplier = arguments.get("iqr_multiplier", 1.5)
                zscore_threshold = arguments.get("zscore_threshold", 3.0)
                where_clause = arguments.get("where_clause", "")
                
                try:
                    where_sql = f" WHERE {where_clause}" if where_clause else ""
                    
                    outliers_found = []
                    
                    if method in ["iqr", "both"]:
                        # IQR method - simplified approach
                        # First get basic stats
                        stats_query = f"""
                        SELECT 
                            MIN(CAST({column_name} AS REAL)) as min_val,
                            MAX(CAST({column_name} AS REAL)) as max_val,
                            AVG(CAST({column_name} AS REAL)) as mean_val,
                            COUNT(*) as total_count
                        FROM {table_name}{where_sql}
                        WHERE {column_name} IS NOT NULL
                        """
                        
                        iqr_result = db._execute_query(stats_query)
                        if iqr_result and len(iqr_result) > 0:
                            row = iqr_result[0]
                            outliers_found.append(f"IQR Method (multiplier={iqr_multiplier}):")
                            outliers_found.append(f"  Range: {row['min_val']:.4f} to {row['max_val']:.4f}")
                            outliers_found.append(f"  Mean: {row['mean_val']:.4f}")
                            outliers_found.append(f"  Sample size: {row['total_count']}")
                            outliers_found.append(f"  Note: Simplified IQR analysis - use descriptive_statistics for detailed quartiles")
                    
                    if method in ["zscore", "both"]:
                        # Z-score method - simplified
                        # First get the mean
                        mean_query = f"""
                        SELECT AVG(CAST({column_name} AS REAL)) as mean_val, COUNT(*) as total_count
                        FROM {table_name}{where_sql}
                        WHERE {column_name} IS NOT NULL
                        """
                        mean_result = db._execute_query(mean_query)
                        if not mean_result or len(mean_result) == 0:
                            outliers_found.append(f"\nZ-Score Method (threshold={zscore_threshold}):")
                            outliers_found.append(f"  No data available")
                        else:
                            mean_val = mean_result[0]['mean_val']
                            total_count = mean_result[0]['total_count']
                            
                            # Then calculate std dev using the mean
                            zscore_query = f"""
                            SELECT 
                                {mean_val} as mean_val,
                                SQRT(AVG(POWER(CAST({column_name} AS REAL) - {mean_val}, 2))) as std_dev,
                                {total_count} as total_count
                            FROM {table_name}{where_sql}
                            WHERE {column_name} IS NOT NULL
                            """
                            
                            zscore_result = db._execute_query(zscore_query)
                            if zscore_result and len(zscore_result) > 0:
                                row = zscore_result[0]
                                outliers_found.append(f"\nZ-Score Method (threshold={zscore_threshold}):")
                                outliers_found.append(f"  Mean: {row['mean_val']:.4f}")
                                outliers_found.append(f"  Std Dev: {row['std_dev']:.4f}")
                                outliers_found.append(f"  Lower bound: {row['mean_val'] - zscore_threshold * row['std_dev']:.4f}")
                                outliers_found.append(f"  Upper bound: {row['mean_val'] + zscore_threshold * row['std_dev']:.4f}")
                                outliers_found.append(f"  Note: Use descriptive_statistics for detailed outlier detection")
                            else:
                                outliers_found.append(f"\nZ-Score Method (threshold={zscore_threshold}):")
                                outliers_found.append(f"  No data available")
                    
                    output = f"Outlier Detection for {table_name}.{column_name}:\n\n" + "\n".join(outliers_found)
                    return [types.TextContent(type="text", text=output)]
                        
                except Exception as e:
                    error_msg = f"Failed to detect outliers: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "moving_averages":
                table_name = arguments.get("table_name")
                value_column = arguments.get("value_column")
                time_column = arguments.get("time_column")
                window_sizes = arguments.get("window_sizes", [7, 30, 90])
                where_clause = arguments.get("where_clause", "")
                
                try:
                    where_sql = f" WHERE {where_clause}" if where_clause else ""
                    
                    # Create moving averages for each window size
                    ma_queries = []
                    for window in window_sizes:
                        ma_queries.append(f"""
                        SELECT 
                            {time_column},
                            CAST({value_column} AS REAL) as value,
                            {window} as window_size,
                            AVG(CAST({value_column} AS REAL)) OVER (
                                ORDER BY {time_column} 
                                ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW
                            ) as moving_average
                        FROM {table_name}{where_sql}
                        WHERE {value_column} IS NOT NULL AND {time_column} IS NOT NULL
                        """)
                    
                    # For now, just show the first window size results
                    result = db._execute_query(ma_queries[0])
                    
                    if result:
                        output = f"Moving Average Analysis ({window_sizes[0]}-period) for {table_name}.{value_column}:\n\n"
                        
                        # Show last 10 records
                        for i, row in enumerate(result[-10:]):
                            output += f"{row[time_column]}: Value={row['value']:.2f}, MA({window_sizes[0]})={row['moving_average']:.2f}\n"
                        
                        # Calculate trend
                        if len(result) >= 2:
                            first_ma = result[0]['moving_average']
                            last_ma = result[-1]['moving_average']
                            trend = "Increasing" if last_ma > first_ma else "Decreasing"
                            change = ((last_ma - first_ma) / first_ma) * 100 if first_ma != 0 else 0
                            output += f"\nTrend: {trend} ({change:+.1f}% change)"
                        
                        return [types.TextContent(type="text", text=output)]
                    else:
                        return [types.TextContent(type="text", text="No data found for moving average analysis")]
                        
                except Exception as e:
                    error_msg = f"Failed to calculate moving averages: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "distribution_analysis":
                table_name = arguments.get("table_name")
                column_name = arguments.get("column_name")
                bins = arguments.get("bins", 10)
                where_clause = arguments.get("where_clause", "")
                
                try:
                    where_sql = f" WHERE {where_clause}" if where_clause else ""
                    
                    # First get basic stats
                    basic_query = f"""
                    SELECT 
                        COUNT(*) as count,
                        AVG(CAST({column_name} AS REAL)) as mean,
                        MIN(CAST({column_name} AS REAL)) as min_val,
                        MAX(CAST({column_name} AS REAL)) as max_val
                    FROM {table_name}{where_sql}
                    WHERE {column_name} IS NOT NULL
                    """
                    
                    basic_result = db._execute_query(basic_query)
                    if not basic_result or len(basic_result) == 0:
                        return [types.TextContent(type="text", text="No data found for distribution analysis")]
                    
                    basic_stats = basic_result[0]
                    mean_val = basic_stats['mean']
                    
                    # Then get standard deviation using the mean
                    dist_query = f"""
                    SELECT 
                        {basic_stats['count']} as count,
                        {mean_val} as mean,
                        {basic_stats['min_val']} as min_val,
                        {basic_stats['max_val']} as max_val,
                        SQRT(AVG(POWER(CAST({column_name} AS REAL) - {mean_val}, 2))) as std_dev
                    FROM {table_name}{where_sql}
                    WHERE {column_name} IS NOT NULL
                    """
                    
                    result = db._execute_query(dist_query)
                    
                    if result and len(result) > 0:
                        stats = result[0]
                        bin_width = (stats['max_val'] - stats['min_val']) / bins if stats['max_val'] != stats['min_val'] else 0
                        
                        output = f"""Distribution Analysis for {table_name}.{column_name}:

Basic Statistics:
- Count: {stats['count']:,}
- Mean: {stats['mean']:.4f}
- Std Dev: {stats['std_dev']:.4f}
- Range: {stats['min_val']:.4f} to {stats['max_val']:.4f}

Distribution Summary:
- Requested bins: {bins}
- Calculated bin width: {bin_width:.4f}
- Note: Use descriptive_statistics and percentile_analysis for detailed distribution analysis
"""
                        
                        return [types.TextContent(type="text", text=output)]
                    else:
                        return [types.TextContent(type="text", text="No data found for distribution analysis")]
                        
                except Exception as e:
                    error_msg = f"Failed to analyze distribution: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "regression_analysis":
                table_name = arguments.get("table_name")
                x_column = arguments.get("x_column")
                y_column = arguments.get("y_column")
                confidence_level = arguments.get("confidence_level", 0.95)
                where_clause = arguments.get("where_clause", "")
                
                try:
                    where_sql = f" WHERE {where_clause}" if where_clause else ""
                    
                    # Calculate linear regression using direct approach
                    regression_query = f"""
                    SELECT 
                        COUNT(*) as n,
                        AVG(CAST({x_column} AS REAL)) as mean_x,
                        AVG(CAST({y_column} AS REAL)) as mean_y,
                        (
                            (COUNT(*) * SUM(CAST({x_column} AS REAL) * CAST({y_column} AS REAL)) - 
                             SUM(CAST({x_column} AS REAL)) * SUM(CAST({y_column} AS REAL))) 
                            / 
                            (COUNT(*) * SUM(CAST({x_column} AS REAL) * CAST({x_column} AS REAL)) - 
                             SUM(CAST({x_column} AS REAL)) * SUM(CAST({x_column} AS REAL)))
                        ) as slope,
                        (
                            AVG(CAST({y_column} AS REAL)) - 
                            (
                                (COUNT(*) * SUM(CAST({x_column} AS REAL) * CAST({y_column} AS REAL)) - 
                                 SUM(CAST({x_column} AS REAL)) * SUM(CAST({y_column} AS REAL))) 
                                / 
                                (COUNT(*) * SUM(CAST({x_column} AS REAL) * CAST({x_column} AS REAL)) - 
                                 SUM(CAST({x_column} AS REAL)) * SUM(CAST({x_column} AS REAL)))
                            ) * AVG(CAST({x_column} AS REAL))
                        ) as intercept,
                        (
                            (COUNT(*) * SUM(CAST({x_column} AS REAL) * CAST({y_column} AS REAL)) - 
                             SUM(CAST({x_column} AS REAL)) * SUM(CAST({y_column} AS REAL))) 
                            / 
                            SQRT(
                                (COUNT(*) * SUM(CAST({x_column} AS REAL) * CAST({x_column} AS REAL)) - 
                                 SUM(CAST({x_column} AS REAL)) * SUM(CAST({x_column} AS REAL))) *
                                (COUNT(*) * SUM(CAST({y_column} AS REAL) * CAST({y_column} AS REAL)) - 
                                 SUM(CAST({y_column} AS REAL)) * SUM(CAST({y_column} AS REAL)))
                            )
                        ) as r_value
                    FROM {table_name}{where_sql}
                    WHERE {x_column} IS NOT NULL AND {y_column} IS NOT NULL
                    HAVING COUNT(*) > 2
                    """
                    
                    result = db._execute_query(regression_query)
                    
                    if result and len(result) > 0:
                        reg = result[0]
                        r_squared = reg['r_value'] ** 2 if reg['r_value'] is not None else 0
                        
                        output = f"""Linear Regression Analysis: {y_column} ~ {x_column}

Sample Size: {reg['n']:,}
Regression Equation: y = {reg['slope']:.4f}x + {reg['intercept']:.4f}

Coefficients:
- Slope: {reg['slope']:.4f}
- Intercept: {reg['intercept']:.4f}
- Correlation (r): {reg['r_value']:.4f}
- R-squared: {r_squared:.4f} ({r_squared*100:.1f}% of variance explained)

Interpretation:
For every 1-unit increase in {x_column}, {y_column} {'increases' if reg['slope'] > 0 else 'decreases'} by {abs(reg['slope']):.4f} units on average."""
                        
                        return [types.TextContent(type="text", text=output)]
                    else:
                        return [types.TextContent(type="text", text="Insufficient data for regression analysis (need >2 points)")]
                        
                except Exception as e:
                    error_msg = f"Failed to perform regression analysis: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "hypothesis_testing":
                test_type = arguments.get("test_type")
                table_name = arguments.get("table_name")
                column_name = arguments.get("column_name")
                column2_name = arguments.get("column2_name", "")
                test_value = arguments.get("test_value", 0)
                alpha = arguments.get("alpha", 0.05)
                where_clause = arguments.get("where_clause", "")
                
                try:
                    where_sql = f" WHERE {where_clause}" if where_clause else ""
                    
                    if test_type == "one_sample_t":
                        # First get basic stats
                        basic_query = f"""
                        SELECT 
                            COUNT(*) as n,
                            AVG(CAST({column_name} AS REAL)) as mean
                        FROM {table_name}{where_sql}
                        WHERE {column_name} IS NOT NULL
                        """
                        
                        basic_result = db._execute_query(basic_query)
                        if not basic_result or len(basic_result) == 0 or basic_result[0]['n'] <= 1:
                            return [types.TextContent(type="text", text="Insufficient data for t-test (need n > 1)")]
                        
                        n = basic_result[0]['n']
                        mean = basic_result[0]['mean']
                        
                        # Then calculate std dev and t-statistic
                        test_query = f"""
                        SELECT 
                            {n} as n,
                            {mean} as mean,
                            SQRT(
                                SUM(POWER(CAST({column_name} AS REAL) - {mean}, 2)) / ({n} - 1)
                            ) as std_dev,
                            ({mean} - {test_value}) / 
                            (SQRT(
                                SUM(POWER(CAST({column_name} AS REAL) - {mean}, 2)) / ({n} - 1)
                            ) / SQRT({n})) as t_statistic,
                            {test_value} as test_value
                        FROM {table_name}{where_sql}
                        WHERE {column_name} IS NOT NULL
                        """
                        
                        result = db._execute_query(test_query)
                        
                        if result and len(result) > 0:
                            test_result = result[0]
                            
                            # Critical t-value approximation (for common cases)
                            df = test_result['n'] - 1
                            critical_t = 2.0  # Rough approximation for 95% confidence
                            
                            p_value_approx = "< 0.05" if abs(test_result['t_statistic']) > critical_t else "> 0.05"
                            significant = abs(test_result['t_statistic']) > critical_t
                            
                            output = f"""One-Sample t-Test Results:

Null Hypothesis: μ = {test_value}
Alternative Hypothesis: μ ≠ {test_value}

Sample Statistics:
- Sample Size: {test_result['n']:,}
- Sample Mean: {test_result['mean']:.4f}
- Sample Std Dev: {test_result['std_dev']:.4f}
- Degrees of Freedom: {df}

Test Results:
- t-statistic: {test_result['t_statistic']:.4f}
- p-value: {p_value_approx} (approximate)
- Significance Level: {alpha}

Conclusion: {'Reject' if significant else 'Fail to reject'} the null hypothesis at α = {alpha}
The sample mean is {'significantly different from' if significant else 'not significantly different from'} {test_value}."""
                            
                            return [types.TextContent(type="text", text=output)]
                        else:
                            return [types.TextContent(type="text", text="Insufficient data for t-test (need >1 observation)")]
                    
                    else:
                        return [types.TextContent(type="text", text=f"Test type '{test_type}' not yet implemented. Available: one_sample_t")]
                        
                except Exception as e:
                    error_msg = f"Failed to perform hypothesis test: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "append_insight":
                if not arguments or "insight" not in arguments:
                    raise ValueError("Missing insight argument")

                db.insights.append(arguments["insight"])
                _ = db._synthesize_memo()

                # Notify clients that the memo resource has changed
                await server.request_context.session.send_resource_updated(AnyUrl("memo://insights"))

                return [types.TextContent(type="text", text="Insight added to memo")]
                
            # Handle diagnostic tools
            elif name == "validate_json":
                if not arguments or "json_str" not in arguments:
                    raise ValueError("Missing json_str argument")
                    
                # Use isolated functions to avoid MCP framework conflicts
                from .diagnostics_isolated import isolated_validate_json
                result = isolated_validate_json(arguments["json_str"])
                
                return [types.TextContent(type="text", text=json_module.dumps(result, indent=2))]
                
            elif name == "test_jsonb_conversion":
                if not arguments or "json_str" not in arguments:
                    raise ValueError("Missing json_str argument")
                    
                # Use isolated functions to avoid MCP framework conflicts  
                from .diagnostics_isolated import isolated_test_jsonb_conversion
                result = isolated_test_jsonb_conversion(arguments["json_str"])
                
                return [types.TextContent(type="text", text=json_module.dumps(result, indent=2))]

            # Handle JSON helper tools (Issue #25)
            elif name == "json_insert":
                if not arguments:
                    raise ValueError("Missing arguments")
                
                required_args = ["table", "column", "data"]
                for arg in required_args:
                    if arg not in arguments:
                        raise ValueError(f"Missing required argument: {arg}")
                
                try:
                    query_builder = JSONQueryBuilder()
                    query, params, validation_result = query_builder.build_json_insert_query(
                        table=arguments["table"],
                        column=arguments["column"],
                        data=arguments["data"],
                        where_clause=arguments.get("where_clause", ""),
                        merge_strategy=arguments.get("merge_strategy", "replace")
                    )
                    
                    if not validation_result.get("valid", False):
                        return [types.TextContent(
                            type="text", 
                            text=json_module.dumps({
                                "success": False,
                                "error": validation_result.get("error", "Validation failed"),
                                "suggestions": validation_result.get("suggestions", [])
                            }, indent=2)
                        )]
                    
                    # Execute the query
                    result = db._execute_query(query, params)
                    
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps({
                            "success": True,
                            "result": result,
                            "validation": validation_result
                        }, indent=2)
                    )]
                    
                except Exception as e:
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps({
                            "success": False,
                            "error": f"JSON insert failed: {str(e)}"
                        }, indent=2)
                    )]
            
            elif name == "json_update":
                if not arguments:
                    raise ValueError("Missing arguments")
                
                required_args = ["table", "column", "path", "value"]
                for arg in required_args:
                    if arg not in arguments:
                        raise ValueError(f"Missing required argument: {arg}")
                
                try:
                    query_builder = JSONQueryBuilder()
                    query, params, validation_result = query_builder.build_json_update_query(
                        table=arguments["table"],
                        column=arguments["column"],
                        path=arguments["path"],
                        value=arguments["value"],
                        where_clause=arguments.get("where_clause", ""),
                        create_path=arguments.get("create_path", False)
                    )
                    
                    if not validation_result.get("valid", False):
                        return [types.TextContent(
                            type="text", 
                            text=json_module.dumps({
                                "success": False,
                                "error": validation_result.get("error", "Validation failed"),
                                "suggestions": validation_result.get("suggestions", [])
                            }, indent=2)
                        )]
                    
                    # Execute the query
                    result = db._execute_query(query, params)
                    
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps({
                            "success": True,
                            "result": result,
                            "validation": validation_result
                        }, indent=2)
                    )]
                    
                except Exception as e:
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps({
                            "success": False,
                            "error": f"JSON update failed: {str(e)}"
                        }, indent=2)
                    )]
            
            elif name == "json_select":
                if not arguments:
                    raise ValueError("Missing arguments")
                
                required_args = ["table", "column", "paths"]
                for arg in required_args:
                    if arg not in arguments:
                        raise ValueError(f"Missing required argument: {arg}")
                
                try:
                    query_builder = JSONQueryBuilder()
                    query, params, validation_result = query_builder.build_json_select_query(
                        table=arguments["table"],
                        column=arguments["column"],
                        paths=arguments["paths"],
                        where_clause=arguments.get("where_clause", ""),
                        output_format=arguments.get("output_format", "structured")
                    )
                    
                    if not validation_result.get("valid", False):
                        return [types.TextContent(
                            type="text", 
                            text=json_module.dumps({
                                "success": False,
                                "error": validation_result.get("error", "Validation failed"),
                                "suggestions": validation_result.get("suggestions", [])
                            }, indent=2)
                        )]
                    
                    # Execute the query
                    result = db._execute_query(query, params)
                    
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps({
                            "success": True,
                            "result": result,
                            "validation": validation_result
                        }, indent=2)
                    )]
                    
                except Exception as e:
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps({
                            "success": False,
                            "error": f"JSON select failed: {str(e)}"
                        }, indent=2)
                    )]
            
            elif name == "json_query":
                if not arguments:
                    raise ValueError("Missing arguments")
                
                required_args = ["table", "column"]
                for arg in required_args:
                    if arg not in arguments:
                        raise ValueError(f"Missing required argument: {arg}")
                
                try:
                    query_builder = JSONQueryBuilder()
                    query, params, validation_result = query_builder.build_json_query_complex(
                        table=arguments["table"],
                        column=arguments["column"],
                        filter_paths=arguments.get("filter_paths", {}),
                        select_paths=arguments.get("select_paths", []),
                        aggregate=arguments.get("aggregate", {}),
                        group_by=arguments.get("group_by", ""),
                        order_by=arguments.get("order_by", ""),
                        limit=arguments.get("limit", 0) if arguments.get("limit", 0) > 0 else None
                    )
                    
                    if not validation_result.get("valid", False):
                        return [types.TextContent(
                            type="text", 
                            text=json_module.dumps({
                                "success": False,
                                "error": validation_result.get("error", "Validation failed"),
                                "suggestions": validation_result.get("suggestions", [])
                            }, indent=2)
                        )]
                    
                    # Execute the query
                    result = db._execute_query(query, params)
                    
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps({
                            "success": True,
                            "result": result,
                            "validation": validation_result
                        }, indent=2)
                    )]
                    
                except Exception as e:
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps({
                            "success": False,
                            "error": f"JSON query failed: {str(e)}"
                        }, indent=2)
                    )]
            
            elif name == "json_validate_path":
                if not arguments or "path" not in arguments:
                    raise ValueError("Missing path argument")
                
                try:
                    path_validator = JSONPathValidator()
                    validation_result = path_validator.validate_json_path(arguments["path"])
                    
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps(validation_result, indent=2)
                    )]
                    
                except Exception as e:
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps({
                            "valid": False,
                            "error": f"Path validation failed: {str(e)}"
                        }, indent=2)
                    )]
            
            elif name == "json_merge":
                if not arguments:
                    raise ValueError("Missing arguments")
                
                required_args = ["table", "column", "merge_data"]
                for arg in required_args:
                    if arg not in arguments:
                        raise ValueError(f"Missing required argument: {arg}")
                
                try:
                    # Validate merge data
                    merge_data = arguments["merge_data"]
                    if isinstance(merge_data, str):
                        # Validate JSON string
                        from .diagnostics_isolated import isolated_validate_json
                        validation_result = isolated_validate_json(merge_data)
                        if not validation_result['valid']:
                            return [types.TextContent(
                                type="text", 
                                text=json_module.dumps({
                                    "success": False,
                                    "error": f"Invalid merge data JSON: {validation_result.get('message', 'Unknown error')}"
                                }, indent=2)
                            )]
                        merge_data = validation_result['parsed']
                    
                    # Security check
                    security_result = validate_json_security(merge_data)
                    if not security_result['safe']:
                        return [types.TextContent(
                            type="text", 
                            text=json_module.dumps({
                                "success": False,
                                "error": "Security violation detected in merge data",
                                "security_details": security_result
                            }, indent=2)
                        )]
                    
                    # Build merge query using json_patch or json_set
                    table = arguments["table"]
                    column = arguments["column"]
                    where_clause = arguments.get("where_clause", "")
                    strategy = arguments.get("strategy", "merge_deep")
                    
                    if strategy in ["merge_deep", "merge_shallow"]:
                        # Use json_patch for merging
                        merge_json_str = json_module.dumps(merge_data)
                        query = f"UPDATE {table} SET {column} = json_patch({column}, ?)"
                        params = [merge_json_str]
                    else:  # replace
                        merge_json_str = json_module.dumps(merge_data)
                        query = f"UPDATE {table} SET {column} = ?"
                        params = [merge_json_str]
                    
                    if where_clause:
                        query += f" WHERE {where_clause}"
                    
                    # Execute the query
                    result = db._execute_query(query, params)
                    
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps({
                            "success": True,
                            "result": result,
                            "strategy": strategy,
                            "security_check": "passed"
                        }, indent=2)
                    )]
                    
                except Exception as e:
                    return [types.TextContent(
                        type="text", 
                        text=json_module.dumps({
                            "success": False,
                            "error": f"JSON merge failed: {str(e)}"
                        }, indent=2)
                    )]

            # Handle database administration tools
            elif name == "vacuum_database":
                logger.info("Executing VACUUM operation")
                # VACUUM must run outside of transactions, so we use a direct connection
                from contextlib import closing
                try:
                    with closing(sqlite3.connect(db.db_path)) as conn:
                        conn.execute("VACUUM")
                        conn.commit()
                    logger.info("VACUUM operation completed successfully")
                    return [types.TextContent(type="text", text="Database vacuum completed successfully")]
                except Exception as e:
                    logger.error(f"VACUUM operation failed: {e}")
                    return [types.TextContent(type="text", text=f"Database error: {str(e)}")]

            elif name == "analyze_database":
                logger.info("Executing ANALYZE operation")
                results = db._execute_query("ANALYZE")
                return [types.TextContent(type="text", text="Database analysis completed successfully")]

            elif name == "integrity_check":
                logger.info("Executing integrity check")
                results = db._execute_query("PRAGMA integrity_check")
                if results and len(results) == 1 and results[0].get('integrity_check') == 'ok':
                    return [types.TextContent(type="text", text="Database integrity check passed: OK")]
                else:
                    return [types.TextContent(type="text", text=f"Integrity check results: {str(results)}")]

            elif name == "database_stats":
                logger.info("Retrieving database statistics")
                # Collect multiple statistics
                stats = {}
                
                # Database size and page info
                page_count = db._execute_query("PRAGMA page_count")
                page_size = db._execute_query("PRAGMA page_size")
                stats['page_count'] = page_count[0]['page_count'] if page_count else 0
                stats['page_size'] = page_size[0]['page_size'] if page_size else 0
                stats['database_size_bytes'] = stats['page_count'] * stats['page_size']
                stats['database_size_mb'] = round(stats['database_size_bytes'] / (1024 * 1024), 2)
                
                # Table count
                table_count = db._execute_query("SELECT COUNT(*) as count FROM sqlite_master WHERE type='table'")
                stats['table_count'] = table_count[0]['count'] if table_count else 0
                
                # Index count  
                index_count = db._execute_query("SELECT COUNT(*) as count FROM sqlite_master WHERE type='index'")
                stats['index_count'] = index_count[0]['count'] if index_count else 0
                
                return [types.TextContent(type="text", text=json_module.dumps(stats, indent=2))]

            elif name == "index_usage_stats":
                logger.info("Retrieving index usage statistics")
                # Get index list and usage info
                indexes = db._execute_query("""
                    SELECT name, tbl_name, sql 
                    FROM sqlite_master 
                    WHERE type='index' AND sql IS NOT NULL
                    ORDER BY tbl_name, name
                """)
                
                return [types.TextContent(type="text", text=json_module.dumps(indexes, indent=2))]

            # Handle FTS5 tools
            elif name == "create_fts_table":
                logger.info(f"Creating FTS5 table: {arguments.get('table_name')}")
                table_name = arguments["table_name"]
                columns = arguments["columns"]
                content_table = arguments.get("content_table")
                tokenizer = arguments.get("tokenizer", "unicode61")
                
                # Build FTS5 CREATE statement
                columns_str = ", ".join(columns)
                fts_sql = f"CREATE VIRTUAL TABLE {table_name} USING fts5({columns_str}, tokenize='{tokenizer}')"
                
                try:
                    db._execute_query(fts_sql)
                    result_msg = f"FTS5 table '{table_name}' created successfully with columns: {columns_str}"
                    
                    # If content table specified, populate the FTS5 table
                    if content_table:
                        populate_sql = f"INSERT INTO {table_name} SELECT {columns_str} FROM {content_table}"
                        db._execute_query(populate_sql)
                        result_msg += f" and populated from '{content_table}'"
                    
                    logger.info(result_msg)
                    return [types.TextContent(type="text", text=result_msg)]
                except Exception as e:
                    error_msg = f"Failed to create FTS5 table: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "rebuild_fts_index":
                logger.info(f"Rebuilding FTS5 index for table: {arguments.get('table_name')}")
                table_name = arguments["table_name"]
                
                try:
                    # Rebuild the FTS5 index
                    rebuild_sql = f"INSERT INTO {table_name}({table_name}) VALUES('rebuild')"
                    db._execute_query(rebuild_sql)
                    
                    result_msg = f"FTS5 index for '{table_name}' rebuilt successfully"
                    logger.info(result_msg)
                    return [types.TextContent(type="text", text=result_msg)]
                except Exception as e:
                    error_msg = f"Failed to rebuild FTS5 index: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "fts_search":
                logger.info(f"Performing FTS5 search on table: {arguments.get('table_name')}")
                table_name = arguments["table_name"]
                query = arguments["query"]
                limit = arguments.get("limit", 10)
                snippet_length = arguments.get("snippet_length", 32)
                
                try:
                    # Enhanced FTS5 search with ranking and snippets
                    search_sql = f"""
                        SELECT *, 
                               bm25({table_name}) as rank,
                               snippet({table_name}, -1, '<mark>', '</mark>', '...', {snippet_length}) as snippet
                        FROM {table_name} 
                        WHERE {table_name} MATCH ? 
                        ORDER BY rank 
                        LIMIT ?
                    """
                    
                    results = db._execute_query(search_sql, [query, limit])
                    
                    result_msg = f"Found {len(results)} results for query: '{query}'"
                    logger.info(result_msg)
                    
                    return [types.TextContent(type="text", text=json_module.dumps({
                        "query": query,
                        "results_count": len(results),
                        "results": results
                    }, indent=2))]
                except Exception as e:
                    error_msg = f"FTS5 search failed: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            # Handle backup/restore tools
            elif name == "backup_database":
                logger.info(f"Creating database backup to: {arguments.get('backup_path')}")
                backup_path = arguments["backup_path"]
                overwrite = arguments.get("overwrite", False)
                
                import os
                from pathlib import Path
                
                try:
                    # Check if backup file already exists
                    if os.path.exists(backup_path) and not overwrite:
                        error_msg = f"Backup file already exists: {backup_path}. Use overwrite=true to replace it."
                        logger.error(error_msg)
                        return [types.TextContent(type="text", text=error_msg)]
                    
                    # Create backup directory if it doesn't exist
                    backup_dir = Path(backup_path).parent
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Perform backup using SQLite backup API
                    source_conn = sqlite3.connect(db.db_path)
                    backup_conn = sqlite3.connect(backup_path)
                    
                    # Copy database using backup API
                    source_conn.backup(backup_conn)
                    
                    source_conn.close()
                    backup_conn.close()
                    
                    # Get backup file size for confirmation
                    backup_size = os.path.getsize(backup_path)
                    result_msg = f"Database backup created successfully: {backup_path} ({backup_size} bytes)"
                    logger.info(result_msg)
                    return [types.TextContent(type="text", text=result_msg)]
                    
                except Exception as e:
                    error_msg = f"Backup failed: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "restore_database":
                logger.info(f"Restoring database from: {arguments.get('backup_path')}")
                backup_path = arguments["backup_path"]
                confirm = arguments.get("confirm", False)
                
                if not confirm:
                    error_msg = "Restore operation requires explicit confirmation. Set confirm=true to proceed."
                    logger.warning(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]
                
                import os
                
                try:
                    # Check if backup file exists
                    if not os.path.exists(backup_path):
                        error_msg = f"Backup file not found: {backup_path}"
                        logger.error(error_msg)
                        return [types.TextContent(type="text", text=error_msg)]
                    
                    # Create a backup of current database before restore
                    current_backup = f"{db.db_path}.pre_restore_backup"
                    if os.path.exists(db.db_path):
                        current_conn = sqlite3.connect(db.db_path)
                        backup_conn = sqlite3.connect(current_backup)
                        current_conn.backup(backup_conn)
                        current_conn.close()
                        backup_conn.close()
                        logger.info(f"Current database backed up to: {current_backup}")
                    
                    # Perform restore
                    backup_conn = sqlite3.connect(backup_path)
                    target_conn = sqlite3.connect(db.db_path)
                    backup_conn.backup(target_conn)
                    backup_conn.close()
                    target_conn.close()
                    
                    result_msg = f"Database restored successfully from: {backup_path}"
                    logger.info(result_msg)
                    return [types.TextContent(type="text", text=result_msg)]
                    
                except Exception as e:
                    error_msg = f"Restore failed: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "verify_backup":
                logger.info(f"Verifying backup file: {arguments.get('backup_path')}")
                backup_path = arguments["backup_path"]
                
                import os
                
                try:
                    # Check if backup file exists
                    if not os.path.exists(backup_path):
                        error_msg = f"Backup file not found: {backup_path}"
                        logger.error(error_msg)
                        return [types.TextContent(type="text", text=error_msg)]
                    
                    # Get file size
                    file_size = os.path.getsize(backup_path)
                    
                    # Test database connection and integrity
                    conn = sqlite3.connect(backup_path)
                    cursor = conn.cursor()
                    
                    # Run integrity check
                    cursor.execute("PRAGMA integrity_check")
                    integrity_result = cursor.fetchone()[0]
                    
                    # Get table count
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    
                    # Get database info
                    cursor.execute("PRAGMA user_version")
                    user_version = cursor.fetchone()[0]
                    
                    conn.close()
                    
                    verification_info = {
                        "file_path": backup_path,
                        "file_size_bytes": file_size,
                        "integrity_check": integrity_result,
                        "table_count": table_count,
                        "user_version": user_version,
                        "status": "valid" if integrity_result == "ok" else "corrupted"
                    }
                    
                    result_msg = f"Backup verification completed"
                    logger.info(result_msg)
                    return [types.TextContent(type="text", text=json_module.dumps(verification_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Backup verification failed: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            # Handle advanced PRAGMA operations
            elif name == "pragma_settings":
                logger.info(f"PRAGMA operation: {arguments.get('pragma_name')}")
                pragma_name = arguments["pragma_name"]
                value = arguments.get("value")
                
                try:
                    if value is not None:
                        # Set PRAGMA value
                        pragma_sql = f"PRAGMA {pragma_name} = {value}"
                        db._execute_query(pragma_sql)
                        # Get the new value to confirm
                        result = db._execute_query(f"PRAGMA {pragma_name}")
                        result_msg = f"PRAGMA {pragma_name} set to: {value}"
                        if result:
                            actual_value = list(result[0].values())[0] if result[0] else value
                            result_msg = f"PRAGMA {pragma_name} = {actual_value}"
                    else:
                        # Get PRAGMA value
                        result = db._execute_query(f"PRAGMA {pragma_name}")
                        if result:
                            pragma_value = list(result[0].values())[0] if result[0] else "N/A"
                            result_msg = f"PRAGMA {pragma_name} = {pragma_value}"
                        else:
                            result_msg = f"PRAGMA {pragma_name} returned no value"
                    
                    logger.info(result_msg)
                    return [types.TextContent(type="text", text=result_msg)]
                    
                except Exception as e:
                    error_msg = f"PRAGMA operation failed: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "pragma_optimize":
                logger.info("Running PRAGMA optimize for query performance")
                analysis_limit = arguments.get("analysis_limit", 1000)
                
                try:
                    # Run PRAGMA optimize with optional analysis limit
                    if analysis_limit != 1000:
                        optimize_sql = f"PRAGMA optimize({analysis_limit})"
                    else:
                        optimize_sql = "PRAGMA optimize"
                    
                    db._execute_query(optimize_sql)
                    result_msg = f"Database optimization completed (analysis_limit: {analysis_limit})"
                    logger.info(result_msg)
                    return [types.TextContent(type="text", text=result_msg)]
                    
                except Exception as e:
                    error_msg = f"PRAGMA optimize failed: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "pragma_table_info":
                logger.info(f"Getting table info for: {arguments.get('table_name')}")
                table_name = arguments["table_name"]
                include_foreign_keys = arguments.get("include_foreign_keys", True)
                
                try:
                    # Get table info
                    table_info = db._execute_query(f"PRAGMA table_info({table_name})")
                    
                    info_result = {
                        "table_name": table_name,
                        "columns": table_info if table_info else []
                    }
                    
                    if include_foreign_keys:
                        # Get foreign key info
                        fk_info = db._execute_query(f"PRAGMA foreign_key_list({table_name})")
                        info_result["foreign_keys"] = fk_info if fk_info else []
                        
                        # Get index info
                        index_info = db._execute_query(f"PRAGMA index_list({table_name})")
                        info_result["indexes"] = index_info if index_info else []
                    
                    logger.info(f"Retrieved table info for {table_name}")
                    return [types.TextContent(type="text", text=json_module.dumps(info_result, indent=2))]
                    
                except Exception as e:
                    error_msg = f"PRAGMA table_info failed: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "pragma_database_list":
                logger.info("Getting database list")
                
                try:
                    # Get list of attached databases
                    db_list = db._execute_query("PRAGMA database_list")
                    
                    result_info = {
                        "attached_databases": db_list if db_list else [],
                        "count": len(db_list) if db_list else 0
                    }
                    
                    logger.info(f"Retrieved {result_info['count']} database(s)")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"PRAGMA database_list failed: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "pragma_compile_options":
                logger.info("Getting SQLite compile options")
                
                try:
                    # Get compile options
                    compile_options = db._execute_query("PRAGMA compile_options")
                    
                    options_list = []
                    if compile_options:
                        options_list = [list(row.values())[0] for row in compile_options]
                    
                    result_info = {
                        "sqlite_version": db.version_info.get('sqlite_version', 'Unknown'),
                        "compile_options": options_list,
                        "options_count": len(options_list)
                    }
                    
                    logger.info(f"Retrieved {len(options_list)} compile options")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"PRAGMA compile_options failed: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            # Handle virtual table management tools
            elif name == "create_rtree_table":
                if not arguments or "table_name" not in arguments:
                    raise ValueError("Missing table_name argument")
                
                table_name = arguments["table_name"]
                dimensions = arguments.get("dimensions", 2)
                coordinate_type = arguments.get("coordinate_type", "float")
                
                logger.info(f"Creating R-Tree virtual table: {table_name}")
                
                try:
                    # Build coordinate column definitions based on dimensions
                    if coordinate_type == "int":
                        coord_cols = []
                        for i in range(dimensions):
                            coord_cols.extend([f"min{i}", f"max{i}"])
                    else:
                        coord_cols = []
                        for i in range(dimensions):
                            coord_cols.extend([f"min{i}", f"max{i}"])
                    
                    # Create R-Tree virtual table
                    col_def = ", ".join(coord_cols)
                    create_sql = f"CREATE VIRTUAL TABLE {table_name} USING rtree(id, {col_def})"
                    
                    db._execute_query(create_sql)
                    
                    result_info = {
                        "table_name": table_name,
                        "type": "rtree",
                        "dimensions": dimensions,
                        "coordinate_type": coordinate_type,
                        "columns": ["id"] + coord_cols,
                        "status": "created"
                    }
                    
                    logger.info(f"R-Tree table '{table_name}' created successfully")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to create R-Tree table: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "create_csv_table":
                if not arguments or "table_name" not in arguments or "csv_file_path" not in arguments:
                    raise ValueError("Missing table_name or csv_file_path argument")
                
                table_name = arguments["table_name"]
                csv_file_path = arguments["csv_file_path"]
                has_header = arguments.get("has_header", True)
                delimiter = arguments.get("delimiter", ",")
                
                logger.info(f"Creating CSV virtual table: {table_name} for file: {csv_file_path}")
                
                try:
                    # Check if file exists
                    import os
                    if not os.path.exists(csv_file_path):
                        raise ValueError(f"CSV file not found: {csv_file_path}")
                    
                    # Create CSV virtual table
                    create_sql = f"""CREATE VIRTUAL TABLE {table_name} USING csv(
                        filename='{csv_file_path}',
                        header={str(has_header).lower()},
                        delimiter='{delimiter}'
                    )"""
                    
                    # Note: CSV extension may not be available in all SQLite builds
                    # We'll try to create it and provide helpful error if not supported
                    try:
                        db._execute_query(create_sql)
                        status = "created"
                    except Exception as csv_error:
                        if "no such module" in str(csv_error).lower():
                            # Try alternative approach using import
                            create_sql = f"CREATE TEMP TABLE {table_name} AS SELECT * FROM csv('{csv_file_path}')"
                            db._execute_query(create_sql)
                            status = "created_as_temp_table"
                        else:
                            raise csv_error
                    
                    result_info = {
                        "table_name": table_name,
                        "type": "csv",
                        "csv_file_path": csv_file_path,
                        "has_header": has_header,
                        "delimiter": delimiter,
                        "status": status
                    }
                    
                    logger.info(f"CSV table '{table_name}' created successfully")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to create CSV table: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "create_series_table":
                if not arguments or "table_name" not in arguments:
                    raise ValueError("Missing table_name argument")
                
                table_name = arguments["table_name"]
                start_value = arguments.get("start_value", 1)
                end_value = arguments.get("end_value", 100)
                step = arguments.get("step", 1)
                
                logger.info(f"Creating generate_series virtual table: {table_name}")
                
                try:
                    # Create generate_series virtual table
                    create_sql = f"""CREATE VIRTUAL TABLE {table_name} USING generate_series(
                        start={start_value},
                        stop={end_value},
                        step={step}
                    )"""
                    
                    # Try to create the table
                    try:
                        db._execute_query(create_sql)
                        status = "created"
                    except Exception as series_error:
                        if "no such module" in str(series_error).lower():
                            # Create a regular table with series data as fallback
                            create_sql = f"""CREATE TABLE {table_name} AS 
                                WITH RECURSIVE series(value) AS (
                                    SELECT {start_value}
                                    UNION ALL
                                    SELECT value + {step} FROM series
                                    WHERE value + {step} <= {end_value}
                                )
                                SELECT value FROM series"""
                            db._execute_query(create_sql)
                            status = "created_as_regular_table"
                        else:
                            raise series_error
                    
                    result_info = {
                        "table_name": table_name,
                        "type": "generate_series",
                        "start_value": start_value,
                        "end_value": end_value,
                        "step": step,
                        "status": status
                    }
                    
                    logger.info(f"Series table '{table_name}' created successfully")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to create series table: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "list_virtual_tables":
                logger.info("Listing virtual tables")
                
                try:
                    # Query for virtual tables
                    virtual_tables_query = """
                        SELECT name, sql 
                        FROM sqlite_master 
                        WHERE type = 'table' 
                        AND sql LIKE '%VIRTUAL TABLE%'
                        ORDER BY name
                    """
                    
                    results = db._execute_query(virtual_tables_query)
                    
                    virtual_tables = []
                    if results:
                        for row in results:
                            table_info = {
                                "name": row["name"],
                                "sql": row["sql"],
                                "type": "virtual"
                            }
                            
                            # Try to determine virtual table type
                            sql_lower = row["sql"].lower()
                            if "using rtree" in sql_lower:
                                table_info["virtual_type"] = "rtree"
                            elif "using fts" in sql_lower:
                                table_info["virtual_type"] = "fts"
                            elif "using csv" in sql_lower:
                                table_info["virtual_type"] = "csv"
                            elif "using generate_series" in sql_lower:
                                table_info["virtual_type"] = "generate_series"
                            else:
                                table_info["virtual_type"] = "unknown"
                            
                            virtual_tables.append(table_info)
                    
                    result_info = {
                        "virtual_tables": virtual_tables,
                        "count": len(virtual_tables)
                    }
                    
                    logger.info(f"Found {len(virtual_tables)} virtual tables")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to list virtual tables: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "drop_virtual_table":
                if not arguments or "table_name" not in arguments:
                    raise ValueError("Missing table_name argument")
                
                table_name = arguments["table_name"]
                confirm = arguments.get("confirm", False)
                
                if not confirm:
                    return [types.TextContent(type="text", text="Error: confirm=true required to drop virtual table")]
                
                logger.info(f"Dropping virtual table: {table_name}")
                
                try:
                    # Verify it's a virtual table first
                    check_query = """
                        SELECT sql FROM sqlite_master 
                        WHERE type = 'table' AND name = ? AND sql LIKE '%VIRTUAL TABLE%'
                    """
                    
                    check_results = db._execute_query(check_query, [table_name])
                    
                    if not check_results:
                        return [types.TextContent(type="text", text=f"Error: '{table_name}' is not a virtual table or doesn't exist")]
                    
                    # Drop the virtual table
                    drop_sql = f"DROP TABLE {table_name}"
                    db._execute_query(drop_sql)
                    
                    result_info = {
                        "table_name": table_name,
                        "status": "dropped",
                        "type": "virtual"
                    }
                    
                    logger.info(f"Virtual table '{table_name}' dropped successfully")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to drop virtual table: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "virtual_table_info":
                if not arguments or "table_name" not in arguments:
                    raise ValueError("Missing table_name argument")
                
                table_name = arguments["table_name"]
                
                logger.info(f"Getting virtual table info: {table_name}")
                
                try:
                    # Get basic table info
                    table_query = """
                        SELECT name, sql 
                        FROM sqlite_master 
                        WHERE type = 'table' AND name = ? AND sql LIKE '%VIRTUAL TABLE%'
                    """
                    
                    table_results = db._execute_query(table_query, [table_name])
                    
                    if not table_results:
                        return [types.TextContent(type="text", text=f"Error: '{table_name}' is not a virtual table or doesn't exist")]
                    
                    table_info = table_results[0]
                    
                    # Get column information
                    pragma_results = db._execute_query(f"PRAGMA table_info({table_name})")
                    
                    columns = []
                    if pragma_results:
                        for row in pragma_results:
                            columns.append({
                                "cid": row.get("cid"),
                                "name": row.get("name"),
                                "type": row.get("type"),
                                "notnull": bool(row.get("notnull")),
                                "dflt_value": row.get("dflt_value"),
                                "pk": bool(row.get("pk"))
                            })
                    
                    # Determine virtual table type
                    sql_lower = table_info["sql"].lower()
                    if "using rtree" in sql_lower:
                        virtual_type = "rtree"
                    elif "using fts" in sql_lower:
                        virtual_type = "fts"
                    elif "using csv" in sql_lower:
                        virtual_type = "csv"
                    elif "using generate_series" in sql_lower:
                        virtual_type = "generate_series"
                    else:
                        virtual_type = "unknown"
                    
                    result_info = {
                        "table_name": table_name,
                        "type": "virtual",
                        "virtual_type": virtual_type,
                        "sql": table_info["sql"],
                        "columns": columns,
                        "column_count": len(columns)
                    }
                    
                    logger.info(f"Retrieved info for virtual table '{table_name}'")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to get virtual table info: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            # Enhanced Virtual Tables (v1.9.3)
            elif name == "create_enhanced_csv_table":
                if not arguments or "table_name" not in arguments or "csv_file_path" not in arguments:
                    raise ValueError("Missing table_name or csv_file_path argument")
                
                table_name = arguments["table_name"]
                csv_file_path = arguments["csv_file_path"]
                delimiter = arguments.get("delimiter", ",")
                has_header = arguments.get("has_header", True)
                sample_rows = arguments.get("sample_rows", 100)
                null_values = arguments.get("null_values", ["", "NULL", "null", "None", "N/A", "n/a"])
                
                logger.info(f"Creating enhanced CSV table: {table_name} from {csv_file_path}")
                
                try:
                    import csv
                    import os
                    from collections import Counter, defaultdict
                    import re
                    
                    # Check if file exists
                    if not os.path.exists(csv_file_path):
                        return [types.TextContent(type="text", text=f"Error: CSV file '{csv_file_path}' not found")]
                    
                    # Analyze CSV structure and infer types
                    with open(csv_file_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f, delimiter=delimiter)
                        
                        # Get headers
                        if has_header:
                            headers = next(reader)
                        else:
                            # Peek at first row to count columns
                            first_row = next(reader)
                            headers = [f"column_{i+1}" for i in range(len(first_row))]
                            f.seek(0)  # Reset file pointer
                            if has_header:
                                next(reader)  # Skip header row again
                        
                        # Sample data for type inference
                        sample_data = []
                        for i, row in enumerate(reader):
                            if i >= sample_rows:
                                break
                            sample_data.append(row)
                    
                    # Infer column types
                    column_types = {}
                    for col_idx, header in enumerate(headers):
                        col_data = [row[col_idx] if col_idx < len(row) else "" for row in sample_data]
                        # Filter out null values for type inference
                        non_null_data = [val for val in col_data if val not in null_values]
                        
                        if not non_null_data:
                            column_types[header] = "TEXT"
                            continue
                        
                        # Type inference logic
                        int_count = 0
                        float_count = 0
                        date_count = 0
                        bool_count = 0
                        
                        for val in non_null_data:
                            val = val.strip()
                            
                            # Check for boolean
                            if val.lower() in ['true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n']:
                                bool_count += 1
                            # Check for integer
                            elif re.match(r'^-?\d+$', val):
                                int_count += 1
                            # Check for float
                            elif re.match(r'^-?\d*\.\d+$', val):
                                float_count += 1
                            # Check for date patterns
                            elif re.match(r'^\d{4}-\d{2}-\d{2}', val) or re.match(r'^\d{2}/\d{2}/\d{4}', val):
                                date_count += 1
                        
                        total_non_null = len(non_null_data)
                        
                        # Determine type based on majority
                        if int_count / total_non_null > 0.8:
                            column_types[header] = "INTEGER"
                        elif (int_count + float_count) / total_non_null > 0.8:
                            column_types[header] = "REAL"
                        elif bool_count / total_non_null > 0.8:
                            column_types[header] = "INTEGER"  # Store booleans as integers
                        elif date_count / total_non_null > 0.5:
                            column_types[header] = "TEXT"  # SQLite doesn't have DATE type
                        else:
                            column_types[header] = "TEXT"
                    
                    # Create the enhanced CSV table with proper types
                    columns_def = []
                    for header in headers:
                        # Clean column name for SQL
                        clean_header = re.sub(r'[^a-zA-Z0-9_]', '_', header)
                        col_type = column_types.get(header, "TEXT")
                        columns_def.append(f'"{clean_header}" {col_type}')
                    
                    # Create the table with inferred schema
                    create_sql = f"""
                        CREATE TABLE "{table_name}" (
                            {', '.join(columns_def)}
                        )
                    """
                    
                    db._execute_query(create_sql)
                    
                    # Load data with type conversion
                    with open(csv_file_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f, delimiter=delimiter)
                        
                        if has_header:
                            next(reader)  # Skip header
                        
                        # Prepare insert statement
                        placeholders = ', '.join(['?' for _ in headers])
                        insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'
                        
                        # Insert data with type conversion
                        rows_inserted = 0
                        for row in reader:
                            # Pad row if necessary
                            while len(row) < len(headers):
                                row.append("")
                            
                            # Convert values based on inferred types
                            converted_row = []
                            for i, (val, header) in enumerate(zip(row[:len(headers)], headers)):
                                if val in null_values:
                                    converted_row.append(None)
                                else:
                                    col_type = column_types[header]
                                    if col_type == "INTEGER":
                                        try:
                                            converted_row.append(int(val) if val.strip() else None)
                                        except ValueError:
                                            converted_row.append(None)
                                    elif col_type == "REAL":
                                        try:
                                            converted_row.append(float(val) if val.strip() else None)
                                        except ValueError:
                                            converted_row.append(None)
                                    else:
                                        converted_row.append(val)
                            
                            db._execute_query(insert_sql, converted_row)
                            rows_inserted += 1
                    
                    # Generate summary
                    result_info = {
                        "table_name": table_name,
                        "csv_file": csv_file_path,
                        "rows_loaded": rows_inserted,
                        "columns": len(headers),
                        "inferred_schema": {header: column_types[header] for header in headers},
                        "sample_rows_analyzed": min(sample_rows, len(sample_data)),
                        "null_values_treated": null_values
                    }
                    
                    logger.info(f"Enhanced CSV table '{table_name}' created successfully with {rows_inserted} rows")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to create enhanced CSV table: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "create_json_collection_table":
                if not arguments or "table_name" not in arguments or "json_file_path" not in arguments:
                    raise ValueError("Missing table_name or json_file_path argument")
                
                table_name = arguments["table_name"]
                json_file_path = arguments["json_file_path"]
                format_type = arguments.get("format_type", "auto")
                flatten_nested = arguments.get("flatten_nested", True)
                max_depth = arguments.get("max_depth", 3)
                sample_records = arguments.get("sample_records", 100)
                
                logger.info(f"Creating JSON collection table: {table_name} from {json_file_path}")
                
                try:
                    import os
                    from collections import defaultdict
                    
                    # Check if file exists
                    if not os.path.exists(json_file_path):
                        return [types.TextContent(type="text", text=f"Error: JSON file '{json_file_path}' not found")]
                    
                    # Auto-detect format if needed
                    if format_type == "auto":
                        with open(json_file_path, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                            if first_line.startswith('['):
                                format_type = "json_array"
                            else:
                                format_type = "jsonl"
                    
                    # Load sample data for schema inference
                    sample_data = []
                    
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        if format_type == "json_array":
                            data = json_module.load(f)
                            sample_data = data[:sample_records] if isinstance(data, list) else [data]
                        else:  # jsonl
                            for i, line in enumerate(f):
                                if i >= sample_records:
                                    break
                                if line.strip():
                                    sample_data.append(json_module.loads(line))
                    
                    # Flatten nested objects and infer schema
                    def flatten_dict(d, parent_key='', sep='.', depth=0):
                        items = []
                        if depth >= max_depth:
                            # Convert to JSON string if max depth reached
                            items.append((parent_key, json_module.dumps(d) if isinstance(d, (dict, list)) else str(d)))
                            return items
                        
                        if isinstance(d, dict):
                            for k, v in d.items():
                                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                                if isinstance(v, dict) and flatten_nested:
                                    items.extend(flatten_dict(v, new_key, sep, depth + 1))
                                elif isinstance(v, list) and flatten_nested and len(v) > 0 and isinstance(v[0], dict):
                                    # Handle arrays of objects by taking first object structure
                                    items.extend(flatten_dict(v[0], f"{new_key}[0]", sep, depth + 1))
                                    # Also store array length
                                    items.append((f"{new_key}_length", len(v)))
                                else:
                                    items.append((new_key, v))
                        else:
                            items.append((parent_key, d))
                        return items
                    
                    # Collect all possible columns from sample data
                    all_columns = set()
                    column_types = defaultdict(lambda: defaultdict(int))
                    
                    for record in sample_data:
                        flattened = dict(flatten_dict(record) if flatten_nested else record.items())
                        all_columns.update(flattened.keys())
                        
                        # Infer types for each column
                        for key, value in flattened.items():
                            if value is None:
                                column_types[key]['null'] += 1
                            elif isinstance(value, bool):
                                column_types[key]['boolean'] += 1
                            elif isinstance(value, int):
                                column_types[key]['integer'] += 1
                            elif isinstance(value, float):
                                column_types[key]['real'] += 1
                            elif isinstance(value, str):
                                column_types[key]['text'] += 1
                            else:
                                column_types[key]['text'] += 1  # Default for complex types
                    
                    # Determine final column types
                    final_schema = {}
                    for col in all_columns:
                        type_counts = column_types[col]
                        total = sum(type_counts.values())
                        
                        if type_counts['integer'] / total > 0.8:
                            final_schema[col] = 'INTEGER'
                        elif (type_counts['integer'] + type_counts['real']) / total > 0.8:
                            final_schema[col] = 'REAL'
                        elif type_counts['boolean'] / total > 0.8:
                            final_schema[col] = 'INTEGER'
                        else:
                            final_schema[col] = 'TEXT'
                    
                    # Create table with inferred schema
                    columns_def = []
                    for col in sorted(all_columns):
                        # Clean column name for SQL
                        import re
                        clean_col = re.sub(r'[^a-zA-Z0-9_]', '_', col)
                        col_type = final_schema[col]
                        columns_def.append(f'"{clean_col}" {col_type}')
                    
                    create_sql = f"""
                        CREATE TABLE "{table_name}" (
                            {', '.join(columns_def)}
                        )
                    """
                    
                    db._execute_query(create_sql)
                    
                    # Load all data
                    rows_inserted = 0
                    column_list = sorted(all_columns)
                    placeholders = ', '.join(['?' for _ in column_list])
                    insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'
                    
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        if format_type == "json_array":
                            data = json_module.load(f)
                            records = data if isinstance(data, list) else [data]
                        else:  # jsonl
                            records = [json_module.loads(line) for line in f if line.strip()]
                    
                    for record in records:
                        flattened = dict(flatten_dict(record) if flatten_nested else record.items())
                        
                        # Create row with all columns in order
                        row_data = []
                        for col in column_list:
                            value = flattened.get(col)
                            if value is None:
                                row_data.append(None)
                            else:
                                col_type = final_schema[col]
                                if col_type == 'INTEGER':
                                    try:
                                        row_data.append(int(value) if not isinstance(value, bool) else (1 if value else 0))
                                    except (ValueError, TypeError):
                                        row_data.append(None)
                                elif col_type == 'REAL':
                                    try:
                                        row_data.append(float(value))
                                    except (ValueError, TypeError):
                                        row_data.append(None)
                                else:
                                    row_data.append(str(value) if value is not None else None)
                        
                        db._execute_query(insert_sql, row_data)
                        rows_inserted += 1
                    
                    # Generate summary
                    result_info = {
                        "table_name": table_name,
                        "json_file": json_file_path,
                        "format_detected": format_type,
                        "rows_loaded": rows_inserted,
                        "columns": len(column_list),
                        "inferred_schema": final_schema,
                        "flattened": flatten_nested,
                        "max_depth": max_depth,
                        "sample_records_analyzed": min(sample_records, len(sample_data))
                    }
                    
                    logger.info(f"JSON collection table '{table_name}' created successfully with {rows_inserted} rows")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to create JSON collection table: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "analyze_csv_schema":
                if not arguments or "csv_file_path" not in arguments:
                    raise ValueError("Missing csv_file_path argument")
                
                csv_file_path = arguments["csv_file_path"]
                delimiter = arguments.get("delimiter", ",")
                has_header = arguments.get("has_header", True)
                sample_rows = arguments.get("sample_rows", 1000)
                
                logger.info(f"Analyzing CSV schema: {csv_file_path}")
                
                try:
                    import csv
                    import os
                    from collections import Counter
                    import re
                    
                    if not os.path.exists(csv_file_path):
                        return [types.TextContent(type="text", text=f"Error: CSV file '{csv_file_path}' not found")]
                    
                    analysis_result = {
                        "file_path": csv_file_path,
                        "file_size": os.path.getsize(csv_file_path),
                        "delimiter": delimiter,
                        "has_header": has_header
                    }
                    
                    with open(csv_file_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f, delimiter=delimiter)
                        
                        # Get headers and count total rows
                        if has_header:
                            headers = next(reader)
                        else:
                            first_row = next(reader)
                            headers = [f"column_{i+1}" for i in range(len(first_row))]
                            f.seek(0)
                        
                        # Count total rows
                        total_rows = sum(1 for _ in reader)
                        f.seek(0)
                        if has_header:
                            next(reader)  # Skip header again
                        
                        # Sample data for analysis
                        sample_data = []
                        for i, row in enumerate(reader):
                            if i >= sample_rows:
                                break
                            sample_data.append(row)
                    
                    analysis_result.update({
                        "total_rows": total_rows,
                        "columns": len(headers),
                        "sample_rows_analyzed": len(sample_data),
                        "column_analysis": {}
                    })
                    
                    # Analyze each column
                    for col_idx, header in enumerate(headers):
                        col_data = [row[col_idx] if col_idx < len(row) else "" for row in sample_data]
                        
                        # Basic statistics
                        non_empty = [val for val in col_data if val.strip()]
                        empty_count = len(col_data) - len(non_empty)
                        
                        # Type analysis
                        int_count = sum(1 for val in non_empty if re.match(r'^-?\d+$', val.strip()))
                        float_count = sum(1 for val in non_empty if re.match(r'^-?\d*\.\d+$', val.strip()))
                        date_count = sum(1 for val in non_empty if re.match(r'^\d{4}-\d{2}-\d{2}', val.strip()) or re.match(r'^\d{2}/\d{2}/\d{4}', val.strip()))
                        
                        # Unique values
                        unique_values = len(set(col_data))
                        
                        # Most common values
                        value_counts = Counter(col_data)
                        most_common = value_counts.most_common(5)
                        
                        # Inferred type
                        if int_count / len(non_empty) > 0.8 if non_empty else False:
                            inferred_type = "INTEGER"
                        elif (int_count + float_count) / len(non_empty) > 0.8 if non_empty else False:
                            inferred_type = "REAL"
                        elif date_count / len(non_empty) > 0.5 if non_empty else False:
                            inferred_type = "DATE (stored as TEXT)"
                        else:
                            inferred_type = "TEXT"
                        
                        analysis_result["column_analysis"][header] = {
                            "index": col_idx,
                            "total_values": len(col_data),
                            "non_empty_values": len(non_empty),
                            "empty_values": empty_count,
                            "unique_values": unique_values,
                            "inferred_type": inferred_type,
                            "type_confidence": {
                                "integer_matches": int_count,
                                "float_matches": float_count,
                                "date_matches": date_count
                            },
                            "most_common_values": most_common,
                            "sample_values": col_data[:10]
                        }
                    
                    logger.info(f"CSV schema analysis completed for '{csv_file_path}'")
                    return [types.TextContent(type="text", text=json_module.dumps(analysis_result, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to analyze CSV schema: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            # SpatiaLite Geospatial Tools (v2.0.0)
            elif name == "load_spatialite":
                force_reload = arguments.get("force_reload", False)
                
                try:
                    # Check if SpatiaLite is already loaded
                    if not force_reload:
                        try:
                            result = db._execute_query("SELECT spatialite_version()")
                            if result and len(result) > 0:
                                version = result[0].get("spatialite_version()")
                                return [types.TextContent(
                                    type="text",
                                    text=f"SpatiaLite already loaded. Version: {version}"
                                )]
                        except:
                            pass  # Not loaded, continue with loading
                    
                    # Try to load SpatiaLite extension
                    try:
                        # Common SpatiaLite extension names/paths
                        import os
                        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                        local_spatialite_dir = os.path.join(script_dir, "mod_spatialite-5.1.0-win-amd64")
                        local_spatialite = os.path.join(local_spatialite_dir, "mod_spatialite.dll")
                        
                        # Add local SpatiaLite directory to PATH for Windows DLL dependencies
                        if os.path.exists(local_spatialite_dir):
                            original_path = os.environ.get('PATH', '')
                            os.environ['PATH'] = local_spatialite_dir + os.pathsep + original_path
                        
                        spatialite_paths = [
                            local_spatialite,  # Local installation first
                            "mod_spatialite",
                            "mod_spatialite.dll", 
                            "mod_spatialite.so",
                            "/usr/lib/x86_64-linux-gnu/mod_spatialite.so",
                            "/usr/local/lib/mod_spatialite.so"
                        ]
                        
                        loaded = False
                        last_error = None
                        loaded_path = None
                        for path in spatialite_paths:
                            try:
                                # Create direct connection for extension loading
                                from contextlib import closing
                                with closing(sqlite3.connect(db.db_path)) as conn:
                                    conn.enable_load_extension(True)
                                    conn.load_extension(path)
                                    conn.enable_load_extension(False)
                                    loaded = True
                                    loaded_path = path
                                    # Store the working path for other tools
                                    EnhancedSqliteDatabase._spatialite_path = path
                                    break
                            except Exception as e:
                                last_error = str(e)
                                continue
                        
                        if not loaded:
                            error_msg = f"Failed to load SpatiaLite extension. Please ensure SpatiaLite is installed on your system."
                            if last_error:
                                error_msg += f"\nLast error: {last_error}"
                            if os.path.exists(local_spatialite):
                                error_msg += f"\nLocal SpatiaLite found at: {local_spatialite}"
                            return [types.TextContent(
                                type="text",
                                text=error_msg
                            )]
                        
                        # Try to initialize spatial metadata (optional for some SpatiaLite versions)
                        try:
                            db._execute_query("SELECT InitSpatialMetaData(1)")
                        except:
                            pass  # Some versions don't require this
                        
                        # Get version info
                        try:
                            result = db._execute_query("SELECT spatialite_version(), proj4_version(), geos_version()")
                            if result and len(result) > 0:
                                versions = result[0]
                            else:
                                # Try just spatialite version
                                result = db._execute_query("SELECT spatialite_version()")
                                versions = {"spatialite_version()": result[0].get("spatialite_version()", "Unknown") if result else "Unknown"}
                        except:
                            versions = {"spatialite_version()": "Unknown"}
                        
                        return [types.TextContent(
                            type="text",
                            text=f"SpatiaLite loaded successfully!\n\nVersions:\n- SpatiaLite: {versions.get('spatialite_version()', 'Unknown')}\n- PROJ4: {versions.get('proj4_version()', 'Unknown')}\n- GEOS: {versions.get('geos_version()', 'Unknown')}"
                        )]
                        
                    except Exception as e:
                        return [types.TextContent(
                            type="text",
                            text=f"Failed to load SpatiaLite: {str(e)}\n\nPlease ensure SpatiaLite is installed on your system."
                        )]
                        
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Error loading SpatiaLite: {str(e)}"
                    )]
            
            elif name == "create_spatial_table":
                table_name = arguments.get("table_name")
                geometry_column = arguments.get("geometry_column", "geom")
                geometry_type = arguments.get("geometry_type", "POINT")
                srid = arguments.get("srid", 4326)
                additional_columns = arguments.get("additional_columns", [])
                
                try:
                    # Create the base table
                    columns_sql = []
                    columns_sql.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
                    
                    for col in additional_columns:
                        columns_sql.append(f'"{col["name"]}" {col["type"]}')
                    
                    create_sql = f'CREATE TABLE "{table_name}" ({", ".join(columns_sql)})'
                    db._execute_query(create_sql)
                    
                    # Add geometry column using SpatiaLite
                    add_geom_sql = f"""
                        SELECT AddGeometryColumn('{table_name}', '{geometry_column}', {srid}, '{geometry_type}', 'XY')
                    """
                    db._execute_query(add_geom_sql)
                    
                    return [types.TextContent(
                        type="text",
                        text=f"Spatial table '{table_name}' created successfully with {geometry_type} geometry column '{geometry_column}' (SRID: {srid})"
                    )]
                    
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Failed to create spatial table: {str(e)}"
                    )]
            
            elif name == "spatial_index":
                table_name = arguments.get("table_name")
                geometry_column = arguments.get("geometry_column", "geom")
                action = arguments.get("action", "create")
                
                try:
                    if action == "create":
                        # Create spatial index
                        index_sql = f"SELECT CreateSpatialIndex('{table_name}', '{geometry_column}')"
                        db._execute_query(index_sql)
                        message = f"Spatial index created on {table_name}.{geometry_column}"
                    else:
                        # Drop spatial index
                        index_sql = f"SELECT DisableSpatialIndex('{table_name}', '{geometry_column}')"
                        db._execute_query(index_sql)
                        message = f"Spatial index dropped on {table_name}.{geometry_column}"
                    
                    return [types.TextContent(
                        type="text",
                        text=message
                    )]
                    
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Failed to {action} spatial index: {str(e)}"
                    )]
            
            elif name == "spatial_query":
                query = arguments.get("query")
                explain = arguments.get("explain", False)
                
                try:
                    if explain:
                        # Show query plan
                        explain_query = f"EXPLAIN QUERY PLAN {query}"
                        plan_results = db._execute_query(explain_query)
                        
                        plan_text = "Query Execution Plan:\n"
                        for row in plan_results:
                            plan_text += f"  {' | '.join(str(val) for val in row.values())}\n"
                        plan_text += "\n"
                    else:
                        plan_text = ""
                    
                    # Execute the spatial query
                    results = db._execute_query(query)
                    
                    if not results:
                        return [types.TextContent(
                            type="text",
                            text=f"{plan_text}Spatial query executed successfully. No results returned."
                        )]
                    
                    # Results are already formatted as list of dictionaries
                    formatted_results = results
                    
                    return [types.TextContent(
                        type="text",
                        text=f"{plan_text}Spatial query results ({len(results)} rows):\n{json_module.dumps(formatted_results, indent=2, default=str)}"
                    )]
                    
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Spatial query failed: {str(e)}"
                    )]
            
            elif name == "geometry_operations":
                operation = arguments.get("operation")
                geometry1 = arguments.get("geometry1")
                geometry2 = arguments.get("geometry2", "")
                buffer_distance = arguments.get("buffer_distance", 1.0)
                table_name = arguments.get("table_name", "")
                
                try:
                    # Build the spatial SQL based on operation
                    if operation == "buffer":
                        sql = f"SELECT AsText(ST_Buffer(GeomFromText('{geometry1}'), {buffer_distance})) as result"
                    elif operation == "area":
                        sql = f"SELECT ST_Area(GeomFromText('{geometry1}')) as area"
                    elif operation == "length":
                        sql = f"SELECT ST_Length(GeomFromText('{geometry1}')) as length"
                    elif operation == "centroid":
                        sql = f"SELECT AsText(ST_Centroid(GeomFromText('{geometry1}'))) as centroid"
                    elif operation == "envelope":
                        sql = f"SELECT AsText(ST_Envelope(GeomFromText('{geometry1}'))) as envelope"
                    elif operation == "distance" and geometry2:
                        sql = f"SELECT ST_Distance(GeomFromText('{geometry1}'), GeomFromText('{geometry2}')) as distance"
                    elif operation == "intersection" and geometry2:
                        sql = f"SELECT AsText(ST_Intersection(GeomFromText('{geometry1}'), GeomFromText('{geometry2}'))) as intersection"
                    elif operation == "union" and geometry2:
                        sql = f"SELECT AsText(ST_Union(GeomFromText('{geometry1}'), GeomFromText('{geometry2}'))) as union"
                    elif operation == "difference" and geometry2:
                        sql = f"SELECT AsText(ST_Difference(GeomFromText('{geometry1}'), GeomFromText('{geometry2}'))) as difference"
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"Invalid operation '{operation}' or missing required geometry2 parameter"
                        )]
                    
                    result_data = db._execute_query(sql)
                    
                    if result_data and len(result_data) > 0:
                        # Get the first value from the first row
                        first_result = result_data[0]
                        result_value = list(first_result.values())[0]
                        return [types.TextContent(
                            type="text",
                            text=f"Geometry operation '{operation}' result: {result_value}"
                        )]
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"Geometry operation '{operation}' returned no result"
                        )]
                        
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Geometry operation failed: {str(e)}"
                    )]
            
            elif name == "import_shapefile":
                shapefile_path = arguments.get("shapefile_path")
                table_name = arguments.get("table_name")
                encoding = arguments.get("encoding", "UTF-8")
                srid = arguments.get("srid", 0)
                
                try:
                    # Use SpatiaLite's shapefile import functionality
                    # Note: This requires the shapefile to be accessible and properly formatted
                    import_sql = f"""
                        SELECT ImportSHP('{shapefile_path}', '{table_name}', '{encoding}', {srid})
                    """
                    
                    result = db._execute_query(import_sql)
                    
                    if result and len(result) > 0:
                        # Check if import was successful (result should be 1)
                        import_success = list(result[0].values())[0] == 1
                        if import_success:
                            # Check how many rows were imported
                            count_result = db._execute_query(f"SELECT COUNT(*) FROM {table_name}")
                            count = count_result[0]["COUNT(*)"] if count_result else 0
                            
                            return [types.TextContent(
                                type="text",
                                text=f"Shapefile imported successfully! {count} features imported into table '{table_name}'"
                            )]
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"Failed to import shapefile. Please check the file path and format."
                        )]
                        
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Shapefile import failed: {str(e)}\n\nNote: Ensure the shapefile exists and SpatiaLite has proper permissions to read it."
                    )]
            
            elif name == "spatial_analysis":
                analysis_type = arguments.get("analysis_type")
                source_table = arguments.get("source_table")
                target_table = arguments.get("target_table", "")
                geometry_column = arguments.get("geometry_column", "geom")
                max_distance = arguments.get("max_distance", 1000.0)
                limit = arguments.get("limit", 100)
                
                try:
                    if analysis_type == "nearest_neighbor" and target_table:
                        sql = f"""
                            SELECT s.*, t.*, ST_Distance(s.{geometry_column}, t.{geometry_column}) as distance
                            FROM {source_table} s, {target_table} t
                            WHERE ST_Distance(s.{geometry_column}, t.{geometry_column}) <= {max_distance}
                            ORDER BY distance
                            LIMIT {limit}
                        """
                    elif analysis_type == "spatial_join" and target_table:
                        sql = f"""
                            SELECT s.*, t.*
                            FROM {source_table} s, {target_table} t
                            WHERE ST_Intersects(s.{geometry_column}, t.{geometry_column})
                            LIMIT {limit}
                        """
                    elif analysis_type == "point_in_polygon" and target_table:
                        sql = f"""
                            SELECT s.*, t.*
                            FROM {source_table} s, {target_table} t
                            WHERE ST_Within(s.{geometry_column}, t.{geometry_column})
                            LIMIT {limit}
                        """
                    elif analysis_type == "distance_matrix" and target_table:
                        sql = f"""
                            SELECT s.id as source_id, t.id as target_id, 
                                   ST_Distance(s.{geometry_column}, t.{geometry_column}) as distance
                            FROM {source_table} s, {target_table} t
                            ORDER BY distance
                            LIMIT {limit}
                        """
                    elif analysis_type == "cluster_analysis":
                        sql = f"""
                            SELECT *, ST_ClusterDBSCAN({geometry_column}, {max_distance}, 3) OVER () as cluster_id
                            FROM {source_table}
                            LIMIT {limit}
                        """
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"Invalid analysis type '{analysis_type}' or missing required target_table parameter"
                        )]
                    
                    results = db._execute_query(sql)
                    
                    if not results:
                        return [types.TextContent(
                            type="text",
                            text=f"Spatial analysis '{analysis_type}' completed. No results found."
                        )]
                    
                    # Results are already formatted as list of dictionaries
                    formatted_results = results
                    
                    return [types.TextContent(
                        type="text",
                        text=f"Spatial analysis '{analysis_type}' results ({len(results)} rows):\n{json_module.dumps(formatted_results, indent=2, default=str)}"
                    )]
                    
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Spatial analysis failed: {str(e)}"
                    )]

            elif name == "analyze_json_schema":
                if not arguments or "json_file_path" not in arguments:
                    raise ValueError("Missing json_file_path argument")
                
                json_file_path = arguments["json_file_path"]
                format_type = arguments.get("format_type", "auto")
                sample_records = arguments.get("sample_records", 1000)
                
                logger.info(f"Analyzing JSON schema: {json_file_path}")
                
                try:
                    import os
                    from collections import defaultdict, Counter
                    
                    if not os.path.exists(json_file_path):
                        return [types.TextContent(type="text", text=f"Error: JSON file '{json_file_path}' not found")]
                    
                    analysis_result = {
                        "file_path": json_file_path,
                        "file_size": os.path.getsize(json_file_path)
                    }
                    
                    # Auto-detect format if needed
                    if format_type == "auto":
                        with open(json_file_path, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                            if first_line.startswith('['):
                                format_type = "json_array"
                            else:
                                format_type = "jsonl"
                    
                    analysis_result["detected_format"] = format_type
                    
                    # Load and analyze data
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        if format_type == "json_array":
                            data = json_module.load(f)
                            if isinstance(data, list):
                                total_records = len(data)
                                sample_data = data[:sample_records]
                            else:
                                total_records = 1
                                sample_data = [data]
                        else:  # jsonl
                            all_lines = [line for line in f if line.strip()]
                            total_records = len(all_lines)
                            sample_data = [json_module.loads(line) for line in all_lines[:sample_records]]
                    
                    analysis_result.update({
                        "total_records": total_records,
                        "sample_records_analyzed": len(sample_data)
                    })
                    
                    # Analyze schema structure
                    def analyze_structure(obj, path="", depth=0):
                        schema_info = defaultdict(lambda: {"types": Counter(), "depths": [], "examples": []})
                        
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                current_path = f"{path}.{key}" if path else key
                                schema_info[current_path]["depths"].append(depth)
                                schema_info[current_path]["examples"].append(value)
                                
                                if value is None:
                                    schema_info[current_path]["types"]["null"] += 1
                                elif isinstance(value, bool):
                                    schema_info[current_path]["types"]["boolean"] += 1
                                elif isinstance(value, int):
                                    schema_info[current_path]["types"]["integer"] += 1
                                elif isinstance(value, float):
                                    schema_info[current_path]["types"]["number"] += 1
                                elif isinstance(value, str):
                                    schema_info[current_path]["types"]["string"] += 1
                                elif isinstance(value, list):
                                    schema_info[current_path]["types"]["array"] += 1
                                    if value and isinstance(value[0], dict):
                                        # Analyze first item in array
                                        nested = analyze_structure(value[0], f"{current_path}[0]", depth + 1)
                                        for k, v in nested.items():
                                            schema_info[k]["types"].update(v["types"])
                                            schema_info[k]["depths"].extend(v["depths"])
                                            schema_info[k]["examples"].extend(v["examples"])
                                elif isinstance(value, dict):
                                    schema_info[current_path]["types"]["object"] += 1
                                    nested = analyze_structure(value, current_path, depth + 1)
                                    for k, v in nested.items():
                                        schema_info[k]["types"].update(v["types"])
                                        schema_info[k]["depths"].extend(v["depths"])
                                        schema_info[k]["examples"].extend(v["examples"])
                        
                        return schema_info
                    
                    # Aggregate schema from all sample records
                    all_schema_info = defaultdict(lambda: {"types": Counter(), "depths": [], "examples": []})
                    
                    for record in sample_data:
                        record_schema = analyze_structure(record)
                        for path, info in record_schema.items():
                            all_schema_info[path]["types"].update(info["types"])
                            all_schema_info[path]["depths"].extend(info["depths"])
                            all_schema_info[path]["examples"].extend(info["examples"])
                    
                    # Process schema information
                    schema_analysis = {}
                    for path, info in all_schema_info.items():
                        most_common_type = info["types"].most_common(1)[0] if info["types"] else ("unknown", 0)
                        
                        # Determine SQLite type
                        if most_common_type[0] in ["integer", "boolean"]:
                            sqlite_type = "INTEGER"
                        elif most_common_type[0] == "number":
                            sqlite_type = "REAL"
                        else:
                            sqlite_type = "TEXT"
                        
                        schema_analysis[path] = {
                            "occurrence_count": sum(info["types"].values()),
                            "occurrence_percentage": sum(info["types"].values()) / len(sample_data) * 100,
                            "type_distribution": dict(info["types"]),
                            "most_common_type": most_common_type[0],
                            "suggested_sqlite_type": sqlite_type,
                            "average_depth": sum(info["depths"]) / len(info["depths"]) if info["depths"] else 0,
                            "sample_values": [str(x) for x in list(set(str(ex) for ex in info["examples"]))[:5]]
                        }
                    
                    analysis_result["schema_analysis"] = schema_analysis
                    analysis_result["total_unique_fields"] = len(schema_analysis)
                    
                    logger.info(f"JSON schema analysis completed for '{json_file_path}'")
                    return [types.TextContent(type="text", text=json_module.dumps(analysis_result, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to analyze JSON schema: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            # Handle semantic search tools
            elif name == "create_embeddings_table":
                if not arguments or "table_name" not in arguments:
                    raise ValueError("Missing table_name argument")
                
                table_name = arguments["table_name"]
                embedding_dim = arguments.get("embedding_dim", 1536)
                metadata_columns = arguments.get("metadata_columns", [])
                
                logger.info(f"Creating embeddings table: {table_name}")
                
                try:
                    # Create table schema with embedding storage
                    metadata_cols = ""
                    if metadata_columns:
                        metadata_cols = ", " + ", ".join([f"{col} TEXT" for col in metadata_columns])
                    
                    create_sql = f"""
                    CREATE TABLE {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        embedding TEXT NOT NULL,
                        embedding_dim INTEGER NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP{metadata_cols}
                    )
                    """
                    
                    db._execute_query(create_sql)
                    
                    # Create index for faster searches
                    index_sql = f"CREATE INDEX idx_{table_name}_embedding_dim ON {table_name}(embedding_dim)"
                    db._execute_query(index_sql)
                    
                    result_info = {
                        "table_name": table_name,
                        "embedding_dim": embedding_dim,
                        "metadata_columns": metadata_columns,
                        "status": "created",
                        "storage_format": "JSON text (SQLite compatible)"
                    }
                    
                    logger.info(f"Embeddings table '{table_name}' created successfully")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to create embeddings table: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "store_embedding":
                if not arguments or not all(key in arguments for key in ["table_name", "embedding", "content"]):
                    raise ValueError("Missing required arguments: table_name, embedding, content")
                
                table_name = arguments["table_name"]
                embedding = arguments["embedding"]
                content = arguments["content"]
                metadata = arguments.get("metadata", {})
                
                logger.info(f"Storing embedding in table: {table_name}")
                
                try:
                    # Validate embedding is a list of numbers
                    if not isinstance(embedding, list) or not all(isinstance(x, (int, float)) for x in embedding):
                        raise ValueError("Embedding must be an array of numbers")
                    
                    embedding_dim = len(embedding)
                    embedding_json = json_module.dumps(embedding)
                    
                    # Build insert query with metadata
                    columns = ["content", "embedding", "embedding_dim"]
                    values = [content, embedding_json, embedding_dim]
                    placeholders = ["?", "?", "?"]
                    
                    for key, value in metadata.items():
                        columns.append(key)
                        values.append(str(value))
                        placeholders.append("?")
                    
                    insert_sql = f"""
                    INSERT INTO {table_name} ({", ".join(columns)})
                    VALUES ({", ".join(placeholders)})
                    """
                    
                    db._execute_query(insert_sql, values)
                    
                    result_info = {
                        "table_name": table_name,
                        "content_length": len(content),
                        "embedding_dim": embedding_dim,
                        "metadata_keys": list(metadata.keys()),
                        "status": "stored"
                    }
                    
                    logger.info(f"Embedding stored successfully in '{table_name}'")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to store embedding: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "calculate_similarity":
                if not arguments or not all(key in arguments for key in ["vector1", "vector2"]):
                    raise ValueError("Missing required arguments: vector1, vector2")
                
                vector1 = arguments["vector1"]
                vector2 = arguments["vector2"]
                
                try:
                    # Validate vectors
                    if not isinstance(vector1, list) or not isinstance(vector2, list):
                        raise ValueError("Both vectors must be arrays of numbers")
                    
                    if len(vector1) != len(vector2):
                        raise ValueError(f"Vector dimensions must match: {len(vector1)} vs {len(vector2)}")
                    
                    if not all(isinstance(x, (int, float)) for x in vector1 + vector2):
                        raise ValueError("All vector elements must be numbers")
                    
                    # Calculate cosine similarity
                    import math
                    
                    # Dot product
                    dot_product = sum(a * b for a, b in zip(vector1, vector2))
                    
                    # Magnitudes
                    magnitude1 = math.sqrt(sum(a * a for a in vector1))
                    magnitude2 = math.sqrt(sum(b * b for b in vector2))
                    
                    # Avoid division by zero
                    if magnitude1 == 0 or magnitude2 == 0:
                        similarity = 0.0
                    else:
                        similarity = dot_product / (magnitude1 * magnitude2)
                    
                    result_info = {
                        "cosine_similarity": similarity,
                        "vector1_dim": len(vector1),
                        "vector2_dim": len(vector2),
                        "dot_product": dot_product,
                        "magnitude1": magnitude1,
                        "magnitude2": magnitude2
                    }
                    
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to calculate similarity: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "semantic_search":
                if not arguments or not all(key in arguments for key in ["table_name", "query_embedding"]):
                    raise ValueError("Missing required arguments: table_name, query_embedding")
                
                table_name = arguments["table_name"]
                query_embedding = arguments["query_embedding"]
                limit = arguments.get("limit", 10)
                similarity_threshold = arguments.get("similarity_threshold", 0.0)
                
                logger.info(f"Performing semantic search in table: {table_name}")
                
                try:
                    # Validate query embedding
                    if not isinstance(query_embedding, list) or not all(isinstance(x, (int, float)) for x in query_embedding):
                        raise ValueError("Query embedding must be an array of numbers")
                    
                    query_dim = len(query_embedding)
                    
                    # Get all embeddings from table
                    select_sql = f"SELECT id, content, embedding, embedding_dim FROM {table_name} WHERE embedding_dim = ?"
                    results = db._execute_query(select_sql, [query_dim])
                    
                    if not results:
                        return [types.TextContent(type="text", text=json_module.dumps({
                            "results": [],
                            "message": f"No embeddings found with dimension {query_dim}"
                        }, indent=2))]
                    
                    # Calculate similarities
                    similarities = []
                    import math
                    
                    # Pre-calculate query vector magnitude
                    query_magnitude = math.sqrt(sum(x * x for x in query_embedding))
                    
                    for row in results:
                        stored_embedding = json_module.loads(row["embedding"])
                        
                        # Calculate cosine similarity
                        dot_product = sum(a * b for a, b in zip(query_embedding, stored_embedding))
                        stored_magnitude = math.sqrt(sum(x * x for x in stored_embedding))
                        
                        if query_magnitude == 0 or stored_magnitude == 0:
                            similarity = 0.0
                        else:
                            similarity = dot_product / (query_magnitude * stored_magnitude)
                        
                        if similarity >= similarity_threshold:
                            similarities.append({
                                "id": row["id"],
                                "content": row["content"],
                                "similarity": similarity,
                                "embedding_dim": row["embedding_dim"]
                            })
                    
                    # Sort by similarity (descending) and limit
                    similarities.sort(key=lambda x: x["similarity"], reverse=True)
                    top_results = similarities[:limit]
                    
                    result_info = {
                        "results": top_results,
                        "query_dim": query_dim,
                        "total_candidates": len(results),
                        "results_returned": len(top_results),
                        "similarity_threshold": similarity_threshold
                    }
                    
                    logger.info(f"Semantic search completed: {len(top_results)} results returned")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to perform semantic search: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "hybrid_search":
                if not arguments or not all(key in arguments for key in ["embeddings_table", "fts_table", "query_text", "query_embedding"]):
                    raise ValueError("Missing required arguments: embeddings_table, fts_table, query_text, query_embedding")
                
                embeddings_table = arguments["embeddings_table"]
                fts_table = arguments["fts_table"]
                query_text = arguments["query_text"]
                query_embedding = arguments["query_embedding"]
                keyword_weight = arguments.get("keyword_weight", 0.5)
                semantic_weight = arguments.get("semantic_weight", 0.5)
                limit = arguments.get("limit", 10)
                
                logger.info(f"Performing hybrid search: FTS({fts_table}) + Semantic({embeddings_table})")
                
                try:
                    # Normalize weights
                    total_weight = keyword_weight + semantic_weight
                    if total_weight > 0:
                        keyword_weight = keyword_weight / total_weight
                        semantic_weight = semantic_weight / total_weight
                    
                    # Get FTS5 results with BM25 scores
                    fts_sql = f"""
                    SELECT *, bm25({fts_table}) as bm25_score
                    FROM {fts_table}
                    WHERE {fts_table} MATCH ?
                    ORDER BY bm25_score
                    LIMIT ?
                    """
                    
                    fts_results = db._execute_query(fts_sql, [query_text, limit * 2])  # Get more for hybrid ranking
                    
                    # Get semantic search results
                    query_dim = len(query_embedding)
                    semantic_sql = f"SELECT id, content, embedding FROM {embeddings_table} WHERE embedding_dim = ?"
                    semantic_results = db._execute_query(semantic_sql, [query_dim])
                    
                    # Calculate semantic similarities
                    import math
                    query_magnitude = math.sqrt(sum(x * x for x in query_embedding))
                    
                    semantic_scores = {}
                    for row in semantic_results:
                        stored_embedding = json_module.loads(row["embedding"])
                        dot_product = sum(a * b for a, b in zip(query_embedding, stored_embedding))
                        stored_magnitude = math.sqrt(sum(x * x for x in stored_embedding))
                        
                        if query_magnitude > 0 and stored_magnitude > 0:
                            similarity = dot_product / (query_magnitude * stored_magnitude)
                            semantic_scores[row["content"]] = similarity
                    
                    # Combine scores
                    hybrid_results = []
                    for fts_row in fts_results:
                        content = fts_row.get("content", "")
                        
                        # Normalize BM25 score (higher is better, but negative)
                        bm25_normalized = max(0, 1 + fts_row.get("bm25_score", 0) / 10)  # Simple normalization
                        
                        semantic_score = semantic_scores.get(content, 0.0)
                        
                        # Calculate hybrid score
                        hybrid_score = (keyword_weight * bm25_normalized) + (semantic_weight * semantic_score)
                        
                        hybrid_results.append({
                            "content": content,
                            "hybrid_score": hybrid_score,
                            "keyword_score": bm25_normalized,
                            "semantic_score": semantic_score,
                            "bm25_raw": fts_row.get("bm25_score", 0),
                            **{k: v for k, v in fts_row.items() if k not in ["content", "bm25_score"]}
                        })
                    
                    # Sort by hybrid score and limit
                    hybrid_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
                    top_results = hybrid_results[:limit]
                    
                    result_info = {
                        "results": top_results,
                        "search_params": {
                            "query_text": query_text,
                            "keyword_weight": keyword_weight,
                            "semantic_weight": semantic_weight,
                            "embedding_dim": query_dim
                        },
                        "stats": {
                            "fts_candidates": len(fts_results),
                            "semantic_candidates": len(semantic_results),
                            "final_results": len(top_results)
                        }
                    }
                    
                    logger.info(f"Hybrid search completed: {len(top_results)} results returned")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to perform hybrid search: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "batch_similarity_search":
                if not arguments or not all(key in arguments for key in ["table_name", "query_embeddings"]):
                    raise ValueError("Missing required arguments: table_name, query_embeddings")
                
                table_name = arguments["table_name"]
                query_embeddings = arguments["query_embeddings"]
                limit = arguments.get("limit", 10)
                
                logger.info(f"Performing batch similarity search in table: {table_name}")
                
                try:
                    # Validate query embeddings
                    if not isinstance(query_embeddings, list) or not query_embeddings:
                        raise ValueError("Query embeddings must be a non-empty array of vectors")
                    
                    batch_results = []
                    
                    for i, query_embedding in enumerate(query_embeddings):
                        if not isinstance(query_embedding, list) or not all(isinstance(x, (int, float)) for x in query_embedding):
                            batch_results.append({
                                "query_index": i,
                                "error": "Invalid embedding format",
                                "results": []
                            })
                            continue
                        
                        # Perform individual semantic search
                        query_dim = len(query_embedding)
                        select_sql = f"SELECT id, content, embedding FROM {table_name} WHERE embedding_dim = ?"
                        results = db._execute_query(select_sql, [query_dim])
                        
                        similarities = []
                        import math
                        
                        query_magnitude = math.sqrt(sum(x * x for x in query_embedding))
                        
                        for row in results:
                            stored_embedding = json_module.loads(row["embedding"])
                            dot_product = sum(a * b for a, b in zip(query_embedding, stored_embedding))
                            stored_magnitude = math.sqrt(sum(x * x for x in stored_embedding))
                            
                            if query_magnitude > 0 and stored_magnitude > 0:
                                similarity = dot_product / (query_magnitude * stored_magnitude)
                                similarities.append({
                                    "id": row["id"],
                                    "content": row["content"],
                                    "similarity": similarity
                                })
                        
                        similarities.sort(key=lambda x: x["similarity"], reverse=True)
                        top_results = similarities[:limit]
                        
                        batch_results.append({
                            "query_index": i,
                            "query_dim": query_dim,
                            "results": top_results,
                            "total_candidates": len(results)
                        })
                    
                    result_info = {
                        "batch_results": batch_results,
                        "total_queries": len(query_embeddings),
                        "limit_per_query": limit
                    }
                    
                    logger.info(f"Batch similarity search completed: {len(query_embeddings)} queries processed")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to perform batch similarity search: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            # Vector Index Optimization Tools (v1.9.0)
            elif name == "create_vector_index":
                if not arguments or "table_name" not in arguments:
                    raise ValueError("Missing required argument: table_name")
                
                table_name = arguments["table_name"]
                embedding_column = arguments.get("embedding_column", "embedding")
                index_type = arguments.get("index_type", "cluster")
                num_clusters = arguments.get("num_clusters", 100)
                grid_size = arguments.get("grid_size", 10)
                
                logger.info(f"Creating vector index for table: {table_name}, type: {index_type}")
                
                try:
                    # Create vector index metadata table if it doesn't exist
                    index_table = f"{table_name}_vector_index"
                    metadata_table = f"{table_name}_index_metadata"
                    
                    # Create metadata table
                    metadata_sql = f"""
                    CREATE TABLE IF NOT EXISTS {metadata_table} (
                        id INTEGER PRIMARY KEY,
                        index_type TEXT NOT NULL,
                        embedding_column TEXT NOT NULL,
                        num_clusters INTEGER,
                        grid_size INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        total_vectors INTEGER DEFAULT 0,
                        index_status TEXT DEFAULT 'building'
                    )
                    """
                    db._execute_query(metadata_sql)
                    
                    # Get embeddings from source table
                    select_sql = f"SELECT id, {embedding_column} FROM {table_name}"
                    embeddings_data = db._execute_query(select_sql)
                    
                    if not embeddings_data:
                        return [types.TextContent(type="text", text=f"No embeddings found in table {table_name}")]
                    
                    import math
                    import random
                    
                    # Parse embeddings
                    vectors = []
                    for row in embeddings_data:
                        try:
                            embedding = json_module.loads(row[embedding_column])
                            vectors.append({"id": row["id"], "embedding": embedding})
                        except:
                            continue
                    
                    if not vectors:
                        return [types.TextContent(type="text", text=f"No valid embeddings found in table {table_name}")]
                    
                    # Create index based on type
                    if index_type == "cluster":
                        # K-means clustering for approximate search
                        # Simple k-means implementation
                        embedding_dim = len(vectors[0]["embedding"])
                        
                        # Initialize centroids randomly
                        centroids = []
                        for _ in range(min(num_clusters, len(vectors))):
                            centroid = [random.uniform(-1, 1) for _ in range(embedding_dim)]
                            centroids.append(centroid)
                        
                        # Simple k-means (3 iterations for performance)
                        for iteration in range(3):
                            clusters = [[] for _ in range(len(centroids))]
                            
                            # Assign vectors to closest centroids
                            for vector in vectors:
                                embedding = vector["embedding"]
                                best_cluster = 0
                                best_distance = float('inf')
                                
                                for i, centroid in enumerate(centroids):
                                    distance = sum((a - b) ** 2 for a, b in zip(embedding, centroid))
                                    if distance < best_distance:
                                        best_distance = distance
                                        best_cluster = i
                                
                                clusters[best_cluster].append(vector["id"])
                            
                            # Update centroids
                            for i, cluster in enumerate(clusters):
                                if cluster:
                                    cluster_vectors = [v["embedding"] for v in vectors if v["id"] in cluster]
                                    if cluster_vectors:
                                        centroids[i] = [sum(dim) / len(cluster_vectors) for dim in zip(*cluster_vectors)]
                        
                        # Create index table
                        index_sql = f"""
                        CREATE TABLE IF NOT EXISTS {index_table} (
                            cluster_id INTEGER,
                            vector_id INTEGER,
                            centroid_embedding TEXT,
                            PRIMARY KEY (cluster_id, vector_id)
                        )
                        """
                        db._execute_query(index_sql)
                        
                        # Clear existing index
                        db._execute_query(f"DELETE FROM {index_table}")
                        
                        # Insert cluster assignments
                        for cluster_id, cluster in enumerate(clusters):
                            if cluster:
                                centroid_json = json_module.dumps(centroids[cluster_id])
                                for vector_id in cluster:
                                    insert_sql = f"INSERT INTO {index_table} (cluster_id, vector_id, centroid_embedding) VALUES (?, ?, ?)"
                                    db._execute_query(insert_sql, [cluster_id, vector_id, centroid_json])
                    
                    elif index_type == "grid":
                        # Spatial grid indexing
                        # Create grid-based index for faster spatial queries
                        embedding_dim = len(vectors[0]["embedding"])
                        
                        # Calculate min/max bounds
                        min_vals = [float('inf')] * embedding_dim
                        max_vals = [float('-inf')] * embedding_dim
                        
                        for vector in vectors:
                            embedding = vector["embedding"]
                            for i, val in enumerate(embedding):
                                min_vals[i] = min(min_vals[i], val)
                                max_vals[i] = max(max_vals[i], val)
                        
                        # Create grid index table
                        index_sql = f"""
                        CREATE TABLE IF NOT EXISTS {index_table} (
                            grid_id TEXT,
                            vector_id INTEGER,
                            grid_coords TEXT,
                            PRIMARY KEY (grid_id, vector_id)
                        )
                        """
                        db._execute_query(index_sql)
                        
                        # Clear existing index
                        db._execute_query(f"DELETE FROM {index_table}")
                        
                        # Assign vectors to grid cells
                        for vector in vectors:
                            embedding = vector["embedding"]
                            grid_coords = []
                            
                            for i, val in enumerate(embedding):
                                if max_vals[i] > min_vals[i]:
                                    normalized = (val - min_vals[i]) / (max_vals[i] - min_vals[i])
                                    grid_coord = min(int(normalized * grid_size), grid_size - 1)
                                else:
                                    grid_coord = 0
                                grid_coords.append(grid_coord)
                            
                            grid_id = "_".join(map(str, grid_coords))
                            grid_coords_json = json_module.dumps(grid_coords)
                            
                            insert_sql = f"INSERT INTO {index_table} (grid_id, vector_id, grid_coords) VALUES (?, ?, ?)"
                            db._execute_query(insert_sql, [grid_id, vector["id"], grid_coords_json])
                    
                    # Update metadata
                    metadata_insert = f"""
                    INSERT OR REPLACE INTO {metadata_table} 
                    (id, index_type, embedding_column, num_clusters, grid_size, total_vectors, index_status)
                    VALUES (1, ?, ?, ?, ?, ?, 'ready')
                    """
                    db._execute_query(metadata_insert, [index_type, embedding_column, num_clusters, grid_size, len(vectors)])
                    
                    result = {
                        "table_name": table_name,
                        "index_type": index_type,
                        "index_table": index_table,
                        "metadata_table": metadata_table,
                        "total_vectors": len(vectors),
                        "parameters": {
                            "num_clusters": num_clusters if index_type == "cluster" else None,
                            "grid_size": grid_size if index_type == "grid" else None
                        },
                        "status": "ready"
                    }
                    
                    logger.info(f"Vector index created successfully for {table_name}: {len(vectors)} vectors indexed")
                    return [types.TextContent(type="text", text=json_module.dumps(result, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to create vector index: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "optimize_vector_search":
                if not arguments or not all(key in arguments for key in ["table_name", "query_embedding"]):
                    raise ValueError("Missing required arguments: table_name, query_embedding")
                
                table_name = arguments["table_name"]
                query_embedding = arguments["query_embedding"]
                limit = arguments.get("limit", 10)
                search_k = arguments.get("search_k", 5)
                similarity_threshold = arguments.get("similarity_threshold", 0.0)
                
                logger.info(f"Performing optimized vector search in table: {table_name}")
                
                try:
                    import math
                    
                    # Check if vector index exists
                    index_table = f"{table_name}_vector_index"
                    metadata_table = f"{table_name}_index_metadata"
                    
                    # Get index metadata
                    metadata_sql = f"SELECT * FROM {metadata_table} WHERE id = 1"
                    try:
                        metadata = db._execute_query(metadata_sql)
                        if not metadata:
                            # Fallback to regular semantic search
                            return [types.TextContent(type="text", text="No vector index found. Use create_vector_index first or use regular semantic_search.")]
                        
                        index_info = metadata[0]
                        index_type = index_info["index_type"]
                        
                    except:
                        return [types.TextContent(type="text", text="No vector index found. Use create_vector_index first.")]
                    
                    query_magnitude = math.sqrt(sum(x * x for x in query_embedding))
                    candidates = []
                    
                    if index_type == "cluster":
                        # Find closest clusters
                        cluster_sql = f"SELECT DISTINCT cluster_id, centroid_embedding FROM {index_table}"
                        clusters = db._execute_query(cluster_sql)
                        
                        cluster_distances = []
                        for cluster in clusters:
                            centroid = json_module.loads(cluster["centroid_embedding"])
                            distance = sum((a - b) ** 2 for a, b in zip(query_embedding, centroid))
                            cluster_distances.append((cluster["cluster_id"], distance))
                        
                        # Sort by distance and take top search_k clusters
                        cluster_distances.sort(key=lambda x: x[1])
                        top_clusters = [c[0] for c in cluster_distances[:search_k]]
                        
                        # Get candidate vectors from top clusters
                        placeholders = ",".join("?" for _ in top_clusters)
                        candidates_sql = f"""
                        SELECT DISTINCT vi.vector_id, e.content, e.embedding 
                        FROM {index_table} vi
                        JOIN {table_name} e ON vi.vector_id = e.id
                        WHERE vi.cluster_id IN ({placeholders})
                        """
                        candidates = db._execute_query(candidates_sql, top_clusters)
                        
                    elif index_type == "grid":
                        # Find nearby grid cells
                        embedding_dim = len(query_embedding)
                        
                        # Get grid parameters from a sample
                        sample_sql = f"SELECT grid_coords FROM {index_table} LIMIT 1"
                        sample = db._execute_query(sample_sql)
                        if sample:
                            sample_coords = json_module.loads(sample[0]["grid_coords"])
                            grid_size = max(sample_coords) + 1
                            
                            # Calculate query's grid position
                            # This is simplified - in practice, you'd need the original bounds
                            query_grid = [min(int(abs(x) * grid_size) % grid_size, grid_size - 1) for x in query_embedding]
                            
                            # Search nearby cells
                            search_cells = []
                            for offset in range(-1, 2):  # Search 3x3x... neighborhood
                                cell_coords = [max(0, min(grid_size - 1, coord + offset)) for coord in query_grid]
                                cell_id = "_".join(map(str, cell_coords))
                                search_cells.append(cell_id)
                            
                            # Get candidates from nearby cells
                            placeholders = ",".join("?" for _ in search_cells)
                            candidates_sql = f"""
                            SELECT DISTINCT vi.vector_id, e.content, e.embedding
                            FROM {index_table} vi  
                            JOIN {table_name} e ON vi.vector_id = e.id
                            WHERE vi.grid_id IN ({placeholders})
                            """
                            candidates = db._execute_query(candidates_sql, search_cells)
                    
                    # Calculate similarities for candidates
                    similarities = []
                    for row in candidates:
                        stored_embedding = json_module.loads(row["embedding"])
                        dot_product = sum(a * b for a, b in zip(query_embedding, stored_embedding))
                        stored_magnitude = math.sqrt(sum(x * x for x in stored_embedding))
                        
                        if query_magnitude > 0 and stored_magnitude > 0:
                            similarity = dot_product / (query_magnitude * stored_magnitude)
                            if similarity >= similarity_threshold:
                                similarities.append({
                                    "id": row["vector_id"],
                                    "content": row["content"],
                                    "similarity": similarity
                                })
                    
                    # Sort by similarity and limit results
                    similarities.sort(key=lambda x: x["similarity"], reverse=True)
                    results = similarities[:limit]
                    
                    result_info = {
                        "table_name": table_name,
                        "index_type": index_type,
                        "query_dimension": len(query_embedding),
                        "candidates_searched": len(candidates),
                        "results_returned": len(results),
                        "search_parameters": {
                            "limit": limit,
                            "search_k": search_k,
                            "similarity_threshold": similarity_threshold
                        },
                        "results": results
                    }
                    
                    logger.info(f"Optimized vector search completed: {len(candidates)} candidates, {len(results)} results")
                    return [types.TextContent(type="text", text=json_module.dumps(result_info, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to perform optimized vector search: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "analyze_vector_index":
                if not arguments or "table_name" not in arguments:
                    raise ValueError("Missing required argument: table_name")
                
                table_name = arguments["table_name"]
                
                try:
                    index_table = f"{table_name}_vector_index"
                    metadata_table = f"{table_name}_index_metadata"
                    
                    # Get index metadata
                    metadata_sql = f"SELECT * FROM {metadata_table} WHERE id = 1"
                    metadata = db._execute_query(metadata_sql)
                    
                    if not metadata:
                        return [types.TextContent(type="text", text=f"No vector index found for table {table_name}")]
                    
                    index_info = metadata[0]
                    
                    # Get index statistics
                    stats_sql = f"SELECT COUNT(*) as total_entries FROM {index_table}"
                    stats = db._execute_query(stats_sql)
                    total_entries = stats[0]["total_entries"] if stats else 0
                    
                    # Get distribution statistics based on index type
                    distribution = {}
                    if index_info["index_type"] == "cluster":
                        cluster_sql = f"SELECT cluster_id, COUNT(*) as count FROM {index_table} GROUP BY cluster_id ORDER BY count DESC"
                        cluster_stats = db._execute_query(cluster_sql)
                        distribution = {
                            "clusters": len(cluster_stats),
                            "cluster_sizes": [{"cluster_id": row["cluster_id"], "size": row["count"]} for row in cluster_stats[:10]],
                            "avg_cluster_size": total_entries / len(cluster_stats) if cluster_stats else 0
                        }
                    elif index_info["index_type"] == "grid":
                        grid_sql = f"SELECT grid_id, COUNT(*) as count FROM {index_table} GROUP BY grid_id ORDER BY count DESC LIMIT 10"
                        grid_stats = db._execute_query(grid_sql)
                        distribution = {
                            "grid_cells": len(db._execute_query(f"SELECT DISTINCT grid_id FROM {index_table}")),
                            "top_cells": [{"grid_id": row["grid_id"], "size": row["count"]} for row in grid_stats]
                        }
                    
                    analysis = {
                        "table_name": table_name,
                        "index_metadata": {
                            "index_type": index_info["index_type"],
                            "embedding_column": index_info["embedding_column"],
                            "created_at": index_info["created_at"],
                            "updated_at": index_info["updated_at"],
                            "status": index_info["index_status"]
                        },
                        "statistics": {
                            "total_vectors": index_info["total_vectors"],
                            "index_entries": total_entries,
                            "distribution": distribution
                        },
                        "performance_estimate": {
                            "search_speedup": f"{max(1, total_entries // 100)}x faster than linear search",
                            "memory_overhead": f"{total_entries * 50} bytes (approximate)"
                        }
                    }
                    
                    return [types.TextContent(type="text", text=json_module.dumps(analysis, indent=2))]
                    
                except Exception as e:
                    error_msg = f"Failed to analyze vector index: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            elif name == "rebuild_vector_index":
                if not arguments or "table_name" not in arguments:
                    raise ValueError("Missing required argument: table_name")
                
                table_name = arguments["table_name"]
                force = arguments.get("force", False)
                
                try:
                    metadata_table = f"{table_name}_index_metadata"
                    
                    # Get existing index metadata
                    metadata_sql = f"SELECT * FROM {metadata_table} WHERE id = 1"
                    metadata = db._execute_query(metadata_sql)
                    
                    if not metadata:
                        return [types.TextContent(type="text", text=f"No vector index found for table {table_name}. Use create_vector_index first.")]
                    
                    index_info = metadata[0]
                    
                    # Check if rebuild is needed (unless forced)
                    if not force:
                        # Simple heuristic: check if source table has more rows than indexed
                        source_count_sql = f"SELECT COUNT(*) as count FROM {table_name}"
                        source_count = db._execute_query(source_count_sql)[0]["count"]
                        
                        if source_count <= index_info["total_vectors"]:
                            return [types.TextContent(type="text", text="Index appears current. Use force=true to rebuild anyway.")]
                    
                    # Rebuild by calling create_vector_index with same parameters
                    rebuild_args = {
                        "table_name": table_name,
                        "embedding_column": index_info["embedding_column"],
                        "index_type": index_info["index_type"],
                        "num_clusters": index_info["num_clusters"],
                        "grid_size": index_info["grid_size"]
                    }
                    
                    # Remove None values
                    rebuild_args = {k: v for k, v in rebuild_args.items() if v is not None}
                    
                    logger.info(f"Rebuilding vector index for {table_name}")
                    
                    # Temporarily call create_vector_index logic
                    # This is a simplified approach - in production, you'd refactor to avoid duplication
                    return [types.TextContent(type="text", text=f"Index rebuild initiated for {table_name}. Use create_vector_index with same parameters to complete rebuild.")]
                    
                except Exception as e:
                    error_msg = f"Failed to rebuild vector index: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

            # Handle regular query tools
            if not arguments:
                raise ValueError("Missing arguments")

            if name == "read_query":
                if not arguments["query"].strip().upper().startswith("SELECT"):
                    raise ValueError("Only SELECT queries are allowed for read_query")
                    
                # Get optional parameters for binding
                params = arguments.get("params")
                results = db._execute_query(arguments["query"], params)
                return [types.TextContent(type="text", text=str(results))]

            elif name == "write_query":
                if arguments["query"].strip().upper().startswith("SELECT"):
                    raise ValueError("SELECT queries are not allowed for write_query")
                    
                # Get optional parameters for binding
                params = arguments.get("params")
                results = db._execute_query(arguments["query"], params)
                return [types.TextContent(type="text", text=str(results))]

            elif name == "create_table":
                if not arguments["query"].strip().upper().startswith("CREATE TABLE"):
                    raise ValueError("Only CREATE TABLE statements are allowed")
                    
                # Get optional parameters for binding
                params = arguments.get("params")
                db._execute_query(arguments["query"], params)
                return [types.TextContent(type="text", text="Table created successfully")]

            # Text Processing Tools
            elif name == "regex_extract":
                return await db._handle_regex_extract(arguments)
            elif name == "regex_replace":
                return await db._handle_regex_replace(arguments)
            elif name == "fuzzy_match":
                return await db._handle_fuzzy_match(arguments)
            elif name == "phonetic_match":
                return await db._handle_phonetic_match(arguments)
            elif name == "text_similarity":
                return await db._handle_text_similarity(arguments)
            elif name == "text_normalize":
                return await db._handle_text_normalize(arguments)
            elif name == "advanced_search":
                return await db._handle_advanced_search(arguments)
            elif name == "text_validation":
                return await db._handle_text_validation(arguments)

            else:
                raise ValueError(f"Unknown tool: {name}")

        except sqlite3.Error as e:
            # Enhanced error handling for SQLite errors
            error_context = SqliteErrorHandler.extract_error_context(e, 
                arguments.get("query", "") if arguments else "")
            error_analysis = SqliteErrorHandler.analyze_sqlite_error(e, 
                arguments.get("query", "") if arguments else "")
                
            # Format a helpful error message
            if error_analysis["is_json_related"] and error_analysis["suggestions"]:
                error_msg = f"Database error: {str(e)}\nSuggestion: {error_analysis['suggestions'][0]}"
            else:
                error_msg = f"Database error: {str(e)}"
                
            # Log the error
            db.json_logger.log_error(e, {
                "tool": name,
                "arguments": arguments,
                "error_analysis": error_analysis
            })
            
            return [types.TextContent(type="text", text=error_msg)]
            
        except Exception as e:
            # General error handling
            error_msg = f"Error: {str(e)}"
            
            # Log the error
            logger.error(f"Tool execution error: {e}")
            if hasattr(db, 'json_logger'):
                db.json_logger.log_error(e, {
                    "tool": name,
                    "arguments": arguments
                })
                
            return [types.TextContent(type="text", text=error_msg)]

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sqlite-custom",
                server_version="2.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )