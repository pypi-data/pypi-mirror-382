# callback-md — OAuth callback server (Flask) documentation

A minimal server designed to **receive the OAuth callback** at `https://127.0.0.1:<port>/<path>` with a **simple** setup that’s ready for **professional environments** (a lightweight production mode) without sacrificing ease of use.

> This document describes only the `callback.py` module and its API. It does not include a license or token-exchange code; it is an integration guide for the module in your project/SDK.

---

## Features

* **HTTPS by default** (recommended/required by most providers).
* **Two TLS modes**:

  * **PEM**: certificates as files (`ssl_cert`, `ssl_key`) → recommended for production use.
  * **Adhoc**: `adhoc_ssl=True` creates an in‑memory, temporary certificate (requires `cryptography`) → ideal for development.
* **Simple production mode** with `gevent.pywsgi` (if installed) or fallback to Werkzeug.
* **High-level API** (`run_callback_server(...)`) and **CLI**.
* **Robust parameter capture**: query (GET), form (POST), JSON, and tokens in the URL `#fragment` via a bridge page that reposts them by POST.
* **Optional JSON response** at the callback route using `Accept: application/json` or `?format=json`.
* **Customizable pages**: provide file paths for **Success HTML** and **Error HTML**; if files are missing or fail to load, readable **fallbacks** are used.
* **Clean shutdown**, even over HTTPS.

---

## Requirements

* **Python** ≥ 3.8
* **Dependencies**:

  * Required: `Flask`
  * Optional:

    * `gevent` (production mode without the dev warning)
    * `cryptography` (for `adhoc_ssl=True`)
    * `requests` (clean shutdown over HTTPS)

### Installation

```bash
pip install Flask
# Simple production (recommended):
pip install gevent
# Adhoc SSL (if you'll use adhoc_ssl=True):
pip install cryptography
# Clean HTTPS shutdown:
pip install requests
```

---

## Quick start

### As a library (simple production with PEM certificates)

```python
from callback import run_callback_server

res = run_callback_server(
    host="127.0.0.1",
    port=8080,
    path="/callback",
    timeout=180,
    ssl_cert="cert.pem",
    ssl_key="key.pem",
    server="auto",   # uses gevent if installed
    success_html_path="/path/to/success.html",  # optional
    error_html_path="/path/to/error.html",      # optional
)

if res is None:
    raise TimeoutError("Callback did not arrive in time")

params = res["params"]
print(params)  # {'code': '...', 'state': '...'} or tokens if the provider returns them
```

### As a library (rapid development with adhoc certificate)

```python
res = run_callback_server(
    host="127.0.0.1",
    port=8080,
    path="/callback",
    timeout=180,
    adhoc_ssl=True,
    server="werkzeug",  # you'll see the dev warning; normal in tests
    # success_html_path / error_html_path are also valid here
)
```

### CLI (production; uses gevent if installed and --server auto)

```bash
python callback.py \
  --host 127.0.0.1 --port 8080 --path callback \
  --timeout 180 --ssl-cert cert.pem --ssl-key key.pem --server auto \
  --success-html /path/to/success.html --error-html /path/to/error.html
```

### CLI (development; adhoc certificate)

```bash
python callback.py \
  --host 127.0.0.1 --port 8080 --path callback \
  --timeout 180 --adhoc-ssl --server werkzeug \
  --success-html /path/to/success.html --error-html /path/to/error.html
```

**Expected output (single-line JSON):**

```json
{"params":{"code":"...","state":"..."},"method":"GET","path":"/callback","received_at":1730000000}
```

---

## Custom HTML pages (Success / Error)

You can pass file paths to static HTML files to show a final UI to the user:

* **`success_html_path`**: served when the callback includes a `code` or tokens (success).
* **`error_html_path`**: served when the callback includes `error` (failure).

If the file **does not exist** or **fails** to read, the server logs the error and uses:

* **Success** fallback: “Credentials received successfully. You may close this window.”
* **Error** fallback: “Authentication could not be completed. Close this window and try again.”

> If the request includes `Accept: application/json` or `?format=json`, the server **always** returns JSON (useful for automation) and does not render HTML.

