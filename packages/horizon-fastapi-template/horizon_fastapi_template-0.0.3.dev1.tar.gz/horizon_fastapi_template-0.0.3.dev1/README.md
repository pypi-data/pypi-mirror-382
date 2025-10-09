# FastAPI Template

A reusable FastAPI application factory packaged for quick reuse. The package exposes a
single public function, `create_app`, which returns a fully configured FastAPI
instance with logging, metrics, documentation, and health-check routes ready to go.

## 🚀 Quick Start

### Installation

```bash
pip install horizon-fastapi-template
```

### Usage

Create a new file (for example `main.py`) and bootstrap your API:

```python
from horizon_fastapi_template import create_app

app = create_app()
```

Run the application with Uvicorn:

```bash
uvicorn main:app --reload
```

## 🔧 Configuration

Application behaviour is configured through environment variables using
[`pydantic-settings`](https://docs.pydantic.dev/latest/usage/pydantic_settings/).
Create a `.env` file alongside your application if you need to override defaults:

```env
PORT=8000
LOG_LEVEL=INFO
APP_NAME=MyFastAPIApp
PROCESS_TIME_HEADER=X-Process-Time
SWAGGER_STATIC_FILES=/static/swagger
SWAGGER_OPENAPI_JSON_URL=/openapi.json
LOG_REQUEST_EXCLUDE_PATHS=["/health", "/metrics", "/static", "/docs", "/redoc", "/openapi.json", "/.well-known"]
```

The same settings object is used internally to configure logging, documentation,
and middleware. Although the implementation lives under `fastapi_template._internal`,
those modules are considered private and may change without notice.

## 🧩 Features

* **Logging** – Structured logging powered by `loguru` with an optional request
  logging middleware.
* **Monitoring** – Prometheus-compatible metrics endpoint and uptime background
  task ready to register in your observability stack.
* **Documentation** – Swagger UI and ReDoc served through customisable static
  assets bundled with the package.
* **Middleware** – Request timing, exception handling, and request logging
  middleware that can be toggled through configuration flags.
* **Utilities** – Helper clients for HTTP APIs, Bitbucket API, FTP servers, and Kubernetes
  interactions, plus shared Pydantic models for error responses.

## 📁 Project Structure

```
FastApiTemplate/
├── app/
│   └── main.py               # Example application entrypoint
├── package/
│   └── fastapi_template/
│       ├── __init__.py       # Public package exposing `create_app`
│       ├── utils.py          # Public utility functions and classes
│       ├── _internal/        # Private framework modules
│       └── static/           # Bundled static assets for Swagger UI
├── pyproject.toml            # Packaging metadata
├── requirements.txt         # Pinning dependencies for development
└── README.md
```

## 🛠️ Development

Install dependencies in editable mode when working on the package:

```bash
pip install -e .
```

Run the example application from the repository root:

```bash
python -m app.main
```

## 📄 License

Distributed under the terms of the MIT license. See the [LICENSE](LICENSE) file
for details.
