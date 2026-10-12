#!/usr/bin/env python3
"""Static guide generator for seeglance.com/guides. Run: python3 build.py"""
import html, json, re, sys, os, datetime
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = "/mnt/user-data/outputs/guides"
SITE = "https://seeglance.com"
APP = "https://app.seeglance.com"
TODAY = "2026-10-12"
exec(open(os.path.join(ROOT, "guides.py"), encoding="utf-8").read())  # defines GUIDES

CSS = open(os.path.join(ROOT, "style.css"), encoding="utf-8").read()

def esc(s): return html.escape(s, quote=True)

def slugify(t): return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")

def add_ids_and_toc(body):
    toc = []
    def rep(m):
        text = re.sub(r"<[^>]+>", "", m.group(1))
        sid = slugify(text)
        toc.append((sid, text))
        return f'<h2 id="{sid}">{m.group(1)}</h2>'
    body = re.sub(r"<h2>(.*?)</h2>", rep, body, flags=re.S)
    return body, toc

def words(s): return len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", s)))

def page(g):
    slug, lang = g["slug"], g.get("lang", "en")
    body = open(os.path.join(ROOT, "src", slug + ".html"), encoding="utf-8").read()
    body, toc = add_ids_and_toc(body)
    faqs = g.get("faqs", [])
    n_words = words(body) + sum(words(q) + words(a) for q, a in faqs)
    mins = max(3, round(n_words / 220))
    url = f"{SITE}/guides/{slug}.html"
    vi = lang == "vi"
    L = {
        "kicker": "Hướng dẫn" if vi else "Guide",
        "updated": "Cập nhật tháng 10/2026" if vi else "Updated October 2026",
        "read": "phút đọc" if vi else "min read",
        "toc": "Trong bài này" if vi else "In this guide",
        "faq": "Câu hỏi thường gặp" if vi else "FAQ",
        "related": "Bài liên quan" if vi else "Related guides",
        "login": "Đăng nhập" if vi else "Log in",
        "all": "Tất cả hướng dẫn" if vi else "All guides",
        "disc": "Bài viết mang tính tham khảo, không phải tư vấn thuế hay pháp lý." if vi else "General information, not tax, legal or financial advice.",
        "cta_btn": g.get("cta_btn", "Dùng thử SeeGlance →" if vi else "Try SeeGlance →"),
    }
    utm = f"?utm_source=guide&utm_medium=seo&utm_campaign={slug}"
    cta_href = APP + "/signup" + utm
    # hreflang
    alts = ""
    if g.get("alt"):
        a_lang, a_slug = g["alt"]
        alts = (f'<link rel="alternate" hreflang="{lang}" href="{url}">\n'
                f'<link rel="alternate" hreflang="{a_lang}" href="{SITE}/guides/{a_slug}.html">\n'
                f'<link rel="alternate" hreflang="x-default" href="{SITE}/guides/{g["alt"][1] if lang=="vi" else slug}.html">\n')
    ld_article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": g["h1"], "description": g["desc"],
        "datePublished": TODAY, "dateModified": TODAY, "inLanguage": lang,
        "mainEntityOfPage": url,
        "image": f"{SITE}/logo.jpeg",
        "author": {"@type": "Organization", "name": "SeeGlance", "url": SITE},
        "publisher": {"@type": "Organization", "name": "SeeGlance", "url": SITE,
                      "logo": {"@type": "ImageObject", "url": f"{SITE}/logo.jpeg"}},
    }
    ld_bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "SeeGlance", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": L["all"], "item": SITE + "/guides/"},
        {"@type": "ListItem", "position": 3, "name": g["h1"], "item": url}]}
    lds = [ld_article, ld_bc]
    if faqs:
        lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in faqs]})
    ld_html = "\n".join('<script type="application/ld+json">\n' + json.dumps(x, ensure_ascii=False, indent=2) + "\n</script>" for x in lds)
    toc_html = ""
    if len(toc) >= 3:
        toc_html = f'<nav class="toc" aria-label="{L["toc"]}"><strong>{L["toc"]}</strong><ol>' + "".join(
            f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc) + "</ol></nav>"
    faq_html = ""
    if faqs:
        faq_html = f'<h2 id="faq">{L["faq"]}</h2>' + "".join(f"<h3>{esc(q)}</h3><p>{a}</p>" for q, a in faqs)
    by_slug = {x["slug"]: x for x in GUIDES}
    rel = "".join(
        f'<li><a href="/guides/{r}.html">{esc(by_slug[r]["h1"])}</a></li>' for r in g.get("related", []) if r in by_slug)
    rel_html = f'<h2 id="related">{L["related"]}</h2><ul class="rel">{rel}</ul>' if rel else ""
    cta_title = g.get("cta_title", "Chạy toàn bộ quy trình này trong một nơi?" if vi else "Run this whole workflow in one place?")
    cta_text = g.get("cta_text", "")
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(g["title"])}</title>
<meta name="description" content="{esc(g["desc"])}">
<link rel="canonical" href="{url}">
{alts}<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:title" content="{esc(g["title"])}">
<meta property="og:description" content="{esc(g["desc"])}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="SeeGlance">
<meta property="og:image" content="{SITE}/logo.jpeg">
<meta name="twitter:card" content="summary">
<link rel="icon" href="/logo.jpeg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
{ld_html}
<style>
{CSS}
</style>
</head>
<body>
<header>
  <div class="header-inner">
    <a href="/" class="logo"><img src="/logo.jpeg" alt="SeeGlance" class="mark-img" width="26" height="26">SeeGlance</a>
    <div class="header-right">
      <a href="/guides/" class="nav-link">{L["all"]}</a>
      <a href="{APP}/login" class="nav-link">{L["login"]}</a>
      <a href="{cta_href}" class="header-cta">{L["cta_btn"]}</a>
    </div>
  </div>
