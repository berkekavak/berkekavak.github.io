#!/usr/bin/env python3
"""Build the site: one page per language from content/*.json.

    python build.py

Outputs index.html (en), tr/index.html and de/index.html. CSS and JS live in
assets/ and are shared. Copy in the JSON files is trusted HTML (entities and
<strong> allowed).
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://berkekavak.com"
EMAIL = "berkekavak@hotmail.com"
LANGS = {"en": "", "tr": "tr/", "de": "de/"}
LANG_NAMES = {"en": "EN", "tr": "TR", "de": "DE"}

# Inline SVG wordmarks use currentColor so they follow the theme.
SVG_LOGOS = {
    "adidas": ("mark", "adidas"),
    "davies": ("word", "Davies"),
    "sompo": ("word", "Sompo"),
    "philips": ("word", "Philips"),
}
IMG_LOGOS = {
    "esn": '<img src="{r}assets/esn.png" alt="ESN" loading="lazy" width="360" height="360"><img class="word" src="{r}assets/more-nutrition.png" alt="More Nutrition" loading="lazy" width="576" height="196">',
    "pemco": '<img src="{r}assets/pemco.png" alt="PEMCO Insurance" loading="lazy" width="228" height="80">',
    "isyatirim": '<img src="{r}assets/is-yatirim.png" alt="İş Yatırım" loading="lazy" width="720" height="197">',
}


def svg(name):
    cls, label = SVG_LOGOS[name]
    s = open(os.path.join(ROOT, "assets", name + ".svg"), encoding="utf-8").read().strip()
    return s.replace("<svg", f'<svg class="{cls}" role="img" aria-label="{label}"', 1)


def logo(name, r):
    if name in SVG_LOGOS:
        return svg(name)
    return IMG_LOGOS[name].format(r=r)


def delay(i):
    d = i % 4
    return f' data-delay="{d}"' if d else ""


def render(c):
    lang = c["lang"]
    r = "" if lang == "en" else "../"
    a = c["a11y"]
    nav = c["nav"]
    hero = c["hero"]
    sv = c["services"]
    wk = c["work"]
    ap = c["approach"]
    ab = c["about"]
    ct = c["contact"]
    ft = c["footer"]

    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{SITE}/{p}">' for l, p in LANGS.items()
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}/">'

    lang_switch = '<div class="lang" aria-label="' + a["lang"] + '">' + "".join(
        f'<a href="{r}{p}"' + (' aria-current="page"' if l == lang else "") + f' lang="{l}" hreflang="{l}">{LANG_NAMES[l]}</a>'
        for l, p in LANGS.items()
    ) + "</div>"

    nav_links = "".join(
        f'<a href="#{k}">{nav[k]}</a>' for k in ("services", "work", "approach", "about")
    )

    hero_meta = "".join(f"<div><b>{m['b']}</b><span>{m['s']}</span></div>" for m in hero["meta"])

    logo_row = (
        f'<div title="adidas">{svg("adidas")}</div>'
        f'<div class="pair" title="ESN · More Nutrition"><img class="tile" src="{r}assets/esn.png" alt="ESN" loading="lazy" width="360" height="360"><img class="word" src="{r}assets/more-nutrition.png" alt="More Nutrition" loading="lazy" width="576" height="196"></div>'
        f'<div title="PEMCO Insurance"><img src="{r}assets/pemco.png" alt="PEMCO Insurance" loading="lazy" width="228" height="80"></div>'
        f'<div title="Davies">{svg("davies")}</div>'
        f'<div title="İş Yatırım"><img src="{r}assets/is-yatirim.png" alt="İş Yatırım" loading="lazy" width="720" height="197"></div>'
        f'<div title="Sompo">{svg("sompo")}</div>'
        f'<div title="Philips">{svg("philips")}</div>'
    )

    services = "".join(
        f'<article class="card reveal"{delay(i)}>'
        f'<span class="num">0{i + 1}</span>'
        f'<h3 class="h3">{s["title"]}</h3>'
        f'<p>{s["p"]}</p>'
        "<ul>" + "".join(f"<li>{ch}</li>" for ch in s["chips"]) + "</ul>"
        "</article>"
        for i, s in enumerate(sv["items"])
    )

    st = sv.get("stack")
    stack = ""
    if st:
        rows = "".join(f'<div><dt>{row["k"]}</dt><dd>{row["v"]}</dd></div>' for row in st["rows"])
        stack = (
            '<div class="stack reveal">'
            f'<div><p class="label">{st["label"]}</p><h3 class="h3">{st["h3"]}</h3><p>{st["p"]}</p></div>'
            f"<dl>{rows}</dl>"
            "</div>"
        )

    genai = "".join(
        f'<article class="work nda-card reveal"{delay(i)}>'
        f'<span class="tag">{wk["nda_tag"]}</span>'
        f'<h3 class="title">{w["title"]}</h3>'
        f'<span class="sector">{w["sector"]}</span>'
        f'<p>{w["p"]}</p>'
        f'<span class="result">{w["result"]}</span>'
        "</article>"
        for i, w in enumerate(wk["genai"])
    )

    ml = ""
    for i, w in enumerate(wk["ml"]):
        if w["logo"]:
            ml += (
                f'<article class="work reveal"{delay(i)}>'
                f'<div class="logo">{logo(w["logo"], r)}</div>'
                f'<span class="sector">{w["sector"]}</span>'
                f'<p>{w["p"]}</p>'
                f'<span class="result">{w["result"]}</span>'
                "</article>"
            )
        else:
            ml += (
                f'<article class="work more reveal"{delay(i)}>'
                f'<span class="sector">{w["sector"]}</span>'
                f'<p>{w["p"]}</p>'
                f'<a class="link" href="#contact">{w["link"]}</a>'
                "</article>"
            )

    steps = "".join(
        f'<div class="step reveal"{delay(i)}>'
        f'<p class="label">{s["label"]}</p>'
        f'<h3 class="h3">{s["title"]}</h3>'
        f'<p>{s["p"]}</p>'
        "</div>"
        for i, s in enumerate(ap["steps"])
    )
    principles = "".join(
        f'<div class="principle reveal"{delay(i)}>'
        f'<h3 class="h3">{p["title"]}</h3>'
        f'<p>{p["p"]}</p>'
        "</div>"
        for i, p in enumerate(ap["principles"])
    )

    bio = "".join(f"<p>{p}</p>" for p in ab["bio"])
    facts = ""
    for f in ab["facts"]:
        inner = f'<div><dt>{f["dt"]}</dt><dd>{f["dd"]} <span class="sub">{f["sub"]}</span></dd></div>'
        if f["logo"]:
            facts += (
                f'<div><img src="{r}assets/{f["logo"]}.svg" alt="{f["alt"]}" loading="lazy" width="64" height="40">'
                + inner + "</div>"
            )
        else:
            facts += f'<div class="no-logo">{inner}</div>'

    subject = ct["subject"].replace(" ", "%20")

    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>{c["title"]}</title>
<meta name="description" content="{c["description"]}">
<meta property="og:title" content="{c["og_title"]}">
<meta property="og:description" content="{c["og_description"]}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{c["locale"]}">
<meta property="og:url" content="{SITE}/{LANGS[lang]}">
<meta property="og:image" content="{SITE}/assets/berke-kavak.webp">
<link rel="canonical" href="{SITE}/{LANGS[lang]}">
{alternates}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%2317140F'/%3E%3Ctext x='50%25' y='54%25' dominant-baseline='middle' text-anchor='middle' font-family='-apple-system,Segoe UI,sans-serif' font-weight='700' font-size='34' fill='%23fff'%3EB%3C/text%3E%3C/svg%3E">
<script>
/* Apply the stored theme before first paint to avoid a flash. */
(function(){{try{{var t=localStorage.getItem('theme');if(t==='dark'||t==='light'){{document.documentElement.setAttribute('data-theme',t);}}}}catch(e){{}}}})();
</script>
<link rel="stylesheet" href="{r}assets/site.css">
</head>
<body>

<a class="brand" style="position:absolute;left:-9999px" href="#main">{a["skip"]}</a>

<nav class="nav" id="nav" aria-label="{a["nav"]}">
  <div class="wrap">
    <a class="brand" href="#top"><span class="dot" aria-hidden="true"></span>Berke Kavak</a>
    <div class="nav-links">{nav_links}</div>
    <a class="btn btn-primary nav-cta" href="#contact">{nav["cta"]}</a>
    {lang_switch}
    <button class="switch" id="theme" type="button" aria-label="{a["theme"]}" aria-pressed="false">
      <span class="knob" id="knob" aria-hidden="true">
        <svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
        <svg class="moon" viewBox="0 0 24 24" fill="currentColor"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
      </span>
    </button>
    <button class="menu-btn" id="menu-btn" type="button" aria-label="{a["menu_open"]}" data-open="{a["menu_open"]}" data-close="{a["menu_close"]}" aria-expanded="false" aria-controls="sheet">
      <svg class="bars" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
      <svg class="x" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
    </button>
  </div>
</nav>
<div class="scrim" id="scrim" aria-hidden="true"></div>
<div class="sheet" id="sheet" role="dialog" aria-label="{a["menu"]}" aria-modal="false">
  {nav_links}
  <a class="btn btn-primary" href="#contact">{nav["cta"]}</a>
  {lang_switch}
</div>

<main id="main">
  <header class="hero" id="top">
    <div class="wrap">
      <p class="label reveal">{hero["label"]}</p>
      <h1 class="display reveal" data-delay="1">{hero["h1"]}</h1>
      <p class="lead reveal" data-delay="2">{hero["lead"]}</p>
      <div class="hero-actions reveal" data-delay="3">
        <a class="btn btn-primary" href="#contact">{hero["cta"]}</a>
        <a class="btn btn-ghost" href="#work">{hero["cta2"]} <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M5 12l7 7 7-7"/></svg></a>
      </div>
      <div class="hero-meta reveal" data-delay="3">{hero_meta}</div>
    </div>
  </header>

  <div class="logos">
    <div class="wrap">
      <p class="label reveal">{c["logos_label"]}</p>
      <div class="logo-row reveal" data-delay="1">{logo_row}</div>
    </div>
  </div>

  <section id="services" class="alt">
    <div class="wrap">
      <div class="sec-head">
        <p class="label reveal">{sv["label"]}</p>
        <h2 class="h2 reveal" data-delay="1">{sv["h2"]}</h2>
        <p class="lead reveal" data-delay="2">{sv["lead"]}</p>
      </div>
      <div class="grid-3">{services}</div>
      {stack}
    </div>
  </section>

  <section id="work">
    <div class="wrap">
      <div class="sec-head">
        <p class="label reveal">{wk["label"]}</p>
        <h2 class="h2 reveal" data-delay="1">{wk["h2"]}</h2>
        <p class="lead reveal" data-delay="2">{wk["lead"]}</p>
      </div>
      <div class="work-group">
        <p class="label reveal">{wk["group1"]}</p>
        <div class="work-grid four">{genai}</div>
      </div>
      <div class="work-group">
        <p class="label reveal">{wk["group2"]}</p>
        <div class="work-grid">{ml}</div>
      </div>
    </div>
  </section>

  <section id="approach" class="alt">
    <div class="wrap">
      <div class="sec-head">
        <p class="label reveal">{ap["label"]}</p>
        <h2 class="h2 reveal" data-delay="1">{ap["h2"]}</h2>
        <p class="lead reveal" data-delay="2">{ap["lead"]}</p>
      </div>
      <div class="steps">{steps}</div>
      <div class="principles">{principles}</div>
    </div>
  </section>

  <section id="about">
    <div class="wrap">
      <div class="sec-head">
        <p class="label reveal">{ab["label"]}</p>
        <h2 class="h2 reveal" data-delay="1">{ab["h2"]}</h2>
      </div>
      <div class="about">
        <div class="bio reveal">
          <img class="portrait" src="{r}assets/berke-kavak.webp" alt="Berke Kavak" width="560" height="589">
          {bio}
        </div>
        <dl class="facts reveal" data-delay="1">{facts}</dl>
      </div>
    </div>
  </section>

  <section id="contact" class="contact">
    <div class="wrap">
      <p class="label reveal">{ct["label"]}</p>
      <h2 class="display reveal" data-delay="1">{ct["h2"]}</h2>
      <p class="lead reveal" data-delay="2">{ct["lead"]}</p>
      <div class="actions reveal" data-delay="3">
        <a class="btn btn-primary" href="mailto:{EMAIL}?subject={subject}">{ct["email_btn"]}</a>
        <a class="btn btn-ghost" href="https://www.linkedin.com/in/berke-kavak/" rel="noopener">LinkedIn</a>
        <a class="btn btn-ghost" href="https://github.com/berkekavak" rel="noopener">GitHub</a>
      </div>
      <p class="email reveal" data-delay="3">{ct["direct"]} <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
  </section>
</main>

<footer>
  <div class="wrap">
    <span>{ft["copy"]}</span>
    <span class="visits mono" id="visits" hidden><b id="visit-num"></b> {ft["visits"]}</span>
    <a class="up" href="#top">{ft["top"]}</a>
  </div>
</footer>

<script data-goatcounter="https://berkekavak.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
<script src="{r}assets/site.js"></script>
</body>
</html>
"""


def main():
    for lang, path in LANGS.items():
        c = json.load(open(os.path.join(ROOT, "content", lang + ".json"), encoding="utf-8"))
        assert c["lang"] == lang
        html = render(c)
        html = re.sub(r"\n{3,}", "\n\n", html)
        out = os.path.join(ROOT, path, "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        print(f"{out.replace(ROOT + os.sep, '')}: {len(html.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
