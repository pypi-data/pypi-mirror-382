# Juniper Pathfinder Model Context Protocol Server

This MCP Server allows a model to work with the data behind
the tools in the Juniper Pathfinder site (https://apps.juniper.net).

It contains tools in three namespaces:

- `hct_`: Hardware Compatibility Tool
- `feature_explorer_`: Feature Explorer
- `cli_explorer_`: CLI Explorer

## Running the MCP Server

This MCP server is actually a composition of three MCP servers:

- `jnpr_pathfinder_mcp.server.hct`
- `jnpr_pathfinder_mcp.server.feature_explorer`
- `jnpr_pathfinder_mcp.server.cli_explorer`

all built using [FastMCP](https://gofastmcp.com/getting-started/quickstart#run-the-server)
and can run over stdio or streamable http.

### Running the Full Server

To run all three components with a single interface, use 
[`uv`](https://docs.astral.sh/uv/getting-started/installation/)
for the simplest approach:

```bash
$ uv run jnpr_pathfinder_mcp --transport http --port 8888
```

This will expose tools for all supported pathfinder apps.

### Running a Single Server

To run all three components with a single interface, use 
[`uv`](https://docs.astral.sh/uv/getting-started/installation/)
for the simplest approach:

```bash
$ uv run fastmcp jnpr_pathfinder_mcp.server.hct:mcp --transport http --port 8888
```

This will expose tools for the Hardware Compatibility Tool only.

## Running in Docker

It may be even easier to run the MCP server using Docker:

```bash
$ docker run --rm -i -p 8888:8888 cbinckly/jnpr-pathfinder-mcp:latest
```

## Configuring a Client
