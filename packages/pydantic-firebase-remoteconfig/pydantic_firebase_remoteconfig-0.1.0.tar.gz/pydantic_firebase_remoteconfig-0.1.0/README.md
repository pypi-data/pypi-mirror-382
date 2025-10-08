# Firebase Remote config validator for Pydantic

A simple Firebase Remote Config binding for Pydantic, using
remote server configuration only.

## Installation

Package is publicly available on PyPi and can be install using any
supported package manager:

```bash
pip install pydantic-firebase-remoteconfig
```

## Usage

You simply need to implement your `BaseRemoteConfigModel` class
and use the appropriate async validation class method. Let's imagine
you have a server remote configuration with a `foo` variable with `bar`
value:

```python
from pydantic_firebase_remoteconfig import BaseRemoteConfigModel


class MyRemoteConfigModel(BaseRemoteConfigModel):
    foo: str


config = await MyRemoteConfigModel.model_validate_remoteconfig()
print(config.foo)
# bar
```
