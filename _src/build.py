"""Builds the static site from content.py and manifest.json.

Run from anywhere:  python3 _src/build.py
Images are produced by process.py (from the portfolio crops) and listed in manifest.json.
"""
import json, os, html
from PIL import Image
import content as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.dirname(os.path.abspath(__file__))
MAN = json.load(open(os.path.join(SRC, "manifest.json")))
P = C.PERSON
CH = dict(C.CHAPTERS)
BY = {p["slug"]: p for p in C.PROJECTS}
CV_UK = "/cv/Luca-Piergentili-CV-UK.pdf"
CV_EU = "/cv/Luca-Piergentili-CV-EU-Swiss.pdf"
e = html.escape


def img(slug, n):
    return MAN[slug][n - 1]


def fit(slug, n):
    """'contain' when the image sits on a white background (renders, drawings), else 'cover'."""
    path = os.path.join(ROOT, "assets/img", slug, img(slug, n)["sm"])
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = [im.getpixel((x, y)) for x, y in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]]
    return "contain" if all(min(c) > 238 for c in px) else "cover"


NAV = [("/", "Home"), ("/projects/", "Projects"), ("/experience.html", "Experience"), ("/about.html", "About")]


def page(title, body, active="", desc="", noindex=False, og_img="/assets/img/va-55/1.jpg"):
    full = f"{title} · {P['name']}" if title else f"{P['name']} · Aerospace Engineering Portfolio"
    desc = desc or f"Portfolio of {P['name']}, {P['degree']} student at the {P['uni']}."
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{h}"{cur if active == h else ""}>{t}</a>' for h, t in NAV)
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
{robots}
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="https://lucapierg03.github.io{og_img}">
<meta property="og:type" content="website">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/"><span class="brand-mark">LP</span><span class="brand-name">{P['name']}</span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu"><span></span><span></span><span></span></button>
    <nav id="site-nav" class="site-nav">{nav}<a class="nav-cta" href="/about.html#contact">Contact</a></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <div>
      <strong>{P['name']}</strong><br>
      <span class="muted">{P['degree']} · {P['uni']} · {P['grad']}</span>
    </div>
    <div class="footer-links">
      <a href="mailto:{P['email']}">{P['email']}</a>
      <a href="tel:{P['phone_href']}">{P['phone']}</a>
      <a href="{P['linkedin']}" rel="me noopener" target="_blank">LinkedIn</a>
    </div>
  </div>
</footer>
<div class="lightbox" hidden>
  <button class="lb-close" aria-label="Close">×</button>
  <button class="lb-prev" aria-label="Previous image">‹</button>
  <figure><img alt=""><figcaption></figcaption></figure>
  <button class="lb-next" aria-label="Next image">›</button>
</div>
<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""


def cv_buttons(cls=""):
    return (f'<div class="cv-buttons {cls}">'
            f'<a class="btn btn-ghost" href="{CV_UK}" download>CV (UK) <span aria-hidden="true">↓</span></a>'
            f'<a class="btn btn-ghost" href="{CV_EU}" download>CV (EU / Swiss) <span aria-hidden="true">↓</span></a>'
            f'</div>')


def tags(p):
    return "".join(f'<span class="tag tag-{c}">{CH[c]}</span>' for c in p["chapters"])


def card(p, big=False):
    if p.get("cover"):
        m = img(p["slug"], p["cover"])
        media = (f'<img src="/assets/img/{p["slug"]}/{m["sm"]}" width="{m["sw"]}" height="{m["sh"]}" '
                 f'alt="{e(p["title"])}" loading="lazy" class="fit-{fit(p["slug"], p["cover"])}">')
    else:
        n, lab = p["stat"]
        media = f'<div class="stat-tile"><span>{n}</span>{lab}</div>'
    return f"""<a class="card{' card-big' if big else ''}" href="/projects/{p['slug']}.html" data-chapters="{' '.join(p['chapters'])}">
  <div class="card-media">{media}</div>
  <div class="card-body">
    <div class="tags">{tags(p)}</div>
    <h3>{e(p['title'])}</h3>
    <p>{e(p['card'])}</p>
  </div>
</a>"""


