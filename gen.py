import json, re, csv, os, sys

# ---------- sources ----------
meta = json.load(open('meta.json'))
ARTS = meta['scraped_articles']
def slug(u): return re.sub(r'.*/', '', u.strip()).lower()
BY = {slug(a['url']): a for a in ARTS}

pg = json.load(open('pg.json'))
for e in pg['essays']: e['title'] = e['title'].strip()
PG = {e['title']: e for e in pg['essays']}

MONTHS = {m: i for i, m in enumerate(
    ["January","February","March","April","May","June","July","August",
     "September","October","November","December"], 1)}
def ym(datestr):
    mo = next((MONTHS[k] for k in MONTHS if k in datestr), 0)
    y = re.search(r'(19|20)\d\d', datestr); y = int(y.group(0)) if y else 0
    return (y, mo)

# ---------- book definition ----------
BOOK = dict(
    title="Essays", subtitle="Collected Writing", author="Paul Graham")

PARTS = [
 dict(key="I", title="Part One — Hackers and Painters",
      sub="2001–2004",
      epigraph=("Hacking and painting have a lot in common. In fact, of all "
                "the different types of people I've known, hackers and painters "
                "are among the most alike.", "Hackers and Painters")),
 dict(key="II", title="Part Two — The Startup Playbook",
      sub="2005–2008",
      epigraph=("Do what you love doesn't mean, do what you would like to do "
                "most this second.", "How to Do What You Love")),
 dict(key="III", title="Part Three — Ideas and Determination",
      sub="2009–2013",
      epigraph=("Startups take off because the founders make them take off.",
                "Do Things that Don't Scale")),
 dict(key="IV", title="Part Four — Work, Wealth, and Life",
      sub="2014–2022",
      epigraph=("Life is short, as everyone knows.", "Life is Short")),
]

# title -> part index
SEL = {
 "Beating the Averages":0,"Taste for Makers":0,"A Plan for Spam":0,
 "Why Nerds are Unpopular":0,"Hackers and Painters":0,"What You Can't Say":0,
 "How to Make Wealth":0,"Great Hackers":0,"The Age of the Essay":0,
 "What You'll Wish You'd Known":1,"How to Start a Startup":1,
 "How to Do What You Love":1,"The 18 Mistakes That Kill Startups":1,
 "Why to Not Not Start a Startup":1,"Be Good":1,"How to Disagree":1,
 "Cities and Ambition":1,"Lies We Tell Kids":1,
 "Keep Your Identity Small":2,"Startups in 13 Sentences":2,
 "Relentlessly Resourceful":2,"Maker's Schedule, Manager's Schedule":2,
 "The Top Idea in Your Mind":2,"The Acceleration of Addictiveness":2,
 "Schlep Blindness":2,"Startup = Growth":2,"How to Get Startup Ideas":2,
 "Do Things that Don't Scale":2,"How to Raise Money":2,
 "Before the Startup":3,"Default Alive or Default Dead?":3,"Life is Short":3,
 "Economic Inequality":3,"What I Worked On":3,"How to Write Usefully":3,
 "The Four Quadrants of Conformism":3,"How to Think for Yourself":3,
 "How to Work Hard":3,"A Project of One's Own":3,"Putting Ideas into Words":3,
}

# ---------- markdown cleaning ----------
def strip_links(s):
    s = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', s)          # images
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)       # [text](url) -> text
    return s

MONTH_RE = re.compile(r'^(January|February|March|April|May|June|July|August|'
                      r'September|October|November|December)\s+\d{4}\.?$', re.I)

def fix_chars(s):
    # the scrape corrupted a handful of characters into U+FFFD
    s = s.replace('d�class�', 'déclassé').replace('G�del', 'Gödel')
    s = s.replace('�', '—')   # all remaining were em dashes
    return s

