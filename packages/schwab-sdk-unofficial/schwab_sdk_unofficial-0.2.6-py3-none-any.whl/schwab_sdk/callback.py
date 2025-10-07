# callback.py – HTTPS OAuth callback server (Flask) with simple production mode
# and customizable Success/Error HTML pages.
#
# Features:
# - HTTPS required by default (PEM files or adhoc SSL for dev).
# - Simple production mode via gevent.pywsgi (if installed), fallback to Werkzeug.
# - One-shot flow: start() -> wait(timeout) -> shutdown().
# - Returns a dict to the caller; serves JSON when Accept: application/json or ?format=json.
# - Bridge page to capture tokens from URL fragment (#) and POST them as JSON.
# - Custom HTML pages for success and error (file paths); robust fallback if files missing.
# - Does NOT signal completion while showing the bridge page (prevents early return).
# - CLI flags for PEM/adhoc/server selection and custom success/error HTML paths.

from __future__ import annotations

import argparse
import json
import logging
import os
import threading
import time
from typing import Any, Dict, Optional

from flask import Flask, Response, jsonify, request

# Optional: gevent for production WSGI
try:  # pragma: no cover
    from gevent.pywsgi import WSGIServer as _GEventWSGIServer  # type: ignore
except Exception:  # pragma: no cover
    _GEventWSGIServer = None  # type: ignore

# Optional: clean HTTP shutdown helper (only if force_https=False)
try:  # pragma: no cover
    from werkzeug.serving import make_server  # type: ignore
except Exception:  # pragma: no cover
    make_server = None  # type: ignore


# ------------------------- Defaults (HTML fallbacks) -------------------------

_HTML_OK_FALLBACK = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Authentication completed</title>
    <style>body{font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif;margin:2rem;line-height:1.5}</style>
  </head>
  <body>
    <h1>Credentials received successfully</h1>
    <p>You can now close this window.</p>
  </body>
</html>"""

_HTML_ERROR_FALLBACK = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Authentication error</title>
    <style>body{font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif;margin:2rem;line-height:1.5}</style>
  </head>
  <body>
    <h1>Authentication could not be completed</h1>
    <p>Close this window and try again.</p>
  </body>
</html>"""

_HTML_FRAGMENT_BRIDGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Finalizing sign-in...</title>
    <style>body{font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif;margin:2rem;line-height:1.5}</style>
  </head>
  <body>
    <h1>Processing data...</h1>
    <p>If this page does not close automatically, you can close it now.</p>
    <script>
      (function(){
        try {
          var hash = window.location.hash || "";
          if (hash.startsWith("#")) hash = hash.substring(1);
          var params = {};
          if (hash.length > 0) {
            hash.split("&").forEach(function(kv){
              var p = kv.split("=");
              if (p.length === 2) params[decodeURIComponent(p[0])] = decodeURIComponent(p[1]);
            });
          }
          if (Object.keys(params).length > 0) {
            fetch(window.location.pathname, {
              method: 'POST',
              headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
              body: JSON.stringify({ fragment_params: params })
            }).then(function(){
              // Optionally update UI; the server response may not replace this page due to fetch()
              document.body.innerHTML = '<h1>Data sent. You can close this window.</h1>';
            }).catch(function(){
              document.body.innerHTML = '<h1>The data could not be sent automatically.</h1><p>Please close this window and try again.</p>';
            });
          }
        } catch (e) { /* ignore */ }
      })();
    </script>
  </body>
