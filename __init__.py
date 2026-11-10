"""tinyproxy's hooks. Each runs the plugins the request's location names,
in the order it names them."""

import importlib
import pkgutil

from . import errors, plugins

_plugins = {}  # By name, once a request has named it.


def _load(name):
    if name not in _plugins:
        module_name = f"{__name__}.plugins.{name}"
        try:
            _plugins[name] = importlib.import_module(module_name)
        except ModuleNotFoundError as error:
            if error.name != module_name:
                raise  # Something the plugin imports is missing.
            raise LookupError(f"no plugin named {name!r}") from None
    return _plugins[name]


def init():
    """Import every plugin, as Kong loads its plugins at startup, so one
    that can't start, such as jwt without its secret, stops tinyproxy
    rather than failing a request later."""
    for module in pkgutil.iter_modules(plugins.__path__):
        plugin = _load(module.name)
        if hasattr(plugin, "init"):
            plugin.init()


def _hooks(request, phase):
    """The location's plugins' functions for phase, in order."""
    names = request.settings.get("plugins", "").split()
    plugins = [_load(name) for name in names]
    return [getattr(p, phase) for p in plugins if hasattr(p, phase)]


def access(request):
    for hook in _hooks(request, "access"):
        hook(request)
        if request.responded:
            return


def balancer(request, endpoints):
    for hook in _hooks(request, "balancer"):
        endpoint = hook(request, endpoints)
        if endpoint is not None:
            return endpoint
    return None


def header_filter(request):
    for hook in _hooks(request, "header_filter"):
        hook(request)


def log(request):
    for hook in _hooks(request, "log"):
        hook(request)


def error(request, status):
    return errors.problem_details(status)
