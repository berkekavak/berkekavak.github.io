# berkekavak.com

Agentic AI consulting site (working name: Pappel AI), Berlin. English, Turkish and German.

- `content/en.json`, `content/tr.json`, `content/de.json`: all copy, per language. `{brand}` is replaced at build time.
- `build.py`: renders `index.html`, `tr/index.html`, `de/index.html`, plus `impressum/` and `datenschutz/` (German legal pages). Brand name, email and optional form endpoint are constants at the top.
- `assets/`: shared `site.css`, `site.js`, images and logos

Edit a content file or a constant, then run:

```
python build.py
```

The generated pages are committed, so GitHub Pages needs no build step.

Before going live: fill the placeholders in `build.py` (IMPRESSUM and DATENSCHUTZ: address, VAT status) and optionally set `FORM_ENDPOINT` to a form service URL. Without an endpoint the contact form opens the visitor's mail client with the message prefilled.
