from pathlib import Path
from typing import Dict
import yaml
from .config import Settings
from .providers import (
    GenericHTTPProvider,
    OllamaProvider,
    MistralProvider,
    BaseProvider,
)

_prompts = None


def load_prompts(path: str = ''):
    global _prompts
    if _prompts is None:
        path = path or str(Path(__file__).parent / "prompts.yaml")
        with open(path, "r") as f:
            _prompts = yaml.safe_load(f) or {}
    return _prompts


_PROVIDER_TYPES = {
    "generic": GenericHTTPProvider,
    "ollama": OllamaProvider,
    "mistral": MistralProvider,
}


class ProviderManager:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._instances: Dict[str, BaseProvider] = {}

    def get(self, name: str) -> BaseProvider:
        if name in self._instances:
            return self._instances[name]
        cfg = self._settings.providers.get(name)
        if not cfg:
            raise KeyError(f"Provider {name} not found")
        cls = _PROVIDER_TYPES.get(cfg.type, GenericHTTPProvider)
        inst = cls(cfg)
        self._instances[name] = inst
        return inst


def redaction(
    provider: BaseProvider,
    sujet: str,
    sources: list | None = None,
    meta: dict | None = None,
    format: str = "text",
) -> str:
    """Generate a redaction. If format=='html', instruct the model to return accessible HTML fragment."""
    prompts = load_prompts()
    template = prompts.get(
        "redaction", "Rédige un texte sur: {{ sujet }}. Sources: {{ sources }}"
    )
    # If HTML requested, prefix an instruction that asks for accessible HTML output
    if format == "html":
        html_instr = (
            "Retourne uniquement un fragment HTML accessible "
            "(balises sémantiques, titres, paragraphes, listes "
            "si besoin, et attributs ARIA appropriés). "
            "Ne fournis pas de page complète ni de styles CSS "
            "externes."
        )
        template = html_instr + "\n" + template

    rendered = template.replace("{{ sujet }}", sujet).replace(
        "{{ sources }}", str(sources or "")
    )
    out = provider.generate(
        rendered,
        sujet=sujet,
        sources=sources,
        meta=meta,
        format=format,
    )
    # If HTML output requested, apply the same cleaning to ensure it's storable
    if format == "html":
        out = _clean_html_fragment(out)
    return out


# Convenience helpers to use the service from a config file or CLI
def load_settings(path: str = "config.yaml") -> Settings:
    return Settings.load(path)


def redaction_by_name(
    provider_name: str,
    sujet: str,
    sources: list | None = None,
    meta: dict | None = None,
    config_path: str = "config.yaml",
    format: str = "text",
) -> str:
    """Load settings from `config_path`, create provider and run redaction."""
    settings = load_settings(config_path)
    pm = ProviderManager(settings)
    prov = pm.get(provider_name)
    return redaction(prov, sujet, sources=sources, meta=meta, format=format)


def _clean_html_fragment(s: str) -> str:
    """
    Clean HTML fragment from common LLM artifacts:
    - Remove Markdown code fences (```html or ```)
    - Replace literal backslash-n with real newlines
    - Replace literal backslash-quote with real quotes
    """
    import re

    if s is None:
        return s
    text = s.strip()

    # Remove Markdown fences like ```html or ```
    m = re.search(r"^```(?:html)?\s*(.*)\s*```$", text, flags=re.S)
    if m:
        text = m.group(1).strip()

    # Critical: Replace LITERAL \n sequences (two chars: backslash + n)
    # NOT Python escape sequences (which would be \\n in source)
    # The LLM outputs the actual characters '\' followed by 'n'
    text = text.replace(r"\n", "\n")  # literal \n → real newline
    text = text.replace(r"\t", "\t")  # literal \t → real tab
    text = text.replace(r"\"", '"')  # literal \" → real quote
    text = text.replace(r"\'", "'")  # literal \' → real quote

    # Strip surrounding whitespace again
    text = text.strip()
    return text


def mise_en_forme(provider: BaseProvider, texte: str) -> str:
    prompts = load_prompts()
    template = prompts.get(
        "mise_en_forme", "Formate le texte suivant en HTML accessible: {{ texte }}"
    )
    rendered = template.replace("{{ texte }}", texte)
    out = provider.generate(rendered, texte=texte)
    # Clean typical artifacts (fenced code blocks, escaped newlines, etc.)
    return _clean_html_fragment(out)


def mise_en_forme_by_name(
    provider_name: str, texte: str, config_path: str = "config.yaml"
) -> str:
    settings = load_settings(config_path)
    pm = ProviderManager(settings)
    prov = pm.get(provider_name)
    return mise_en_forme(prov, texte)


def list_providers(config_path: str = "config.yaml") -> list:
    settings = load_settings(config_path)
    return list(settings.providers.keys())
