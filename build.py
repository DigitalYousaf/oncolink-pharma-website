# -*- coding: utf-8 -*-
"""ONCOLINK Pharma Distributors static site generator.
Builds the full site into the same directory (website/) from data/products.json.
Run: python3 build.py
"""
import json, os, re, html as htmllib
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "products.json")
BASE = "https://oncolinkpharma.com"
V = "v=3"
WA_NUM = "923218406899"
PHONE_DISPLAY = "+92 42 35882906"
PHONE_TEL = "+924235882906"
WA_DISPLAY = "+92 321 8406899"
EMAIL1 = "info@oncolinkpharma.com"
EMAIL2 = "orders@oncolinkpharma.com"
ADDRESS = "Plot 216 A, Block A Muslim Town, Lahore, Pakistan"

PRODUCTS = json.load(open(DATA, encoding="utf-8"))
BY_SLUG = {p["slug"]: p for p in PRODUCTS}

def esc(s):
    return htmllib.escape(str(s), quote=True)

def wa_link(text):
    return "https://wa.me/" + WA_NUM + "?text=" + quote(text)

def wa_order(p):
    t = "Hello Oncolink, I need " + p["name"]
    if p.get("manufacturer"):
        t += " (" + p["manufacturer"] + ")"
    t += ". Please share availability and delivery details."
    return wa_link(t)

def price_html(p):
    if p.get("price_anomaly"):
        return '<div class="prod-price">Call for price</div><div class="prod-note">Price to be confirmed. WhatsApp us.</div>'
    if not p.get("has_price"):
        return '<div class="prod-price">Call for price</div><div class="prod-note">WhatsApp us for today\'s price.</div>'
    if p["price_min"] == p["price_max"]:
        return '<div class="prod-price">Rs {:,}</div>'.format(int(round(p["price_min"])))
    return '<div class="prod-price">Rs {:,} <small>to</small> Rs {:,}</div>'.format(int(round(p["price_min"])), int(round(p["price_max"])))

def price_text(p):
    if p.get("price_anomaly") or not p.get("has_price"):
        return "Call for price"
    if p["price_min"] == p["price_max"]:
        return "Rs {:,}".format(int(round(p["price_min"])))
    return "Rs {:,} to Rs {:,}".format(int(round(p["price_min"])), int(round(p["price_max"])))

def stock_badge(p):
    if p["in_stock"]:
        return '<span class="badge badge-in">In Stock</span>'
    return '<span class="badge badge-out">Out of Stock</span>'

def prod_card(p, rel=""):
    btn = ('<a class="btn btn-wa btn-block" href="' + wa_order(p) + '" target="_blank" rel="noopener">Order on WhatsApp</a>'
           if p["in_stock"] else
           '<a class="btn btn-outline btn-block" href="' + wa_order(p) + '" target="_blank" rel="noopener">Check availability</a>')
    gen = ('<div class="prod-generic">' + esc(p["generic"]) + '</div>'
           if p.get("generic") and p["generic"].lower() not in p["name"].lower() else '')
    mfr = '<div class="prod-mfr">' + esc(p["manufacturer"]) + '</div>' if p.get("manufacturer") else '<div class="prod-mfr">&nbsp;</div>'
    img = ('<a href="' + rel + 'product/' + p["slug"] + '.html"><img class="prod-img" src="' + rel + p.get("image", "") + '" alt="' + esc(p["name"]) + '" loading="lazy"></a>'
           if p.get("image") else '')
    return ('<article class="prod">' + img + stock_badge(p) +
            '<div class="prod-cat">' + esc(p["category"]) + '</div>' +
            '<h3><a href="' + rel + 'product/' + p["slug"] + '.html">' + esc(p["name"]) + '</a></h3>' +
            gen + mfr + price_html(p) + btn + '</article>')

# ---------------- shared chrome ----------------
NAV = [
    ("index.html", "Home"), ("shop.html", "Medicines"), ("services.html", "Services"),
    ("hospitals.html", "Hospitals"), ("cold-chain.html", "Cold Chain"),
    ("patient-support.html", "Patient Support"), ("blog.html", "Blog"), ("contact.html", "Contact"),
]

def header(active, rel=""):
    items = []
    for href, label in NAV:
        cls = ' class="active"' if href == active else ""
        items.append('<a href="' + rel + href + '"' + cls + '>' + label + '</a>')
    return f'''<header class="site-header"><div class="container">
<a class="logo" href="{rel}index.html"><img class="logo-img" src="{rel}assets/img/logo-old.png" alt="ONCOLINK Pharma Distributors" width="130" height="90"><span class="logo-text"><b>ONCOLINK Pharma Distributors</b><span>Oncology medicines, Lahore since 2006</span></span></a>
<form class="header-search" id="header-search"><input id="header-search-input" type="search" placeholder="Search a medicine..." aria-label="Search medicines"><button type="submit">Search</button></form>
<button class="nav-toggle" aria-label="Menu">&#9776;</button>
<nav class="main-nav">{''.join(items)}</nav>
<div class="nav-cta"><a class="btn btn-navy btn-sm" href="tel:{PHONE_TEL}">Call us</a><a class="btn btn-wa btn-sm" href="https://wa.me/{WA_NUM}" target="_blank" rel="noopener">WhatsApp</a></div>
</div></header>
<div class="trustbar"><div class="container"><div><b>Since 2006</b><span>Patients &amp; hospitals</span></div><div><b>4.5 stars</b><span>24 Google reviews</span></div><div><b>WHO GDP</b><span>Good Distribution</span></div><div><b>Cold chain 2-8 C</b><span>Temperature controlled</span></div></div></div>'''

