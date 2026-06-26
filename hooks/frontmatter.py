"""MkDocs hook: render each page's YAML frontmatter as a visible, collapsible block.

The KB's framework/pipeline/app pages carry rich YAML frontmatter (triggers, funding,
activations, indicators…) — the structured half of the content. MkDocs parses that into
`page.meta` and would otherwise hide it. This prepends it as a collapsed "Page details"
admonition so the site mirrors the *full* page, not just the prose body.
"""
import yaml

# keys that are display/markup concerns, not KB content — don't echo them
_SKIP = {"hide", "template", "search", "title", "description"}


def on_page_markdown(markdown, page, config, files):
    meta = {k: v for k, v in (page.meta or {}).items() if k not in _SKIP}
    if not meta:
        return markdown
    try:
        dump = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=100).rstrip()
    except yaml.YAMLError:
        return markdown
    body = "\n".join("    " + line for line in dump.splitlines())
    block = f'??? abstract "Page details (frontmatter)"\n\n    ```yaml\n{body}\n    ```\n\n'
    return block + markdown