</html>"""


# ---------------------------- Internal HTTP runner ---------------------------

class _WSGIServerThread(threading.Thread):
    """HTTP runner with clean shutdown (used only if force_https=False)."""

    def __init__(self, app: Flask, host: str, port: int):
        super().__init__(daemon=True)
        self._app = app
        self._host = host
        self._port = port
        self._server = None

    def run(self) -> None:  # pragma: no cover
        if make_server is None:
            raise RuntimeError("werkzeug.make_server is unavailable; cannot run threaded HTTP server.")
        self._server = make_server(self._host, self._port, self._app)
        self._server.serve_forever()  # type: ignore

    def shutdown(self) -> None:
        if self._server is not None:
            self._server.shutdown()  # type: ignore


# --------------------------------- Server ------------------------------------

class CallbackServer:
    """
    OAuth callback server with simple production support and customizable HTML pages.

    Flow: start() -> wait() -> shutdown().

    wait() returns a dict like:
        {
          "params": {...},
          "method": "GET" | "POST",
          "path": "/callback",
          "received_at": <epoch_seconds>
        }
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        path: str = "/callback",
        *,
        # TLS selection
        ssl_cert: Optional[str] = None,
        ssl_key: Optional[str] = None,
        adhoc_ssl: bool = False,
        force_https: bool = True,
        # Server selection
        server: str = "auto",  # auto | gevent | werkzeug
        # Custom HTML pages
        success_html_path: Optional[str] = None,
        error_html_path: Optional[str] = None,
        # Logging
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.host = host
        self.port = int(port)
        self.path = "/" + path.strip("/") if path else "/callback"
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.adhoc_ssl = adhoc_ssl
        self.force_https = force_https
        self.server = server.lower().strip()
        if self.server not in {"auto", "gevent", "werkzeug"}:
            raise ValueError("server must be one of: auto, gevent, werkzeug")

        # Logger
        self.log = logger or logging.getLogger("callback")
        if not self.log.handlers:
            # Simple console handler by default
            h = logging.StreamHandler()
            fmt = logging.Formatter("[%(levelname)s] %(message)s")
            h.setFormatter(fmt)
            self.log.addHandler(h)
            self.log.setLevel(logging.INFO)

        # HTTPS constraints
        if self.force_https:
            if self.server == "gevent" and not (self.ssl_cert and self.ssl_key):
                raise RuntimeError("gevent requires ssl_cert and ssl_key (does not support adhoc)")
            if self.server in {"auto", "werkzeug"} and not (self.adhoc_ssl or (self.ssl_cert and self.ssl_key)):
                raise RuntimeError("HTTPS is required: use adhoc_ssl=True or provide ssl_cert and ssl_key")

        # Flask app and internals
        self._app = Flask(__name__)
        self._result: Optional[Dict[str, Any]] = None
        self._event = threading.Event()
        self._thread_http: Optional[_WSGIServerThread] = None
        self._thread_https: Optional[threading.Thread] = None
        self._gevent_server = None
        self._server_kind: Optional[str] = None  # "gevent" | "werkzeug" | "http"

        # Load optional custom HTML files
        self._success_html = self._load_optional_html(success_html_path, kind="success")
        self._error_html = self._load_optional_html(error_html_path, kind="error")

        # Routes
        self._app.add_url_rule(self.path, view_func=self._handle_callback, methods=["GET", "POST"])
        self._app.add_url_rule("/health", view_func=lambda: ("OK", 200))
        # Internal route for clean shutdown in Werkzeug
        self._app.add_url_rule("/__shutdown__", view_func=self._shutdown_route, methods=["GET"])

    # ------------------------- Public lifecycle methods -------------------------

    def start(self) -> None:
        """Start the server in a background thread."""
        # HTTPS branch
        if self.force_https and (self.adhoc_ssl or (self.ssl_cert and self.ssl_key)):
            # Prefer gevent if selected or auto and available with certs
            can_gevent = _GEventWSGIServer is not None and (self.ssl_cert and self.ssl_key)
            use_gevent = (self.server == "gevent") or (self.server == "auto" and can_gevent)

            if use_gevent:
                # gevent production server (no dev warning)
                self._gevent_server = _GEventWSGIServer(
                    (self.host, self.port), self._app,
                    keyfile=self.ssl_key, certfile=self.ssl_cert
                )
                self._server_kind = "gevent"

                def _run_gevent():  # pragma: no cover
                    self._gevent_server.serve_forever()

                self._thread_https = threading.Thread(target=_run_gevent, daemon=True)
                self._thread_https.start()
                self.log.info(f"Starting gevent HTTPS on https://{self.host}:{self.port}{self.path}")
            else:
                # werkzeug (dev) – supports ssl_context="adhoc" or (cert,key)
                if self.adhoc_ssl:
                    ssl_context = "adhoc"
                    self.log.info(f"Starting Werkzeug HTTPS (adhoc) on https://{self.host}:{self.port}{self.path}")
                else:
                    ssl_context = (self.ssl_cert, self.ssl_key)
                    self.log.info(f"Starting Werkzeug HTTPS on https://{self.host}:{self.port}{self.path}")

                def _run_wz():  # pragma: no cover
                    self._app.run(host=self.host, port=self.port, ssl_context=ssl_context, debug=False, use_reloader=False)

                self._server_kind = "werkzeug"
                self._thread_https = threading.Thread(target=_run_wz, daemon=True)
                self._thread_https.start()
            return

        # HTTP branch (only if force_https=False)
        if not self.force_https:
            self._server_kind = "http"
            self._thread_http = _WSGIServerThread(self._app, self.host, self.port)
            self._thread_http.start()
            self.log.warning(f"Starting HTTP (NOT RECOMMENDED) on http://{self.host}:{self.port}{self.path}")
            return

        # If we got here, configuration was invalid
        raise RuntimeError("Invalid SSL configuration")

    def wait(self, timeout: Optional[float] = 180.0) -> Optional[Dict[str, Any]]:
        """Block until a valid callback (success/error) is received or timeout expires. Return dict or None."""
        signaled = self._event.wait(timeout=timeout)
        return self._result if signaled else None

    def shutdown(self) -> None:
        """Stop the server."""
        try:
            if self._server_kind == "gevent" and self._gevent_server is not None:
                try:
                    self._gevent_server.stop(timeout=1)
                except Exception:
                    pass
            elif self._server_kind == "werkzeug" and self._thread_https is not None and self._thread_https.is_alive():
                self._shutdown_via_request()
            elif self._server_kind == "http" and self._thread_http is not None:
                self._thread_http.shutdown()
        finally:
            time.sleep(0.2)

    # ------------------------------- Internals ---------------------------------

    def _load_optional_html(self, path: Optional[str], *, kind: str) -> Optional[str]:
        """Try to read an HTML file; return content or None if not provided or cannot be read."""
        if not path:
            return None
        try:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"File not found: {path}")
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                self.log.info(f"Loaded {kind} HTML from: {path}")
                return content
        except Exception as e:
            self.log.error(f"Could not load {kind} HTML ('{path}'): {e}. Using fallback.")
            return None

    def _shutdown_route(self):
        func = request.environ.get("werkzeug.server.shutdown")
        if func is None:
            return ("Not running with the Werkzeug Server", 500)
        func()
        return ("OK", 200)

    def _shutdown_via_request(self) -> None:
        # Call the internal shutdown route using local HTTPS/HTTP
        scheme = "https" if self.force_https else "http"
        try:
            import requests as _r  # lazy import
            _r.get(f"{scheme}://{self.host}:{self.port}/__shutdown__", verify=False, timeout=2)
        except Exception:
            pass

    @staticmethod
    def _wants_json() -> bool:
        acc = (request.headers.get("Accept", "") or "").lower()
        return ("application/json" in acc) or (request.args.get("format") == "json")

    @staticmethod
    def _has_tokenish(params: Dict[str, Any]) -> bool:
        tokenish = ("code", "access_token", "id_token", "refresh_token")
        return any(k in params and params.get(k) for k in tokenish)

    def _handle_callback(self) -> Response:
        # If already completed once: keep idempotent behavior (show OK page or JSON ok)
        if self._event.is_set():
            if self._wants_json():
                return jsonify({"ok": True})
            # show success fallback again (idempotent)
            return Response(self._success_html or _HTML_OK_FALLBACK, mimetype="text/html")

        # Merge params from GET, POST (form), JSON (incl. fragment_params)
        params: Dict[str, Any] = {}

        # Query params (GET)
        if request.args:
            for k in request.args.keys():
                vals = request.args.getlist(k)
                params[k] = vals if len(vals) > 1 else request.args.get(k)

        # POST form
        if request.method == "POST" and request.form:
            for k in request.form.keys():
                vals = request.form.getlist(k)
                params[k] = vals if len(vals) > 1 else request.form.get(k)

        # JSON body (incl. fragment_params from the bridge)
        body = request.get_json(silent=True) or {}
        if isinstance(body, dict):
            frag = body.get("fragment_params")
            if isinstance(frag, dict):
                for k, v in frag.items():
                    params.setdefault(k, v)
            for k, v in body.items():
                if k != "fragment_params":
                    params.setdefault(k, v)

        # Determine status
        is_error = "error" in params and params.get("error")
        has_tokenish = self._has_tokenish(params)

        # If no tokens and no explicit error -> show bridge (do not signal completion yet)
        if not is_error and not has_tokenish:
            if self._wants_json():
                # For API-like usage, report "pending"
                return jsonify({"ok": False, "pending": True, "hint": "Awaiting fragment POST or query params"})
            return Response(_HTML_FRAGMENT_BRIDGE, mimetype="text/html")

        # Success or error -> record result and signal
        self._result = {
            "params": params,
            "method": request.method,
            "path": request.path,
            "received_at": int(time.time()),
        }
        self._event.set()

        # Choose representation
        if self._wants_json():
            return jsonify({"ok": True, **self._result})

        # Serve custom HTML (with fallback) per status
        if is_error:
            html = self._error_html or _HTML_ERROR_FALLBACK
        else:
            html = self._success_html or _HTML_OK_FALLBACK

        return Response(html, mimetype="text/html")


