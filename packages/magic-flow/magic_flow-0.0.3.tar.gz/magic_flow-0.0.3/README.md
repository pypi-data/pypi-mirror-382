# Magic Flow Python SDK

A comprehensive Python SDK for building applications that interact with the Flow blockchain network. This SDK provides a complete set of tools for developers to query, transact, and build on Flow.

[![PyPI](https://img.shields.io/pypi/v/magic-flow.svg)](https://pypi.org/project/magic-flow/)
[![codecov](https://codecov.io/gh/magiclabs/magic-flow-python/branch/master/graph/badge.svg)](https://codecov.io/gh/magiclabs/magic-flow-python)
[![Python](https://img.shields.io/pypi/pyversions/magic-flow.svg)](https://pypi.org/project/magic-flow/)
[![License](https://img.shields.io/pypi/l/magic-flow.svg)](https://pypi.org/project/magic-flow/)

## Features

- 🔗 **Complete Flow Integration** - Full support for Flow blockchain operations
- 🚀 **Async/Await Support** - Modern Python async programming patterns
- 🔐 **Advanced Signing** - Support for complex transaction signing scenarios
- 📊 **Query Capabilities** - Query blocks, accounts, events, and transactions
- 🛠️ **Script Execution** - Execute Cadence scripts on the Flow network
- 🏗️ **Account Management** - Create and manage Flow accounts
- 📝 **Contract Deployment** - Deploy, update, and manage smart contracts
- 🧪 **Emulator Compatible** - Works with Flow Emulator for local development

## Quick Start

### Installation

Requires Python 3.10 or higher.

```bash
pip install magic-flow
```

Or with Poetry:

```bash
poetry add magic-flow
```

### Basic Usage

```python
import asyncio
from magic_flow_python.client import flow_client

async def main():
    async with flow_client(host="127.0.0.1", port=3569) as client:
        # Get the latest block
        block = await client.get_latest_block()
        print(f"Latest block height: {block.height}")

        # Get account information
        account = await client.get_account(address="0x01")
        print(f"Account balance: {account.balance}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

- 📖 **[Complete Guide](https://magiclabs.github.io/magic-flow-python/python_SDK_guide/)** - Comprehensive documentation
- 🔧 **[API Reference](https://magiclabs.github.io/magic-flow-python/api_docs/)** - Detailed API documentation
- 💡 **[Examples](https://magiclabs.github.io/magic-flow-python/examples/)** - Code examples and tutorials

## Development

This SDK is fully compatible with the Flow Emulator and can be used for local development.

### Requirements

- Python 3.10+
- Flow Emulator (for local development)

### Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributors

<a href="https://github.com/magiclabs/magic-flow-python/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=magiclabs/magic-flow-python" />
</a>

Made with [contrib.rocks](https://contrib.rocks).
