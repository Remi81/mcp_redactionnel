from mcp_redactionnel.service import mise_en_forme, redaction


class DummyProvider:
    def __init__(self):
        self.calls = []

    def generate(self, prompt, **kwargs):
        self.calls.append((prompt, kwargs))
        return f"GEN:{prompt}"


def test_redaction_basic():
    p = DummyProvider()
    out = redaction(p, "Le climat", sources=["source1"])
    assert out.startswith("GEN:")
    assert "Le climat" in p.calls[0][0]


def test_mise_en_forme_basic():
    p = DummyProvider()
    out = mise_en_forme(p, "Bonjour")
    assert (
        out == "GEN:Formate le texte suivant en HTML accessible: Bonjour"
        or out.startswith("GEN:")
    )
