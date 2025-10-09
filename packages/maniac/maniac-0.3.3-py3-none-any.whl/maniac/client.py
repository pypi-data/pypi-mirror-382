# maniac/client_sync.py
from typing import Any, Dict, Iterable, Optional
from .transports.httpx_sync import HttpxTransport
from .token_manager import TokenManager
from .types import (
    ChatCompletion,
    ChatCompletionCreateParams,
    ChatCompletionChunk,
    ContainerCreateParams,
    Container,
    RegisterCompletionsParams,
    RegisterCompletionsSuccess,
)

import os
import json


# supabase edge functions expect maniac-apikey. the reason it isnt in Authorization: Bearer is that
# those edge functions also need to be able to be called from an authenticated sb client, which handles the bearer token and is not an api key
def _headers(
    api_key: Optional[str], extra: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    h = {"content-type": "application/json", "maniac-apikey": api_key or ""}
    if api_key:
        h["authorization"] = f"Bearer {api_key}"
    if extra:
        h.update(extra)
    return h


class Maniac:
    # initialize with standard arguments
    # we use TokenManager to handle the jwt token minting, so that we dont need to authenticate api keys on every request
    # we also use HttpxTransport which handles retries, reminting tokens on 401, etc
    def __init__(self, opts: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        opts = {**(opts or {}), **kwargs}
        self.apiKey = (
            opts.get("api_key")
            or opts.get("apiKey")
            or os.environ.get("MANIAC_API_KEY")
        )
        self.baseURL = (opts.get("baseURL") or "https://api.maniac.ai").rstrip("/")
        self.baseURLIsCustom = opts.get("baseURL") is not None
        tm = TokenManager(self.baseURL, self.apiKey or "")
        self._tx = HttpxTransport(self.baseURL, tm)

    def close(self) -> None:
        if hasattr(self._tx, "close"):
            self._tx.close()

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        self.close()

    # containers
    class _Containers:
        def __init__(self, p: "Maniac"):
            self._p = p

        # create a new container
        def create(
            self, params: ContainerCreateParams | None = None, **kw
        ) -> Container:
            body = json.dumps({**(params or {}), **kw})
            res = self._p._tx.request_json(
                "/functions/v1/containers-create-client",
                {"method": "POST", "headers": _headers(self._p.apiKey), "body": body},
            )
            return res.get("data")

        # get a container by label. currently, the containers-create-client edge function handles "get or create" logic
        def get(self, label_or_params, **kw) -> Container:
            params = (
                {"label": label_or_params}
                if isinstance(label_or_params, str)
                else {**(label_or_params or {}), **kw}
            )
            body = json.dumps(params)
            res = self._p._tx.request_json(
                "/functions/v1/containers-create-client",
                {"method": "POST", "headers": _headers(self._p.apiKey), "body": body},
            )
            return res.get("data")

    # expose containers to the client
    @property
    def containers(self):
        return Maniac._Containers(self)

    # completions
    class _Completions:
        def __init__(self, p: "Maniac"):
            self._p = p

        # register a new completions dataset
        def register(
            self, input: RegisterCompletionsParams | None = None, **kw
        ) -> RegisterCompletionsSuccess[Any]:
            input = {**(input or {}), **kw}
            container = input.get("container")
            dataset = input.get("dataset")
            if not container:
                raise RuntimeError("container is required")
            if not isinstance(dataset, list) or not dataset:
                raise RuntimeError("dataset must be a non-empty array")
            inferred = dataset[0].get("messages", [])[0].get("content")
            converted = []
            for datapoint in dataset:
                additional_parameters = {
                    k: v
                    for k, v in datapoint.items()
                    if k not in ("messages", "output")
                }
                converted.append(
                    {
                        "input": datapoint.get("messages"),
                        "output": datapoint.get("output"),
                        "system_prompt": datapoint.get("messages", [])[0].get(
                            "content"
                        ),
                        "additional_parameters": additional_parameters,
                    }
                )
            payload = {
                "task": {"system_prompt": inferred, "label": container.get("label")},
                "data": converted,
            }
            raw = self._p._tx.request_json(
                "/functions/v1/direct-insert",
                {
                    "method": "POST",
                    "headers": _headers(self._p.apiKey),
                    "body": json.dumps(payload),
                },
                subdomain="api",
            )
            return {
                "status": "ok",
                "label": container.get("label"),
                "dataCount": len(converted),
                "raw": raw,
            }

        # create a new completions
        def create(
            self, params: ChatCompletionCreateParams | None = None, **kw
        ) -> ChatCompletion:
            p = {**(params or {}), **kw}

            # split out a stream request

            stream = p.get("stream")
            if stream is True:
                print("streaming")
                return self.stream(params, **kw)

            container = p.get("container")
            messages = p.get("messages") or []

            rest = {k: v for k, v in p.items() if k not in ("container", "messages")}

            if not container:
                body = {
                    **rest,
                    "model": rest.get("model") or "openai/gpt-4o-mini",
                    "messages": messages,
                }
            else:
                cb = container.get("inference_body", {})
                sys = cb.get("system_prompt")
                rest_cb = {k: v for k, v in cb.items() if k != "system_prompt"}
                msgs = (
                    [{"role": "system", "content": sys}] + messages if sys else messages
                )
                body = {**rest, **rest_cb, "messages": msgs}

            res = self._p._tx.post_json_with_jwt(
                "/v1/chat/completions",
                body,
                subdomain="api" if self._p.baseURLIsCustom else "inference",
            )
            res["output_text"] = (
                (res.get("choices") or [{}])[0].get("message") or {}
            ).get("content", "")
            return res

        def stream(
            self, params: ChatCompletionCreateParams | None = None, **kw
        ) -> Iterable[ChatCompletionChunk]:
            p = {**(params or {}), **kw}
            container = p.get("container")
            messages = p.get("messages") or []
            rest = {k: v for k, v in p.items() if k not in ("container", "messages")}
            if not container:
                body = {
                    **rest,
                    "model": rest.get("model") or "openai/gpt-4o-mini",
                    "messages": messages,
                    "stream": True,
                }
            else:
                cb = container.get("inference_body", {})
                sys = cb.get("system_prompt")
                rest_cb = {k: v for k, v in cb.items() if k != "system_prompt"}
                msgs = (
                    [{"role": "system", "content": sys}] + messages if sys else messages
                )
                body = {**rest, **rest_cb, "messages": msgs, "stream": True}

            sub = "api" if self._p.baseURLIsCustom else "inference"

            for evt in self._p._tx.sse_events("/v1/chat/completions", body, sub):
                yield evt

    @property
    def chat(self):
        class _Chat:
            def __init__(self, p):
                self.completions = Maniac._Completions(p)

        return _Chat(self)