def clean_body(md):
    md = fix_chars(md)
    md = strip_links(md)
    # block-split on blank/whitespace-only lines
    blocks, cur = [], []
    for ln in md.split('\n'):
        if ln.strip() == '':
            if cur: blocks.append(cur); cur = []
        else:
            cur.append(ln)
    if cur: blocks.append(cur)

    paras = []
    for b in blocks:
        text = re.sub(r'\s+', ' ', ' '.join(x.strip() for x in b)).strip()
        if not text: continue
        if text.startswith('#'): continue                # stray heading
        if text.startswith('|'): continue                # nav / translation tables
        if text.strip('-') == '': continue               # horizontal rule
        if set(text) <= set('|-* '): continue
        if 'Want to start a startup' in text: continue
        if text.lower().startswith('get funded by y combinator'): continue
        if 'Translation' in text and ('|' in text or text.count(' ') < 6): continue
        if MONTH_RE.match(text): continue                # header date line
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)     # tidy stray spaces
        paras.append(text)
    # normalize a Notes divider into a bold label if present as bare word
    return paras

def essay_paras(title):
    a = BY[slug(PG[title]['url'])]
    return clean_body(a['markdown'])

# ---------- write raw/ + index.csv ----------
os.makedirs('raw', exist_ok=True)
for f in os.listdir('raw'):
    if f.endswith('.md'): os.remove(os.path.join('raw', f))

def fslug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')[:50]

ordered = sorted(SEL, key=lambda t: (ym(PG[t]['date']), t))
rows = []
for i, t in enumerate(ordered, 1):
    date = PG[t]['date']
    paras = essay_paras(t)
    wc = sum(len(p.split()) for p in paras)
    with open(f"raw/{i:02d}-{fslug(t)}.md", 'w') as f:
        f.write(f"# {t}\n\n*{date}*\n\n" + "\n\n".join(paras) + "\n")
    rows.append(dict(n=i, title=t, date=date, wc=wc, part=SEL[t], paras=len(paras)))

with open('index.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(["number", "title", "date", "word_count"])
    for r in rows:
        w.writerow([r['n'], r['title'], r['date'], r['wc']])

# ---------- assemble manuscript.md ----------
YAML = """---
title: "Essays"
author: "Paul Graham"
documentclass: book
classoption:
  - openany
geometry:
  - paperwidth=6in
  - paperheight=9in
  - top=0.6in
  - bottom=0.6in
  - left=0.6in
  - right=0.6in
fontsize: 10pt
linestretch: 1.15
---
"""

out = [YAML.strip(), ""]
# title page
out += [f"# {BOOK['title']}", "", f"## {BOOK['subtitle']}", "",
        f"### By {BOOK['author']}", ""]

# table of contents (bullet lists, no page numbers)
out += ["## Table of Contents", ""]
for pi, p in enumerate(PARTS):
    out.append(f"**{p['title']}** ({p['sub']})")
    out.append("")
    for t in ordered:
        if SEL[t] == pi:
            out.append(f"- {t} — *{PG[t]['date']}*")
    out.append("")

# parts + essays
for pi, p in enumerate(PARTS):
    out += [f"# {p['title']}", "", f"*{p['sub']}*", ""]
    q, src = p['epigraph']
    out += [f"> *{q}*", ">", f"> — Paul Graham, “{src}”", ""]
    for t in ordered:
        if SEL[t] != pi: continue
        out += [f"# {t}", "", f"*{PG[t]['date']}*", ""]
        out += essay_paras(t)
        out.append("")

open('manuscript.md', 'w').write("\n\n".join(x for x in out) + "\n")

# ---------- verification / stats ----------
print("=== EPIGRAPH CHECK ===")
def norm(s): return re.sub(r'[\s_*]+', '', s).lower()
for p in PARTS:
    q, src = p['epigraph']
    body = norm(' '.join(essay_paras(src)))
    print(f"[{'OK ' if norm(q) in body else 'FAIL'}] {p['key']}  <- {src}")

print("\n=== STATS ===")
print("essays:", len(rows))
print("total words:", sum(r['wc'] for r in rows))
for pi, p in enumerate(PARTS):
    rs = [r for r in rows if r['part'] == pi]
    print(f"  {p['key']}: {len(rs)} essays, {sum(r['wc'] for r in rs)} words")
print("\nfewest paragraphs (sanity):")
for r in sorted(rows, key=lambda r: r['paras'])[:5]:
    print(f"  {r['paras']:3d} paras  {r['wc']:5d} w  {r['title']}")
print("\nmanuscript bytes:", os.path.getsize('manuscript.md'))
