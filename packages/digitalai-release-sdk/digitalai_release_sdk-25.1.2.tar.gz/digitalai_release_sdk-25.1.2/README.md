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

### Version 25.1.2

#### 🛠️ Enhancements
- **Added support** for the `lookup` functionality in task fields, allowing dynamic population of field values based on runtime data or external sources.

### Version 25.1.1

#### ✨ New Features
- **Introduced** a ready-to-use `dai_logger` object to simplify logging across all tasks

#### 🔧 Changes & Improvements
- **Refactored** the client creation process for the cluster

### Version 25.1.0

#### 🚨 Breaking Changes
- **Removed `get_default_api_client()`** from the `BaseTask` class.
- **Removed `digitalai.release.v1` package**, which contained OpenAPI-generated stubs for Release API functions.
  - These stubs were difficult to use and had several non-functioning methods.
  - A new, simplified API client replaces them for better usability and reliability.
  - The removed package will be released as a separate library in the future.

#### ✨ New Features
- **Introduced `get_release_api_client()`** in the `BaseTask` class as a replacement for `get_default_api_client()`.
- **New `ReleaseAPIClient` class** for simplified API interactions.
  - Functions in `ReleaseAPIClient` take an **endpoint URL** and **body as a dictionary**, making API calls more intuitive and easier to work with.

#### 🔧 Changes & Improvements
- **Updated minimum Python version requirement to 3.8**.
- **Updated dependency versions** to enhance compatibility and security.
- **Bundled `requests` library** to ensure seamless HTTP request handling.

---
## 🔁 Upgrading from `digitalai-release-sdk` 24.1.0 or 23.3.0 to 25.1.0

With the release of **digitalai-release-sdk 25.1.0**, the API stubs have been separated into a standalone package. 

👉 [`digitalai-release-api-stubs`](https://pypi.org/project/digitalai-release-api-stubs/)

To upgrade your project, follow these steps:

### Step 1: Install the API Stubs Package

You must explicitly install the new API stubs package:

```bash
pip install digitalai-release-api-stubs==25.1.0
```

Or, add it to your `requirements.txt` as needed.

---

### Step 2: Update Your Code

In previous versions, API clients were created like this:

```python
# Old code (pre-25.1.0)
configuration_api = ConfigurationApi(self.get_default_api_client())
```

In version **25.1.0**, use the following approach:

```python
# New code (25.1.0)

# Create a configuration object
configuration = Configuration(
    host=self.get_release_server_url(),
    username=self.get_task_user().username,
    password=self.get_task_user().password
)

# Instantiate the API client using the configuration
apiclient = ApiClient(configuration)

# Create the Configuration API client
configuration_api = ConfigurationApi(apiclient)
```

This pattern should be used for all API clients, such as `TemplateApi`, `TaskApi`, etc.

---

## 🔗 Related Resources

- 🧪 **Python Template Project**: [release-integration-template-python](https://github.com/digital-ai/release-integration-template-python)  
  A starting point for building custom integrations using Digital.ai Release and Python.

- 📘 **Official Documentation**: [Digital.ai Release Python SDK Docs](https://docs.digital.ai/release/docs/category/python-sdk)  
  Comprehensive guide to using the Python SDK and building custom tasks.

- 📦 **Digital.ai Release Python SDK**: [digitalai-release-sdk on PyPI](https://pypi.org/project/digitalai-release-sdk/)  
  The official SDK package for integrating with Digital.ai Release.