# -------------------------- Convenience top-level API -------------------------

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
    """
    Start the server, wait for exactly one result (success or error), then shut it down.
    Return a dict or None if the timeout elapses.

    With `server="auto"`, try gevent if certs are provided and the library is installed;
    otherwise fall back to Werkzeug (or HTTP if `force_https=False`).
    """
    srv = CallbackServer(
        host=host,
        port=port,
        path=path,
        ssl_cert=ssl_cert,
        ssl_key=ssl_key,
        adhoc_ssl=adhoc_ssl,
        force_https=force_https,
        server=server,
        success_html_path=success_html_path,
        error_html_path=error_html_path,
        logger=logger,
    )
    srv.start()
    try:
        return srv.wait(timeout=timeout)
    finally:
        srv.shutdown()


# ----------------------------------- CLI -------------------------------------

def _cli() -> None:
    parser = argparse.ArgumentParser(description="Run an HTTPS OAuth callback server (Flask).")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind (default: 8080)")
    parser.add_argument("--path", default="callback", help="Callback path (default: callback)")
    parser.add_argument("--timeout", type=float, default=180.0, help="Seconds to wait for a callback before exit")
    parser.add_argument("--server", choices=["auto", "gevent", "werkzeug"], default="auto", help="WSGI server to use")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--adhoc-ssl", action="store_true", help="Use adhoc self-signed certificate (Werkzeug)")
    mode.add_argument("--ssl-cert", default=None, help="Path to SSL certificate (PEM) for HTTPS")
    parser.add_argument("--ssl-key", default=None, help="Path to SSL private key (PEM) for HTTPS (required if --ssl-cert)")

    # Custom HTML paths
    parser.add_argument("--success-html", default=None, help="Path to custom Success HTML file")
    parser.add_argument("--error-html", default=None, help="Path to custom Error HTML file")

    args = parser.parse_args()

    # Simple validation for PEM pair if chosen
    if args.ssl_cert and not args.ssl_key:
        parser.error("--ssl-key is required when using --ssl-cert")

    # gevent checks
    if args.server == "gevent" and not args.ssl_cert:
        parser.error("--server gevent requires --ssl-cert and --ssl-key (does not support adhoc)")
    if args.server == "gevent" and _GEventWSGIServer is None:
        parser.error("gevent is not installed. Install with: pip install gevent")

    # Normalize path
    path = "/" + args.path.strip("/")

    print(f"[callback.py] Starting on https://{args.host}:{args.port}{path} (server={args.server})")

    res = run_callback_server(
        host=args.host,
        port=args.port,
        path=path,
        timeout=args.timeout,
        ssl_cert=args.ssl_cert,
        ssl_key=args.ssl_key,
        adhoc_ssl=args.adhoc_ssl,
        force_https=True,
        server=args.server,
        success_html_path=args.success_html,
        error_html_path=args.error_html,
    )

    if res is None:
        print("[callback.py] Timeout waiting for callback.")
    else:
        print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    _cli()
