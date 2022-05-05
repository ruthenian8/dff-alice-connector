
# Dff Alice Connector

[Df Alice Connector](https://github.com/ruthenian8/dff-alice-connector) is an extension to the [Dialogflow Engine](https://github.com/deepmipt/dialog_flow_engine), a minimalistic open-source engine for conversational services.

[Df Alice Connector](https://github.com/ruthenian8/dff-alice-connector) allows you to program FSM-based skills for Yandex's Alice using df_engine. Using this add-on, you can take advantage of the features Alice offers, like the recognition of entities and intents, and incorporate them in your script as conditions for FSM transitions.

<!-- uncomment one of these to add badges to your project description -->
<!-- [![Documentation Status](https://dff-alice-connector.readthedocs.io/en/stable/?badge=stable)](https://readthedocs.org/projects/dff-alice-connector/badge/?version=stable) -->
<!-- [![Coverage Status](https://coveralls.io/repos/github/ruthenian8/dff-alice-connector/badge.svg?branch=main)](https://coveralls.io/github/ruthenian8/dff-alice-connector?branch=main) -->
[![Codestyle](https://github.com/ruthenian8/dff-alice-connector/workflows/codestyle/badge.svg)](https://github.com/ruthenian8/dff-alice-connector)
[![Tests](https://github.com/ruthenian8/dff-alice-connector/workflows/test_coverage/badge.svg)](https://github.com/ruthenian8/dff-alice-connector)
[![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ruthenian8/dff-alice-connector/blob/main/LICENSE)
![Python 3.6, 3.7, 3.8, 3.9](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-green.svg)
<!-- [![PyPI](https://img.shields.io/pypi/v/dff-alice-connector)](https://pypi.org/project/dff-alice-connector/)
[![Downloads](https://pepy.tech/badge/dff-alice-connector)](https://pepy.tech/project/dff-alice-connector) -->

# Quick Start
## Installation
```bash
pip install df-alice-connector
```

## Conditions

### Entities & intents
```python
import df_alice_connector as AliceConn
from df_alice_connector.request import GeoEntity, FioEntity, DateTimeEntity, YandexDefaultIntents, Intent

# Use this method to filter out requests that include one or several entities of a certain type.
AliceConn.cnd.has_geo(entities=[GeoEntity(...), GeoEntity(...)], full_match=...)
AliceConn.cnd.has_fio(entities=[FioEntity(...), FioEntity(...)], full_match=...)
AliceConn.cnd.has_datetime(entities=[DatetimeEntity(...), DatetimeEntity(...)], full_match=...)
AliceConn.cnd.has_number(enities=[1.0, 1.2])

# Use `has_intents` to filter requests that include a certain standard yandex intent.
AliceConn.cnd.has_intents(intents=[YandexDefaultIntents.HELP, YandexDefaultIntents.REPEAT])

intent: Intent
AliceConn.cnd.has_intents(func = lambda intent: intent.slots["some_slot"]["value"] == "y")
```

### Request properties

```python
import df_alice_connector as AliceConn
from df_alice_connector.request import YandexRequestType

# Use `has_request_type` to filter requests depending on the type.
AliceConn.cnd.has_request_type(types=[YandexRequestType.SIMPLEUTTERANCE, ...])

# Use `has_payload` to process requests sent on button press. 
AliceConn.cnd.has_payload(func = lambda x: x["key"] == "value", payload={"key": "value"})
```

### Other conditions

```python
import df_alice_connector as AliceConn
from df_alice_connector.request import YandexRequestModel

# Use `has_tokens` to filter requests depending on whether or not they include `tokens` or `banned_tokens`.
AliceConn.cnd.has_tokens(tokens=["token_1", ...], banned_tokens=["token_3", ...])

# Use the `apply` method to compare the request against any boolean function.
request: YandexRequestModel
AliceConn.cnd.apply(func=lambda request: request.command.startswith("включи свет"))
```

To get more advanced examples, take a look at [examples](https://github.com/ruthenian8/dff-alice-connector/tree/main/examples) on GitHub.

# Contributing to the Dialog Flow Engine

Please refer to [CONTRIBUTING.md](https://github.com/deepmipt/dialog_flow_engine/blob/dev/CONTRIBUTING.md).