---

## High-level API

### `run_callback_server(...)`

**Signature**

```python
def run_callback_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    path: str = "/callback",
    *,
    timeout: float = 180.0,
    ssl_cert: Optional[str] = None,
    ssl_key: Optional[str] = None,
    adhoc_ssl: bool = False,
    force_https: bool = True,
    server: str = "auto",
    success_html_path: Optional[str] = None,
    error_html_path: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> Optional[Dict[str, Any]]:
    ...
```

**Description**: Starts the server, waits for **one** response (one‑shot pattern), then shuts it down. Returns a `dict` with the callback data, or `None` if `timeout` expires.

**Parameters**

* `host`: usually `"127.0.0.1"` for local use.
* `port`: e.g., `8080`. Must match the registered `redirect_uri`.
* `path`: e.g., `"/callback"`. Normalized if you pass `"callback"`.
* `timeout`: seconds to wait before returning `None`.
* `ssl_cert`, `ssl_key`: PEM file paths for TLS (recommended for simple production).
* `adhoc_ssl`: generates an in‑memory temporary certificate (requires `cryptography`). Useful for development.
* `force_https`: if `True` (default), requires TLS (adhoc or PEM). If `False`, allows HTTP (not recommended).
* `server`: `"auto"` | `"gevent"` | `"werkzeug"`.

  * `auto`: uses gevent if PEM certs are present and `gevent` is installed; otherwise falls back to Werkzeug (or HTTP if `force_https=False`).
  * `gevent`: force gevent (requires PEM certs).
  * `werkzeug`: uses `app.run` (dev server), compatible with `adhoc_ssl`.
* `success_html_path`: success HTML path (optional). If it fails, the success fallback is used.
* `error_html_path`: error HTML path (optional). If it fails, the error fallback is used.
* `logger`: lets you inject your own `logging.Logger`.

**Return value**

```json
{
  "params": { "code": "...", "state": "..." },
  "method": "GET",
  "path": "/callback",
  "received_at": 1730000000
}
```

---

## Low-level API (optional)

### `CallbackServer`

* `start()`: launches the server in a background thread.
* `wait(timeout: Optional[float]) -> Optional[dict]`: blocks until the first callback arrives or `timeout` is reached.
* `shutdown()`: cleanly stops the server. In HTTPS + Werkzeug, it uses an internal route `GET /__shutdown__` (invoked with `verify=False` over loopback).

**Exposed routes**

* `/<path>` (your `path`): captures parameters.
* `/health`: returns `200 OK` (text `OK`).
* `/__shutdown__`: (internal) stops the Werkzeug server; used only for shutdown.

---

## HTTP behavior

* **HTML response** by default with an *ok* message.
* **JSON response** if the client sends `Accept: application/json` or appends `?format=json` to the URL.
* **Fragment bridge**: if the provider returns tokens in `#fragment`, the route’s HTML runs a script that:

  1. extracts the fragment,
  2. turns it into an object (`{access_token: ..., id_token: ..., ...}`),
  3. POSTs it as JSON to the same route as `{ "fragment_params": { ... } }`.
* The server **merges**: query (GET) + form (POST) + JSON + `fragment_params` (if present) into `result["params"]`.
* If the callback arrives with neither `error` nor `code/tokens`, the **bridge** is displayed and the flow is **not** marked complete until the POST with `fragment_params` is received.

---

## TLS/server configuration matrix

| `server`   | Certificates             | Outcome                  |
| ---------- | ------------------------ | ------------------------ |
| `auto`     | PEM + `gevent` installed | **gevent.pywsgi** (prod) |
| `auto`     | PEM only (no `gevent`)   | Werkzeug (dev server)    |
| `auto`     | `adhoc_ssl=True`         | Werkzeug (dev + adhoc)   |
| `gevent`   | **PEM required**         | **gevent.pywsgi** (prod) |
| `werkzeug` | PEM or `adhoc_ssl=True`  | Werkzeug (dev server)    |

> Note: gevent **does not** support `adhoc_ssl`. For adhoc, use `werkzeug`.

