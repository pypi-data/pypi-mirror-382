import sys
import traceback
import os
import logging
import inspect
import uuid
from six.moves import range
from six.moves import zip
from io import open
from datetime import datetime, timezone

from .version import __version__
from .plugins import default_plugin_manager
from .utils import filter_dict

logger = logging.getLogger("honeybadger.payload")

# Prevent infinite loops in exception cause chains
MAX_CAUSE_DEPTH = 15


def error_payload(exception, exc_traceback, config, fingerprint=None, tags=None):
    def _filename(name):
        return name.replace(config.project_root, "[PROJECT_ROOT]")

    def is_not_honeybadger_frame(frame):
        # TODO: is there a better way to do this?
        # simply looking for 'honeybadger' in the path doesn't seem
        # specific enough but this approach seems too specific and
        # would need to be updated if we re-factored the call stack
        # for building a payload.
        return not (
            "honeybadger" in frame[0]
            and frame[2]
            in ["notify", "_send_notice", "create_payload", "error_payload"]
        )

    def prepare_exception_payload(exception, exclude=None):
        return {
            "token": str(uuid.uuid4()),
            "class": type(exception) is dict
            and exception["error_class"]
            or exception.__class__.__name__,
            "message": type(exception) is dict
            and exception["error_message"]
            or str(exception),
            "backtrace": [
                dict(
                    number=f[1],
                    file=_filename(f[0]),
                    method=f[2],
                    source=read_source(f),
                )
                for f in reversed(tb)
            ],
        }

    def extract_exception_causes(exception):
        """
        Traverses the __cause__ chain of an exception and returns a list of prepared payloads.
        Limits depth to prevent infinite loops from circular references.
        """
        causes = []
        depth = 0

        while (
            getattr(exception, "__cause__", None) is not None
            and depth < MAX_CAUSE_DEPTH
        ):
            exception = exception.__cause__
            causes.append(prepare_exception_payload(exception))
            depth += 1

        if depth == MAX_CAUSE_DEPTH:
            causes.append(
                {
                    "token": str(uuid.uuid4()),
                    "class": "HoneybadgerWarning",
                    "type": "HoneybadgerWarning",
                    "message": f"Exception cause chain truncated after {MAX_CAUSE_DEPTH} levels. Possible circular reference.",
                }
            )

        return causes

    if exc_traceback:
        tb = traceback.extract_tb(exc_traceback)
    else:
        tb = [f for f in traceback.extract_stack() if is_not_honeybadger_frame(f)]

    logger.debug(tb)

    payload = prepare_exception_payload(exception)
    payload["causes"] = extract_exception_causes(exception)
    payload["tags"] = tags or []

    if fingerprint is not None:
        payload["fingerprint"] = fingerprint and str(fingerprint).strip() or None

    return payload


def read_source(frame, source_radius=3):
    if os.path.isfile(frame[0]):
        with open(frame[0], "rt", encoding="utf-8") as f:
            contents = f.readlines()

        start = max(1, frame[1] - source_radius)
        end = min(len(contents), frame[1] + source_radius)

        return dict(zip(range(start, end + 1), contents[start - 1 : end]))

    return {}


def server_payload(config):
    return {
        "project_root": config.project_root,
        "environment_name": config.environment,
        "hostname": config.hostname,
        "time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pid": os.getpid(),
        "stats": stats_payload(),
    }


def stats_payload():
    try:
        import psutil
    except ImportError:
        return {}
    else:
        s = psutil.virtual_memory()
        loadavg = psutil.getloadavg()

        free = float(s.free) / 1048576.0
        buffers = hasattr(s, "buffers") and float(s.buffers) / 1048576.0 or 0.0
        cached = hasattr(s, "cached") and float(s.cached) / 1048576.0 or 0.0
        total_free = free + buffers + cached
        payload = {}

        payload["mem"] = {
            "total": float(s.total) / 1048576.0,  # bytes -> megabytes
            "free": free,
            "buffers": buffers,
            "cached": cached,
            "total_free": total_free,
        }

        payload["load"] = dict(zip(("one", "five", "fifteen"), loadavg))

        return payload


def create_payload(
    exception,
    exc_traceback=None,
    config=None,
    context=None,
    fingerprint=None,
    correlation_context=None,
    tags=None,
):
    # if using local_variables get them
    local_variables = None
    if config and config.report_local_variables:
        try:
            local_variables = filter_dict(
                inspect.trace()[-1][0].f_locals, config.params_filters
            )
        except Exception as e:
            pass

    if exc_traceback is None:
        exc_traceback = sys.exc_info()[2]

    # if context is None, Initialize as an emptty dict
    if not context:
        context = {}

    payload = {
        "notifier": {
            "name": "Honeybadger for Python",
            "url": "https://github.com/honeybadger-io/honeybadger-python",
            "version": __version__,
        },
        "error": error_payload(exception, exc_traceback, config, fingerprint, tags),
        "server": server_payload(config),
        "request": {"context": context, "local_variables": local_variables},
    }

    if correlation_context:
        payload["correlation_context"] = correlation_context

    return default_plugin_manager.generate_payload(payload, config, context)
