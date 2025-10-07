# Python Module for API Usage

This guide explains how to use the **official Python module** to interact with the API. It covers **installation, setup, authentication, and using the main modules** such as games, tools, reseller, and user management.

> ⚠️ **Important:** Always verify which endpoints are available in which version. Not all endpoints exist in every version, and some features are only available from v3 and above. Make sure your project uses a supported API version.

## Installation

```bash
pip install ricardoneud-api
```

## Initialization

The client can be initialized with either an **API Key** or a **Secret token**:

```python
from ricardoneud.api.client import RicardoNeudAPI

api = RicardoNeudAPI(
    api_key='your-api-key',  # OR use secret='your-secret'
    version='v4'
)
```

### Changing Version

```python
api.set_version('v4')  # Verify which endpoints are supported in v4
```

## Authentication

### API Key

1. Log in at [Ricardoneud.com](https://auth.ricardoneud.com/login)
2. Go to **Dashboard → API Keys**
3. Click **Create API Key**, configure permissions, and set environment to `Production`.
4. Use the API Key in your client:

```python
api.set_api_key('your-api-key')
```

### Secret Token (Login-based)

Short-lived tokens provide session-based access (valid for 24 hours).

```python
login_response = api.user.login('usernameOrEmail', 'password', True)
print(login_response['secret'])  # Use this token in subsequent requests
```

```python
api = RicardoNeudAPI(secret='your-secret')
```

You can revoke tokens when needed:

```python
api.user.revoke_secret('usernameOrEmail', 'password', 'your-secret')
```

## Core Modules

### Games

```python
server = api.games.minecraft('play.hypixel.net')
fivem_server = api.games.fivem('127.0.0.1', '30120')
```

### Tools

```python
dns = api.tools.dns_check('example.com', 'A')
domain = api.tools.domain_check('google.com')
subdomains = api.tools.subdomain_finder('example.com')
geoip = api.tools.geo_ip('8.8.8.8')
```

Mail verification:

```python
mail = api.tools.mail_check('example.com', 'selector')
mail_host = api.tools.mail_host_check('example.com')
```

### Reseller

```python
api.reseller.check_license('LICENSE_KEY')

api.reseller.generate_license({
    'registeredTo': 'John Doe',
    'domainOrIp': 'example.com',
    'status': 'active',
    'productId': 123,
    'projectId': 456
})

api.reseller.update_license('LICENSE_KEY', { 'status': 'inactive' })
api.reseller.delete_license('LICENSE_KEY')
```

### User

```python
login_response = api.user.login('usernameOrEmail', 'password', True)
api.user.revoke_secret('usernameOrEmail', 'password', 'secret-token')
```

### OAuth

```python
token = api.oauth2.get_access_token('code', 'redirectUri', 'clientId', 'clientSecret')
profile = api.oauth2.get_profile(token['access_token'])
```

## Request Handling

All HTTP requests are handled internally with `requests`, including error handling. Every method returns a **Python dictionary**.

```python
try:
    result = api.tools.geo_ip('8.8.8.8')
    print(result)
except Exception as error:
    print(error)
```

## Type Hinting Support

The SDK is fully typed with Python type hints and is compatible with modern IDEs such as PyCharm and VS Code.

```python
from ricardoneud.api.client import RicardoNeudAPI

api = RicardoNeudAPI(api_key='your-api-key', version='v4')
```

## Notes

* You must provide either an **API Key** or a **Secret token**.
* Secret tokens expire after 24 hours and are visible in your dashboard.
* API Key and Secret are mutually exclusive; setting one clears the other.
* Always check the supported API version to ensure endpoint compatibility.
