"""Checks the request's JWT and tells the service who sent it, in
X-User-Id, as ../DESIGN.md's "The jwt plugin" says."""

import base64
import binascii
import hashlib
import hmac
import json
import os

from ..errors import problem_details

_secret = None


def init():
    global _secret
    secret = os.environ.get("SHOP_JWT_SECRET", "")
    if not secret:
        raise RuntimeError("jwt: set SHOP_JWT_SECRET, the secret tokens "
                           "are signed with")
    _secret = secret.encode()


def access(request):
    token = _bearer_token(request.headers)
    if token is None:
        _deny(request, "No token; log in first.", "Bearer")
        return
    user_id = _user_id(token)
    if user_id is None:
        _deny(request, "The token isn't valid; log in again.",
              'Bearer error="invalid_token"')
        return
    # Replaces any the client sent, so it can't name a user itself.
    request.set_header("X-User-Id", str(user_id))
    request.state["user_id"] = user_id


def _bearer_token(headers):
    for name, value in headers:
        if name.lower() == "authorization":
            scheme, _, token = value.strip().partition(" ")
            # The scheme ignores case (RFC 9110).
            if scheme.lower() == "bearer" and token.strip():
                return token.strip()
            return None
    return None


def _user_id(token):
    """The id in a valid token's sub, or None."""
    parts = token.split(".")
    if len(parts) != 3:
        return None
    header, payload, signature = (_decode(p) for p in parts)
    if header is None or payload is None or signature is None:
        return None
    header, payload = _json_object(header), _json_object(payload)
    # Only HS256, so a token can't choose "none" or another algorithm.
    if header is None or payload is None or header.get("alg") != "HS256":
        return None
    signed = f"{parts[0]}.{parts[1]}".encode()
    expected = hmac.new(_secret, signed, hashlib.sha256).digest()
    # compare_digest takes as long however much matches, so the time
    # doesn't give the signature away a byte at a time.
    if not hmac.compare_digest(expected, signature):
        return None
    sub = payload.get("sub")
    if not (isinstance(sub, str) and sub.isascii() and sub.isdigit()):
        return None
    return int(sub) or None


def _decode(part):
    # JWTs leave off base64's = padding. validate refuses characters
    # outside the alphabet, which would otherwise be skipped.
    try:
        return base64.b64decode(part + "=" * (-len(part) % 4),
                                altchars=b"-_", validate=True)
    except (binascii.Error, ValueError):
        return None


def _json_object(data):
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _deny(request, detail, challenge):
    status, headers, body = problem_details(
        401, detail, [("WWW-Authenticate", challenge)])
    request.respond(status, headers, body)
