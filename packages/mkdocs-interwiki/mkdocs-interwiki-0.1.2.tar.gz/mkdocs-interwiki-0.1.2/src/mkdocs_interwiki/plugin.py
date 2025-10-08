from __future__ import annotations
from typing import Dict, Any
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from .interwiki import InterWikiExtension

class InterWikiPlugin(BasePlugin):
    config_scheme = (
        ('maps',  config_options.Type(dict, default={})),
        ('extra', config_options.Type(dict, default={})),
    )

    def on_config(self, config: MkDocsConfig, **kwargs):
        # Create and keep a handle to the extension instance
        self._ext = InterWikiExtension(maps=self.config.get('maps', {}),
                                       extra=self.config.get('extra', {}))
        config.markdown_extensions.append(self._ext)
        return config

    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files):
        # Merge per-page overrides (if any) into the extension before this page renders
        meta: Dict[str, Any] = page.meta or {}
        per_page_extra = meta.get('interwiki_extra', {})
        merged = dict(self.config.get('extra', {}))
        if isinstance(per_page_extra, dict):
            merged.update(per_page_extra)
        # Update the already-registered pattern
        self._ext.set_extra(merged)
        return markdown