</header>
<article>
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">SeeGlance</a> › <a href="/guides/">{L["all"]}</a></nav>
    <div class="kicker">{esc(g.get("kicker", L["kicker"]))}</div>
    <h1>{esc(g["h1"])}</h1>
    <p class="meta">{L["updated"]} · {mins} {L["read"]}</p>
    <p class="lede">{g["lede"]}</p>
    {toc_html}
    {body}
    {faq_html}
    <div class="cta-box">
      <h3>{esc(cta_title)}</h3>
      <p>{cta_text}</p>
      <a href="{cta_href}" class="cta-btn">{L["cta_btn"]}</a>
    </div>
    {rel_html}
  </div>
</article>
<footer>
  <div class="wrap">
    <p><a href="/">SeeGlance</a> · <a href="/guides/">{L["all"]}</a> · <a href="{APP}/vs">Comparisons</a> · <a href="/pricing/">Pricing</a></p>
    <p>© 2026 SeeGlance. {L["disc"]}</p>
  </div>
</footer>
</body>
</html>
"""

EXTRA = [
 {"slug":"how-to-get-paid-internationally-without-us-bank-account","tag":"Payments","h1":"How to get paid internationally without a US bank account","desc":"Payoneer, Wise, Skrill and crypto compared for freelancers working with clients abroad."},
 {"slug":"from-full-time-to-freelance-first-90-days-after-layoff","tag":"Getting started","h1":"From full-time to freelance: your first 90 days after a layoff","desc":"A practical guide to pricing, finding first clients and avoiding first-timer mistakes."},
]
def index_page():
    cards = []
    for g in GUIDES + EXTRA:
        cards.append(f'<a class="gcard" href="/guides/{g["slug"]}.html"><span class="tag">{esc(g.get("tag","Guide"))}</span><strong>{esc(g["h1"])}</strong><span class="ex">{esc(g["desc"])}</span></a>')
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "SeeGlance guides for freelancers and small studios",
          "url": SITE + "/guides/", "hasPart": [{"@type": "Article", "headline": g["h1"], "url": f'{SITE}/guides/{g["slug"]}.html'} for g in GUIDES + EXTRA]}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Freelance guides: invoicing, contracts, taxes and getting paid | SeeGlance</title>
<meta name="description" content="Practical guides and templates for freelancers outside the US: change orders, milestone invoicing, retainers, payment reminders, W-8BEN and payout fees.">
<link rel="canonical" href="{SITE}/guides/">
<meta property="og:title" content="Freelance guides and templates | SeeGlance">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/guides/">
<meta property="og:image" content="{SITE}/logo.jpeg">
<link rel="icon" href="/logo.jpeg">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
<style>
{CSS}
.grid{{display:grid;gap:14px;margin-top:28px}}
.gcard{{display:flex;flex-direction:column;gap:6px;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 20px;color:var(--text)}}
.gcard:hover{{border-color:var(--crimson-dim);text-decoration:none}}
.gcard .tag{{font-size:11.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--crimson)}}
.gcard strong{{font-size:17px;color:#fff;line-height:1.35}}
.gcard .ex{{font-size:14px;color:var(--text-dim)}}
</style>
</head>
<body>
<header><div class="header-inner">
  <a href="/" class="logo"><img src="/logo.jpeg" alt="SeeGlance" class="mark-img" width="26" height="26">SeeGlance</a>
  <div class="header-right"><a href="{APP}/login" class="nav-link">Log in</a>
  <a href="{APP}/signup?utm_source=guide&utm_medium=seo&utm_campaign=index" class="header-cta">Try SeeGlance →</a></div>
</div></header>
<article><div class="wrap">
  <div class="kicker">Guides</div>
  <h1>Guides and templates for freelancers and small studios</h1>
  <p class="lede">Written for people who work with international clients but sit outside the US, Canada, UK or Australia: how to scope, bill and get paid — and how to see whether a project actually made money.</p>
  <div class="grid">{''.join(cards)}</div>
</div></article>
<footer><div class="wrap"><p><a href="/">SeeGlance</a> · <a href="{APP}/vs">Comparisons</a> · <a href="/pricing/">Pricing</a></p><p>© 2026 SeeGlance. General information, not tax, legal or financial advice.</p></div></footer>
</body></html>
"""

def sitemap():
    urls = [(SITE + "/", "weekly", "1.0"), (SITE + "/guides/", "weekly", "0.8")] + [
        (f'{SITE}/guides/{g["slug"]}.html', "monthly", "0.7") for g in GUIDES + EXTRA]
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, f, p in urls:
        out.append(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{f}</changefreq><priority>{p}</priority></url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for g in GUIDES:
        open(os.path.join(OUT, g["slug"] + ".html"), "w", encoding="utf-8").write(page(g))
        print("built", g["slug"])
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index_page())
    open("/mnt/user-data/outputs/sitemap.xml", "w", encoding="utf-8").write(sitemap())
    open("/mnt/user-data/outputs/robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
