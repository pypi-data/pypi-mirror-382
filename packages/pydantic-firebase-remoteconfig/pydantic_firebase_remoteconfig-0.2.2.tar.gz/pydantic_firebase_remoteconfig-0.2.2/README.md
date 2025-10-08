# Firebase Remote config validator for Pydantic

[![PyPI - Version](https://img.shields.io/pypi/v/pydantic-firebase-remoteconfig)](https://pypi.org/project/pydantic-firebase-remoteconfig/) [![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)

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

### With custom model configuration

A custom model configuration dict is also available.

#### Key prefix

```python
from pydantic_firebase_remoteconfig import RemoteConfigConfigDict


class MyRemoteConfigModel(BaseRemoteConfigModel):
    model_config = RemoteConfigConfigDict(
        # This would evaluate remote configuration
        # variable `myprefix_foo`.
        rc_prefix="myprefix_",
    )
    foo: str
```

#### Parameter group selection


```python
from pydantic_firebase_remoteconfig import RemoteConfigConfigDict


class MyRemoteConfigModel(BaseRemoteConfigModel):
    model_config = RemoteConfigConfigDict(
        # This would evaluate remote configuration
        # variable `foo` under group `my_group`.
        rc_group="my_group",
    )
    foo: str
```

#### Complex model using nested delimiter

Using the same pattern than [pydantic_settings](), nested
configuration can be evaluated, based on either:

- A submodel is designed as a JSON parameter on RemoteConfig.
- A submodel is designed as combinaison of flat value with delimiter.

```python
from pydantic import BaseModel
from pydantic_firebase_remoteconfig import RemoteConfigConfigDict


class MyNestedConfig(BaseModel):
    foo: str


class MyRemoteConfigModel(BaseRemoteConfigModel):
    model_config = RemoteConfigConfigDict(
        # This would evaluate remote configuration
        # variable `nested_config__foo`.
        rc_nested_delimiter="__",
    )

    nested_config: MyNestedConfig
```
