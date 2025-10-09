# TinyEdgeLLM Documentation

This directory contains the MkDocs documentation for TinyEdgeLLM.

## Building Documentation Locally

1. Install documentation dependencies:
```bash
pip install -e ".[docs]"
```

2. Serve documentation locally:
```bash
mkdocs serve
```

3. Build documentation:
```bash
mkdocs build
```

## Documentation Structure

- `index.md` - Main documentation page
- `stylesheets/extra.css` - Custom CSS styles
- `requirements.txt` - Documentation dependencies

## Deployment

Documentation is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the `main` branch.

The live documentation is available at: https://krish567366.github.io/tinyedgellm/