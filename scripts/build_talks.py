#!/usr/bin/env python3
"""Convert _talks/*.md files to talks/*.html and regenerate seminars.html"""

import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pip install pyyaml markdown")

try:
    import markdown
except ImportError:
    sys.exit("Missing dependency: pip install pyyaml markdown")

REPO_ROOT = Path(__file__).parent.parent
TALKS_SRC = REPO_ROOT / "_talks"
TALKS_OUT = REPO_ROOT / "talks"
SEMINARS_HTML = REPO_ROOT / "seminars.html"

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)

# Static content preserved from seminars.html
SEMINARS_HEADER = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Online Seminar Series — ASA Marketing Section</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
<header class="site-header">
  <a class="nav-title" href="index.html">ASA Marketing Section</a>
  <nav>
    <a href="index.html">Home</a>
    <a href="seminars.html" class="active">Seminars</a>
    <a href="jsm.html">JSM Sessions</a>
    <a href="awards.html">Student Paper Awards</a>
  </nav>
</header>
<main class="page-content">

  <h1 class="page-title">Online Seminar Series</h1>

  <div class="about-section">
    <p>The <strong>American Statistical Association (ASA) Marketing Section</strong> is excited to present an online research seminar series. This series aims to foster research, discussions, and engagement at the intersection of marketing and statistics, driven by the rapid advancements in both fields. Seminars this semester are on Tuesdays from 3:00\u20134:00 PM Eastern Time, featuring a 45-minute presentation followed by a 15-minute Q&amp;A.</p>
    <p>Follow us on <a href="https://www.linkedin.com/groups/14601729/" target="_blank" rel="noopener">LinkedIn</a> to stay up to date.</p>
    <p><strong>Subscribe to our calendar:</strong> <a href="https://calendar.google.com/calendar/embed?src=c_219b6a770fca4e387d40582828a9114de0617e71692dc6d15f5be71816f72af1%40group.calendar.google.com&ctz=America%2FNew_York" target="_blank" rel="noopener">Google Calendar</a> &nbsp;·&nbsp; <a href="https://calendar.google.com/calendar/ical/c_219b6a770fca4e387d40582828a9114de0617e71692dc6d15f5be71816f72af1%40group.calendar.google.com/public/basic.ics">iCal</a></p>
    <p><strong>Current Organizers:</strong> Max Matthe (IU Kelley), Gourab Mukherjee (USC Marshall), Sam Levy (UVA Darden), and Dinesh Puranam (USF Muma)</p>
    <p>For any questions, please feel free to reach out to us at <a href="mailto:mpmatthe@iu.edu">mpmatthe [at] iu [dot] edu</a>.</p>
  </div>
"""

SEMINARS_FOOTER = """\

</main>
<footer class="site-footer">
  American Statistical Association — Marketing Section
</footer>
</body>
</html>
"""


def parse_md(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError(f"No YAML front matter found in {path}")

    meta = yaml.safe_load(m.group(1))
    body = m.group(2).strip()

    talks = meta.get("talks", None)
    is_multi = isinstance(talks, list) and len(talks) > 1

    if is_multi:
        # Split body by "---" separator into per-talk abstracts
        sections = re.split(r'\n\s*---\s*\n', body)
        for i, t in enumerate(talks):
            abstract_text = sections[i].strip() if i < len(sections) else ""
            t["abstract_html"] = markdown.markdown(abstract_text)
        title = ""  # no single title; handled per-talk in template
        abstract_html = ""
    else:
        # First line starting with "# " is the title
        title = ""
        abstract_lines = []
        for line in body.splitlines():
            if not title and line.startswith("# "):
                title = line[2:].strip()
            else:
                abstract_lines.append(line)
        abstract_md = "\n".join(abstract_lines).strip()
        abstract_html = markdown.markdown(abstract_md)

    # Parse date string into a datetime for sorting
    date_str = str(meta.get("date", ""))
    try:
        date_obj = datetime.strptime(date_str, "%B %d, %Y")
    except ValueError:
        date_obj = datetime.min

    return {
        **meta,
        "title": title,
        "abstract_html": abstract_html,
        "slug": path.stem,
        "date_obj": date_obj,
        "is_multi": is_multi,
    }


def render_talk_html(data: dict) -> str:
    date = data.get("date", "")
    time = data.get("time", "")
    zoom = data.get("zoom", "")
    is_multi = data.get("is_multi", False)
    talks = data.get("talks", [])

    meta_line = f"{date} &nbsp;·&nbsp; {time}" if date else ""
    zoom_block = (
        f'  <a class="action-link zoom-link" href="{zoom}" target="_blank" rel="noopener">Join via Zoom ↗</a>'
        if zoom else ""
    )

    if is_multi:
        page_title = " & ".join(t.get("title", "") for t in talks) + " — ASA Marketing Section"
        talk_sections = ""
        for i, t in enumerate(talks):
            if i > 0:
                talk_sections += '\n  <hr style="margin: 2rem 0; border: none; border-top: 1px solid #eee;">\n\n'
            talk_sections += f"""  <h1 class="talk-detail-title">{t.get("title", "")}</h1>

  <div class="talk-detail-speaker">
    <strong>{t.get("speaker", "")}</strong>
    <br>{t.get("affiliation", "")}
  </div>

  <div class="abstract-heading">Abstract</div>
  <div class="abstract-text">
    {t.get("abstract_html", "")}
  </div>
