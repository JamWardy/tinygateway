"""Lets pages from other origins call the API, as ../DESIGN.md's "The cors
plugin" says."""

KONG_METHODS = "GET, HEAD, PUT, PATCH, POST, DELETE, OPTIONS, TRACE, CONNECT"


def access(request):
    if not _is_preflight(request):
        return
    headers = [("Access-Control-Allow-Methods",
                request.settings.get("cors_methods", KONG_METHODS))]
    allowed_headers = request.settings.get(
        "cors_headers", _header(request, "Access-Control-Request-Headers"))
    if allowed_headers:
        headers.append(("Access-Control-Allow-Headers", allowed_headers))
    max_age = request.settings.get("cors_max_age")
    if max_age:
        headers.append(("Access-Control-Max-Age", max_age))
    # Access-Control-Allow-Origin is added in header_filter, as for every
    # reply.
    request.respond(204, headers)


def header_filter(request):
    origin = _header(request, "Origin")
    allowed = request.settings.get("cors_origins", "").split()
    if origin is None or not ("*" in allowed or origin in allowed):
        return
    request.reply_headers[:] = [
        (name, value) for name, value in request.reply_headers
        if name.lower() != "access-control-allow-origin"]
    if "*" in allowed:
        request.reply_headers.append(("Access-Control-Allow-Origin", "*"))
    else:
        request.reply_headers.append(("Access-Control-Allow-Origin", origin))
        request.reply_headers.append(("Vary", "Origin"))


def _is_preflight(request):
    return (request.method == "OPTIONS"
            and _header(request, "Origin") is not None
            and _header(request, "Access-Control-Request-Method") is not None)


def _header(request, name):
    # None for a request that couldn't be read.
    for key, value in request.headers or ():
        if key.lower() == name.lower():
            return value
    return None