FOOTER = '''<footer class="site-footer"><div class="container"><div class="cols">
<div><img class="logo-img foot-logo" src="{rel}assets/img/logo-old.png" alt="ONCOLINK Pharma Distributors" width="130" height="90">
<p style="margin-top:12px">Oncolink Pharma Distributors is a trusted pharmaceutical company committed to supplying high-quality medicines across Pakistan. We specialize in oncology and specialty care, ensuring timely delivery, proper storage, and genuine products.</p>
<div class="social-icons"><a href="https://www.facebook.com/oncolinkpharma/" target="_blank" rel="noopener" aria-label="Oncolink on Facebook"><svg viewBox="0 0 24 24" fill="#c9a24b"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg></a><a href="https://pk.linkedin.com/in/muhammad-sajid-42415ba2" target="_blank" rel="noopener" aria-label="Muhammad Sajid on LinkedIn"><svg viewBox="0 0 24 24" fill="#c9a24b"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.226.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z"/></svg></a></div></div>
<div><h4>Medicines</h4><ul>
<li><a href="shop.html">All medicines</a></li>
<li><a href="shop.html?cat=Anti%20Cancer">Anti Cancer</a></li>
<li><a href="shop.html?cat=Haematology">Haematology</a></li>
<li><a href="shop.html?cat=Rheumatology">Rheumatology</a></li>
<li><a href="shop.html?cat=Patient%20Assistance">Patient Assistance</a></li>
<li><a href="patient-support.html">Patient Support</a></li></ul></div>
<div><h4>Company</h4><ul>
<li><a href="about.html">About us</a></li>
<li><a href="services.html">Services</a></li>
<li><a href="hospitals.html">Hospitals &amp; Doctors</a></li>
<li><a href="cold-chain.html">Cold Chain</a></li>
<li><a href="blog.html">Blog</a></li>
<li><a href="faq.html">FAQs</a></li></ul></div>
<div><h4>Contact</h4><ul class="f-contact">
<li><svg class="f-ic" viewBox="0 0 24 24" fill="none" stroke="#c9a24b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg><span>Plot 216 A, Block A Muslim Town, Lahore, Pakistan</span></li>
<li><svg class="f-ic" viewBox="0 0 24 24" fill="none" stroke="#c9a24b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg><span>Phone: <a href="tel:+924235882906">+92 42 35882906</a></span></li>
<li><svg class="f-ic" viewBox="0 0 32 32" fill="#c9a24b"><path d="M16 3C9.4 3 4 8.4 4 15c0 2.4.7 4.6 2 6.5L4 29l7.7-2c1.8.9 3.9 1.5 6 1.5h.3c6.6 0 12-5.4 12-12S22.6 3 16 3zm0 22.5c-1.9 0-3.8-.5-5.4-1.5l-.4-.2-4.6 1.2 1.2-4.5-.3-.4C6 18.4 5.5 16.7 5.5 15 5.5 9.2 10.2 4.5 16 4.5S26.5 9.2 26.5 15 21.8 25.5 16 25.5zm6.3-7.6c-.3-.2-2-1-2.3-1.1-.3-.1-.6-.2-.8.2-.2.3-.9 1.1-1.1 1.3-.2.2-.4.2-.8.1-.3-.2-1.5-.6-2.9-1.8-1.1-.9-1.8-2.1-2-2.4-.2-.3 0-.5.2-.7l.5-.6c.2-.2.2-.4.3-.6.1-.2 0-.4 0-.6-.1-.2-.8-2-1.1-2.7-.3-.7-.6-.6-.8-.6h-.7c-.2 0-.6.1-.9.4-.3.3-1.2 1.2-1.2 2.9s1.2 3.4 1.4 3.6c.2.2 2.4 3.7 5.8 5.2.8.3 1.4.5 1.9.7.8.3 1.5.2 2.1.1.6-.1 2-.8 2.3-1.6.3-.8.3-1.4.2-1.6-.1-.1-.3-.2-.7-.4z"/></svg><span>WhatsApp: <a href="https://wa.me/923218406899" target="_blank" rel="noopener">+92 321 8406899</a></span></li>
<li><svg class="f-ic" viewBox="0 0 24 24" fill="none" stroke="#c9a24b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg><span>Email: <a href="mailto:info@oncolinkpharma.com">info@oncolinkpharma.com</a></span></li>
<li><svg class="f-ic" viewBox="0 0 24 24" fill="none" stroke="#c9a24b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg><span>Mon to Fri 9 AM to 6 PM<br>Sat 9 AM to 5 PM, Sun closed</span></li></ul></div>
</div></div>
<div class="bottom"><div class="container"><span>Copyright 2026 Oncolink Pharma Distributors. All rights reserved.</span><span><a href="privacy.html">Privacy</a> &nbsp;|&nbsp; <a href="terms.html">Terms</a> &nbsp;|&nbsp; <a href="shipping.html">Shipping</a> &nbsp;|&nbsp; <a href="returns.html">Returns</a></span></div></div></footer>
<a class="wa-float" href="https://wa.me/923218406899?text=Hello%20Oncolink%2C%20I%20need%20help%20with%20a%20medicine." target="_blank" rel="noopener" aria-label="Chat on WhatsApp"><svg viewBox="0 0 32 32" fill="#fff"><path d="M16 3C9.4 3 4 8.4 4 15c0 2.4.7 4.6 2 6.5L4 29l7.7-2c1.8.9 3.9 1.5 6 1.5h.3c6.6 0 12-5.4 12-12S22.6 3 16 3zm0 22.5c-1.9 0-3.8-.5-5.4-1.5l-.4-.2-4.6 1.2 1.2-4.5-.3-.4C6 18.4 5.5 16.7 5.5 15 5.5 9.2 10.2 4.5 16 4.5S26.5 9.2 26.5 15 21.8 25.5 16 25.5zm6.3-7.6c-.3-.2-2-1-2.3-1.1-.3-.1-.6-.2-.8.2-.2.3-.9 1.1-1.1 1.3-.2.2-.4.2-.8.1-.3-.2-1.5-.6-2.9-1.8-1.1-.9-1.8-2.1-2-2.4-.2-.3 0-.5.2-.7l.5-.6c.2-.2.2-.4.3-.6.1-.2 0-.4 0-.6-.1-.2-.8-2-1.1-2.7-.3-.7-.6-.6-.8-.6h-.7c-.2 0-.6.1-.9.4-.3.3-1.2 1.2-1.2 2.9s1.2 3.4 1.4 3.6c.2.2 2.4 3.7 5.8 5.2.8.3 1.4.5 1.9.7.8.3 1.5.2 2.1.1.6-.1 2-.8 2.3-1.6.3-.8.3-1.4.2-1.6-.1-.1-.3-.2-.7-.4z"/></svg></a>'''

def rel_footer(rel):
    out = FOOTER.replace("{rel}", rel)
    if not rel:
        return out
    def repl(m):
        url = m.group(1)
        if url.startswith(("http", "tel:", "mailto:", "#")):
            return 'href="' + url + '"'
        return 'href="' + rel + url + '"'
    return re.sub(r'href="([^"]*)"', repl, out)

def page(title, desc, active, body, rel="", extra_head=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{rel}assets/img/logo-old.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}assets/css/style.css?{V}">
{extra_head}</head>
<body>
{header(active, rel)}
{body}
{rel_footer(rel)}
<script src="{rel}assets/js/main.js?{V}"></script>
</body>
</html>'''

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def cta_band(rel=""):
    return f'''<section class="section alt"><div class="container center">
<h2>Need a medicine? Talk to us directly.</h2>
<p class="lead" style="margin:0 auto 18px">Send the medicine name on WhatsApp or call us. We confirm price and availability, then arrange delivery.</p>
<a class="btn btn-wa" href="https://wa.me/{WA_NUM}" target="_blank" rel="noopener">WhatsApp {WA_DISPLAY}</a>
&nbsp; <a class="btn btn-navy" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a></div></section>'''

# ---------------- home ----------------
POPULAR_SLUGS = [
    "abiteron-tablet-250mg-abiraterone-acetate", "avastin-inj-bevacizumab",
    "herceptin-trastuzumab", "nexavar-200-mg-tab-25c-60-s-sorafenib",
    "tecentriq-1200mg-20ml-atezolizumab", "zytux-injection-rituximab",
    "imatigliv-imatinib", "stivant-injection-bevacizumab",
]

REVIEWS = [
    ("Farrukh Javed", "Good distributor in oncology related products. Famous name."),
    ("Kamran Taj", "Excellent."),
    ("Rizwan Butt", "Easy link to find oncology products."),
    ("Umar Khokhar", "Good distributor. Recommended."),
    ("Zeshan Malik", "Good staaf."),
]

def build_home():
    popular = [BY_SLUG[s] for s in POPULAR_SLUGS if s in BY_SLUG]
    cards = "".join(prod_card(p) for p in popular)
    revs = "".join(
        '<div class="review"><div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div><p>&ldquo;' + esc(t) + '&rdquo;</p><div class="who">' + esc(n) + ' &middot; Google review</div></div>'
        for n, t in REVIEWS)
    body = f'''<section class="hero"><div class="container">
