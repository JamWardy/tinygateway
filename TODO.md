# TODO

How it works is in `DESIGN.md`. The stages are the ones in `../TODO.md`.

```
tinygateway/
  __init__.py     tinyproxy's hooks, running each location's plugins
  errors.py       tinyproxy's errors as Problem Details
  plugins/
    __init__.py
    jwt.py        the token check and X-User-Id
    cors.py       letting pages from other origins call the API
    rate_limit.py how many requests each client may send
```

## Stage 8: plugins at the phases

- [x] The hooks, each running the location's plugins in order, in
      `__init__.py`
- [x] Problem Details for tinyproxy's errors, in `errors.py`
- [x] Try it by hand: a `404` and a `502` through tinyproxy as Problem
      Details; a test plugin in each phase, and two in order; an
      unknown plugin (`500`)

## Stage 9: authentication

As in `DESIGN.md`, "The jwt plugin":

- [x] `init()` in `__init__.py`, importing every plugin and calling
      its `init()`
- [x] A `detail` and extra headers for `problem_details` in
      `errors.py`
- [x] `plugins/jwt.py`
- [x] Try it by hand, with a config in front of items and orders: no
      token, not `Bearer`, a bad signature, `alg` `none`, a `sub` that
      isn't an id, and a forged `X-User-Id` with no token, each `401`;
      a real token from `POST /login` makes a listing with the right
      seller, with a forged `X-User-Id` replaced; tinyproxy refusing
      to start without `SHOP_JWT_SECRET`

## CORS

As in `DESIGN.md`, "The cors plugin":

- [x] `plugins/cors.py`
- [x] `cors` on every location in `../shop/gateway.conf`, before `jwt`
- [x] Try it by hand: a preflight from an allowed origin and from
      another; a `POST` with a token and one without (`401`), and an
      unknown path (`404`), each with `Access-Control-Allow-Origin`;
      `*`; a service's own header replaced; an `OPTIONS` that isn't a
      preflight going on to the service

## Stage 10: rate limiting

As in `DESIGN.md`, "The rate_limit plugin":

- [x] `request.location` in tinyproxy, as `../tinyproxy/DESIGN.md`
      says, in `../tinyproxy/python/request_attributes.c`
- [x] `request.state["user_id"]` in `plugins/jwt.py`
- [x] `plugins/rate_limit.py`
- [x] `rate_limit` and each location's limits in
      `../shop/gateway.conf`, as "High-level architecture" in
      `../DESIGN.md` says
- [x] Try it by hand: `/login` past its limit by IP (`429`,
      `Retry-After`, the `RateLimit-*` headers) while `/search` still
      answers; two users on `/orders` counted apart; a preflight not
      counted; the count starting again in the next window; a location
      with no limits, or a bad one (`500`)
