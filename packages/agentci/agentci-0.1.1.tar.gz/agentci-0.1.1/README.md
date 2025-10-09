# AgentCI CLI

Command-line interface for interacting with AgentCI.

## Installation

```bash
uv pip add agentci
```

## Usage

```bash
agentci <command> [options]
```

### Commands

#### `validate`

Validate all AgentCI evaluation configurations in a directory:

```bash
# Validate configs in current directory
agentci validate

# Validate configs in specific directory
agentci validate /path/to/repository
```

By default, AgentCI looks for configurations in `.agentci/evals/`. You can customize this location using the `AGENTCI_CLIENT_BASE_PATH` environment variable:

```bash
AGENTCI_CLIENT_BASE_PATH="custom/path" agentci validate
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- Website: <https://agent-ci.com>
- Issues: <https://github.com/Agent-CI/cli/issues>