<div class="hero-grid">
<div class="hero-copy">
<div class="eyebrow">Oncology medicine distributor, Lahore since 2006</div>
<h1>Genuine cancer medicines, delivered with care.</h1>
<p>We supply oncology and specialty medicines to hospitals, pharmacies, doctors and patients across Pakistan. Every product is genuine, stored correctly and delivered on time.</p>
<form class="hero-search" id="hero-search"><input id="hero-search-input" type="search" placeholder="Search a medicine by brand or generic name..." aria-label="Search medicines"><button type="submit">Search</button></form>
<div class="hero-quick"><a href="shop.html?cat=Anti%20Cancer">Anti Cancer</a><a href="shop.html?q=bevacizumab">Bevacizumab</a><a href="shop.html?q=rituximab">Rituximab</a><a href="shop.html?q=imatinib">Imatinib</a><a href="shop.html?q=trastuzumab">Trastuzumab</a></div>
</div>
<div class="hero-visual">
<div class="hero-visual-card">
<span class="hero-badge">100% Genuine</span>
<img class="hero-main-img" src="assets/img/products/avastin-inj-bevacizumab.webp" alt="Avastin 400 mg/16 ml injection box by Roche" loading="eager">
<div class="hero-visual-row">
<img src="assets/img/products/herceptin-trastuzumab.webp" alt="Herceptin 600 mg/5 ml injection box by Roche" loading="lazy">
<img src="assets/img/products/nexavar-200-mg-tab-25c-60-s-sorafenib.webp" alt="Nexavar 200 mg film-coated tablets box by Bayer" loading="lazy">
</div>
<p class="hero-visual-cap">Genuine packs from Roche, Bayer and other leading makers.</p>
</div>
</div>
</div>
<div class="hero-cards">
<div class="hero-card"><b>1. Find your medicine</b><p>Search by brand or generic name. See the price and stock status right away.</p></div>
<div class="hero-card"><b>2. WhatsApp or call us</b><p>Confirm availability and price in one message. No account needed.</p></div>
<div class="hero-card"><b>3. Fast delivery</b><p>Same day delivery in Lahore. Delivery across Pakistan. Cold chain kept intact.</p></div>
</div></div></section>
<section class="section"><div class="container">
<div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:10px"><h2>Popular medicines</h2><a href="shop.html" class="card-link">See all 236 medicines &rarr;</a></div>
<p class="lead">Prices shown are from our current list. Prices can change, so WhatsApp us to confirm today's price before you order.</p>
<div class="prod-grid">{cards}</div></div></section>
<section class="section alt"><div class="container">
<h2>What we do</h2>
<p class="lead">Four services, one promise. Genuine medicines, handled properly, delivered on time.</p>
<div class="grid2" style="margin-top:18px">
<div class="card"><div class="icon-badge">&#127973;</div><h3>Distribution for institutions</h3><p>We work with government, semi-government and private institutions in Lahore on tender business. We keep manufacturers informed about tenders, share the details they need to win, and supply as per PPRA rules.</p><a class="card-link" href="services-institutions.html">Learn more &rarr;</a></div>
<div class="card"><div class="icon-badge">&#127968;</div><h3>Patient home supply</h3><p>We deliver regular use medicines for oncology, hepatology and nephrology to the patient's doorstep. Same day orders in Lahore are delivered the same day. We keep a complete record of patients, addresses and phone numbers.</p><a class="card-link" href="services-home-supply.html">Learn more &rarr;</a></div>
<div class="card"><div class="icon-badge">&#10052;</div><h3>Cold chain products</h3><p>Temperature sensitive medicines stay at 2 to 8 C from our cold room to your door. Solar power is our first source of electricity, Wapda is second, and a generator is third. Refrigerators are calibrated and validated every year.</p><a class="card-link" href="services-cold-chain.html">Learn more &rarr;</a></div>
<div class="card"><div class="icon-badge">&#128138;</div><h3>Distribution for pharmacies</h3><p>We arrange supplies for selected pharmaceutical companies at all leading pharmacies of Lahore, so patients can find their medicine close to home.</p><a class="card-link" href="services-pharmacies.html">Learn more &rarr;</a></div>
</div></div></section>
<section class="section"><div class="container">
<div class="grid2">
<div><h2>Why hospitals and patients trust us</h2>
<p>We have been doing this since 2006. That is nearly twenty years of supplying cancer medicines in Lahore and beyond. Our principals include Bayer, Roche, Pfizer, Novartis, Sanofi and Eli Lilly. Our procedures follow WHO Good Distribution Practices, and a dedicated team checks every product before it leaves us.</p>
<p>We serve government institutions, private hospitals, doctors, pharmacies and patients in Lahore, Gujranwala, Faisalabad, Multan and other allocated areas of Pakistan.</p>
<a class="btn btn-navy" href="about.html">Read our story</a></div>
<div><div class="google-badge"><span class="big">4.5</span><span><span class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span><br>24 Google reviews</span></div>
<div style="display:grid;gap:14px;margin-top:16px">{revs}</div></div>
</div></div></section>
<section class="section alt"><div class="container">
<h2>Our principals</h2>
<p class="lead">We distribute for leading multinational and national pharmaceutical companies.</p>
<div class="principals" style="margin-top:16px"><span class="principal">Bayer</span><span class="principal">Roche</span><span class="principal">Pfizer</span><span class="principal">Novartis</span><span class="principal">Sanofi</span><span class="principal">Eli Lilly</span><span class="principal">ICI Pakistan</span><span class="principal">Atco Pharma</span><span class="principal">AJM Pharma</span><span class="principal">Medinet</span></div></div></section>
<section class="section"><div class="container">
<h2>Questions patients ask us</h2>
<div style="margin-top:16px">
<div class="faq-item"><button class="faq-q">How do I order a medicine? <span>+</span></button><div class="faq-a"><p>Search for the medicine on this website, then tap Order on WhatsApp. Send us the name and strength. We confirm the price and availability, then arrange delivery or pickup.</p></div></div>
<div class="faq-item"><button class="faq-q">Do you deliver outside Lahore? <span>+</span></button><div class="faq-a"><p>Yes, we deliver across Pakistan. Same day delivery is available in Lahore. For other cities, WhatsApp us and we will confirm the delivery time for your city.</p></div></div>
<div class="faq-item"><button class="faq-q">How do I know the medicine is genuine? <span>+</span></button><div class="faq-a"><p>We buy directly from the manufacturers and their authorised principals, including Bayer, Roche, Pfizer and Novartis. Every pack is checked before dispatch. You can also read our guide on checking genuine medicine in the blog.</p></div></div>
</div>
<p style="margin-top:14px"><a href="faq.html">See all FAQs &rarr;</a></p></div></section>
{cta_band()}'''
    return write("index.html", page(
        "ONCOLINK Pharma Distributors | Cancer Medicine Distributor Lahore",
        "Genuine oncology and specialty medicines in Lahore since 2006. 236 medicines with prices, same day delivery in Lahore, cold chain 2 to 8 C. Order on WhatsApp.",
        "index.html", body))

# ---------------- shop ----------------
def build_shop():
    body = '''<div class="page-head"><div class="container">
<h1>All medicines</h1>
<p>236 medicines with prices. Search by brand name or generic name, filter by category and manufacturer, and order on WhatsApp in one tap. Prices can change, so WhatsApp us to confirm today's price.</p></div></div>
<section class="section"><div class="container">
<div class="shop-toolbar">
<div class="field grow"><label for="f-q">Search</label><input id="f-q" type="search" placeholder="Type a brand or generic name, for example bevacizumab..."></div>
<div class="field"><label for="f-cat">Category</label><select id="f-cat"><option value="">All categories</option></select></div>
<div class="field"><label for="f-mfr">Manufacturer</label><select id="f-mfr"><option value="">All manufacturers</option></select></div>
<div class="field"><label for="f-price">Price</label><select id="f-price"><option value="">Any price</option><option value="under5k">Under Rs 5,000</option><option value="5to25k">Rs 5,000 to 25,000</option><option value="25to100k">Rs 25,000 to 100,000</option><option value="over100k">Over Rs 100,000</option><option value="noprice">Call for price</option></select></div>
<div class="field"><label for="f-sort">Sort</label><select id="f-sort"><option value="">Featured</option><option value="low">Price: low to high</option><option value="high">Price: high to low</option><option value="az">Name: A to Z</option></select></div>
<label class="check-row"><input type="checkbox" id="f-stock"> In stock only</label>
</div>
<p class="shop-count" id="shop-count">Loading medicines...</p>
<div class="prod-grid" id="prod-grid"></div>
<div class="callout" style="margin-top:22px"><b>Can not find your medicine?</b> WhatsApp us the name and strength. We will check availability and price for you, usually within minutes during working hours.</div>
</div></section>
<script src="assets/js/shop.js?v=1"></script>'''
    return write("shop.html", page(
        "All Medicines | ONCOLINK Pharma Distributors Lahore",
        "Search 236 oncology and specialty medicines with prices. Anti cancer, haematology, rheumatology and more. Order on WhatsApp, same day delivery in Lahore.",
        "shop.html", body))

# ---------------- product pages ----------------
def related(p, n=4):
    same_mfr = [x for x in PRODUCTS if x["slug"] != p["slug"] and x.get("manufacturer") and x["manufacturer"] == p.get("manufacturer")]
    same_cat = [x for x in PRODUCTS if x["slug"] != p["slug"] and x["category"] == p["category"] and x not in same_mfr]
    out = (same_mfr + same_cat)[:n]
    if len(out) < n:
        rest = [x for x in PRODUCTS if x["slug"] != p["slug"] and x not in out]
        out += rest[:n - len(out)]
    return out

def build_products():
    count = 0
    for p in PRODUCTS:
        rel = "../"
        schema = ""
        if p.get("has_price") and p["in_stock"]:
            schema = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Product",'
                      '"name":' + json.dumps(p["name"]) + ',"description":' + json.dumps((p["generic"] + " " if p.get("generic") else "") + "Available at Oncolink Pharma Distributors, Lahore.") +
                      ',"brand":{"@type":"Brand","name":' + json.dumps(p["manufacturer"] or "Oncolink") + '},'
                      '"image":"https://oncolinkpharma.com/' + p.get("image", "") + '",'
                      '"offers":{"@type":"Offer","priceCurrency":"PKR","price":' + str(int(round(p["price_min"]))) +
                      ',"availability":"https://schema.org/InStock"}}</script>')
        price_block = price_html(p)
        if p["in_stock"]:
            order_btn = '<a class="btn btn-wa btn-block" href="' + wa_order(p) + '" target="_blank" rel="noopener">Order on WhatsApp</a>'
        else:
            order_btn = '<a class="btn btn-outline btn-block" href="' + wa_order(p) + '" target="_blank" rel="noopener">Check availability on WhatsApp</a>'
        meta_rows = ""
        if p.get("generic"):
            meta_rows += "<tr><td>Generic name</td><td>" + esc(p["generic"]) + "</td></tr>"
        if p.get("manufacturer"):
            meta_rows += "<tr><td>Manufacturer</td><td>" + esc(p["manufacturer"]) + "</td></tr>"
        meta_rows += "<tr><td>Category</td><td>" + esc(p["category"]) + "</td></tr>"
        meta_rows += "<tr><td>Availability</td><td>" + ("In stock" if p["in_stock"] else "Out of stock") + "</td></tr>"
        cold_note = ('<div class="callout"><b>Cold chain:</b> If this medicine needs cold storage, we pack and ship it in insulated packaging with cold packs, and keep it at 2 to 8 C. Ask us on WhatsApp and we will confirm how your medicine is stored and shipped.</div>'
                     if p["category"] in ("Anti Cancer", "Haematology") else "")
        rel_cards = "".join(prod_card(x, "../") for x in related(p))
        pd_img = ('<div class="pd-img"><img src="../' + p.get("image", "") + '" alt="' + esc(p["name"]) + '" loading="lazy"></div>'
                  if p.get("image") else "")
        body = f'''<div class="page-head"><div class="container"><div class="breadcrumb"><a href="../index.html">Home</a> &rsaquo; <a href="../shop.html">Medicines</a> &rsaquo; {esc(p["name"])}</div>