def figure(slug, n, cls="", group="g"):
    m = img(slug, n)
    return (f'<figure class="shot {cls}"><a href="/assets/img/{slug}/{m["src"]}" class="lb" data-group="{group}" '
            f'data-caption="{e(m["cap"])}"><img src="/assets/img/{slug}/{m["sm"]}" width="{m["sw"]}" height="{m["sh"]}" '
            f'alt="{e(m["cap"])}" loading="lazy" class="fit-{fit(slug, n)}"></a>'
            f'<figcaption>{e(m["cap"])}</figcaption></figure>')


# ---------- Home ----------
def home():
    me = MAN["_me"]
    stats = "".join(f'<div class="stat"><strong>{n}</strong><span>{e(t)}</span></div>' for n, t in C.HOME_STATS)
    feat = "".join(card(p, True) for p in C.PROJECTS if p.get("featured"))
    exp = "".join(
        f'<li><span class="xp-dates">{x["dates"]}</span><span class="xp-role"><strong>{e(x["org"])}</strong> · {e(x["role"])}</span></li>'
        for x in C.EXPERIENCE)
    chips = "".join(f'<a class="chip" href="/projects/#{k}">{v}</a>' for k, v in C.CHAPTERS)
    body = f"""
<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-text">
      <p class="eyebrow">{P['degree']} · {P['uni']}</p>
      <h1>{P['name']}</h1>
      <p class="lead">{e(C.HOME_LEAD)}</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="/projects/">See my projects</a>
        <a class="btn btn-ghost" href="/about.html#contact">Get in touch</a>
      </div>
      {cv_buttons('cv-small')}
    </div>
    <div class="hero-photo">
      <img src="/assets/img/me/luca.jpg" width="{me['w']}" height="{me['h']}" alt="Portrait of {P['name']}">
    </div>
  </div>
</section>
<section class="band">
  <div class="wrap stats">{stats}</div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>Featured projects</h2><a class="more" href="/projects/">All projects →</a></div>
    <div class="grid grid-3">{feat}</div>
    <div class="chip-row"><span class="muted">Browse by chapter:</span>{chips}</div>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap two-col">
    <div>
      <h2>Experience</h2>
      <p class="muted">Two industrial placements, an airline internship and an industry design challenge.</p>
      <a class="more" href="/experience.html">Full experience →</a>
    </div>
    <ul class="xp-list">{exp}</ul>
  </div>
</section>
<section class="cta">
  <div class="wrap cta-inner">
    <div><h2>Looking for a graduate role from summer 2027</h2>
    <p>Aerospace and engineering design roles across Switzerland, Europe and the UK.</p></div>
    <a class="btn btn-light" href="/about.html#contact">Contact me</a>
  </div>
</section>"""
    return page("", body, "/")


# ---------- Projects index ----------
def projects_index():
    btns = '<button class="filter is-active" data-filter="all">All</button>' + "".join(
        f'<button class="filter" data-filter="{k}">{v}</button>' for k, v in C.CHAPTERS)
    cards = "".join(card(p) for p in C.PROJECTS)
    body = f"""
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Portfolio</p>
    <h1>Projects</h1>
    <p class="lead">Industry placements, university design projects, school research and things I build for fun. Filter by chapter, or open any project for the full story and images.</p>
    <div class="filters" role="toolbar" aria-label="Filter projects">{btns}</div>
  </div>
</section>
<section class="section section-tight">
  <div class="wrap"><div class="grid grid-3 project-grid">{cards}</div></div>
</section>"""
    return page("Projects", body, "/projects/", "All of Luca Piergentili's engineering projects.")


