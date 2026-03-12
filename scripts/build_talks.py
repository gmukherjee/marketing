#!/usr/bin/env python3
"""Convert _talks/*.md files to talks/*.html"""

import re
import sys
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

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)


def parse_md(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError(f"No YAML front matter found in {path}")

    meta = yaml.safe_load(m.group(1))
    body = m.group(2).strip()

    # First non-empty line starting with "# " is the title
    title = ""
    abstract_lines = []
    for line in body.splitlines():
        if not title and line.startswith("# "):
            title = line[2:].strip()
        else:
            abstract_lines.append(line)

    abstract_md = "\n".join(abstract_lines).strip()
    abstract_html = markdown.markdown(abstract_md)

    return {**meta, "title": title, "abstract_html": abstract_html}


def render_html(data: dict) -> str:
    title = data.get("title") or "Title TBD"
    date = data.get("date", "")
    time = data.get("time", "")
    speaker = data.get("speaker", "")
    affiliation = data.get("affiliation", "")
    zoom = data.get("zoom", "")
    abstract_html = data.get("abstract_html", "<p>Abstract TBD</p>")

    page_title = f"{title} — ASA Marketing Section"
    meta_line = f"{date} &nbsp;·&nbsp; {time}" if date else ""
    zoom_block = (
        f'  <a class="action-link zoom-link" href="{zoom}" target="_blank" rel="noopener">Join via Zoom ↗</a>'
        if zoom
        else ""
    )

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


def build_all():
    TALKS_OUT.mkdir(exist_ok=True)
    md_files = list(TALKS_SRC.glob("*.md"))
    if not md_files:
        print("No .md files found in _talks/")
        return

    for md_path in md_files:
        slug = md_path.stem
        out_path = TALKS_OUT / f"{slug}.html"
        try:
            data = parse_md(md_path)
            html = render_html(data)
            out_path.write_text(html, encoding="utf-8")
            print(f"  {md_path.name} → talks/{slug}.html")
        except Exception as e:
            print(f"  ERROR processing {md_path.name}: {e}", file=sys.stderr)


if __name__ == "__main__":
    build_all()