<h1>{esc(p["name"])}</h1></div></div>
<section class="section"><div class="container"><div class="pd-wrap">
<div class="pd-main">
{pd_img}
{stock_badge(p)} <span class="pill">{esc(p["category"])}</span>
<table class="pd-meta">{meta_rows}</table>
<p>Prices can change. WhatsApp us to confirm today's price before you order. If this medicine is out of stock, message us and we will check when it will be available again.</p>
{cold_note}
<div class="callout warn"><b>Important:</b> This page is for information only. It is not medical advice. Always use medicines as your doctor directs. A prescription may be required.</div>
</div>
<div class="pd-side">
<div class="pd-price">{price_text(p)}</div>
<p style="color:var(--muted);font-size:.9rem">Price in Pakistani rupees. {"" if p.get("has_price") else "Call or WhatsApp us for today's price."}</p>
{order_btn}
<a class="btn btn-navy btn-block" style="margin-top:10px" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
<p style="margin-top:14px;font-size:.9rem;color:var(--muted)">Same day delivery in Lahore. Delivery across Pakistan. Genuine products, checked before dispatch.</p>
</div></div>
<h2 style="margin-top:40px">Related medicines</h2>
<div class="prod-grid" style="margin-top:16px">{rel_cards}</div>
</div></section>
{cta_band("../")}'''
        title = p["name"] + " Price in Pakistan | ONCOLINK Pharma Lahore"
        desc = (p["name"] + ((" (" + p["generic"] + ")") if p.get("generic") else "") + " at Oncolink Pharma Distributors, Lahore. " + price_text(p) + ". Order on WhatsApp, same day delivery in Lahore.")
        write("product/" + p["slug"] + ".html",
              page(title, desc, "shop.html", body, rel="../", extra_head=schema))
        count += 1
    return count

# ---------------- content pages ----------------
def simple_page(path, title, desc, active, head_html, body_html, rel=""):
    body = f'''<div class="page-head"><div class="container">{head_html}</div></div>
<section class="section"><div class="container">{body_html}</div></section>
{cta_band(rel)}'''
    return write(path, page(title, desc, active, body, rel=rel))

def build_about():
    head = "<h1>About Oncolink Pharma Distributors</h1><p>Supplying genuine medicines across Pakistan since 2006.</p>"
    body = '''<div class="article">
<p>Oncolink Pharma Distributors is a trusted pharmaceutical company committed to supplying high-quality medicines across Pakistan. We specialize in oncology and specialty care, ensuring timely delivery, proper storage, and genuine products. Our focus is reliability, compliance, and customer satisfaction, supporting healthcare providers with efficient and professional services every day.</p>
<h2>Our story</h2>
<p>Oncolink Pharma Distributor was established in 2006. Since then we have served patients as well as institutions, and we offer distribution services to multinational and national pharmaceutical companies in Lahore.</p>
<p>Our objective is simple. Provide the best service in the supply of quality medicines to customers, patients, doctors, pharmacies and government institutions, on top priority, to save human lives.</p>
<h2>How we work</h2>
<p>Our vision is to provide the best services to companies and promote their business. We have qualified, trained and experienced professional staff working as per Oncolink SOPs.</p>
<p>We have established Standard Operating Procedures in compliance with WHO Good Distribution Practices. We ensure that only the best quality product reaches our clients. A dedicated team of highly trained professionals examines each product before dispatch.</p>
<p>We cover government institutions, private institutions, pharmacies and patients in Lahore, Gujranwala, Faisalabad, Multan and other allocated areas of Pakistan.</p>
<h2>What we stand for</h2>
<ul>
<li><b>Commitment.</b> We do what we say we will do.</li>
<li><b>On time delivery.</b> Same day delivery in Lahore for urgent orders.</li>
<li><b>Special care of our customers.</b> Patients, doctors, pharmacies and hospitals all get the same attention.</li>
<li><b>Special care of our suppliers.</b> We work closely with the companies whose products we distribute.</li>
<li><b>Our cold chain system.</b> Temperature sensitive medicines stay at 2 to 8 C.</li>
<li><b>Quality of products and services.</b> Checked before dispatch, every time.</li>
<li><b>Coverage of area.</b> Lahore and beyond, across Pakistan.</li>
<li><b>Team work.</b> Trained staff, clear procedures, no shortcuts.</li>
</ul>
<h2>Leadership</h2>
<p>Oncolink Pharma Distributors is led by Muhammad Sajid, Chief Executive Officer.</p>
<h2>Our principals</h2>
<p>We distribute for Bayer Pakistan, Sanofi Pakistan, Roche Pakistan, Pfizer Pakistan, ICI Pakistan, Novartis Oncology, Atco Pharma, Eli Lilly, AJM Pharma and Medinet Pharmaceutical.</p>
<p><a class="btn btn-navy" href="contact.html">Contact us</a> &nbsp; <a class="btn btn-outline" href="shop.html">See our medicines</a></p>
</div>'''
    return simple_page("about.html",
        "About Us | ONCOLINK Pharma Distributors Lahore",
        "Oncolink Pharma Distributors has supplied genuine oncology and specialty medicines across Pakistan since 2006. WHO Good Distribution Practices, cold chain 2 to 8 C.",
        "index.html", head, body)

def build_services():
    head = "<h1>Our services</h1><p>Four services, one promise. Genuine medicines, handled properly, delivered on time.</p>"
    body = '''<div class="grid2">
<div class="card"><div class="icon-badge">&#127973;</div><h3>Distribution for institutions</h3><p>We work with all government institutions for tender business in Lahore. We keep manufacturers informed about tenders, share the details they need to win, and supply as per PPRA rules for the purchase of medicine.</p><a class="card-link" href="services-institutions.html">Learn more &rarr;</a></div>
<div class="card"><div class="icon-badge">&#127968;</div><h3>Patient home supply</h3><p>We deliver regular use medicines for hepatology, nephrology and oncology to the patient's doorstep. Same day orders in Lahore are delivered the same day. We keep a complete record of patients, addresses and phone numbers.</p><a class="card-link" href="services-home-supply.html">Learn more &rarr;</a></div>
<div class="card"><div class="icon-badge">&#10052;</div><h3>Cold chain products</h3><p>Temperature sensitive medicines stay at 2 to 8 C from our cold room to your door. Solar power is our first source of electricity, Wapda is second, and a generator is third. Refrigerators are calibrated and validated every year.</p><a class="card-link" href="services-cold-chain.html">Learn more &rarr;</a></div>
<div class="card"><div class="icon-badge">&#128138;</div><h3>Distribution for pharmacies</h3><p>We have arrangements with selected pharmaceutical companies to ensure their supplies reach all leading pharmacies of Lahore, so patients can find their medicine close to home.</p><a class="card-link" href="services-pharmacies.html">Learn more &rarr;</a></div>
</div>'''
    return simple_page("services.html",
        "Services | ONCOLINK Pharma Distributors Lahore",
        "Distribution for institutions, patient home supply, cold chain products and pharmacy distribution. Genuine oncology medicines across Pakistan since 2006.",
        "services.html", head, body)

def service_detail(path, title, desc, heading, intro, points, extra=""):
    head = f"<h1>{heading}</h1><p>{intro}</p>"
    lis = "".join("<li>" + p + "</li>" for p in points)
    body = f'''<div class="article"><ul>{lis}</ul>{extra}
