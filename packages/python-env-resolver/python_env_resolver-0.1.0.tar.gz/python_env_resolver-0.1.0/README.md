# python-env-resolver

Type-safe environment configuration for Python services, powered by Pydantic. Model the shape of your settings once, enforce policies centrally, and keep secrets fresh without burning latency.

```bash
pip install python-env-resolver
# or
uv add python-env-resolver
```

## Why teams reach for it

- Strong typing and validation with your Pydantic models.
- Resolver pipeline that merges `os.environ`, `.env`, cloud stores, or any async source.
- Built-in policies to lock down where secrets may come from, especially in production.
- Audit trail for compliance or debugging misconfigured environments.
- Smart TTL caching with stale-while-revalidate so background refreshes never block callers.

## Quickstart

### Async

```python
from pydantic import BaseModel, HttpUrl
from python_env_resolver import resolve

class AppConfig(BaseModel):
    port: int = 3000
    database_url: HttpUrl
    debug: bool = False
    api_key: str | None = None

async def main():
    config = await resolve(AppConfig)
    print(config.database_url)
```

### Sync

```python
from pydantic import BaseModel, HttpUrl
from python_env_resolver import resolve_sync

class AppConfig(BaseModel):
    port: int = 3000
    database_url: HttpUrl
    debug: bool = False
    api_key: str | None = None

config = resolve_sync(AppConfig)
print(config.database_url)
```

Both APIs share identical behavior. By default they read from `process_env()` (plain `os.environ`). Pass additional resolvers when you need more.

## Resolvers and merge strategy

```python
from python_env_resolver import dotenv, process_env, resolve, resolve_sync, ResolveOptions

async def load_config():
    return await resolve(
        AppConfig,
        resolvers=[dotenv(".env"), process_env()],
        options=ResolveOptions(priority="last")  # later resolvers override earlier ones
    )

# Or synchronously:
config = resolve_sync(
    AppConfig,
    resolvers=[dotenv(".env"), process_env()],
    options=ResolveOptions(priority="last"),
)
```

Resolvers are async callables that return `dict[str, str]`. Custom sources only need to implement a `.load()` coroutine and a `name`.

## Custom resolvers

Build your own resolver to load from any source—databases, HTTP APIs, vault systems, or custom file formats. The interface is minimal and composable:

```python
from python_env_resolver import BaseResolver

class ConsulResolver(BaseResolver):
    def __init__(self, host: str, prefix: str):
        super().__init__(name="consul")
        self.host = host
        self.prefix = prefix
    
    async def load(self) -> dict[str, str]:
        # Your logic to fetch key-value pairs from Consul
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.host}/v1/kv/{self.prefix}?recurse=true")
            data = response.json()
            return {item["Key"]: item["Value"] for item in data}

# Use it like any built-in resolver
config = await resolve(
    AppConfig,
    resolvers=[ConsulResolver("http://localhost:8500", "app/config"), process_env()],
)
```

You can also create simple function-based resolvers for one-off needs:

```python
from python_env_resolver import create_resolver

async def load_from_api():
    # Fetch environment variables from your API
    return {"API_KEY": "secret123", "REGION": "us-west-2"}

api_resolver = create_resolver("my-api", load_from_api)
config = await resolve(AppConfig, resolvers=[api_resolver])
```

## Custom validators

Compose Pydantic validators with built-in utilities or create your own for domain-specific constraints:

```python
from pydantic import BaseModel, field_validator
from python_env_resolver import resolve, validate_url, validate_port

class AppConfig(BaseModel):
    api_url: str
    port: int
    redis_host: str
    
    @field_validator("api_url")
    @classmethod
    def check_api_url(cls, v: str) -> str:
        # Use built-in validator
        return validate_url(v, require_https=True)
    
    @field_validator("port")
    @classmethod
    def check_port(cls, v: int) -> int:
        # Compose with built-in validator
        return validate_port(v, min_port=1024, max_port=65535)
    
    @field_validator("redis_host")
    @classmethod
    def check_redis_host(cls, v: str) -> str:
        # Custom validation logic
        if not v.endswith(".cache.amazonaws.com") and v != "localhost":
            raise ValueError("Redis must be ElastiCache or localhost")
        return v

config = await resolve(AppConfig)
```

