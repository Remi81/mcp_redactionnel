p = 'test.html'
s = open(p, 'r', encoding='utf-8').read()
print('RAW preview (first 400 chars):')
print(s[:400])

# Step 1: unescape visible \n and \t and \" sequences
s2 = s.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')

# Step 2: strip leading/trailing whitespace
s2 = s2.strip()

# Step 3: remove markdown fences if present
if s2.startswith('```'):
    # find first newline after opening fence
    # remove leading fence line
    lines = s2.split('\n')
    if lines[0].startswith('```'):
        # remove first line
        lines = lines[1:]
    # remove trailing fence if present
    if lines and lines[-1].startswith('```'):
        lines = lines[:-1]
    s3 = '\n'.join(lines).strip()
else:
    s3 = s2

print('\n--- CLEANED PREVIEW ---\n')
print(s3[:1000])

# Simple sanity check: ensure it begins with <
if not s3.startswith('<'):
    print(
        '\n[Warning] cleaned content does not start with "<" '
        '— may not be valid HTML fragment'
    )
else:
    print('\n[OK] cleaned content looks like HTML fragment')