# ---------- Project pages ----------
def project(p, prev, nxt):
    slug = p["slug"]
    n_imgs = len(MAN.get(slug, []))
    hero = ""
    if n_imgs and not p.get("sections"):
        hero = f'<div class="wrap">{figure(slug, 1, "hero-shot")}</div>'
    stats = ""
    if p.get("stats"):
        stats = '<div class="stats stats-card">' + "".join(
            f'<div class="stat"><strong>{n}</strong><span>{e(t)}</span></div>' for n, t in p["stats"]) + "</div>"
    did = ""
    if p.get("did"):
        did = "<h2>What I did</h2><ul class=\"ticks\">" + "".join(f"<li>{e(d)}</li>" for d in p["did"]) + "</ul>"
    sections = ""
    if p.get("sections"):
        for s in p["sections"]:
            figs = "".join(figure(slug, n) for n in s["imgs"])
            para = f'<p>{e(s["p"])}</p>' if s["p"] else ""
            sections += f'<section class="part"><h2>{e(s["h"])}</h2>{para}' + (
                f'<div class="gallery">{figs}</div>' if figs else "") + "</section>"
    gallery = ""
    if n_imgs > 1 and not p.get("sections"):
        gallery = '<h2 class="gallery-title">Gallery</h2><div class="gallery">' + "".join(
            figure(slug, n) for n in range(2, n_imgs + 1)) + "</div>"
    skills = "".join(f'<span class="chip chip-static">{e(s)}</span>' for s in p["skills"])
    docs = ""
    if p.get("docs"):
        rows = ""
        for folder, fname, label in p["docs"]:
            href = f"/docs/{folder}/{fname}"
            size = os.path.getsize(os.path.join(ROOT, href.lstrip("/"))) / 1e6
            size = f"{size:.1f} MB" if size >= 1 else f"{size * 1000:.0f} KB"
            rows += (f'<li><a class="doc-view" href="{href}" target="_blank" rel="noopener">{e(label)}</a>'
                     f'<span class="doc-meta">PDF, {size} · <a href="{href}" download>Download</a></span></li>')
        docs = f'<div class="side-docs"><span class="dt">Documents</span><ul class="doc-list">{rows}</ul></div>'
    og = f"/assets/img/{slug}/1.jpg" if n_imgs else "/assets/img/va-55/1.jpg"
    body = f"""
<article class="project">
  <section class="page-head">
    <div class="wrap">
      <a class="back" href="/projects/">← All projects</a>
      <div class="tags">{tags(p)}</div>
      <h1>{e(p['title'])}</h1>
      <p class="meta">{e(p['meta'])}</p>
    </div>
  </section>
  {hero}
  <div class="wrap project-layout">
    <div class="project-main">
      {stats}
      <h2>Context</h2>
      <p>{e(p['context'])}</p>
      {did}
    </div>
    <aside class="project-side">
      <dl>
        <dt>Role</dt><dd>{e(p['role'])}</dd>
        <dt>Result</dt><dd>{e(p['result'])}</dd>
      </dl>
      <div class="side-skills"><span class="dt">Skills</span><div>{skills}</div></div>
      {docs}
    </aside>
  </div>
  <div class="wrap">{sections}{gallery}</div>
  <nav class="wrap pager" aria-label="More projects">
    <a href="/projects/{prev['slug']}.html"><span>Previous</span>{e(prev['title'])}</a>
    <a href="/projects/{nxt['slug']}.html" class="next"><span>Next</span>{e(nxt['title'])}</a>
  </nav>
</article>"""
    return page(p["title"], body, "/projects/", p["card"], og_img=og)


# ---------- Experience ----------
def experience():
    items = ""
    for x in C.EXPERIENCE:
        pts = "".join(f"<li>{e(t)}</li>" for t in x["points"])
        links = "".join(f'<a class="chip" href="/projects/{s}.html">{e(t)} →</a>' for s, t in x["links"])
        poster = ""
        if x.get("poster"):
            m = img("andel", 12)
            poster = (f'<a class="poster-thumb lb" data-group="poster" href="/assets/img/andel/{m["src"]}" '
                      f'data-caption="{e(m["cap"])}"><img src="/assets/img/andel/{m["sm"]}" alt="Andel placement poster" '
                      f'loading="lazy" width="{m["sw"]}" height="{m["sh"]}"><span>View my placement poster</span></a>')
        items += f"""<li class="tl-item">
  <div class="tl-dates">{x['dates']}</div>
  <div class="tl-body">
    <h3>{e(x['role'])}</h3>
    <p class="tl-org"><strong>{e(x['org'])}</strong> · {e(x['place'])}</p>
    <p class="muted">{e(x['about'])}</p>
    <ul>{pts}</ul>
    {poster}
    <div class="chip-row">{links}</div>
  </div>
</li>"""
    edu = ""
    for x in C.EDUCATION:
        pts = "".join(f"<li>{e(t)}</li>" for t in x["points"])
        edu += f"""<li class="tl-item">
  <div class="tl-dates">{x['dates']}</div>
  <div class="tl-body"><h3>{e(x['org'])}</h3><p class="tl-org">{e(x['role'])}</p><ul>{pts}</ul></div>
</li>"""
    body = f"""
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Experience</p>
    <h1>Work and education</h1>
    <p class="lead">From pharmaceutical containment valves to flood sensors and airline continuing airworthiness.</p>
    {cv_buttons()}
  </div>
</section>
<section class="section section-tight">
  <div class="wrap">
    <h2>Work</h2>
    <ol class="timeline">{items}</ol>
    <h2>Education</h2>
    <ol class="timeline">{edu}</ol>
  </div>
</section>"""
    return page("Experience", body, "/experience.html", "Luca Piergentili's placements, internship and education.")


