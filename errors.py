"""Errors as Problem Details (RFC 9457), as ../DESIGN.md's "Errors" says."""

import http
import json


def problem_details(status, detail=None, headers=()):
    """The reply for status: its own words as the title, as for any error
    without a title of its own."""
    try:
        title = http.HTTPStatus(status).phrase
    except ValueError:
        title = "Error"
    problem = {"title": title, "status": status}
    if detail is not None:
        problem["detail"] = detail
    headers = [("Content-Type", "application/problem+json"), *headers]
    return status, headers, json.dumps(problem)
