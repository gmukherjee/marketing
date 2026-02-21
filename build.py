#!/usr/bin/env python3
"""
Build script for ASA Marketing Section website.

Usage:
    python3 build.py

Reads:  _talks/*.md          (one file per talk)
Writes: index.html           (homepage)
        seminars.html        (seminar series listing)
        jsm.html             (JSM sessions)
        awards.html          (student paper awards)
        talks/*.html         (one detail page per talk)

Each .md file must start with a YAML front-matter block:
---
date:        November 11, 2025
time:        6:00–7:00 PM Eastern
season:      Fall 2025
speaker:     Yuyan Wang
affiliation: Stanford Graduate School of Business
website:     https://...          (optional, links speaker name)
zoom:        https://...          (optional)
video:       https://...          (optional, post-talk recording)
slides:      https://...          (optional)
coauthors:   Joint work with ...  (optional)
---

The H1 heading in the markdown body is used as the talk title.
Everything after the H1 is the abstract.
"""

import os, re, glob
from pathlib import Path
from datetime import datetime
import markdown as md_lib

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent
TALKS_SRC = ROOT / "_talks"
TALKS_OUT = ROOT / "talks"
TALKS_OUT.mkdir(exist_ok=True)

# ── Season sort order ──────────────────────────────────────────────────────
SEASON_ORDER = [
    "Fall 2025", "Spring 2025", "Fall 2024", "Spring 2024",
    "Fall 2023", "Spring 2023",
]

def season_key(s):
    try:
        return SEASON_ORDER.index(s)
    except ValueError:
        return 999

def parse_date(date_str):
    """Parse a date string like 'November 11, 2025' into a datetime for sorting."""
    for fmt in ("%B %d, %Y", "%B %Y", "%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return datetime.min

# ── Parse front-matter ─────────────────────────────────────────────────────
def parse_frontmatter(text):
    meta = {}
    body = text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip().lower()] = v.strip()
        body = m.group(2)
    return meta, body

# ── Extract title from first H1 ────────────────────────────────────────────
def extract_title(body):
    m = re.match(r"#\s+(.+)\n", body)
    if m:
        title = m.group(1).strip()
        body_without_title = body[m.end():]
        return title, body_without_title
    return "Untitled", body

# ── HTML templates ─────────────────────────────────────────────────────────
def navbar(root="", active=""):
    links = [
        ("index.html",    "Home"),
        ("seminars.html", "Seminars"),
        ("jsm.html",      "JSM Sessions"),
        ("awards.html",   "Student Paper Awards"),
    ]
    nav_items = ""
    for href, label in links:
        cls = ' class="active"' if label == active else ""
        nav_items += f'    <a href="{root}{href}"{cls}>{label}</a>\n'
    return f"""\
<header class="site-header">
  <a class="nav-title" href="{root}index.html">ASA Marketing Section</a>
  <nav>
{nav_items}  </nav>
</header>"""

FOOTER = """\
<footer class="site-footer">
  American Statistical Association — Marketing Section
</footer>"""