# ---------- About ----------
def about():
    me = MAN["_me"]
    bio = "".join(f"<p>{e(t)}</p>" for t in C.ABOUT)
    skills = "".join(
        f'<div class="skill-group"><h3>{e(g)}</h3><div>' + "".join(
            f'<span class="chip chip-static">{e(s)}</span>' for s in items) + "</div></div>"
        for g, items in C.SKILLS)
    langs = "".join(f'<li><strong>{l}</strong><span>{lv}</span></li>' for l, lv in C.LANGUAGES)
    body = f"""
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">About</p>
    <h1>Hello, I'm Luca</h1>
  </div>
</section>
<section class="section section-tight">
  <div class="wrap about-layout">
    <div class="about-text">{bio}</div>
    <div class="about-photo"><img src="/assets/img/me/luca.jpg" width="{me['w']}" height="{me['h']}" alt="Portrait of {P['name']}"></div>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap">
    <h2>Skills</h2>
    <div class="skills">{skills}</div>
    <h3 class="lang-title">Languages</h3>
    <ul class="langs">{langs}</ul>
  </div>
</section>
<section class="section" id="contact">
  <div class="wrap contact">
    <div>
      <h2>Contact</h2>
      <p class="lead">I'm looking for a graduate role from summer 2027. The quickest way to reach me is by email.</p>
      {cv_buttons()}
    </div>
    <ul class="contact-list">
      <li><span>Email</span><a href="mailto:{P['email']}">{P['email']}</a></li>
      <li><span>Phone</span><a href="tel:{P['phone_href']}">{P['phone']}</a></li>
      <li><span>LinkedIn</span><a href="{P['linkedin']}" rel="me noopener" target="_blank">{P['linkedin_label']}</a></li>
      <li><span>Work eligibility</span>{e(P['eligibility'])}</li>
    </ul>
  </div>
</section>"""
    return page("About", body, "/about.html", "About Luca Piergentili: skills, languages and contact details.")


# ---------- Personal life (mockup) ----------
def life():
    groups = ""
    for g in C.LIFE:
        cards = "".join(
            f'<div class="life-card"><div class="ph">Photo coming soon</div><h3>{e(t)}</h3><p>{e(d)}</p></div>'
            for t, d in g["items"])
        groups += f'<h2>{e(g["group"])}</h2><div class="grid grid-3">{cards}</div>'
    body = f"""
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Beyond engineering</p>
    <h1>Sport, music and the stage</h1>
    <p class="lead">Team sport and performing have taught me as much about working with people as any project.</p>
  </div>
</section>
<section class="section section-tight"><div class="wrap">{groups}</div></section>"""
    return page("Beyond engineering", body, "", "Luca Piergentili outside engineering.", noindex=True)


def notfound():
    body = """<section class="page-head"><div class="wrap"><h1>Page not found</h1>
<p class="lead">That page doesn't exist. Try the <a href="/projects/">projects</a> or go <a href="/">home</a>.</p></div></section>"""
    return page("Not found", body, noindex=True)


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


if __name__ == "__main__":
    write("index.html", home())
    write("projects/index.html", projects_index())
    ps = C.PROJECTS
    for i, p in enumerate(ps):
        write(f"projects/{p['slug']}.html", project(p, ps[i - 1], ps[(i + 1) % len(ps)]))
    write("experience.html", experience())
    write("about.html", about())
    write("life.html", life())
    write("404.html", notfound())
    # Old project URLs (pages merged or renamed on 20 Oct 2026).
    for old, new in [("andel-bundguard", "andel"), ("andel-products", "andel"), ("gearbox-actuator", "year-1")]:
        write(f"projects/{old}.html", f'<!doctype html><meta charset="utf-8"><title>Moved</title>'
              f'<meta name="robots" content="noindex"><link rel="canonical" href="/projects/{new}.html">'
              f'<meta http-equiv="refresh" content="0; url=/projects/{new}.html">'
              f'<p>This page has moved to <a href="/projects/{new}.html">/projects/{new}.html</a>.</p>')
    print("built", len(ps), "projects")
