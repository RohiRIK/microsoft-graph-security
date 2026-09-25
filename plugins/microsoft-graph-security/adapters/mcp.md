# Other MCP-compatible agents

Use the packaged `mcp.json` or the repository's `.mcp.json` as the MCP server configuration. The command must start the gateway or packaged gateway binary, and the working directory must be chosen so the server can find its own runtime and configuration.

The package intentionally contains no host-specific executable extension. Any agent that supports MCP can use the gateway, while agents with native skills should point them at the canonical `skills/` directory.

Do not add credentials, tenant IDs, or machine-specific absolute paths to a host configuration in version control. Configure tenant selection and authentication locally with the repository's `settings.yaml` rules.