def page(title, body_html, root="", active=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — ASA Marketing Section</title>
  <link rel="stylesheet" href="{root}style.css" />
</head>
<body>
{navbar(root=root, active=active)}
<main class="page-content">
{body_html}
</main>
{FOOTER}
</body>
</html>"""

# ── Build one talk detail page ─────────────────────────────────────────────
def build_talk_page(src_path):
    text = src_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    title, abstract_md = extract_title(body)
    abstract_html = md_lib.markdown(abstract_md.strip(), extensions=["extra"])

    slug = src_path.stem
    out_path = TALKS_OUT / f"{slug}.html"

    # optional links
    links_html = ""
    if meta.get("zoom"):
        links_html += f'<a class="action-link zoom-link" href="{meta["zoom"]}" target="_blank" rel="noopener">Join via Zoom ↗</a>\n'
    if meta.get("video"):
        links_html += f'<a class="action-link video-link" href="{meta["video"]}" target="_blank" rel="noopener">Watch Recording ↗</a>\n'
    if meta.get("slides"):
        links_html += f'<a class="action-link slides-link" href="{meta["slides"]}" target="_blank" rel="noopener">Slides ↗</a>\n'

    time_html = f"&nbsp;·&nbsp; {meta['time']}" if meta.get("time") else ""

    speaker_html = (
        f'<strong><a href="{meta["website"]}" target="_blank" rel="noopener">{meta.get("speaker", "")}</a></strong>'
        if meta.get("website") else
        f'<strong>{meta.get("speaker", "")}</strong>'
    )

    body_html = f"""
  <a class="back-link" href="../seminars.html">← Back to all seminars</a>

  <div class="talk-detail-meta">
    {meta.get('date', '')} {time_html}
  </div>

  <h1 class="talk-detail-title">{title}</h1>

  <div class="talk-detail-speaker">
    {speaker_html}
    <br>{meta.get('affiliation', '')}
    {('<br><span class="coauthors">' + meta['coauthors'] + '</span>') if meta.get('coauthors') else ''}
  </div>

  {links_html}

  <hr style="margin: 2rem 0; border: none; border-top: 1px solid #eee;">

  <div class="abstract-heading">Abstract</div>
  <div class="abstract-text">
    {abstract_html}
  </div>
"""
    out_path.write_text(page(title, body_html, root="../", active="Seminars"), encoding="utf-8")
    return {
        "slug": slug,
        "title": title,
        "date": meta.get("date", ""),
        "time": meta.get("time", ""),
        "season": meta.get("season", ""),
        "speaker": meta.get("speaker", ""),
        "affiliation": meta.get("affiliation", ""),
        "has_detail": True,
    }

# ── Build seminars page ────────────────────────────────────────────────────
def build_seminars(talks):
    seasons = {}
    for t in talks:
        s = t["season"] or "Other"
        seasons.setdefault(s, []).append(t)

    sections_html = ""
    for season in sorted(seasons.keys(), key=season_key):
        sections_html += f'  <h2 class="season-heading">{season}</h2>\n'
        sorted_talks = sorted(seasons[season], key=lambda t: parse_date(t["date"]), reverse=True)
        for t in sorted_talks:
            time_html = f"&nbsp;·&nbsp; {t['time']}" if t["time"] else ""
            detail_link = (
                f'<a class="read-more" href="talks/{t["slug"]}.html">Read more →</a>'
                if t["has_detail"] else ""
            )
            affil_html = f'&nbsp;<em>· {t["affiliation"]}</em>' if t["affiliation"] else ""
            sections_html += f"""  <div class="talk-card">
    <div class="talk-meta">{t['date']} {time_html}</div>
    <div class="talk-title">{t['title']}</div>
    <div class="talk-speaker">{t['speaker']}{affil_html}</div>
    {detail_link}
  </div>\n"""

    body_html = f"""
  <h1 class="page-title">Online Seminar Series</h1>

  <div class="about-section">
    <p>The <strong>American Statistical Association (ASA) Marketing Section</strong> is excited to present an online research seminar series. This series aims to foster research, discussions, and engagement at the intersection of marketing and statistics, driven by the rapid advancements in both fields. Seminars this semester are on Tuesdays from 3:00–4:00 PM Eastern Time, featuring a 45-minute presentation followed by a 15-minute Q&amp;A.</p>
    <p>Follow us on <a href="https://www.linkedin.com/groups/14601729/" target="_blank" rel="noopener">LinkedIn</a> to stay up to date.</p>
    <p><strong>Current Organizers:</strong> Max Matthe (IU Kelley), Gourab Mukherjee (USC Marshall), Sam Levy (UVA Darden), and Dinesh Puranam (USF Muma)</p>
    <p>For any questions, please feel free to reach out to us at <a href="mailto:mpmatthe@iu.edu">mpmatthe [at] iu [dot] edu</a>.</p>
  </div>

{sections_html}"""

    (ROOT / "seminars.html").write_text(
        page("Online Seminar Series", body_html, root="", active="Seminars"), encoding="utf-8"
    )

# ── Build homepage ─────────────────────────────────────────────────────────
def build_homepage():
    body_html = """
  <h1 class="page-title">ASA Marketing Section</h1>
  <p class="page-subtitle">American Statistical Association</p>

  <div class="about-section">
    <p>The <strong>Marketing Section</strong> of the American Statistical Association promotes the development and application of statistical methods in marketing research and practice. We bring together academics and practitioners at the intersection of marketing and statistics.</p>
    <p>Follow us on <a href="https://www.linkedin.com/groups/14601729/" target="_blank" rel="noopener">LinkedIn</a> to stay up to date with section news and events.</p>
  </div>

  <h2 class="season-heading">Section Activities</h2>

  <div class="nav-cards">

    <a class="nav-card" href="seminars.html">
      <div class="nav-card-title">Online Seminar Series</div>
      <div class="nav-card-desc">Monthly research seminars at the intersection of marketing and statistics, featuring presentations by leading academics.</div>
    </a>

    <a class="nav-card" href="jsm.html">
      <div class="nav-card-title">JSM Sessions</div>
      <div class="nav-card-desc">Section-organized sessions at the Joint Statistical Meetings, the largest annual gathering of statisticians.</div>
    </a>

    <a class="nav-card" href="awards.html">
      <div class="nav-card-title">Student Paper Awards</div>
      <div class="nav-card-desc">Annual awards recognizing outstanding student research in marketing and statistics.</div>
    </a>

  </div>
"""
    (ROOT / "index.html").write_text(
        page("Home", body_html, root="", active="Home"), encoding="utf-8"
    )

# ── Build JSM page ─────────────────────────────────────────────────────────
def build_jsm():
    body_html = """
  <h1 class="page-title">JSM Sessions</h1>
  <p class="page-subtitle">Joint Statistical Meetings</p>

  <div class="about-section">
    <p>The ASA Marketing Section organizes sessions at the <strong>Joint Statistical Meetings (JSM)</strong>, the largest annual gathering of statisticians in North America. These sessions highlight cutting-edge research at the intersection of marketing and statistics.</p>
  </div>

  <h2 class="season-heading">JSM 2025 — Nashville, TN</h2>

  <!-- Session 1 -->
  <div class="jsm-session">
    <div class="jsm-session-type">Invited Paper Session</div>
    <div class="jsm-session-title">Probabilistic Machine Learning in Marketing</div>
    <div class="jsm-session-meta">
      Monday, August 4 &nbsp;·&nbsp; 10:30 AM – 12:20 PM &nbsp;·&nbsp; Music City Center, Room CC-202B
    </div>
    <div class="jsm-session-organizer">Organizer &amp; Chair: Hortense Fong</div>
    <ul class="jsm-talk-list">
      <li>
        <div class="jsm-talk-title">"A Bayesian Approach to Inferring the Effects of Events Using Cohorted Data"</div>
        <div class="jsm-talk-speaker">Shin Oblander (University of British Columbia) &mdash; with Leyao Tan</div>
      </li>
      <li>
        <div class="jsm-talk-title">"Graph Representation Learning for Inferring Market Structure"</div>
        <div class="jsm-talk-speaker">Mingyung Kim (Fisher College of Business, Ohio State University)</div>
      </li>
      <li>
        <div class="jsm-talk-title">"Thin But Not Forgotten: Deep Kernel Learning for Credit Risk Modeling with High-Dimensional Missingness"</div>
        <div class="jsm-talk-speaker">Longxiu Tian (UNC Kenan-Flagler Business School)</div>
      </li>
      <li>
        <div class="jsm-talk-title">"Unified Marketing Measurement: How to fuse experimental data with marketing mix data?"</div>
        <div class="jsm-talk-speaker">Nicolas Padilla (London Business School) &mdash; with Ryan Dew (Wharton)</div>
      </li>
    </ul>
  </div>

  <!-- Session 2 -->
  <div class="jsm-session">
    <div class="jsm-session-type">Topic-Contributed Paper Session</div>
    <div class="jsm-session-title">2025 ASA Statistics in Marketing Doctoral Research Award Finalists Presentation</div>
    <div class="jsm-session-meta">
      Wednesday, August 6 &nbsp;·&nbsp; 2:00 PM – 3:50 PM &nbsp;·&nbsp; Music City Center, Room CC-207C
    </div>
    <div class="jsm-session-organizer">Organizers: Shibo Li, Hortense Fong &nbsp;·&nbsp; Chair: Shibo Li</div>
    <ul class="jsm-talk-list">
      <li>
        <div class="jsm-talk-title">"A New Estimator for Encouragement Design in Randomized Controlled Trials When the Exclusion Restriction Is Violated"</div>
        <div class="jsm-talk-speaker">Guangying Chen (Washington University in St. Louis, Olin)</div>
      </li>
      <li>
        <div class="jsm-talk-title">"A Representative Sampling Method for Peer Encouragement Designs in Network Experiments"</div>
        <div class="jsm-talk-speaker">Yanyan Li (University of Southern California, Marshall)</div>
      </li>
      <li>
        <div class="jsm-talk-title">"Algorithmic Collusion of Pricing and Advertising on E-commerce Platforms"</div>
        <div class="jsm-talk-speaker">Hangcheng Zhao (University of Pennsylvania, Wharton)</div>
      </li>
      <li>
        <div class="jsm-talk-title">"Attribution and Compensation Design in Online Advertising"</div>
        <div class="jsm-talk-speaker">Yunhao Huang (University of California Berkeley, Haas)</div>
      </li>
      <li>
        <div class="jsm-talk-title">"What Makes for A Good Thumbnail? Video Content Summarization into A Single Image"</div>
        <div class="jsm-talk-speaker">Jasmine Yang (Columbia University)</div>
      </li>
    </ul>
  </div>

  <!-- Session 3 -->
  <div class="jsm-session jsm-session-mixer">
    <div class="jsm-session-type jsm-type-mixer">Mixer Meeting</div>
    <div class="jsm-session-title">Section on Statistics in Marketing Mixer</div>
    <div class="jsm-session-meta">
      Monday, August 4 &nbsp;·&nbsp; 3:00 PM – 5:00 PM &nbsp;·&nbsp; Omni Nashville Hotel, Room H – Broadway D
    </div>
  </div>
"""
    (ROOT / "jsm.html").write_text(
        page("JSM Sessions", body_html, root="", active="JSM Sessions"), encoding="utf-8"
    )

# ── Build awards page ──────────────────────────────────────────────────────
def build_awards():
    body_html = """
  <h1 class="page-title">Student Paper Awards</h1>
  <p class="page-subtitle">ASA Marketing Section</p>

  <div class="about-section">
    <p>The ASA Marketing Section presents annual awards to recognize outstanding student research at the intersection of marketing and statistics. Award winners are invited to present their work at JSM.</p>
  </div>

  <h2 class="season-heading">Doctoral Dissertation Award — 2025</h2>

  <div class="about-section">
    <p>The American Statistical Association (ASA) Section on Statistics in Marketing announces the winner and finalists for the <strong>2025 Best Doctoral Dissertation Proposal Competition</strong>. Congratulations to our finalists and their thesis advisors!</p>
  </div>

  <div class="award-block">
    <div class="award-label recipient-label">Recipient</div>
    <ul class="award-list">
      <li><strong>Yunhao Huang</strong> (University of California Berkeley, Haas)<br>
        <em>"Attribution and Compensation Design in Online Advertising"</em></li>
    </ul>
  </div>

  <div class="award-block">
    <div class="award-label finalist-label">Finalists</div>
    <ul class="award-list">
      <li><strong>Yanyan Li</strong> (University of Southern California, Marshall)<br>
        <em>"A Representative Sampling Method for Peer Encouragement Designs in Network Experiments"</em></li>
      <li><strong>Jasmine Yang</strong> (Columbia Business School)<br>
        <em>"A Scalable Framework for the Optimization of Video Content Summarization"</em></li>
      <li><strong>Hangcheng Zhao</strong> (University of Pennsylvania, Wharton)<br>
        <em>"Algorithmic Collusion of Pricing and Advertising on E-commerce Platforms"</em></li>
      <li><strong>Guangying Chen</strong> (Washington University in St. Louis, Olin)<br>
        <em>"A New Estimator for Encouragement Design in Randomized Controlled Trials When the Exclusion Restriction Is Violated"</em></li>
    </ul>
  </div>

  <h2 class="season-heading">Past Recipients</h2>

  <table class="award-table">
    <thead>
      <tr><th>Year</th><th>Recipient</th><th>Dissertation</th></tr>
    </thead>
    <tbody>
      <tr><td>2024</td><td><strong>Boya Xu</strong></td><td><em>"A Scalable Recommendation Engine for New Users and Items"</em></td></tr>
      <tr><td>2023</td><td>Yingkang Xie</td><td><em>"Platform Leakage: Incentive Conflicts in Two-Sided Markets"</em></td></tr>
      <tr><td>2022</td><td>Hortense Fong</td><td><em>"A Theory-Based Interpretable Deep Learning Architecture for Music Emotion"</em></td></tr>
      <tr><td>2021</td><td>Jeremy Yang</td><td><em>"Targeting for Long-Term Outcomes"</em></td></tr>
      <tr><td>2020</td><td>Min Kim</td><td><em>"Discovering Online Shopping Preference Structures in Large and Frequently Changing Assortments"</em></td></tr>
      <tr><td>2020</td><td>Omid Rafieian</td><td><em>"Adaptive Ad Sequencing"</em></td></tr>
      <tr><td>2018</td><td>Liu Liu</td><td><em>"Visual Listening in: Extract Brand Image Portrayed in Social Media"</em></td></tr>
      <tr><td>2018</td><td>Ryan Dew</td><td><em>"Gaussian Processes for Customer Purchasing Dynamics"</em></td></tr>
    </tbody>
  </table>
"""
    (ROOT / "awards.html").write_text(
        page("Student Paper Awards", body_html, root="", active="Student Paper Awards"), encoding="utf-8"
    )

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    src_files = sorted(TALKS_SRC.glob("*.md"))
    if not src_files:
        print("No .md files found in _talks/")
    else:
        talks = []
        for src in src_files:
            info = build_talk_page(src)
            talks.append(info)
            print(f"  built  talks/{info['slug']}.html  ({info['title'][:60]})")
        build_seminars(talks)
        print(f"  built  seminars.html  ({len(talks)} talks)")

    build_homepage()
    print("  built  index.html")
    build_jsm()
    print("  built  jsm.html")
    build_awards()
    print("  built  awards.html")
    print("Done.")

if __name__ == "__main__":
    main()