Mix and match validators for ultimate flexibility:

```python
from python_env_resolver import validate_email, validate_number_range

class ServiceConfig(BaseModel):
    admin_email: str
    max_connections: int
    timeout_seconds: float
    
    @field_validator("admin_email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return validate_email(v)
    
    @field_validator("max_connections")
    @classmethod
    def check_max_connections(cls, v: int) -> int:
        return validate_number_range(v, min_val=1, max_val=1000)
    
    @field_validator("timeout_seconds")
    @classmethod
    def check_timeout(cls, v: float) -> float:
        if v <= 0 or v > 300:
            raise ValueError("Timeout must be between 0 and 300 seconds")
        return v
```

## Keeping secrets fast with caching

Wrap any resolver with `cached()` to enable TTL caching, including stale-while-revalidate. Fresh data is served instantly while a background refresh updates the cache, even when multiple callers arrive simultaneously.

```python
from python_env_resolver import CacheOptions, TTL, cached
from python_env_resolver_aws import aws_secrets  # example integration

secrets_resolver = cached(
    aws_secrets(secret_id="prod/db"),
    CacheOptions(
        ttl=TTL.minutes5,
        max_age=TTL.hour,
        stale_while_revalidate=True,
    ),
)

async def load_config():
    return await resolve(AppConfig, resolvers=[secrets_resolver])
```

Prefer the helper when you like opinionated defaults tuned for AWS Secrets Manager:

```python
from python_env_resolver import aws_cache

secrets_resolver = cached(aws_secrets(secret_id="prod/db"), aws_cache())
```

## Security policies

Keep risky sources out of production or require critical settings to originate from a specific resolver.

```python
from python_env_resolver import PolicyOptions, ResolveOptions

options = ResolveOptions(
    policies=PolicyOptions(
        allow_dotenv_in_production=["LOG_LEVEL"],  # only allow this key from .env
        enforce_allowed_sources={
            "DATABASE_URL": ["aws-secrets"],
        },
    )
)

config = await resolve(AppConfig, options=options)
```

Policy violations surface as clear `ValueError`s before your application boots.

## Audit trail

Enable auditing to record where every value came from—helpful in staging and production alike.

```python
from python_env_resolver import ResolveOptions, get_audit_log

config = await resolve(
    AppConfig,
    options=ResolveOptions(enable_audit=True),
)

for event in get_audit_log():
    print(event.type, event.source, event.details)
```

## Safer boot paths

Need a non-raising API for CLI tools or tests? Use `safe_resolve`:

```python
from python_env_resolver import safe_resolve, safe_resolve_sync

result = await safe_resolve(AppConfig)
if result.success:
    config = result.data
else:
    raise RuntimeError(result.error)

# Synchronous helper
sync_result = safe_resolve_sync(AppConfig)
if not sync_result.success:
    raise RuntimeError(sync_result.error)
```

## Typed helpers

The package ships with focused validators and utilities for common scenarios:

- `TTL` constants for readable cache configuration (`TTL.minutes5`, `TTL.hour`, etc.).
- Validators: `validate_url`, `validate_port`, `validate_email`, `validate_number_range`.
- Resolver factories: `process_env()`, `dotenv(path)`, `create_resolver()`.
- Base classes: `BaseResolver` for building custom resolvers with full type safety.

Use them directly in your Pydantic models or compose your own domain-specific abstractions on top. The library is designed for maximum flexibility—every component is composable and extensible.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/jagreehal/python-env-resolver.git
cd python-env-resolver

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy src

# Lint
ruff check .
```

### Publishing

See [PUBLISHING.md](PUBLISHING.md) for detailed instructions on publishing to PyPI.

## License

MIT License - see [LICENSE](LICENSE) file for details.
