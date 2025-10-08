from __future__ import annotations
import re
import uuid
from typing import Dict, Any, Tuple, List
from urllib.parse import quote
from markdown import Extension
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import InlineProcessor
from markdown.postprocessors import Postprocessor
from xml.etree.ElementTree import Element

# Verbose regex, enabled via (?x) so Markdown won't strip comments.
INTERWIKI_RE = r"""(?x)
\[\[                             # [[
(?P<prefix>[A-Za-z0-9_\-]+)      # prefix
>                                # >
(?P<target>[^\]|]+?)             # target
(?:\|(?P<label>[^\]]+))?         # optional |Label
\]\]                             # ]]
"""

# A simpler, non-verbose matcher for the preprocessor (works line-by-line).
PRE_IW_RE = re.compile(r"\[\[([A-Za-z0-9_\-]+)>([^\]|]+?)(?:\|([^\]]+))?\]\]")

class InterWikiPreprocessor(Preprocessor):
    """
    Replaces [[prefix>target|label]] with placeholders BEFORE block parsing (tables),
    so '|' won't be treated as a table column separator.
    """
    def __init__(self, md, store: Dict[str, Tuple[str, str, str]]):
        super().__init__(md)
        self.store = store

    def run(self, lines: List[str]) -> List[str]:
        out = []
        for line in lines:
            def repl(m):
                prefix = (m.group(1) or "").strip()
                target = (m.group(2) or "").strip()
                label  = (m.group(3) or "").strip()
                key = f"IW-{uuid.uuid4().hex}"
                # Store raw values; we’ll resolve to href later
                self.store[key] = (prefix, target, label)
                return key  # placeholder token (no pipes)
            out.append(PRE_IW_RE.sub(repl, line))
        return out

class InterWikiPattern(InlineProcessor):
    """
    Inline matcher for placeholders emitted by the preprocessor.
    We *don’t* parse [[...]] here anymore; we just replace placeholders with <a>.
    """
    def __init__(self, pattern: str, maps: Dict[str, str], extra: Dict[str, Any], store: Dict[str, Tuple[str, str, str]]):
        super().__init__(pattern)  # pattern is a simple placeholder matcher
        self.maps = maps or {}
        self.extra = extra or {}
        self.store = store

    def handleMatch(self, m, data):
        key = m.group('key')
        if key not in self.store:
            return None, m.start(0), m.end(0)

        prefix, target_raw, label = self.store.pop(key)

        if prefix not in self.maps:
            return None, m.start(0), m.end(0)

        template = self.maps[prefix]
        target_encoded = quote(target_raw, safe="/:@()!$*,;=+-._~")

        fmt_vars = dict(self.extra)
        fmt_vars["target"] = target_encoded

        try:
            href = template.format(**fmt_vars)
        except KeyError:
            return None, m.start(0), m.end(0)

        a = Element('a')
        a.set('href', href)
        a.text = label if label else target_raw
        return a, m.start(0), m.end(0)

class InterWikiCleanup(Postprocessor):
    """
    If any placeholders survive (e.g., unknown prefix), revert them to original text form.
    """
    def __init__(self, md, store: Dict[str, Tuple[str, str, str]]):
        super().__init__(md)
        self.store = store

    def run(self, text: str) -> str:
        for key, (prefix, target, label) in list(self.store.items()):
            pretty = f"[[{prefix}>{target}" + (f"|{label}]]" if label else "]]")
            text = text.replace(key, pretty)
            self.store.pop(key, None)
        return text

class InterWikiExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'maps':  [{}, 'Map of prefixes to URL templates'],
            'extra': [{}, 'Extra template variables'],
            'preprocess': [True, 'Replace interwiki with placeholders before block parsing'],
        }
        super().__init__(**kwargs)
        self._maps = self.getConfig('maps') or {}
        self._extra = self.getConfig('extra') or {}
        self._store: Dict[str, Tuple[str, str, str]] = {}
        self._pattern: InterWikiPattern | None = None
        self._pre: InterWikiPreprocessor | None = None

    def set_extra(self, extra: Dict[str, Any] | None):
        self._extra = extra or {}
        if self._pattern is not None:
            self._pattern.extra = self._extra

    def extendMarkdown(self, md):
        # Optional preprocessor (before 'tables'); lower number = earlier
        if self.getConfig('preprocess'):
            self._pre = InterWikiPreprocessor(md, self._store)
            md.preprocessors.register(self._pre, 'interwiki_pre', 18)
            # Tables is registered at 25 by Python-Markdown's tables ext; 18 runs earlier.

        # Placeholder inline pattern: match tokens like IW-<hex>
        placeholder_re = r"(?P<key>IW\-[0-9a-f]{32})"
        self._pattern = InterWikiPattern(placeholder_re, self._maps, self._extra, self._store)
        md.inlinePatterns.register(self._pattern, 'interwiki', 175)

        # Cleanup after HTML is assembled
        md.postprocessors.register(InterWikiCleanup(md, self._store), 'interwiki_cleanup', 5)
