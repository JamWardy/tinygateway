"""Limits how many requests each client sends to a location, in fixed
windows, as ../DESIGN.md's "The rate_limit plugin" says."""

import math
import time

from ..errors import problem_details

WINDOWS = {"rate_limit_second": 1, "rate_limit_minute": 60,
           "rate_limit_hour": 3600}

# For each window's length: when the current one started, and its count
# for each (location, client).
_windows = {seconds: [None, {}] for seconds in WINDOWS.values()}


def access(request):
    limits = _limits(request)
    now = time.time()
    key = (request.location, request.state.get("user_id",
                                                request.remote_addr))
    windows = []  # (seconds, limit, count, seconds until it ends)
    for seconds, limit in limits:
        start = now // seconds * seconds
        window = _windows[seconds]
        if window[0] != start:
            window[0], window[1] = start, {}
        windows.append((seconds, limit, window[1].get(key, 0),
                        start + seconds - now))

    full = [ends for _, limit, count, ends in windows if count >= limit]
    if not full:
        for seconds, _, _, _ in windows:
            counts = _windows[seconds][1]
            counts[key] = counts.get(key, 0) + 1
        windows = [(s, limit, count + 1, ends)
                   for s, limit, count, ends in windows]

    # The longest window wins a tie, as nothing is left until it ends.
    _, limit, count, ends = min(windows,
                                key=lambda w: (w[1] - w[2], -w[0]))
    request.state["rate_limit_headers"] = [
        ("RateLimit-Limit", str(limit)),
        ("RateLimit-Remaining", str(max(limit - count, 0))),
        ("RateLimit-Reset", str(math.ceil(ends))),
    ]
    if full:
        wait = math.ceil(max(full))
        status, headers, body = problem_details(
            429, f"Too many requests; try again in {wait} seconds.",
            [("Retry-After", str(wait))])
        request.respond(status, headers, body)


def header_filter(request):
    request.reply_headers.extend(request.state.get("rate_limit_headers", ()))


def _limits(request):
    """(window seconds, limit) for each limit the location sets."""
    limits = []
    for name, seconds in WINDOWS.items():
        value = request.settings.get(name)
        if value is None:
            continue
        if not (value.isascii() and value.isdigit() and int(value) >= 1):
            raise ValueError(f"rate_limit: {name} must be a whole number "
                             f"from 1 up, not {value!r}")
        limits.append((seconds, int(value)))
    if not limits:
        raise ValueError("rate_limit: the location sets none of "
                         + ", ".join(WINDOWS))
    return limits
