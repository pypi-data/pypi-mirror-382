# Plain Flags Python SDK

This module facilitates your software's connection to the Plain Flags feature flag system.

## Requirements

You must host an installation of the Plain Flags feature flag back end services.

More about Plain Flags at [plainflags.dev](https://plainflags.dev)

The Plain Flags back end must run in an environment where your software can make http requests.

## Installation

```
pip install plain-flags-sdk
```

## Usage

Import the Plain Flags SDK package:

```python
from plainflags import PlainFlags, PlainFlagsConfig
```

Create and configure an object of type PlainFlags at the start of your software's execution:

```python
    config = PlainFlagsConfig(
        service_url="http://my-plainflags-states.dev",
        api_key="mySharedSecret",
        timeout_ms=10000,
        poll_interval_ms=30000)  # Poll every 30 seconds, or set to 0 to disable polling

    feature_flags = PlainFlags(config,
                              infoFunc=logging.info,  # Optional: provide custom logging functions
                              errorFunc=logging.error)
```

Initialize the object. The init() method is a coroutine:

```python
    await feature_flags.init()
```

When your application is shutting down, stop the background polling if enabled:

```python
    await feature_flags.stop_updates()
```

Any feature code you wish to enable and disable with feature flags will be within conditions like this:

```python
if feature_flags.is_on("My feature"):
    # Your feature code here
    pass
```

You can provide a default value to return if the flag is not found:

```python
if feature_flags.is_on("My feature", default=False):
    # Your feature code here
    pass
```

If your features are constrained to subsets of your users, you must specify which user is currently using the software (and other context you constrain your feature for, if applicable).

```python
if feature_flags.is_on("My Feature", default=False, context={
    "userId": current_user().id,
    "countryCode": current_country_code(),
}):
    # Your feature code here
    pass
```

The keys **userId** and **countryCode** must match the constraint keys you created in the dashboard

## Source code

[github link](https://github.com/andreileonte1981/plain-flags/tree/main/sdk/python)