<p><a class="btn btn-wa" href="https://wa.me/{WA_NUM}" target="_blank" rel="noopener">WhatsApp us</a> &nbsp; <a class="btn btn-outline" href="services.html">&larr; All services</a></p></div>'''
    return simple_page(path, title, desc, "services.html", head, body)

def build_service_details():
    service_detail("services-institutions.html",
        "Distribution for Institutions | ONCOLINK Pharma Lahore",
        "Tender supply for government, semi-government and private institutions in Lahore. PPRA rules, on time delivery, genuine oncology medicines.",
        "Distribution for institutions",
        "We supply medicines to government, semi-government and private institutions in Lahore through tender business.",
        ["We work with all government institutions for tender business in Lahore.",
         "We keep manufacturers informed about tenders in time.",
         "We provide the details manufacturers need to win tenders as per PPRA rules for the purchase of medicine.",
         "We supply to public sector hospitals, private hospitals and leading pharmacies."])
    service_detail("services-home-supply.html",
        "Patient Home Supply | ONCOLINK Pharma Lahore",
        "Same day home delivery of oncology, hepatology and nephrology medicines in Lahore. Order on WhatsApp, delivered to your doorstep.",
        "Patient home supply",
        "We deliver regular use medicines to the patient's doorstep, so families do not have to travel for every dose.",
        ["We ensure prompt delivery of medicine to the patient's doorstep for regular use medicines like hepatology, nephrology and oncology drugs.",
         "We maintain a complete record of patients with their addresses and phone numbers.",
         "Same day orders for home supply in Lahore are delivered the same day.",
         "Order on WhatsApp or by phone. We confirm price and availability first."])
    service_detail("services-cold-chain.html",
        "Cold Chain Products | ONCOLINK Pharma Lahore",
        "Temperature controlled delivery of cancer medicines at 2 to 8 C. Solar, Wapda and generator backup, yearly calibration, insulated packaging.",
        "Cold chain products",
        "Some medicines only work if they stay cold. We keep them cold from our cold room to your door.",
        ["We ensure temperature maintained products are delivered as per temperature requirements.",
         "Solar system is installed as the primary source of electricity, Wapda is the second source and a generator is the third.",
         "Calibration and validation is done each year for all refrigerators.",
         "All temperature sensitive shipments are transported in thermostable boxes."],
        '<p><a href="cold-chain.html">Read more about our cold chain &rarr;</a></p>')
    service_detail("services-pharmacies.html",
        "Distribution for Pharmacies | ONCOLINK Pharma Lahore",
        "Medicine supply to leading pharmacies across Lahore. Genuine oncology and specialty products, on time delivery.",
        "Distribution for pharmacies",
        "We keep leading pharmacies in Lahore stocked, so patients can find their medicine close to home.",
        ["We have arrangements with selected pharmaceutical companies to ensure their supplies reach all leading pharmacies of Lahore.",
         "Pharmacies can order by phone or WhatsApp and get on time delivery.",
         "Every product is checked before dispatch."])

def build_hospitals():
    head = "<h1>For hospitals and doctors</h1><p>Tender supply, genuine products, cold chain you can rely on. One call, and we take it from there.</p>"
    body = f'''<div class="article">
<p>If you run a hospital, a clinic or a pharmacy, we can be your oncology supply partner. We have supplied public sector hospitals, private hospitals and pharmacies in Lahore since 2006.</p>
<h2>What we offer institutions</h2>
<ul>
<li><b>Tender business.</b> We work with government, semi-government and private institutions in Lahore. We keep manufacturers informed about tenders and share the details they need to win, as per PPRA rules.</li>
<li><b>Genuine products.</b> We distribute for Bayer, Roche, Pfizer, Novartis, Sanofi, Eli Lilly, ICI, Atco, AJM and Medinet. Every product is checked before dispatch.</li>
<li><b>Cold chain.</b> Temperature sensitive medicines stay at 2 to 8 C, with solar, Wapda and generator backup, and yearly calibration and validation.</li>
<li><b>On time delivery.</b> Same day delivery in Lahore for urgent orders.</li>
<li><b>One contact.</b> A named contact for your orders, so you are not explaining your needs to a different person every time.</li>
</ul>
<h2>Request a quote</h2>
<p>Tell us what you need. We will reply with availability and a quote.</p>
<form class="form" id="quote-form">
<label for="qf-org">Hospital, clinic or pharmacy name</label>
<input id="qf-org" required>
<label for="qf-name">Your name</label>
<input id="qf-name" required>
<label for="qf-phone">Phone / WhatsApp</label>
<input id="qf-phone" required>
<label for="qf-type">You are a</label>
<select id="qf-type"><option>Hospital</option><option>Clinic</option><option>Pharmacy</option><option>Doctor</option><option>Other</option></select>
<label for="qf-msg">What do you need?</label>
<textarea id="qf-msg" placeholder="Medicine names, quantities, how often you order..."></textarea>
<p class="hint">Submitting opens WhatsApp with your message ready to send. We do not store your details on this website.</p>
<button class="btn btn-wa" type="submit">Send request on WhatsApp</button>
</form>
<p style="margin-top:16px">Prefer to talk? Call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> or WhatsApp <a href="https://wa.me/{WA_NUM}" target="_blank" rel="noopener">{WA_DISPLAY}</a>.</p>
</div>'''
    return simple_page("hospitals.html",
        "For Hospitals and Doctors | ONCOLINK Pharma Lahore",
        "Tender supply of genuine oncology medicines for hospitals, clinics and pharmacies in Lahore. PPRA rules, cold chain 2 to 8 C, on time delivery.",
        "hospitals.html", head, body)

def build_cold_chain():
    head = "<h1>Cold chain, done properly</h1><p>Some medicines only work if they stay cold. We keep them at 2 to 8 C, from our cold room to your door.</p>"
    body = '''<div class="article">
<p>Cancer medicines are sensitive. If they get warm, they can lose their effect. That is why cold chain is not a nice extra for us. It is the core of what we do.</p>
<h2>How we keep medicines cold</h2>
<ul>
<li><b>Cold room storage.</b> Temperature sensitive medicines are stored at 2 to 8 C in our cold room.</li>
<li><b>Three power sources.</b> Solar system is our primary source of electricity. Wapda is the second source. A generator is the third. The cold room keeps running even when the power goes out.</li>
<li><b>Yearly calibration.</b> Calibration and validation is done each year for all refrigerators, so the temperature you see is the temperature you get.</li>
<li><b>Insulated packaging.</b> All temperature sensitive shipments travel in thermostable boxes with cold packs, so the medicine stays cold on the road.</li>
<li><b>Checked before dispatch.</b> A dedicated team examines each product before it leaves us.</li>
</ul>
<h2>What this means for you</h2>
<p>If your medicine needs cold storage, tell us when you order. We pack it in insulated packaging with cold packs and deliver it the same day in Lahore. When it arrives, put it in your fridge straight away, at 2 to 8 C, and follow your doctor's storage advice.</p>
<p><a class="btn btn-wa" href="https://wa.me/923218406899?text=Hello%20Oncolink%2C%20I%20have%20a%20question%20about%20cold%20chain%20delivery." target="_blank" rel="noopener">Ask about cold chain delivery</a></p>
</div>'''
    return simple_page("cold-chain.html",
        "Cold Chain Delivery 2 to 8 C | ONCOLINK Pharma Lahore",
        "Temperature controlled storage and delivery of cancer medicines at 2 to 8 C. Solar, Wapda and generator backup, yearly calibration, insulated packaging.",
        "cold-chain.html", head, body)

def build_patient_support():
    head = "<h1>Patient support</h1><p>Cancer treatment is hard enough. Getting the medicine should not be.</p>"
    body = '''<div class="article">
