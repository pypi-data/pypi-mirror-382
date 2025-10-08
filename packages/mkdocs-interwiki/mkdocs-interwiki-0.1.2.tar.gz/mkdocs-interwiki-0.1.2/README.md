# mkdocs-interwiki

DokuWiki-like **InterWiki** links for MkDocs.

## Usage

Write links like:
```

[[wp>Python|Wikipedia: Python]]
[[gh>mkdocs/mkdocs|MkDocs on GitHub]]
[[issue>1234|Bug #1234]]

````

Configure in `mkdocs.yml`:
```yaml
plugins:
  - interwiki:
      maps:
        wp: "https://en.wikipedia.org/wiki/{target}"
        gh: "https://github.com/{target}"
        issue: "https://github.com/{repo}/issues/{target}"
      extra:
        repo: "yourorg/yourrepo"
````

Per-page override (front matter):

```yaml
interwiki_extra:
  repo: "other-org/other-repo"
```

## Install

```bash
pip install mkdocs-interwiki
```

## License

MIT
