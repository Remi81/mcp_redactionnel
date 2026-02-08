def test_clean_html_fragment():
    from mcp_redactionnel.service import _clean_html_fragment

    # Test 1: Remove fences with literal \n sequences
    raw = r"```html\n<article>\n <p>Bonjour</p>\n</article>\n```"
    cleaned = _clean_html_fragment(raw)
    assert cleaned.startswith('<article')
    assert '```' not in cleaned
    # Verify literal \n was converted to real newline
    assert r'\n' not in cleaned  # no literal backslash-n
    assert '\n' in cleaned  # but has real newlines

    # Test 2: Whitespace trimming
    raw2 = '\n\n<article>\n<p>Test</p>\n</article>\n'
    assert _clean_html_fragment(raw2).startswith('<article')
    
    # Test 3: Literal escaped quotes
    raw3 = r'<p id=\"test\">Content</p>'
    cleaned3 = _clean_html_fragment(raw3)
    assert cleaned3 == '<p id="test">Content</p>'
    assert r'\"' not in cleaned3
    
    # Test 4: Real-world Mistral output simulation
    raw4 = r'```html\n<article aria-labelledby=\"title\">\n  <h1 id=\"title\">Test</h1>\n</article>\n```'
    cleaned4 = _clean_html_fragment(raw4)
    assert cleaned4.startswith('<article')
    assert '"title"' in cleaned4
    assert r'\"' not in cleaned4
    assert '```' not in cleaned4