<p>If you or a family member needs a cancer medicine, here is how we can help.</p>
<h2>How to order</h2>
<ul>
<li><b>Search</b> for the medicine on this website, by brand or generic name.</li>
<li><b>WhatsApp or call us</b> with the name and strength. We confirm the price and availability.</li>
<li><b>We deliver</b> the same day in Lahore, and across Pakistan. Cold chain medicines travel in insulated packaging.</li>
</ul>
<h2>Patient assistance programmes</h2>
<p>Some manufacturers run patient support programmes for their medicines. For example, a Pfizer patient support programme is available in Pakistan for Sutent (sunitinib), and Bayer's Nexavar has support options. These programmes can reduce the cost of treatment for eligible patients.</p>
<p>If you want to know whether a programme covers your medicine, WhatsApp us the medicine name. We will check and guide you.</p>
<h2>If a medicine is out of stock</h2>
<p>Message us on WhatsApp. We will check with our principals and tell you when it is expected back, or suggest asking your doctor about an alternative brand with the same generic medicine.</p>
<h2>Payment</h2>
<p>Please call or WhatsApp us to confirm payment options for your order.</p>
<p><a class="btn btn-wa" href="https://wa.me/923218406899?text=Hello%20Oncolink%2C%20I%20need%20help%20with%20a%20medicine." target="_blank" rel="noopener">WhatsApp us for help</a></p>
</div>'''
    return simple_page("patient-support.html",
        "Patient Support | ONCOLINK Pharma Distributors Lahore",
        "How to order cancer medicines, patient assistance programmes, out of stock help and delivery. Same day delivery in Lahore, across Pakistan.",
        "patient-support.html", head, body)

FAQS = [
    ("How do I order a medicine?", "Search for the medicine on this website, then tap Order on WhatsApp. Send us the name and strength. We confirm the price and availability, then arrange delivery or pickup."),
    ("Do you deliver outside Lahore?", "Yes, we deliver across Pakistan. Same day delivery is available in Lahore. For other cities, WhatsApp us and we will confirm the delivery time for your city."),
    ("How do I know the medicine is genuine?", "We buy directly from the manufacturers and their authorised principals, including Bayer, Roche, Pfizer and Novartis. Every pack is checked before dispatch. Our blog has a guide on checking genuine medicine."),
    ("What if my medicine is out of stock?", "Message us on WhatsApp with the name and strength. We will check with our principals and tell you when it is expected back."),
    ("Do I need a prescription?", "Many cancer medicines need a prescription. Please have your prescription ready when you order. If you are unsure, ask us on WhatsApp."),
    ("How are cold chain medicines delivered?", "They stay at 2 to 8 C in our cold room, then travel in insulated packaging with cold packs. Same day delivery in Lahore. Put the medicine in your fridge as soon as it arrives."),
    ("Can I pay on delivery?", "Please call or WhatsApp us to confirm payment options for your order."),
    ("What is your return policy?", "If a medicine is damaged or wrong, tell us within 7 days and we will sort it out. Fridge items kept at 2 to 8 C cannot be returned once they have left our cold chain. See our Returns page for details."),
    ("Do you supply hospitals and pharmacies?", "Yes. We supply government, semi-government and private institutions, hospitals and pharmacies in Lahore through tender and regular orders. See our Hospitals and Doctors page."),
    ("What are your working hours?", "Monday to Friday, 9 AM to 6 PM. Saturday, 9 AM to 5 PM. Sunday closed. WhatsApp messages sent outside working hours are answered the next working day."),
    ("Where are you located?", "Plot 216 A, Block A Muslim Town, Lahore, Pakistan. Call +92 42 35882906 or WhatsApp +92 321 8406899."),
    ("Do prices change?", "Yes, medicine prices can change with the supplier. The price on this website is our current list price. WhatsApp us to confirm today's price before you order."),
]

def build_faq():
    head = "<h1>Frequently asked questions</h1><p>Straight answers. If your question is not here, WhatsApp us.</p>"
    items = "".join(
        '<div class="faq-item"><button class="faq-q">' + esc(q) + ' <span>+</span></button><div class="faq-a"><p>' + esc(a) + '</p></div></div>'
        for q, a in FAQS)
    body = "<div>" + items + "</div>"
    return simple_page("faq.html",
        "FAQs | ONCOLINK Pharma Distributors Lahore",
        "Answers about ordering, delivery, cold chain, payment, prescriptions and returns at Oncolink Pharma Distributors, Lahore.",
        "index.html", head, body)

def build_contact():
    head = "<h1>Contact us</h1><p>Call, WhatsApp or send a message. We reply during working hours.</p>"
    body = f'''<div class="grid2">
