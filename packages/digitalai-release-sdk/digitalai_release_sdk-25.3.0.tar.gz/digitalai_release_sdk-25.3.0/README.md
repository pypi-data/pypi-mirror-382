# Digital.ai Release Python SDK

The **Digital.ai Release Python SDK** (`digitalai-release-sdk`) provides a set of tools for developers to create container-based integration with Digital.ai Release. It simplifies integration creation by offering built-in functions to interact with the execution environment.

## Features
- Define custom tasks using the `BaseTask` abstract class.
- Easily manage input and output properties.
- Interact with the Digital.ai Release environment seamlessly.
- Simplified API client for efficient communication with Release API.


## Installation
Install the SDK using `pip`:

```sh
pip install digitalai-release-sdk
```

## Getting Started

### Example Task: `hello.py`

The following example demonstrates how to create a simple task using the SDK:

```python
from digitalai.release.integration import BaseTask

class Hello(BaseTask):
    
    def execute(self) -> None:
        # Get the name from the input
        name = self.input_properties.get('yourName')
        if not name:
            raise ValueError("The 'yourName' field cannot be empty")

        # Create greeting message
        greeting = f"Hello {name}"

        # Add greeting to the task's comment section in the UI
        self.add_comment(greeting)

        # Store greeting as an output property
        self.set_output_property('greeting', greeting)
```

## Changelog

### Version 25.3.0

#### 🛠️ Enhancements

- **Added support** for the `lookup` functionality in task fields, allowing dynamic population of field values based on runtime data or external sources.

---

## 🔗 Related Resources

- 🧪 **Python Template Project**: [release-integration-template-python](https://github.com/digital-ai/release-integration-template-python)  
  A starting point for building custom integrations using Digital.ai Release and Python.

- 📘 **Official Documentation**: [Digital.ai Release Python SDK Docs](https://docs.digital.ai/release/docs/category/python-sdk)  
  Comprehensive guide to using the Python SDK and building custom tasks.

- 📦 **Digital.ai Release Python SDK**: [digitalai-release-sdk on PyPI](https://pypi.org/project/digitalai-release-sdk/)  
  The official SDK package for integrating with Digital.ai Release.


