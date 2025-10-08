from pathlib import Path
from setuptools import setup, find_packages

ROOT = Path(__file__).parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
CHANGES = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8") if (ROOT / "CHANGELOG.md").exists() else ""

setup(
    name="mkdocs-interwiki",
    version="0.1.2",  # ← bump for each release
    description="DokuWiki-like InterWiki links for MkDocs",
    long_description=README + "\n\n" + CHANGES,
    long_description_content_type="text/markdown",
    author="Gobidesert",
    author_email="gobidesert.mf@gmail.com",
    url="https://github.com/yourname/mkdocs-interwiki",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "mkdocs>=1.4",
        "markdown>=3.4",
    ],
    include_package_data=True,
    keywords=["mkdocs", "markdown", "interwiki", "dokuwiki", "plugin"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: MkDocs",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Documentation",
        "Topic :: Text Processing :: Markup",
    ],
    entry_points={
        "mkdocs.plugins": [
            "interwiki = mkdocs_interwiki.plugin:InterWikiPlugin",
        ]
    },
    project_urls={
        "Source": "https://github.com/yourname/mkdocs-interwiki",
        "Tracker": "https://github.com/yourname/mkdocs-interwiki/issues",
    },
    # If you want wheels: python -m pip install wheel; then python setup.py bdist_wheel
    zip_safe=False,
)