---

## Integration into your project

This section explains **how to plug `callback.py` into any project** (CLI, desktop app, internal service) without imposing structure.

### Suggested structure (optional)

```
project/
  callback.py
  oauth_flow.py           # orchestrates the OAuth flow (your code)
  assets/
    success.html
    error.html
```

### Integration steps

1. **Define the `redirect_uri`** you’ll register with the provider (it must be EXACT):

   * Example: `https://127.0.0.1:8080/callback` → host, port, and path must match.
2. **Build the authorization URL** with `response_type=code`, `client_id`, `redirect_uri`, `scope`, and `state` (a random value you’ll store to validate later).
3. **Open the browser** to that URL (e.g., with `webbrowser.open`).
4. **Start the callback server** with `run_callback_server(...)` using **HTTPS**:

   * In dev: `adhoc_ssl=True` and `server="werkzeug"`.
   * In local prod: `ssl_cert` + `ssl_key` and `server="auto"` (with `gevent` installed).
   * (Optional) Pass `success_html_path` / `error_html_path` for better UX.
5. **Wait for the result** (`dict`) and **validate `state`**. If `error` is present, handle it. If `code`/tokens are present, continue.
6. **Send the `code`** to your token‑exchange layer (NOT included here) and persist the result per your policies.

### Minimal orchestration example (pseudo‑code)

```python
# oauth_flow.py (integration example)
import secrets, webbrowser
from urllib.parse import quote_plus
from callback import run_callback_server

CLIENT_ID = "..."
REDIRECT_URI = "https://127.0.0.1:8080/callback"
SCOPE = "read"

state = secrets.token_urlsafe(24)
auth_url = (
    "https://api.schwabapi.com/v1/oauth/authorize"
    f"?response_type=code&client_id={CLIENT_ID}"
    f"&redirect_uri={quote_plus(REDIRECT_URI)}&scope={SCOPE}&state={state}"
)
webbrowser.open(auth_url, new=2)

result = run_callback_server(
    host="127.0.0.1", port=8080, path="/callback",
    timeout=180,
    ssl_cert="cert.pem", ssl_key="key.pem", server="auto",
    success_html_path="assets/success.html",
    error_html_path="assets/error.html",
)

if result is None:
    raise TimeoutError("Timeout waiting for callback")

params = result["params"]
if params.get("state") != state:
    raise ValueError("Invalid state")
if "error" in params:
    raise RuntimeError(params.get("error_description") or params["error"])  # handle to fit your app
code = params.get("code")
# Here you hand off the `code`→tokens exchange to your own implementation
```

> Your token module (persistence/refresh/rotation) is up to you; `callback.py` only manages the browser return in a safe, user‑friendly way.

---

## Error handling and logs

* If `success_html_path` or `error_html_path` cannot be found/read, an **error log** is recorded and the corresponding **fallback** is used.
* If a callback arrives with `error`, the server:

  * marks the flow as completed,
  * returns JSON (`{"ok": true, ...}`) if JSON was requested,
  * or serves `error_html_path` (or the fallback) in HTML mode.
* If the callback arrives without `code`/tokens and without `error`, the **bridge** is served and completion is deferred until **fragment_params** are posted.

---

## Troubleshooting

* **“WARNING: This is a development server…”**: appears with Werkzeug (dev). To avoid it, install `gevent` and use `server="auto"` or `"gevent"` with PEM.
* **Browser warns about the certificate**: normal with adhoc or self‑signed certs. Use a trusted PEM (e.g., mkcert) to avoid it.
* **Callback never arrives**:

  * Ensure the authorization URL contains the exact `redirect_uri` (including port and path).
  * Check firewall/antivirus.
  * Increase `timeout`.
* **`adhoc_ssl=True` fails**: install `cryptography`.
* **`server="gevent"` fails**: install `gevent` and use PEM (gevent does not support adhoc).
* **Port already in use**: change `port` or free up 8080.

---

## Compatibility

* **OS**: Windows, macOS, Linux.
* **Python**: 3.8+
* **Servers**: Werkzeug (dev), gevent.pywsgi (simple production).