<div class="card">
<h3>Visit us</h3>
<ul class="c-contact">
<li><svg class="f-ic" viewBox="0 0 24 24" fill="none" stroke="#c9a24b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg><span>Plot 216 A, Block A Muslim Town,<br>Lahore, Pakistan</span></li>
<li><svg class="f-ic" viewBox="0 0 24 24" fill="none" stroke="#c9a24b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg><span><b>Phone:</b> <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></span></li>
<li><svg class="f-ic" viewBox="0 0 32 32" fill="#c9a24b"><path d="M16 3C9.4 3 4 8.4 4 15c0 2.4.7 4.6 2 6.5L4 29l7.7-2c1.8.9 3.9 1.5 6 1.5h.3c6.6 0 12-5.4 12-12S22.6 3 16 3zm0 22.5c-1.9 0-3.8-.5-5.4-1.5l-.4-.2-4.6 1.2 1.2-4.5-.3-.4C6 18.4 5.5 16.7 5.5 15 5.5 9.2 10.2 4.5 16 4.5S26.5 9.2 26.5 15 21.8 25.5 16 25.5zm6.3-7.6c-.3-.2-2-1-2.3-1.1-.3-.1-.6-.2-.8.2-.2.3-.9 1.1-1.1 1.3-.2.2-.4.2-.8.1-.3-.2-1.5-.6-2.9-1.8-1.1-.9-1.8-2.1-2-2.4-.2-.3 0-.5.2-.7l.5-.6c.2-.2.2-.4.3-.6.1-.2 0-.4 0-.6-.1-.2-.8-2-1.1-2.7-.3-.7-.6-.6-.8-.6h-.7c-.2 0-.6.1-.9.4-.3.3-1.2 1.2-1.2 2.9s1.2 3.4 1.4 3.6c.2.2 2.4 3.7 5.8 5.2.8.3 1.4.5 1.9.7.8.3 1.5.2 2.1.1.6-.1 2-.8 2.3-1.6.3-.8.3-1.4.2-1.6-.1-.1-.3-.2-.7-.4z"/></svg><span><b>WhatsApp:</b> <a href="https://wa.me/{WA_NUM}" target="_blank" rel="noopener">{WA_DISPLAY}</a></span></li>
<li><svg class="f-ic" viewBox="0 0 24 24" fill="none" stroke="#c9a24b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg><span><b>Email:</b> <a href="mailto:{EMAIL1}">{EMAIL1}</a></span></li>
<li><svg class="f-ic" viewBox="0 0 24 24" fill="none" stroke="#c9a24b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg><span><b>Orders:</b> <a href="mailto:{EMAIL2}">{EMAIL2}</a></span></li>
</ul>
<h3 style="margin-top:18px">Working hours</h3>
<ul class="c-contact">
<li><svg class="f-ic" viewBox="0 0 24 24" fill="none" stroke="#c9a24b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg><span>Monday to Friday: 9 AM to 6 PM<br>Saturday: 9 AM to 5 PM<br>Sunday: Closed</span></li>
</ul>
<p style="font-size:.9rem;color:var(--muted)">Note: our old website listed Friday closing at 7 PM. Our Google listing says 6 PM. We use 6 PM here. Please confirm by phone if you plan to visit late.</p>
</div>
<div class="card">
<h3>Send us a message</h3>
<form class="form" id="contact-form">
<label for="cf-name">Your name</label><input id="cf-name" required>
<label for="cf-phone">Phone / WhatsApp</label><input id="cf-phone" required>
<label for="cf-topic">Topic</label>
<select id="cf-topic"><option>Order a medicine</option><option>Price and availability</option><option>Hospital or pharmacy order</option><option>Delivery question</option><option>Other</option></select>
<label for="cf-msg">Message</label><textarea id="cf-msg" required></textarea>
<p class="hint">Submitting opens WhatsApp with your message ready to send. We do not store your details on this website.</p>
<button class="btn btn-wa" type="submit">Send on WhatsApp</button>
</form></div>
</div>
<div style="margin-top:22px;border:1px solid var(--line);border-radius:var(--radius);overflow:hidden">
<iframe title="Oncolink Pharma Distributors location map" src="https://www.google.com/maps?q=216+A+New+Muslim+Town,+Lahore,+Pakistan&output=embed" width="100%" height="380" style="border:0" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
</div>'''
    return simple_page("contact.html",
        "Contact Us | ONCOLINK Pharma Distributors Lahore",
        "Visit us at Plot 216 A, Block A Muslim Town, Lahore. Phone +92 42 35882906, WhatsApp +92 321 8406899. Mon to Fri 9 AM to 6 PM.",
        "contact.html", head, body)

def policy_page(path, title, desc, heading, html):
    head = f"<h1>{heading}</h1>"
    body = f'<div class="article">{html}</div>'
    return simple_page(path, title, desc, "index.html", head, body)

def build_policies():
    policy_page("privacy.html",
        "Privacy Policy | ONCOLINK Pharma Distributors",
        "How Oncolink Pharma Distributors handles your personal information.",
        "Privacy Policy",
        """<p><b>Last updated:</b> November 2026.</p>
<p>Oncolink Pharma Distributors respects your privacy. This page explains what information we collect and how we use it.</p>
<h2>What we collect</h2>
<p>When you contact us by phone, WhatsApp or through a form on this website, we receive the details you share, such as your name, phone number and the medicine you ask about. We use these details only to answer you, confirm availability and price, and arrange delivery.</p>
<h2>What we do not do</h2>
<p>We do not sell your details. We do not share them with advertisers. We do not store form submissions on this website. Messages sent through WhatsApp are handled under WhatsApp's own privacy terms.</p>
<h2>Prescriptions</h2>
<p>If you share a prescription with us, we use it only to verify your order. We do not share it with anyone else.</p>
<h2>Contact</h2>
<p>If you have a question about your information, call us on +92 42 35882906 or WhatsApp +92 321 8406899.</p>""")
    policy_page("terms.html",
        "Terms of Use | ONCOLINK Pharma Distributors",
        "Terms for using the Oncolink Pharma Distributors website.",
        "Terms of Use",
        """<p><b>Last updated:</b> November 2026.</p>
<p>By using this website, you agree to these terms.</p>
<h2>Information only</h2>
<p>The content on this website is for information only. It is not medical advice, diagnosis or treatment. Always follow your doctor's guidance and read the leaflet that comes with your medicine.</p>
<h2>Prices and availability</h2>
<p>Prices on this website are our current list prices. They can change without notice. Stock status is updated regularly, but it can change. Please confirm the price and availability on WhatsApp or by phone before you order.</p>
<h2>Orders</h2>
<p>Orders are confirmed only when we accept them. Some medicines need a prescription. We may ask you to share it before we confirm your order.</p>
<h2>Contact</h2>
<p>Questions? Call +92 42 35882906 or WhatsApp +92 321 8406899.</p>""")
    policy_page("shipping.html",
        "Shipping and Delivery | ONCOLINK Pharma Distributors",
        "Delivery information for Oncolink Pharma Distributors: same day in Lahore, across Pakistan, cold chain 2 to 8 C.",
        "Shipping and Delivery",
        """<p><b>Last updated:</b> November 2026.</p>
<h2>Lahore</h2>
<p>Same day delivery is available in Lahore for orders placed during working hours. Urgent home delivery is available for patients in Lahore.</p>
<h2>Across Pakistan</h2>
<p>We deliver across Pakistan, including Karachi, Islamabad, Rawalpindi, Faisalabad, Multan, Peshawar and Quetta. Delivery time depends on your city. WhatsApp us and we will confirm the time for your order.</p>
<h2>Cold chain</h2>
<p>Temperature sensitive medicines travel in insulated packaging with cold packs, kept at 2 to 8 C. Please put the medicine in your fridge as soon as it arrives.</p>
<h2>Delivery charges</h2>
<p>Please confirm delivery charges on WhatsApp or by phone when you order. Charges depend on the medicine, the packaging and your city.</p>""")
    policy_page("returns.html",
        "Returns Policy | ONCOLINK Pharma Distributors",
        "Returns information for Oncolink Pharma Distributors. Damaged or wrong medicines, 7 day notice, fridge items.",
        "Returns Policy",
        """<p><b>Last updated:</b> November 2026.</p>
<h2>Damaged or wrong medicine</h2>
<p>If a medicine arrives damaged or wrong, tell us within 7 days. Share a photo of the pack on WhatsApp. We will arrange a replacement or a refund.</p>
<h2>Fridge items</h2>
<p>Medicines that must be kept at 2 to 8 C cannot be returned once they have left our cold chain. This is for your safety, so no one receives a medicine that may have gone warm.</p>
<h2>Change of mind</h2>
<p>Because medicines are sensitive products, we cannot accept returns for change of mind. Please confirm the medicine name, strength and quantity with us before you order.</p>
<h2>How to start a return</h2>
<p>WhatsApp +92 321 8406899 or call +92 42 35882906 within 7 days of delivery.</p>""")

# ---------------- blog ----------------
BLOG_POSTS = [
    ("abiraterone-price-pakistan.html", "Abiraterone price in Pakistan and where to buy it",
     "Abiraterone price in Pakistan, brands available, and how to buy it safely from a licensed distributor in Lahore.",
     "12 Nov 2026", "Abiraterone is a medicine used in prostate cancer treatment. If your doctor has prescribed it, the first question is usually the price. Here is what it costs in Pakistan, what affects the price, and how to buy it safely."),
    ("store-cancer-medicine-cold-chain.html", "How to store cancer medicine at home",
     "Cold chain explained simply. How to store cancer medicine at 2 to 8 C, what to do in a power cut, and when to call your pharmacist.",
     "12 Nov 2026", "Some cancer medicines must stay cold, at 2 to 8 C. If they get warm, they can lose their effect. Here is how to store them properly at home."),
    ("check-genuine-cancer-medicine.html", "How to check if your cancer medicine is genuine",
     "Five simple checks before you buy cancer medicine in Pakistan. Packaging, batch number, expiry, invoice and where you buy it.",
     "12 Nov 2026", "Cancer medicines are expensive, and fake medicines are a real problem. Here are five simple checks you can do before you pay."),
    ("rituximab-price-pakistan.html", "Rituximab price in Pakistan: brands and availability",
     "Rituximab price in Pakistan by brand, including Ristova, Mabthera and Zytux. Availability in Lahore and how to order.",
     "12 Nov 2026", "Rituximab is prescribed for several blood cancers and other conditions. Prices vary a lot by brand. Here is what it costs in Pakistan and how to get it."),
]

ARTICLE_BODIES = {
"abiraterone-price-pakistan.html": """
<p>Abiraterone is a medicine used in prostate cancer treatment. If your doctor has prescribed it, the first question is usually the price. Here is what it costs in Pakistan, what affects the price, and how to buy it safely.</p>
<h2>What does abiraterone cost in Pakistan?</h2>
<p>Abiraterone comes in different brands and strengths. At Oncolink, the current prices are:</p>
<ul>
<li><b>Abiteron 250 mg:</b> Rs 199,788</li>
<li><b>ABYTIGA (abiraterone acetate):</b> Rs 26,000 to Rs 145,400, depending on strength and pack</li>
<li><b>ABIRA-AHP 250 mg:</b> Rs 30,000</li>
</ul>
<p>Prices can change with the supplier, so always confirm today's price on WhatsApp before you order.</p>
<h2>Why does the price vary so much?</h2>
<p>Three things decide the price. First, the brand. Original brands cost more than local brands. Second, the strength and the pack size. Third, availability. When a brand is short in the market, the price goes up.</p>
<p>Your doctor prescribes the generic medicine, abiraterone. The brand can be discussed with your doctor and pharmacist, because the price difference is large.</p>
<h2>Where to buy abiraterone in Lahore</h2>
<p>Buy from a licensed distributor or pharmacy that you can check. Oncolink has supplied oncology medicines in Lahore since 2006, and we distribute for the companies that make these medicines. We confirm the price and availability on WhatsApp before you pay, and we deliver the same day in Lahore.</p>
<h2>Patient assistance</h2>
<p>Some manufacturers run patient support programmes that can reduce the cost of treatment for eligible patients. Ask us on WhatsApp whether a programme covers your medicine.</p>
<div class="disclaimer">This article is for information only. It is not medical advice. Always follow your doctor's guidance, and read the leaflet that comes with your medicine.</div>
""",
"store-cancer-medicine-cold-chain.html": """
<p>Some cancer medicines must stay cold, at 2 to 8 C. If they get warm, they can lose their effect. Here is how to store them properly at home.</p>
<h2>What does 2 to 8 C mean?</h2>
<p>It means fridge temperature, not freezer. The middle shelf of a fridge is usually right. Do not keep the medicine in the fridge door, because the temperature there goes up and down every time the door opens. Do not freeze it. Freezing can damage the medicine just as heat can.</p>
<h2>When your medicine arrives</h2>
<p>Put it in the fridge straight away. Check the pack is sealed and not damaged. Check the expiry date. If the pack feels warm or looks damaged, call us before you use it.</p>
<h2>What to do in a power cut</h2>
<p>Keep the fridge door closed. A closed fridge stays cold for a few hours. Do not open it to check. When the power comes back, check that the fridge is cooling again. If the medicine was warm for a long time, call your doctor or pharmacist and ask what to do. Do not guess.</p>
<h2>How we deliver cold medicines</h2>
<p>At Oncolink, temperature sensitive medicines stay at 2 to 8 C in our cold room. They travel in insulated packaging with cold packs. Our cold room has three power sources: solar, Wapda and a generator, so it keeps running even when the power goes out. Our refrigerators are calibrated and validated every year.</p>
<h2>Travelling with your medicine</h2>
<p>Use an insulated bag with a cold pack. Keep it out of direct sun. If you are travelling far, ask your pharmacist how long the medicine stays safe outside the fridge.</p>
<div class="disclaimer">This article is for information only. It is not medical advice. Always follow your doctor's guidance, and read the leaflet that comes with your medicine.</div>
""",
"check-genuine-cancer-medicine.html": """
<p>Cancer medicines are expensive, and fake medicines are a real problem. Here are five simple checks you can do before you pay.</p>
<h2>1. Buy from a source you can check</h2>
<p>Buy from a licensed distributor or pharmacy with a real address and phone number. Oncolink has been at the same address in Muslim Town, Lahore since 2006, and you can visit us. If a seller has no address, no phone number and only a social media page, be careful.</p>
<h2>2. Check the packaging</h2>
<p>Look at the pack closely. The printing should be sharp and clear. The seals should be intact. The batch number and expiry date should be printed clearly, not stuck on with a label. If the box looks faded, damaged or re-taped, ask questions.</p>
<h2>3. Check the batch and expiry</h2>
<p>Every genuine pack has a batch number and an expiry date. Note them down. If you have any doubt, ask the distributor to confirm the batch with the manufacturer.</p>
<h2>4. Ask for an invoice</h2>
<p>A genuine seller gives you a proper invoice with the medicine name, batch number, price and the seller's name and address. Keep it. It is your proof of purchase.</p>
<h2>5. Check the price</h2>
<p>If a price looks far lower than everywhere else, be careful. Genuine medicines have a real cost. A price that is too good to be true usually is.</p>
<h2>What we do at Oncolink</h2>
<p>We buy directly from the manufacturers and their authorised principals, including Bayer, Roche, Pfizer and Novartis. A dedicated team examines each product before dispatch. Our procedures follow WHO Good Distribution Practices. If you ever have a doubt about a pack you bought from us, bring it back and we will check it with you.</p>
<div class="disclaimer">This article is for information only. It is not medical advice. Always follow your doctor's guidance, and read the leaflet that comes with your medicine.</div>
""",
"rituximab-price-pakistan.html": """
<p>Rituximab is prescribed for several blood cancers and other conditions. Prices vary a lot by brand. Here is what it costs in Pakistan and how to get it.</p>
<h2>What does rituximab cost in Pakistan?</h2>
<p>Rituximab comes in several brands. At Oncolink, the current prices are:</p>
<ul>
<li><b>Ristova vial (rituximab):</b> Rs 20,000 to Rs 100,000, depending on strength</li>
<li><b>Mabthera vial 1400 mg:</b> Rs 120,000</li>
<li><b>RITUXIM injection:</b> Rs 22,000 to Rs 44,000</li>
<li><b>Zytux injection:</b> Rs 11,000 to Rs 36,000</li>
</ul>
<p>Prices can change with the supplier, so always confirm today's price on WhatsApp before you order.</p>
<h2>Why do prices differ between brands?</h2>
<p>Different companies make rituximab under different brand names. The original brand usually costs more. Local and biosimilar brands cost less. Your doctor prescribes rituximab, and the brand can be discussed with your doctor and pharmacist.</p>
<h2>Is rituximab a cold chain medicine?</h2>
<p>Yes. Rituximab must be kept at 2 to 8 C. At Oncolink it stays in our cold room, then travels in insulated packaging with cold packs. When it arrives, put it in your fridge straight away.</p>
<h2>How to order in Lahore</h2>
<p>Search for rituximab on this website, pick the brand your doctor prescribed, and tap Order on WhatsApp. We confirm the price and availability, then deliver the same day in Lahore, or across Pakistan.</p>
<div class="disclaimer">This article is for information only. It is not medical advice. Always follow your doctor's guidance, and read the leaflet that comes with your medicine.</div>
""",
}

def build_blog():
    cards = "".join(
        '<div class="blog-card"><div class="date">' + d + '</div><h3><a href="blog/' + slug + '">' + esc(t) + '</a></h3><p>' + esc(desc) + '</p><a class="card-link" href="blog/' + slug + '">Read article &rarr;</a></div>'
        for slug, t, desc, d, _ in BLOG_POSTS)
    body = f'''<div class="page-head"><div class="container"><h1>Blog: cancer medicine, simply explained</h1><p>Prices, storage, safety and patient support. Written plainly, with real prices from our shop.</p></div></div>
