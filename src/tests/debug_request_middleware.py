import json
import logging

logger = logging.getLogger(__name__)

# Fields whose values should be fully masked in logs
SENSITIVE_BODY_KEYS = {"username", "password"}


def _sanitize_auth_header(header_value: str) -> str:
    """Truncate Bearer token to first 4 characters."""
    if header_value.startswith("Bearer "):
        token = header_value[7:]
        if len(token) > 4:
            token = token[:4] + "... [TRUNCATED]"
        return f"Bearer {token}"
    return header_value


def _mask_sensitive_body(body_bytes: bytes, content_type: str = "") -> str:
    """
    Attempt to parse body as JSON and mask sensitive fields.
    Falls back to plain text truncation if parsing fails or content is not JSON.
    """
    if not body_bytes:
        return "(empty)"

    # Only parse as JSON if content-type looks like JSON
    is_json = "application/json" in content_type.lower()
    if is_json:
        try:
            data = json.loads(body_bytes.decode("utf-8"))
            # Recursively mask sensitive keys
            masked = _mask_dict(data)
            body_str = json.dumps(masked, ensure_ascii=False)
            if len(body_str) > 2000:
                body_str = body_str[:2000] + "... [TRUNCATED]"
            return body_str
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass  # fall back to plain text

    # Plain text (or non‑JSON): just truncate
    body_str = body_bytes.decode("utf-8", errors="replace")
    if len(body_str) > 2000:
        body_str = body_str[:2000] + "... [TRUNCATED]"
    return body_str


def _mask_dict(obj):
    """Recursively replace values of sensitive keys with '***'."""
    if isinstance(obj, dict):
        return {
            k: "***" if k.lower() in SENSITIVE_BODY_KEYS else _mask_dict(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_mask_dict(v) for v in obj]
    return obj


class DebugRequestResponseMiddleware:
    """
    Middleware that logs incoming API requests and outgoing responses,
    with sensitive data sanitized.

    For every request whose path starts with ``/api/``, the following
    is logged at ``INFO`` level:

    **Incoming request**
        * HTTP method and path
        * ``Authorization`` header – token truncated to first 4 chars
          (e.g. ``Bearer eyJh... [TRUNCATED]``)
        * Authenticated user and auth status
        * Request body – fields named ``username`` or ``password``
          (case‑insensitive) are masked with ``***``

    **Outgoing response**
        * Status code and reason phrase
        * Response body – same field‑masking logic applied

    All logged bodies are capped at 2000 characters.

    .. warning::
       Only enable in development or CI environments.
       Not suitable for production – may still leak data if unusual
       content types are used.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        # ---------- Incoming request ----------
        auth_header = request.META.get("HTTP_AUTHORIZATION", "NO HEADER")
        sanitized_auth = _sanitize_auth_header(auth_header)
        msg_parts = [
            f"--- DEBUG REQUEST --- {request.method} {request.path}",
            f"Authorization header: '{sanitized_auth}'",
            f"User: {request.user}  (authenticated: {request.user.is_authenticated})",
        ]

        # Sanitize request body
        content_type = request.META.get("CONTENT_TYPE", "")
        body_str = _mask_sensitive_body(request.body, content_type)
        msg_parts.append(f"Body: {body_str}")

        # Get response
        response = self.get_response(request)

        # ---------- Outgoing response ----------
        msg_parts.append(
            f"--- DEBUG RESPONSE --- {response.status_code} {response.reason_phrase}"
        )

        # Sanitize response body (response content is safe to read in debug)
        if hasattr(response, "content"):
            resp_content_type = response.get("Content-Type", "")
            resp_body_str = _mask_sensitive_body(response.content, resp_content_type)
            msg_parts.append(f"Body: {resp_body_str}")
        else:
            msg_parts.append("Body: (streaming or not available)")

        logger.info("\n".join(msg_parts))
        return response
