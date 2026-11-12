# -*- coding: utf-8 -*-
"""Parse ~/workspace/oncolink/products-catalogue.md into products.json."""
import re, json, os

SRC = os.path.expanduser("~/workspace/oncolink/products-catalogue.md")
OUT = os.path.expanduser("~/workspace/oncolink/website/data/products.json")

text = open(SRC, encoding="utf-8").read()

def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:80].strip("-")

def parse_price(raw):
    """Return (min, max, display) or (None, None, None)."""
    if raw is None:
        return None, None, None
    raw = raw.replace(",", "").strip()
    m = re.match(r"Rs\s*([\d.]+)\s*(?:[–-]\s*Rs\s*([\d.]+))?$", raw)
    if not m:
        return None, None, None
    lo = float(m.group(1))
    hi = float(m.group(2)) if m.group(2) else lo
    return lo, hi, raw

def fmt_price(lo, hi):
    def f(v):
        if v == int(v):
            return f"{int(v):,}"
        return f"{v:,.2f}".rstrip("0").rstrip(".")
    if lo == hi:
        return f"Rs {f(lo)}"
    return f"Rs {f(lo)} to Rs {f(hi)}"

CATEGORIES = {"Anti Cancer", "Haematology", "Rheumatology", "Patient Assistance",
              "Products Range", "General", "Biotech", "Contrast Media", "Oncology"}

ANOMALIES = {
    "paclitaxel": 34.0,
    "fulvedex 250mg/5ml pfs (fulvedex)": 2300.0,
    "flurosol inj 500mg/10ml (5-fluorouracil)": 300.0,
    "pharmatrexate 50mg-inj. (methotrexate sodium)": 221.0,
}

def parse_entry(entry, category):
    """entry like: Name (Generic) — Manufacturer — RsX [OUT OF STOCK]"""
    entry = entry.strip()
    if not entry:
        return None
    oos = "[OUT OF STOCK]" in entry
    entry = entry.replace("[OUT OF STOCK]", "").strip()
    noprice = "[NO PRICE SHOWN]" in entry
    entry = entry.replace("[NO PRICE SHOWN]", "").strip()
    # strip trailing parenthetical notes (e.g. price anomaly note)
    note = ""
    nm = re.search(r"\(([^)]*price anomaly[^)]*)\)\s*$", entry)
    if nm:
        note = nm.group(1)
        entry = entry[:nm.start()].strip()
    # price is the last Rs... token
    pm = re.search(r"Rs\s*[\d,]+(?:\.\d+)?\s*(?:[–-]\s*Rs\s*[\d,]+(?:\.\d+)?)?\s*$", entry)
    price_raw = None
    if pm:
        price_raw = pm.group(0)
        entry = entry[:pm.start()].strip()
    # strip any trailing separator left after price removal
    entry = re.sub(r"\s*[—–-]\s*$", "", entry).strip()
    # split name and manufacturer on em/en dash surrounded by spaces
    parts = re.split(r"\s+[—–]\s+", entry)
    parts = [p.strip() for p in parts if p.strip()]
    name = parts[0] if parts else entry
    manufacturer = ""
    if len(parts) > 1:
        cand = parts[1]
        # category tags are not manufacturers
        cand = re.sub(r"^(anti cancer|haematology|rheumatology|patient assistance|products range)\s*,?\s*", "", cand, flags=re.I)
        manufacturer = cand.strip().rstrip("—-").strip()
    generic = ""
    matches = re.findall(r"\(([^)]+)\)", name)
    if matches:
        generic = matches[-1].rstrip("(").strip()
    lo, hi, _ = parse_price(price_raw)
    is_anomaly = ANOMALIES.get(name.lower()) == lo if lo is not None else False
    return {
        "name": name,
        "generic": generic,
        "manufacturer": manufacturer,
        "category": category,
        "price_min": lo,
        "price_max": hi,
        "price_display": fmt_price(lo, hi) if lo is not None else "",
        "in_stock": not oos,
        "has_price": (lo is not None) and not noprice and not is_anomaly,
        "price_anomaly": bool(is_anomaly),
        "slug": slugify(name),
    }

products = []
seen_slugs = {}

def add(p):
    if not p:
        return
    s = p["slug"]
    if s in seen_slugs:
        seen_slugs[s] += 1
        p["slug"] = f"{s}-{seen_slugs[s]}"
    else:
        seen_slugs[s] = 1
    products.append(p)

# Section 1: Anti Cancer numbered list
sec1 = re.search(r"## 1\. ANTI CANCER \(78\)\n(.*?)\n## 2\.", text, re.S).group(1)
for line in sec1.splitlines():
    m = re.match(r"\d+\.\s+(.*)", line.strip())
    if m:
        add(parse_entry(m.group(1), "Anti Cancer"))

# Sections 2-5: bullets
for sec, cat in [(r"## 2\. HAEMATOLOGY \(2\)\n(.*?)\n## 3\.", "Haematology"),
                 (r"## 3\. RHEUMATOLOGY \(1\)\n(.*?)\n## 4\.", "Rheumatology"),
                 (r"## 4\. PATIENT ASSISTANCE \(1\)\n(.*?)\n## 5\.", "Patient Assistance")]:
    block = re.search(sec, text, re.S).group(1)
    for line in block.splitlines():
        m = re.match(r"-\s+(.*)", line.strip())
        if m:
            add(parse_entry(m.group(1), cat))

sec5 = re.search(r"## 5\. PRODUCTS RANGE \(4\)\n(.*?)\n## 6\.", text, re.S).group(1)
for line in sec5.splitlines():
    m = re.match(r"-\s+(.*)", line.strip())
    if m:
        e = m.group(1)
        e = re.sub(r"\s*\(listed twice\)", "", e)
        e = re.sub(r"\s*\(also in Anti Cancer\)", "", e)
        add(parse_entry(e, "Products Range"))

# Section 6: Shop p.N paragraphs, semicolon separated
sec6 = re.search(r"## 6\. NO NAMED CATEGORY \(153, shop order\)\n(.*)", text, re.S).group(1)
# cut off at the OUT OF STOCK section
sec6 = sec6.split("## OUT OF STOCK")[0]
for line in sec6.splitlines():
    line = line.strip()
    if not line.startswith("Shop p."):
        continue
    body = line.split(":", 1)[1]
    for item in body.split(";"):
        item = item.strip().rstrip(".")
        if item:
            add(parse_entry(item, "General"))

# Dedupe exact duplicates (Biotech twice, Ondansetron twice) keep one of each
uniq = []
seen = set()
for p in products:
    key = (p["name"].lower(), p["manufacturer"].lower(), p["price_display"])
    if key in seen:
        continue
    seen.add(key)
    uniq.append(p)
products = uniq

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(products, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

total = len(products)
oos = sum(1 for p in products if not p["in_stock"])
noprice = sum(1 for p in products if not p["has_price"])
from collections import Counter
cats = Counter(p["category"] for p in products)
print("total:", total)
print("categories:", dict(cats))
print("out of stock:", oos)
print("no price:", noprice)
print("anomalies check:")
for p in products:
    if p["name"].lower().startswith("paclitaxel") and p["price_min"] == 34:
        print("  Paclitaxel Rs34:", p)
    if p["name"].startswith("FULVEDEX"):
        print("  FULVEDEX:", p)
    if p["name"].startswith("FLURUSOL") or p["name"].startswith("FLUROSOL"):
        print("  FLUROSOL:", p)
    if "PHARMATREXATE 50MG-INJ" in p["name"]:
        print("  PHARMATREXATE INJ:", p)