"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{page_title}</title>
  <link rel="stylesheet" href="../style.css" />
</head>
<body>
<header class="site-header">
  <a class="nav-title" href="../index.html">ASA Marketing Section</a>
  <nav>
    <a href="../index.html">Home</a>
    <a href="../seminars.html" class="active">Seminars</a>
    <a href="../jsm.html">JSM Sessions</a>
    <a href="../awards.html">Student Paper Awards</a>
  </nav>
</header>
<main class="page-content">

  <a class="back-link" href="../seminars.html">← Back to all seminars</a>

  <div class="talk-detail-meta">
    {meta_line}
  </div>

{zoom_block}

  <hr style="margin: 2rem 0; border: none; border-top: 1px solid #eee;">

{talk_sections}
</main>
<footer class="site-footer">
  American Statistical Association — Marketing Section
</footer>
</body>
</html>
"""
    else:
        title = data.get("title") or "Title TBD"
        speaker = data.get("speaker", "")
        affiliation = data.get("affiliation", "")
        abstract_html = data.get("abstract_html", "<p>Abstract TBD</p>")
        page_title = f"{title} — ASA Marketing Section"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{page_title}</title>
  <link rel="stylesheet" href="../style.css" />
</head>
<body>
<header class="site-header">
  <a class="nav-title" href="../index.html">ASA Marketing Section</a>
  <nav>
    <a href="../index.html">Home</a>
    <a href="../seminars.html" class="active">Seminars</a>
    <a href="../jsm.html">JSM Sessions</a>
    <a href="../awards.html">Student Paper Awards</a>
  </nav>
</header>
<main class="page-content">

  <a class="back-link" href="../seminars.html">← Back to all seminars</a>

  <div class="talk-detail-meta">
    {meta_line}
  </div>

  <h1 class="talk-detail-title">{title}</h1>

  <div class="talk-detail-speaker">
    <strong>{speaker}</strong>
    <br>{affiliation}

  </div>

{zoom_block}


  <hr style="margin: 2rem 0; border: none; border-top: 1px solid #eee;">

  <div class="abstract-heading">Abstract</div>
  <div class="abstract-text">
    {abstract_html}
  </div>

</main>
<footer class="site-footer">
  American Statistical Association — Marketing Section
</footer>
</body>
</html>
"""


def render_seminars_html(all_talks: list) -> str:
    # Group by season, preserve season ordering (newest first)
    seasons = {}
    for talk in sorted(all_talks, key=lambda t: t["date_obj"], reverse=True):
        season = talk.get("season", "")
        if season not in seasons:
            seasons[season] = []
        seasons[season].append(talk)

    cards_html = ""
    for season, talks in seasons.items():
        cards_html += f'  <h2 class="season-heading">{season}</h2>\n'
        for t in talks:
            date = t.get("date", "")
            time = t.get("time", "")
            slug = t.get("slug", "")
            meta_line = f"{date} &nbsp;·&nbsp; {time}" if date else date

            if t.get("is_multi"):
                talk_list = t.get("talks", [])
                inner = ""
                for i, talk in enumerate(talk_list):
                    style = ' style="margin-top: 0.75rem;"' if i > 0 else ""
                    inner += f'    <div class="talk-title"{style}>{talk.get("title", "")}</div>\n'
                    inner += f'    <div class="talk-speaker">{talk.get("speaker", "")}&nbsp;<em>· {talk.get("affiliation", "")}</em></div>\n'
                cards_html += f"""\
  <div class="talk-card">
    <div class="talk-meta">{meta_line}</div>
{inner}    <a class="read-more" href="talks/{slug}.html">Read more →</a>
  </div>
"""
            else:
                title = t.get("title") or "Title TBD"
                speaker = t.get("speaker", "")
                affiliation = t.get("affiliation", "")
                cards_html += f"""\
  <div class="talk-card">
    <div class="talk-meta">{meta_line}</div>
    <div class="talk-title">{title}</div>
    <div class="talk-speaker">{speaker}&nbsp;<em>· {affiliation}</em></div>
    <a class="read-more" href="talks/{slug}.html">Read more →</a>
  </div>
"""

    return SEMINARS_HEADER + cards_html + SEMINARS_FOOTER


def build_all():
    TALKS_OUT.mkdir(exist_ok=True)
    md_files = list(TALKS_SRC.glob("*.md"))
    if not md_files:
        print("No .md files found in _talks/")
        return

    all_talks = []
    for md_path in md_files:
        slug = md_path.stem
        out_path = TALKS_OUT / f"{slug}.html"
        try:
            data = parse_md(md_path)
            html = render_talk_html(data)
            out_path.write_text(html, encoding="utf-8")
            print(f"  {md_path.name} → talks/{slug}.html")
            all_talks.append(data)
        except Exception as e:
            print(f"  ERROR processing {md_path.name}: {e}", file=sys.stderr)

    # Regenerate seminars.html
    seminars_html = render_seminars_html(all_talks)
    SEMINARS_HTML.write_text(seminars_html, encoding="utf-8")
    print(f"  → seminars.html")


if __name__ == "__main__":
    build_all()
