from mcp_redactionnel.service import redaction_by_name, mise_en_forme_by_name, list_providers


class DummyProvider:
    def __init__(self):
        self.calls = []

    def generate(self, prompt, **kwargs):
        self.calls.append((prompt, kwargs))
        return "DUMMY:" + prompt


def test_redaction_by_name(monkeypatch, tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "providers:\n  dummy:\n    type: generic\n    endpoint: 'http://example'\n"
    )

    # Patch ProviderManager.get to return our dummy provider
    monkeypatch.setattr("mcp_redactionnel.service.ProviderManager.get", lambda self, name: DummyProvider())

    out = redaction_by_name("dummy", "Sujet de test", config_path=str(cfg))
    assert out.startswith("DUMMY:")
    assert "Sujet de test" in out


def test_mise_en_forme_by_name(monkeypatch, tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "providers:\n  dummy:\n    type: generic\n    endpoint: 'http://example'\n"
    )

    monkeypatch.setattr("mcp_redactionnel.service.ProviderManager.get", lambda self, name: DummyProvider())

    out = mise_en_forme_by_name("dummy", "Un texte à formater", config_path=str(cfg))
    assert out.startswith("DUMMY:")
    assert "Un texte à formater" in out


def test_list_providers(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "providers:\n  p1:\n    type: generic\n    endpoint: 'http://x'\n"
        "  p2:\n    type: generic\n    endpoint: 'http://y'\n"
    )

    res = list_providers(config_path=str(cfg))
    assert set(res) == {"p1", "p2"}


def test_redaction_html_prompt(monkeypatch, tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "providers:\n  dummy:\n    type: generic\n    endpoint: 'http://example'\n"
    )

    # Dummy provider to capture the prompt
    dp = DummyProvider()
    monkeypatch.setattr(
        "mcp_redactionnel.service.ProviderManager.get",
        lambda self, name: dp,
    )

    out = redaction_by_name(
        "dummy", "Sujet texte", config_path=str(cfg), format='text'
    )
    assert out.startswith("DUMMY:")
    # Ensure the prompt requests plain text (no HTML)
    # and mentions paragraphs or 'sans balises'
    assert any(
        'sans balises' in call[0]
        or 'paragraph' in call[0]
        or 'paragraphes' in call[0]
        for call in dp.calls
    )
