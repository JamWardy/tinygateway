# How tinygateway works

The API gateway, in Python, for learning how Kong works, as tinyproxy is
for nginx. Kong is Lua run inside nginx by OpenResty; tinygateway is
Python run inside tinyproxy by stage 8's phases, in
`../tinyproxy/DESIGN.md`. Where Kong's way is harder to follow,
tinygateway's is simpler. It uses only Python's own library.

## Running it

tinyproxy runs it, from the gateway's config:

```nginx
http {
    python_path .;
    python_module tinygateway;
    ...
}
```

Its `__init__.py` is tinyproxy's hooks: `access`, `balancer`,
`header_filter`, `log` and `error`, as Kong's nginx config calls
`Kong.access()` and the rest. It has no `body_filter` yet, as no plugin
needs one, and tinyproxy chunks every reply when there is one.

## Plugins

What the gateway does to a request, such as checking its token, is a
plugin, as in Kong.

- Each plugin is a module in `tinygateway/plugins/`, with a function
  for any of the phases it acts in, taking what tinyproxy's hook takes.
- A location names its plugins with tinyproxy's `python_setting`:

  ```nginx
  location /orders {
      python_setting plugins "jwt rate_limit";
      proxy_pass http://orders;
  }
  ```

- At each phase, the hook runs each named plugin's function for it, in
  the order they're named. (Kong orders them by a `PRIORITY` number on
  each plugin, which hides the order.) In `access`, the first plugin
  to `respond` ends the phase. In `balancer`, the first to return an
  endpoint decides. In `body_filter`, each one gets what the one before
  returned.
- The gateway's `init()` imports every module in `plugins/` at
  startup, as Kong loads its plugins in its init phase, and calls each
  one's own `init()`, if it has one. A plugin that won't import, or
  whose `init()` raises, stops tinyproxy starting. A location naming a
  plugin with no module raises when a request comes, so that request
  gets `500` and the error log says which name.

## The jwt plugin

`plugins/jwt.py` checks the token in the `access` phase, as Kong's jwt
plugin does, and tells the service who sent the request.

- `init()` reads the secret from `SHOP_JWT_SECRET`, and raises if it's
  unset or empty, so tinyproxy won't start without it.
- The token comes only from `Authorization: Bearer <token>`. (Kong's
  also looks in a `?jwt=` query parameter and a cookie.)
- A token is valid when it has three base64url parts, its header and
  payload are JSON objects, its header's `alg` is exactly `HS256` (so
  `none` and other algorithms are refused), its signature matches by
  `hmac.compare_digest`, and its `sub` is a string of ASCII digits for
  a whole number from 1 up. `typ` and `iat` aren't checked, and `exp`
  is ignored until token expiry, a follow-up in `../TODO.md`.
- Valid: it removes the client's `X-User-Id`, if any, and sets it to
  `sub`.
- No `Authorization` header, or one that isn't `Bearer`: `401` with
  `WWW-Authenticate: Bearer` and the detail "No token; log in first."
- An invalid token: `401` with `WWW-Authenticate: Bearer
  error="invalid_token"` and the detail "The token isn't valid; log in
  again." (RFC 6750; Kong sends no `WWW-Authenticate`.)
- Both are Problem Details with the title "Unauthorized", the status's
  own words, sent with `request.respond`, as `error` isn't called for
  a plugin's replies.

## Errors

tinyproxy's own errors become Problem Details, as `../DESIGN.md`'s
"Errors" says, in the gateway itself, not a plugin, as Kong's
`handle_error` is: `error` answers with `Content-Type:
application/problem+json` and

```json
{"title": "Bad Gateway", "status": 502}
```

the status's own words as the title, as for any error without a title
of its own.
