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
- A location naming a plugin with no module raises when a request
  comes, so that request gets `500` and the error log says which name.

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
