# TODO

How it works is in `DESIGN.md`. The stages are the ones in `../TODO.md`.

```
tinygateway/
  __init__.py     tinyproxy's hooks, running each location's plugins
  errors.py       tinyproxy's errors as Problem Details
  plugins/
    __init__.py
    jwt.py        the token check and X-User-Id
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

