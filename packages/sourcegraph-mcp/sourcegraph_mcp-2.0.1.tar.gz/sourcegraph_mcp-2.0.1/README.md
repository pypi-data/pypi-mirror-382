# sourcegraph-mcp

Model Context Protocol server for searching code via SourceGraph's GraphQL API. Leverages SourceGraph's indexed symbol search for fast, precise code navigation. Works with both local and cloud SourceGraph instances.

## Why Use This?

Search your entire codebase instantly using SourceGraph's indexed search:
- **Lightning Fast**: Symbol lookups in <100ms using indexed search
- **Precise**: Find exact definitions vs references/usages separately
- **Cost-effective**: ~400 tokens per search vs 50k+ tokens loading files
- **Comprehensive**: Search across all repos, branches, and languages

## Key Features

### 🎯 Symbol Search (Indexed)
- **Find Definitions**: Locate where functions, classes, methods are declared
- **Find References**: See all places where a symbol is used
- **Fast Lookups**: Uses SourceGraph's pre-built symbol index
- **Returns**: Exact file path, line number, and column position

### 🔍 Code Search
- **Text Search**: Find any text pattern across your codebase
- **Regex Search**: Complex pattern matching with full regex support
- **Filters**: By repository, file path, language, and more

## Installation

### Quick Start (with pipx - Recommended)

```bash
pipx install sourcegraph-mcp
```

This installs the `sourcegraph-mcp` command globally and handles all dependencies automatically.

### Verify Installation

```bash
which sourcegraph-mcp
# Should show: /Users/yourusername/.local/bin/sourcegraph-mcp
```

## Configuration

**IMPORTANT:** Replace the URL and token with your actual SourceGraph instance details.

### Option 1: Environment Variables (Recommended)

```bash
export SOURCEGRAPH_URL=http://localhost:3370
export SOURCEGRAPH_TOKEN=sgp_your_token_here
```

### Option 2: Config File

Create `config.json`:

```json
{
  "sourcegraph_url": "http://localhost:3370",
  "access_token": "sgp_your_token_here",
  "timeout": 30
}
```

### Option 3: CLI Arguments

```bash
sourcegraph-mcp --url http://localhost:3370 --token sgp_your_token_here
```

## Setup with MCP Clients

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

**IMPORTANT:** Replace the URL and token with your actual SourceGraph instance details.

```json
{
  "mcpServers": {
    "sourcegraph": {
      "command": "sourcegraph-mcp",
      "env": {
        "SOURCEGRAPH_URL": "http://localhost:3370",
        "SOURCEGRAPH_TOKEN": "sgp_your_token_here"
      }
    }
  }
}
```

### Claude Code

**Important:** First install with `pipx install sourcegraph-mcp`, then configure.

**IMPORTANT:** Replace the URL and token with your actual SourceGraph instance details.

#### Option 1: User-Wide (Recommended - No Permission Prompts)

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "sourcegraph": {
      "command": "sourcegraph-mcp",
      "env": {
        "SOURCEGRAPH_URL": "http://localhost:3370",
        "SOURCEGRAPH_TOKEN": "sgp_your_token_here"
      }
    }
  },
  "permissions": {
    "allow": [
      "mcp__sourcegraph__*"
    ]
  }
}
```

**Note:** If `sourcegraph-mcp` is not in your PATH, use the full path:
```json
"command": "/Users/yourusername/.local/bin/sourcegraph-mcp"
```

Restart Claude Code and verify with `/mcp` command.

#### Option 2: Project-Specific

Create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "sourcegraph": {
      "command": "sourcegraph-mcp",
      "env": {
        "SOURCEGRAPH_URL": "http://localhost:3370",
        "SOURCEGRAPH_TOKEN": "sgp_your_token_here"
      }
    }
  }
}
```

Then add permissions to `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "mcp__sourcegraph__find_symbol_definition",
      "mcp__sourcegraph__find_symbol_references",
      "mcp__sourcegraph__search_sourcegraph",
      "mcp__sourcegraph__search_sourcegraph_regex",
      "mcp__sourcegraph__get_sourcegraph_config"
    ]
  },
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["sourcegraph"]
}
```

**Important:** Permission format must use `mcp__servername__toolname` with double underscores, not colons.

**Note:** The permissions section above is specific to Claude Code. Other MCP clients may not require explicit permissions or may use different permission systems.

### Other MCP Clients (Cursor, Windsurf, Zed, Cline, etc.)

Most MCP clients use similar configuration. The general pattern is:

1. **Install:** `pipx install sourcegraph-mcp`
2. **Add to your client's MCP config file:**

```json
{
  "mcpServers": {
    "sourcegraph": {
      "command": "sourcegraph-mcp",  // or full path: ~/.local/bin/sourcegraph-mcp
      "env": {
        "SOURCEGRAPH_URL": "http://localhost:3370",
        "SOURCEGRAPH_TOKEN": "sgp_your_token_here"
      }
    }
  }
}
```

