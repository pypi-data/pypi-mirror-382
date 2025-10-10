# ADK MongoDB Session Service

[![PyPI version](https://badge.fury.io/py/adk-mongodb-session.svg)](https://badge.fury.io/py/adk-mongodb-session)
[![Python Package CI](https://github.com/SergeySetti/adk-mongodb-session/actions/workflows/python-package.yml/badge.svg)](https://github.com/SergeySetti/adk-mongodb-session/actions/workflows/python-package.yml)

A session management library for the Google ADK framework that uses MongoDB as a backend.

This package provides a `MongodbSessionService` that implements the `google.adk.sessions.base_session_service.BaseSessionService` abstract base class. It allows you to store and manage session state in a MongoDB database, fully replicating the three-tiered state management (`app`, `user`, and `session`) found in the core ADK session services.

## Features

-   **MongoDB Backend**: Persist session and state data in a MongoDB database.
-   **Tiered State Management**: Automatically manage state at the application, user, and session levels.
-   **ADK Integration**: Implements the `BaseSessionService` for seamless integration with the Google ADK framework.
-   **Async Support**: All service methods are asynchronous.

## Installation

You can install the package from PyPI:

```bash
pip install adk-mongodb-session
```

For development, clone the repository and install it in editable mode with the testing dependencies:

```bash
git clone https://github.com/your-username/adk-mongodb-session.git
cd adk-mongodb-session
pip install -e ".[test]"
```

## Usage

First, instantiate the `MongodbSessionService` with your MongoDB connection details.

```python
import asyncio
from adk_mongodb_session.mongodb.sessions import MongodbSessionService

# Initialize the service
session_service = MongodbSessionService(
    db_url="mongodb://localhost:27017/",
    database="my_adk_agent_db",
    collection_prefix="sessions"  # This will create sessions_sessions, sessions_app_states, etc.
)
# ... and then use it in your async context

example_session = await session_service.create_session(
    app_name="my_app",
    user_id="example_user",
    state={"initial_key": "initial_value"} # State can be initialized
)
```

## Running Tests

To run the tests, first install the testing dependencies:

```bash
pip install -e ".[test]"
```

Then, run the tests using `unittest`:

```bash
python -m unittest discover tests
```

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to report bugs, suggest enhancements, and submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
