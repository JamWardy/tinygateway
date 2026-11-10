# TODO

How it works is in `DESIGN.md`. The stages are the ones in `../TODO.md`.

```
tinygateway/
  __init__.py     tinyproxy's hooks, running each location's plugins
  errors.py       tinyproxy's errors as Problem Details
  plugins/
    __init__.py
```

## Stage 8: plugins at the phases

- [x] The hooks, each running the location's plugins in order, in
      `__init__.py`
- [x] Problem Details for tinyproxy's errors, in `errors.py`
- [x] Try it by hand: a `404` and a `502` through tinyproxy as Problem
      Details; a test plugin in each phase, and two in order; an
      unknown plugin (`500`)

