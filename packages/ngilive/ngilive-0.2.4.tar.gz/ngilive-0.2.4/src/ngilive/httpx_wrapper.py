import functools
import json
import logging
from typing import Callable, ParamSpec

import httpx

from ngilive.log import default_handler


P = ParamSpec("P")


class HTTPXWrapper:
    def __init__(self, loglevel) -> None:
        self.get = self._log_call(httpx.get)
        self.post = self._log_call(httpx.post)

        self._logger = logging.getLogger("ngilive.httpx")
        self._logger.setLevel(loglevel)
        if not self._logger.handlers:
            self._logger.addHandler(default_handler())

    def _log_call(self, fn: Callable[P, httpx.Response]) -> Callable[P, httpx.Response]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> httpx.Response:
            url = args[0]
            params = kwargs.get("params", {})

            _params = (
                " ".join(f"{k}={v}" for k, v in params.items())
                if isinstance(params, dict)
                else ""
            )

            resp: httpx.Response = fn(*args, **kwargs)

            status_code = resp.status_code

            response_body = ""
            if status_code >= 400:
                response_body = " "
                try:
                    response_body += json.dumps(resp.json(), ensure_ascii=False)
                except Exception:
                    try:
                        response_body += resp.text
                    except Exception:
                        response_body = ""

                self._logger.error(
                    f"{fn.__name__.upper()} {url} {_params} {status_code}{response_body}"
                )
            else:
                self._logger.debug(
                    f"{fn.__name__.upper()} {url} {_params} {status_code}"
                )

            return resp

        return wrapper
