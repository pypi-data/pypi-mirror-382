# SAT Utilities

This repository contains a collection of shared utility functions.

- Slack: A class to upload files to our Slack workspace
- SATLogger: A standard logger for SAT projects

## Installation

```shell
# Install the package from private PyPI (CLI)
$ pip install sat-utils
```

## Usage

### Slack

```python
from sat.slack import Slack

message = Slack(token="abc123-8dkhnna-97hasdj-xyz")
message.upload_file(channel="support", file_path="C:/files", file_name="support.pdf", file_type="", title="Support manual v3.2", initial_comment="Woot!")
```

### SATLogger

```python
from sat.logs import SATLogger
logger = SATLogger(__name__)

...
logger.info("Hello, world!")
```

### Gravity Forms

Three environment variables are required to authenticate with the Gravity Forms API.

- GRAVITY_FORMS_CONSUMER_KEY
- GRAVITY_FORMS_CONSUMER_SECRET
- GRAVITY_FORMS_BASE_URL

Alternatively, these values can be passed into the GravityForms initialization as parameters.

```python
from sat.gravity_forms import GravityForms


gravity = GravityForms()
cards_requested = gravity.get("/forms/3/entries")
```

## Development

### Setup

Ensure you are in a virtual environment with Python 3.9.6 or higher.

```shell
> make setup
```

### Add dependencies

#### Updating Requirements

This project uses `pip-tools` to manage requirements. To update the requirements add your requirement
to the `pyproject.toml` file.

For dependencies required to run the app in production, add them to the `pyproject.toml` file under the `[project]` section.

```toml
[project]
...
dependencies = [
    "fastapi>=0.95.1, <1.0.0",
    "pyjwt>=2.6.0, <3.0.0",
    "...",
    "<YOUR NEW REQUIREMENT HERE>",
    "...",
]
```

For developer dependencies required or nice to have for development, add them to the `pyproject.toml` file under the `[project.optional-dependencies]` section.

```toml
[project.optional-dependencies]
dev = [
    "pytest>=6.2.5, <7.0.0",
    "...",
    "<YOUR NEW DEV REQUIREMENT HERE>",
    "...",
]
```

When you have add the dependency run:

```shell
> make update-requirements
```

## Build and Publish

Update the version in `pyproject.toml` before building.

### Build

```shell
> flit build
```

### Publish

As long as your PyPI credentials are set up correctly, you can publish to PyPI with the following command:

```shell
> flit publish
```
