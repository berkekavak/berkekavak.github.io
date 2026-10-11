# berkekavak.com

Agentic AI consulting site of Berke Kavak, Berlin. English, Turkish and German.

- `content/en.json`, `content/tr.json`, `content/de.json`: all copy, per language
- `build.py`: renders `index.html`, `tr/index.html`, `de/index.html` from the content files
- `assets/`: shared `site.css`, `site.js`, images and logos

Edit a content file, then run:

```
python build.py
```

The generated pages are committed, so GitHub Pages needs no build step.
