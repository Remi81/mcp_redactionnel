from typing import Any, Optional
import httpx
from jinja2 import Template
from .config import ProviderConfig

class BaseProvider:
    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError


def _extract_path(obj: Any, path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    parts = path.split('.')
    cur = obj
    try:
        for p in parts:
            if isinstance(cur, list):
                idx = int(p)
                cur = cur[idx]
            else:
                cur = cur.get(p)
    except Exception:
        return None
    if isinstance(cur, str):
        return cur
    # fallback to stringify
    return None if cur is None else str(cur)

class GenericHTTPProvider(BaseProvider):
    def __init__(self, config: ProviderConfig):
        self.config = config

    def generate(self, prompt: str, **kwargs) -> str:
        import json

        template = self.config.body_template or '{"prompt": "{{ prompt }}"}'
        body = Template(template).render(prompt=prompt, **kwargs)
        headers = {k: Template(v).render(**kwargs) for k, v in (self.config.headers or {}).items()}

        # Try to send as JSON when the template renders valid JSON
        request_kwargs = {
            "headers": headers,
            "timeout": 30.0,
        }
        try:
            json_body = json.loads(body)
            request_kwargs["json"] = json_body
        except Exception:
            request_kwargs["content"] = body

        resp = httpx.request(
            self.config.method,
            self.config.endpoint,
            **request_kwargs,
        )
        # On error, include response body to ease debugging
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            content = None
            try:
                content = resp.json()
            except Exception:
                content = resp.text
            raise RuntimeError(
                f"HTTP {resp.status_code} from "
                f"{self.config.endpoint}: {content}"
            ) from exc

        try:
            data = resp.json()
        except Exception:
            return resp.text
        extracted = _extract_path(data, self.config.response_path)
        return extracted or (resp.text if isinstance(resp.text, str) else str(data))

class OllamaProvider(GenericHTTPProvider):
    def __init__(self, config: ProviderConfig):
        # Ollama usually expects JSON with 'prompt' and returns 'choices[0].message.content' or similar
        super().__init__(config)

class MistralProvider(GenericHTTPProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)

    def generate(self, prompt: str, **kwargs) -> str:
        # Build payload using Python dicts to avoid pitfalls
        model = (
            getattr(self.config, 'model', None)
            or kwargs.get('model')
            or 'mistral-small-latest'
        )
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': kwargs.get('max_tokens', 512),
            'stream': False,
        }
        headers = {k: Template(v).render(**kwargs) for k, v in (self.config.headers or {}).items()}
        resp = httpx.post(self.config.endpoint, headers=headers, json=payload, timeout=30.0)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            content = None
            try:
                content = resp.json()
            except Exception:
                content = resp.text
            raise RuntimeError(
                f"HTTP {resp.status_code} from "
                f"{self.config.endpoint}: {content}"
            ) from exc

        try:
            data = resp.json()
        except Exception:
            return resp.text
        extracted = _extract_path(data, self.config.response_path)
        return extracted or (resp.text if isinstance(resp.text, str) else str(data))
