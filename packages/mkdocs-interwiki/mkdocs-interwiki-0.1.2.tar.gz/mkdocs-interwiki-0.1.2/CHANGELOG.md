# Changelog

## 0.1.1 — 2025-10-05
- Fix: regex compiled without VERBOSE caused “unbalanced parenthesis”
- Improve: safer per-page overrides via extension handle instead of re-registering

## 0.1.0 — 2025-10-05
- Initial public release with DokuWiki-like `[[prefix>Target|Label]]` links
- Configurable `maps` and `extra` variables
- Per-page `interwiki_extra` overrides
- URL-encoding of `{target}`
