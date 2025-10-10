# MAQ Software RAI SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MAQ Software RAI SDK is a Python client library for Azure Functions API that provides RAI (Responsible AI) operations including prompt review and testcase generation.

## Installation

```bash
pip install rai-temp-sdk
```

## Quick Start

```python
from rai_agent_functions_api import RaiAgentFunctionsAPIClient

# Initialize the client
client = RaiAgentFunctionsAPIClient(
    endpoint="<YOUR_AZURE_FUNCTION_ENDPOINT>",
    credential="<YOUR_CREDENTIAL>"
)

# Use the client for RAI operations
# (Add specific usage examples based on your API)
```

## Features

- **Prompt Review**: Analyze and validate AI prompts for responsible AI compliance
- **Testcase Generation**: Generate comprehensive test cases for AI models
- **Azure Integration**: Seamless integration with Azure Functions
- **Async Support**: Full async/await support for better performance
- **Type Safety**: Complete type annotations for better development experience

## Requirements

- Python 3.8 or higher
- Azure Core libraries
- Active Azure Functions endpoint

## Documentation

For detailed documentation, examples, and API reference, please visit our [GitHub repository](https://github.com/DivyanshuMaq/rai-temp-sdk).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see our contribution guidelines in the repository.

## Support

For support and questions:
- Create an issue in our [GitHub repository](https://github.com/DivyanshuMaq/rai-temp-sdk/issues)
- Contact MAQ Software: divyanshur@maqsoftware.com

---

**About MAQ Software**

MAQ Software is a leading provider of business intelligence, data management, and advanced analytics solutions. Learn more at [www.maqsoftware.com](https://www.maqsoftware.com).