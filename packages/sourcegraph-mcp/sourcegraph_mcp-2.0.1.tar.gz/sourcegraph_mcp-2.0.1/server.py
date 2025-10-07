#!/usr/bin/env python3
"""
SourceGraph MCP Server
A Model Context Protocol server for searching code via SourceGraph's GraphQL API.
Leverages SourceGraph's indexed search for fast symbol lookups, definitions, and references.
Supports both local and cloud SourceGraph instances.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Optional, Sequence

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Default configuration
DEFAULT_CONFIG = {
    "sourcegraph_url": "http://localhost:3370",
    "access_token": "",
    "timeout": 30
}


def load_config(args: Optional[argparse.Namespace] = None) -> dict[str, Any]:
    """Load configuration from file, environment variables, and CLI args.
    
    Priority (highest to lowest):
    1. CLI arguments
    2. Environment variables
    3. Config file (SOURCEGRAPH_CONFIG env var or config.json)
    4. Default values
    """
    config = DEFAULT_CONFIG.copy()
    
    # Try to load from config file
    config_file = None
    if args and args.config:
        config_file = Path(args.config)
    elif config_path := os.getenv("SOURCEGRAPH_CONFIG"):
        config_file = Path(config_path)
    else:
        default_config = Path(__file__).parent / "config.json"
        if default_config.exists():
            config_file = default_config
    
    if config_file and config_file.exists():
        try:
            with open(config_file) as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}", flush=True)
    
    # Environment variables override config file
    if url := os.getenv("SOURCEGRAPH_URL"):
        config["sourcegraph_url"] = url
    if token := os.getenv("SOURCEGRAPH_TOKEN"):
        config["access_token"] = token
    
    # CLI arguments override everything
    if args:
        if args.url:
            config["sourcegraph_url"] = args.url
        if args.token:
            config["access_token"] = args.token
        if args.timeout:
            config["timeout"] = args.timeout
    
    return config


# Global config - will be set in main()
CONFIG = None

# Initialize MCP server
app = Server("sourcegraph-mcp")


async def execute_graphql_query(
    query: str,
    variables: dict[str, Any],
    timeout: Optional[int] = None
) -> dict[str, Any]:
    """
    Execute a GraphQL query against SourceGraph API.
    
    Args:
        query: GraphQL query string
        variables: Query variables
        timeout: Optional timeout override
    
    Returns:
        Dictionary containing API response
    """
    url = CONFIG["sourcegraph_url"].rstrip("/")
    token = CONFIG["access_token"]
    
    if not token:
        return {
            "error": "No access token configured. Please set SOURCEGRAPH_TOKEN or add to config.json"
        }
    
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query,
        "variables": variables
    }
    
    request_timeout = timeout or CONFIG["timeout"]
    
    try:
        async with httpx.AsyncClient(timeout=request_timeout) as client:
            response = await client.post(
                f"{url}/.api/graphql",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    except httpx.TimeoutException:
        return {"error": f"Request timed out after {request_timeout} seconds"}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


async def search_symbols(
    symbol_name: str,
    symbol_kind: Optional[str] = None,
    repo_filter: Optional[str] = None,
    max_results: int = 10
) -> dict[str, Any]:
    """
    Search for symbol definitions (where symbols are declared/defined).
    Uses SourceGraph's indexed symbol search for fast lookups.
    
    Args:
        symbol_name: Name of the symbol to find
        symbol_kind: Optional symbol kind filter (function, class, method, etc.)
        repo_filter: Optional repository filter (e.g., 'repo:owner/name')
        max_results: Maximum number of results
    
    Returns:
        Dictionary containing search results with file paths and line numbers
    """
    # Build query for symbol definitions
    query_parts = [f"type:symbol {symbol_name}"]
    
    if symbol_kind:
        query_parts.append(f"select:symbol.{symbol_kind}")
    
    if repo_filter:
        query_parts.append(repo_filter)
    
    query_parts.append(f"count:{max_results}")
    query_str = " ".join(query_parts)
    
    graphql_query = """
    query SearchSymbols($query: String!) {
        search(query: $query, version: V3, patternType: literal) {
            results {
                matchCount
                results {
                    __typename
                    ... on FileMatch {
                        file {
                            path
                            url
                            repository {
                                name
                                url
                            }
                        }
                        symbols {
                            name
                            kind
                            location {
                                resource {
                                    path
                                }
                                range {
                                    start {
                                        line
                                        character
                                    }
                                    end {
                                        line
                                        character
                                    }
                                }
                            }
                        }
                    }
                }
                limitHit
                cloning {
                    name
                }
                missing {
                    name
                }
            }
        }
    }
    """
    
    return await execute_graphql_query(graphql_query, {"query": query_str})


async def search_code(
    query: str,
    pattern_type: str = "literal",
    max_results: int = 10
) -> dict[str, Any]:
    """
    Search code content (for finding usages/references).
    
    Args:
        query: Search query (supports SourceGraph query syntax)
        pattern_type: Pattern type (literal, regexp, structural)
        max_results: Maximum number of results
    
    Returns:
        Dictionary containing search results
    """
    graphql_query = """
    query SearchCode($query: String!, $patternType: SearchPatternType!) {
        search(query: $query, version: V3, patternType: $patternType) {
            results {
                matchCount
                results {
                    __typename
                    ... on FileMatch {
                        file {
                            path
                            url
                            repository {
                                name
                                url
                            }
                        }
                        lineMatches {
                            preview
                            lineNumber
                            offsetAndLengths
                        }
                    }
                    ... on Repository {
                        name
                        url
                    }
                }
                limitHit
                cloning {
                    name
                }
                missing {
                    name
                }
            }
        }
    }
    """
    
    return await execute_graphql_query(
        graphql_query, 
        {
            "query": f"{query} count:{max_results}",
            "patternType": pattern_type
        }
    )


def format_symbol_results(data: dict[str, Any]) -> str:
    """Format symbol search results (definitions) for display."""
    if "error" in data:
        return f"❌ Error: {data['error']}"
    
    if "errors" in data:
        errors = data["errors"]
        return f"❌ GraphQL Error: {errors[0].get('message', 'Unknown error')}"
    
    try:
        search_data = data["data"]["search"]
        results = search_data["results"]["results"]
        match_count = search_data["results"]["matchCount"]
        
        if not results:
            return "No symbol definitions found."
        
        output = [f"# Symbol Definitions Found\n"]
        output.append(f"**Total matches:** {match_count}\n")
        
        if search_data["results"].get("limitHit"):
            output.append("⚠️ Result limit hit - try narrowing your search with repo: or file: filters\n")
        
        # Process FileMatch results containing symbols
        file_matches = [r for r in results if r["__typename"] == "FileMatch"]
        
        symbol_count = 0
        for file_match in file_matches:
            file_info = file_match["file"]
            repo = file_info["repository"]
            symbols = file_match.get("symbols", [])
            
            if not symbols:
                continue
            
            for symbol in symbols:
                symbol_count += 1
                location = symbol["location"]
                start_line = location["range"]["start"]["line"]
                
                output.append(f"\n## {symbol_count}. `{symbol['name']}` ({symbol['kind']})")
                output.append(f"**File:** `{file_info['path']}`")
                output.append(f"**Line:** {start_line}")
                output.append(f"**Repository:** `{repo['name']}`")
                output.append(f"**URL:** {file_info['url']}")
                
                # Show character position if available
                start_char = location["range"]["start"]["character"]
                if start_char > 0:
                    output.append(f"**Position:** Line {start_line}, Column {start_char}")
        
        if symbol_count == 0:
            return "No symbols found in the results. Try using the general code search instead."
        
        return "\n".join(output)
    
    except (KeyError, TypeError) as e:
        return f"❌ Error parsing results: {str(e)}\nRaw data: {json.dumps(data, indent=2)}"


def format_code_results(data: dict[str, Any]) -> str:
    """Format code search results (usages/references) for display."""
    if "error" in data:
        return f"❌ Error: {data['error']}"
    
    if "errors" in data:
        errors = data["errors"]
        return f"❌ GraphQL Error: {errors[0].get('message', 'Unknown error')}"
    
    try:
        search_data = data["data"]["search"]
        results = search_data["results"]["results"]
        match_count = search_data["results"]["matchCount"]
        
        if not results:
            return "No code matches found."
        
        output = [f"# Code Search Results\n"]
        output.append(f"**Total matches:** {match_count}\n")
        
        if search_data["results"].get("limitHit"):
            output.append("⚠️ Result limit hit - try narrowing your search\n")
        
        # Group results by file
        file_matches = [r for r in results if r["__typename"] == "FileMatch"]
        
        for i, match in enumerate(file_matches, 1):
            file_info = match["file"]
            repo = file_info["repository"]
            
            output.append(f"\n## {i}. `{file_info['path']}`")
            output.append(f"**Repository:** `{repo['name']}`")
            output.append(f"**URL:** {file_info['url']}\n")
            
            # Show line matches with line numbers
            line_matches = match.get("lineMatches", [])
            if line_matches:
                output.append("**Matches:**")
                for line_match in line_matches[:10]:  # Show first 10 matches per file
                    line_num = line_match["lineNumber"]
                    preview = line_match["preview"].strip()
                    output.append(f"- **Line {line_num}:** `{preview}`")
                
                if len(line_matches) > 10:
                    output.append(f"  _(and {len(line_matches) - 10} more matches in this file)_")
        
        return "\n".join(output)
    
    except (KeyError, TypeError) as e:
        return f"❌ Error parsing results: {str(e)}\nRaw data: {json.dumps(data, indent=2)}"


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="find_symbol_definition",
            description=(
                "Find where a symbol (function, class, method, variable, constant) is DEFINED in the codebase. "
                "Returns the exact file path and line number where the symbol is declared.\n\n"
                "This uses SourceGraph's indexed symbol search for fast lookups. "
                "Perfect for 'go to definition' or 'where is X defined?' queries.\n\n"
                "**Returns:** File path, line number, and column position of the definition.\n\n"
                "**Examples:**\n"
                "- Find where the ProcessOrder function is defined\n"
                "- Locate the definition of class CustomerService\n"
                "- Find where variable API_KEY is declared\n"
                "- Show me where the HandleRequest method is defined\n\n"
                "**Tips:**\n"
                "- Use symbol_kind filter to narrow results (function, class, method, variable)\n"
                "- Use repo_filter to search specific repositories (e.g., 'repo:myorg/myrepo')\n"
                "- Searches are case-sensitive by default\n\n"
                "**Note:** To find where a symbol is USED (not defined), use find_symbol_references instead."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol_name": {
                        "type": "string",
                        "description": "Name of the symbol to find (e.g., 'ProcessOrder', 'CustomerService', 'API_KEY')"
                    },
                    "symbol_kind": {
                        "type": "string",
                        "description": "Optional: Filter by symbol kind to narrow results",
                        "enum": ["function", "class", "method", "variable", "constant", "interface", "struct", "enum"]
                    },
                    "repo_filter": {
                        "type": "string",
                        "description": "Optional: Filter by repository (e.g., 'repo:owner/name' or 'repo:^github\\.com/org/project$')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["symbol_name"]
            }
        ),
        Tool(
            name="find_symbol_references",
            description=(
                "Find all places where a symbol is USED/REFERENCED in the codebase. "
                "Returns file paths and line numbers for each usage.\n\n"
                "This searches for actual code references, not the definition. "
                "Use this to see where a function is called, a class is instantiated, "
                "a method is invoked, or a variable is accessed.\n\n"
                "**Returns:** File paths and line numbers showing code context for each reference.\n\n"
                "**Examples:**\n"
                "- Find all calls to the ProcessOrder function\n"
                "- See where CustomerService class is instantiated\n"
                "- Find all references to API_KEY variable\n"
                "- Show me everywhere HandleRequest is called\n\n"
                "**Tips:**\n"
                "- Use repo_filter to search specific repositories\n"
                "- Use file_filter to narrow down to specific files or directories\n"
                "- Add lang:csharp (or other language) to filter by programming language\n\n"
                "**Note:** To find where a symbol is DEFINED, use find_symbol_definition instead."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol_name": {
                        "type": "string",
                        "description": "Name of the symbol to find references for"
                    },
                    "repo_filter": {
                        "type": "string",
                        "description": "Optional: Filter by repository (e.g., 'repo:owner/name')"
                    },
                    "file_filter": {
                        "type": "string",
                        "description": "Optional: Filter by file path (e.g., 'file:\\.cs$' for C# files)"
                    },
                    "lang_filter": {
                        "type": "string",
                        "description": "Optional: Filter by language (e.g., 'csharp', 'python', 'javascript')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)",
                        "default": 20
                    }
                },
                "required": ["symbol_name"]
            }
        ),
        Tool(
            name="search_sourcegraph",
            description=(
                "General code search across your SourceGraph instance. "
                "Use this for text-based searches, finding patterns, or when you need to search "
                "for more than just symbol definitions.\n\n"
                "Supports full SourceGraph query syntax including:\n"
                "- `repo:owner/name` - Filter by repository\n"
                "- `file:pattern` - Filter by file path\n"
                "- `lang:language` - Filter by programming language\n"
                "- `case:yes` - Case-sensitive search\n"
                "- Regular expressions and literals\n\n"
                "**Examples:**\n"
                "- 'PlaceOrder lang:csharp' - Find PlaceOrder in C# files\n"
                "- 'repo:myorg/myrepo TODO' - Find TODOs in a specific repo\n"
                "- 'file:\\.py$ import pandas' - Find pandas imports in Python files\n"
                "- 'error handling lang:java' - Search for error handling in Java\n\n"
                "**Note:** For finding symbol definitions or references specifically, "
                "use find_symbol_definition or find_symbol_references for faster, more accurate results."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query using SourceGraph syntax"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_sourcegraph_regex",
            description=(
                "Search code using regular expressions. "
                "Automatically sets patternType to 'regexp' for regex queries. "
                "Use this for complex pattern matching.\n\n"
                "**Examples:**\n"
                "- 'class \\w+Service' - Find all service classes\n"
                "- 'def (get|set)_\\w+' - Find getter/setter methods\n"
                "- 'TODO|FIXME|HACK' - Find code comments\n"
                "- 'function \\w+\\(.*\\) {' - Find function declarations\n\n"
                "**Tips:**\n"
                "- Use filters parameter for additional constraints\n"
                "- Combine with repo:, file:, and lang: filters\n"
                "- Remember to escape backslashes in regex patterns"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regular expression pattern to search for"
                    },
                    "filters": {
                        "type": "string",
                        "description": "Additional filters (e.g., 'repo:owner/name lang:python')",
                        "default": ""
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["pattern"]
            }
        ),
        Tool(
            name="get_sourcegraph_config",
            description=(
                "Get current SourceGraph MCP server configuration. "
                "Shows the configured URL and whether an access token is set. "
                "Useful for debugging connection issues."
            ),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool execution."""
    
    if name == "find_symbol_definition":
        symbol_name = arguments.get("symbol_name", "")
        symbol_kind = arguments.get("symbol_kind")
        repo_filter = arguments.get("repo_filter")
        max_results = arguments.get("max_results", 10)
        
        if not symbol_name:
            return [TextContent(
                type="text",
                text="❌ Error: symbol_name parameter is required"
            )]
        
        result = await search_symbols(symbol_name, symbol_kind, repo_filter, max_results)
        formatted = format_symbol_results(result)
        
        return [TextContent(type="text", text=formatted)]
    
    elif name == "find_symbol_references":
        symbol_name = arguments.get("symbol_name", "")
        repo_filter = arguments.get("repo_filter")
        file_filter = arguments.get("file_filter")
        lang_filter = arguments.get("lang_filter")
        max_results = arguments.get("max_results", 20)
        
        if not symbol_name:
            return [TextContent(
                type="text",
                text="❌ Error: symbol_name parameter is required"
            )]
        
        # Build query for finding references
        query_parts = [symbol_name]
        
        if repo_filter:
            query_parts.append(repo_filter)
        if file_filter:
            query_parts.append(f"file:{file_filter}")
        if lang_filter:
            query_parts.append(f"lang:{lang_filter}")
        
        query = " ".join(query_parts)
        
        result = await search_code(query, pattern_type="literal", max_results=max_results)
        formatted = format_code_results(result)
        
        return [TextContent(type="text", text=formatted)]
    
    elif name == "search_sourcegraph":
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)
        
        if not query:
            return [TextContent(
                type="text",
                text="❌ Error: Query parameter is required"
            )]
        
        result = await search_code(query, pattern_type="literal", max_results=max_results)
        formatted = format_code_results(result)
        
        return [TextContent(type="text", text=formatted)]
    
    elif name == "search_sourcegraph_regex":
        pattern = arguments.get("pattern", "")
        filters = arguments.get("filters", "")
        max_results = arguments.get("max_results", 10)
        
        if not pattern:
            return [TextContent(
                type="text",
                text="❌ Error: Pattern parameter is required"
            )]
        
        # Construct regex query
        query = f"{filters} {pattern}".strip()
        
        result = await search_code(query, pattern_type="regexp", max_results=max_results)
        formatted = format_code_results(result)
        
        return [TextContent(type="text", text=formatted)]
    
    elif name == "get_sourcegraph_config":
        config_info = {
            "sourcegraph_url": CONFIG["sourcegraph_url"],
            "access_token_set": bool(CONFIG["access_token"]),
            "timeout": CONFIG["timeout"]
        }
        
        output = "# SourceGraph MCP Configuration\n\n"
        output += f"**URL:** `{config_info['sourcegraph_url']}`\n"
        output += f"**Access Token:** {'✓ Configured' if config_info['access_token_set'] else '✗ Not set'}\n"
        output += f"**Timeout:** {config_info['timeout']}s\n"
        
        if not config_info['access_token_set']:
            output += "\n⚠️ **Warning:** No access token configured.\n"
            output += "Set SOURCEGRAPH_TOKEN environment variable or add to config.json"
        
        return [TextContent(type="text", text=output)]
    
    else:
        return [TextContent(
            type="text",
            text=f"❌ Unknown tool: {name}"
        )]


async def main(args: Optional[argparse.Namespace] = None):
    """Run the MCP server."""
    global CONFIG
    CONFIG = load_config(args)
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def cli_entry():
    """Synchronous entry point for package installation."""
    parser = argparse.ArgumentParser(
        description="SourceGraph MCP Server - Search code via SourceGraph's GraphQL API"
    )
    parser.add_argument(
        "--url",
        help="SourceGraph instance URL (default: http://localhost:3370)"
    )
    parser.add_argument(
        "--token",
        help="SourceGraph access token"
    )
    parser.add_argument(
        "--config",
        help="Path to config.json file"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="Request timeout in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    asyncio.run(main(args))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SourceGraph MCP Server - Search code via SourceGraph's GraphQL API"
    )
    parser.add_argument(
        "--url",
        help="SourceGraph instance URL (default: http://localhost:3370)"
    )
    parser.add_argument(
        "--token",
        help="SourceGraph access token"
    )
    parser.add_argument(
        "--config",
        help="Path to config.json file"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="Request timeout in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    asyncio.run(main(args))