<section class="section"><div class="container"><div class="blog-list">{cards}</div></div></section>
{cta_band()}'''
    write("blog.html", page("Blog | ONCOLINK Pharma Distributors Lahore",
        "Cancer medicine prices in Pakistan, cold chain storage, and how to check genuine medicine. Plain guides from Oncolink Pharma Distributors, Lahore.",
        "blog.html", body))
    for slug, title, desc, date, _intro in BLOG_POSTS:
        art = ARTICLE_BODIES[slug]
        body = f'''<div class="page-head"><div class="container"><div class="breadcrumb"><a href="../index.html">Home</a> &rsaquo; <a href="../blog.html">Blog</a> &rsaquo; {esc(title)}</div>
<h1>{esc(title)}</h1><p>{date} &middot; Oncolink Pharma Distributors</p></div></div>
<section class="section"><div class="container"><div class="article">{art}
<p><a class="btn btn-wa" href="https://wa.me/{WA_NUM}" target="_blank" rel="noopener">Ask us about this medicine</a> &nbsp; <a class="btn btn-outline" href="../blog.html">&larr; All articles</a></p>
</div></div></section>
{cta_band("../")}'''
        write("blog/" + slug, page(title + " | ONCOLINK Pharma Lahore", desc, "blog.html", body, rel="../"))

# ---------------- sitemap / robots ----------------
def build_sitemap():
    urls = ["", "shop.html", "about.html", "services.html", "services-institutions.html",
            "services-home-supply.html", "services-cold-chain.html", "services-pharmacies.html",
            "hospitals.html", "cold-chain.html", "patient-support.html", "faq.html", "blog.html",
            "contact.html", "privacy.html", "terms.html", "shipping.html", "returns.html"]
    for slug, *_ in BLOG_POSTS:
        urls.append("blog/" + slug)
    for p in PRODUCTS:
        urls.append("product/" + p["slug"] + ".html")
    items = "".join(f'  <url><loc>{BASE}/{u}</loc></url>\n' for u in urls)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + items + '</urlset>\n'
    write("sitemap.xml", xml)
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: " + BASE + "/sitemap.xml\n")
    return len(urls)

# ---------------- main ----------------
def main():
    built = []
    built.append(build_home())
    built.append(build_shop())
    n = build_products()
    built.append(build_about())
    built.append(build_services())
    build_service_details()
    built.append(build_hospitals())
    built.append(build_cold_chain())
    built.append(build_patient_support())
    built.append(build_faq())
    built.append(build_contact())
    build_policies()
    build_blog()
    urls = build_sitemap()
    # sanity: no em dashes in generated html
    bad = []
    for root, _dirs, files in os.walk(ROOT):
        if "data" in root or ".git" in root:
            continue
        for fn in files:
            if fn.endswith(".html"):
                p = os.path.join(root, fn)
                t = open(p, encoding="utf-8").read()
                if "—" in t or "–" in t:
                    bad.append(os.path.relpath(p, ROOT))
    print("pages built:", len(built), "| product pages:", n, "| sitemap urls:", urls)
    print("files with em/en dashes:", bad if bad else "none")
    print("total products:", len(PRODUCTS),
          "| in stock:", sum(1 for p in PRODUCTS if p["in_stock"]),
          "| out of stock:", sum(1 for p in PRODUCTS if not p["in_stock"]),
          "| no price:", sum(1 for p in PRODUCTS if not p["has_price"] and not p["price_anomaly"]),
          "| price anomalies:", sum(1 for p in PRODUCTS if p["price_anomaly"]))

if __name__ == "__main__":
    main()