**Refer to your client's documentation for the config file location.**

**Community contributions welcome!** If you've successfully set this up with another client, please submit a PR with instructions.

## Usage

Once configured, your AI assistant can leverage SourceGraph's indexed search:

### Symbol Definitions (Fast Lookups)
```
"Find where the ProcessOrder function is defined"
"Where is the CustomerService class declared?"
"Show me the definition of HandleRequest method"
"Locate the API_KEY constant definition"
```

### Symbol References (Find Usages)
```
"Find all calls to ProcessOrder"
"Where is CustomerService used?"
"Show me all references to API_KEY"
"Find everywhere HandleRequest is called"
```

### General Code Search
```
"Search for authentication code"
"Find TODO comments in C# files"
"Show error handling patterns in the api directory"
```

## Available Tools

### 1. `find_symbol_definition`
Find where symbols are **defined** (declarations). Returns exact file path and line number.

**Best for:**
- "Where is X defined?"
- "Go to definition of Y"
- "Show me the declaration of Z"

**Returns:**
- File path
- Line number
- Column position
- Symbol kind (function, class, method, etc.)

### 2. `find_symbol_references`
Find where symbols are **used** (references/calls). Returns all usage locations.

**Best for:**
- "Where is X called?"
- "Find all uses of Y"
- "Show me references to Z"

**Returns:**
- File paths and line numbers for each usage
- Code context around each reference

### 3. `search_sourcegraph`
General text-based code search with full query syntax.

**Query syntax:**
- `repo:owner/name` - Filter by repository
- `file:pattern` - Filter by file path
- `lang:language` - Filter by programming language
- `case:yes` - Case-sensitive search

### 4. `search_sourcegraph_regex`
Search using regular expressions for complex pattern matching.

### 5. `get_sourcegraph_config`
View current configuration (useful for debugging).

## Performance Advantages

### Symbol Search (Indexed)
- ✅ **<100ms**: Instant lookups using pre-built index
- ✅ **Precise**: Distinguishes definitions from references
- ✅ **Scalable**: Works across millions of lines of code

### Text Search
- ✅ **Fast**: Leverages SourceGraph's Zoekt indexing
- ✅ **Flexible**: Full regex and filter support
- ✅ **Comprehensive**: Searches across all content

### vs Loading Files into Context
- **400 tokens** per search vs **50k+ tokens** loading files
- **Instant results** vs waiting for file loads
- **Pinpoint accuracy** vs reading through entire files

## Getting a SourceGraph Token

1. Navigate to your SourceGraph instance
2. Go to Settings → Access tokens
3. Click "Generate new token"
4. Copy the token (starts with `sgp_`)

## Local Development

```bash
# Clone and install
git clone https://github.com/dalebrubaker/sourcegraph-mcp
cd sourcegraph-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Test configuration
python test_connection.py

# Run with config file
python server.py

# Run with CLI args
python server.py --url http://localhost:3370 --token sgp_your_token_here
```

## Troubleshooting

### "Could not connect to MCP server"
- Verify SourceGraph is running and accessible
- Check URL format (include http:// or https://)
- Test token: `curl -H "Authorization: token sgp_..." http://your-url/.api/graphql`
- Verify installation: `which sourcegraph-mcp` should show the installed path
- If not in PATH, use full path in config: `/Users/yourusername/.local/bin/sourcegraph-mcp`

### "Command not found"
- Make sure you installed with `pipx install sourcegraph-mcp`
- Check if `~/.local/bin` is in your PATH: `echo $PATH | grep .local/bin`
- Try using the full path in your config instead of just `sourcegraph-mcp`

### "No symbols found"
- Symbol search requires SourceGraph's symbol indexing to be enabled
- Check if your repositories have been indexed: Settings → Repositories → Indexing
- Symbol indexing may take time for large repos
- Try general code search as a fallback

### Testing Your Setup
```bash
# Test connection and both search types
python test_connection.py
```

## Example Queries

### Finding Definitions
```
User: "Find where the LowerBound method is defined with file name and line number"

MCP Response:
## 1. `LowerBound` (method)
**File:** `src/Collections/SortedList.cs`
**Line:** 142
**Position:** Line 142, Column 8
**Repository:** `myorg/core-lib`
```

### Finding References
```
User: "Show me all places where ProcessOrder is called"

MCP Response:
## 1. `OrderController.cs`
**Repository:** `myorg/api-service`
**URL:** https://sourcegraph.local/...

**Matches:**
- **Line 45:** `var result = await ProcessOrder(orderId);`
- **Line 87:** `return ProcessOrder(order);`

## 2. `OrderProcessor.cs`
...
```

## License

MIT

## Contributing

PRs welcome! Please open an issue first to discuss significant changes.

## Roadmap

- [ ] Support for batch symbol lookups
- [ ] Cached symbol results for faster repeated queries
- [ ] Structural search support
- [ ] Commit and diff search tools
- [ ] Multi-repo symbol search optimization
