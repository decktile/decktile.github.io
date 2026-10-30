#!/usr/bin/env python3
"""Build the decktile website: render every deck in decks/ and write an index page.

Output goes to _site/ (decks as HTML + PDF, assets copied, not symlinked),
ready to upload to GitHub Pages.
"""

import argparse
import html
import re
import shutil
import subprocess
from pathlib import Path

API_DOCS = "https://decktile.github.io/decktile/"
REPO = "https://github.com/decktile/decktile"
PYPI = "https://pypi.org/project/decktile/"

# Order and one-line blurbs for the gallery; decks not listed come last.
DECKS = {
    "features_demo": ("Every feature", "Layouts, cards, metrics, tables, code, diagrams, charts and speaker cards in one deck."),
    "pdg_demo": ("Diagrams", "predictygraph flowcharts, groups and state machines that pick up the slide theme, plus animated diagrams."),
    "timeline_demo": ("Timelines", "Vertical and horizontal timelines that fit four or more steps."),
    "mermaid_demo": ("Mermaid", "Flowcharts and sequence diagrams from mermaid blocks."),
    "seaborn_demo": ("Charts", "Seaborn and matplotlib charts coloured by the theme."),
    "drawings": ("Drawings", "Explainer charts from a real talk: memory, compute and time slicing, drawn with matplotlib."),
    "lucide_demo": ("Icons", "Lucide icons inline in headings, cards and tables."),
    "kubecon_theme": ("Conference theme", "A built-in event theme: logo, watermark and title slide."),
}


class SiteBuilder:
    def __init__(self, src: Path, out: Path, decktile: list[str]):
        self.src = src
        self.out = out
        self.decktile = decktile

    def decks(self) -> list[Path]:
        found = {p.stem: p for p in sorted(self.src.glob("*.md"))}
        order = [s for s in DECKS if s in found] + [s for s in found if s not in DECKS]
        return [found[s] for s in order]

    @staticmethod
    def slide_count(md: Path) -> int:
        text = md.read_text(encoding="utf-8")
        body = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)
        return len(re.split(r"\n---\n", body))

    def render(self, md: Path) -> None:
        subprocess.run([*self.decktile, "-o", str(self.out), "--pdf", str(md)], check=True)

    def copy_assets(self) -> None:
        link = self.out / "assets"
        if link.is_symlink() or link.is_file():
            link.unlink()
        elif link.exists():
            shutil.rmtree(link)
        shutil.copytree(self.src / "assets", link)

    def index(self, decks: list[Path]) -> str:
        cards = []
        for md in decks:
            title, blurb = DECKS.get(md.stem, (md.stem.replace("_", " ").title(), ""))
            n = self.slide_count(md)
            cards.append(f"""
      <article class="deck">
        <a class="thumb" href="{md.stem}.html"><iframe src="{md.stem}.html" loading="lazy" tabindex="-1" title="{html.escape(title)}"></iframe></a>
        <h3><a href="{md.stem}.html">{html.escape(title)}</a></h3>
        <p>{html.escape(blurb)}</p>
        <p class="links"><a href="{md.stem}.html">Slides</a> · <a href="{md.stem}.pdf">PDF</a> ·
          <a href="{REPO}/blob/master/examples/{md.name}">Markdown</a> · {n} slides</p>
      </article>""")
        return PAGE.format(cards="".join(cards), api=API_DOCS, repo=REPO, pypi=PYPI)

    def build(self) -> None:
        if self.out.exists():
            shutil.rmtree(self.out)
        self.out.mkdir(parents=True)
        decks = self.decks()
        for md in decks:
            self.render(md)
        self.copy_assets()
        for f in ("decktile-logo.svg", "decktile-logo-dark.svg", "decktile-mark.svg"):
            shutil.copy(Path(__file__).resolve().parent.parent / f, self.out / f)
        (self.out / "index.html").write_text(self.index(decks), encoding="utf-8")
        (self.out / ".nojekyll").write_text("", encoding="utf-8")
        print(f"built {len(decks)} decks into {self.out}")


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>decktile: Markdown to designed slides</title>
  <meta name="description" content="Write slides in Markdown, get designed decks as HTML, PDF and editable ODP. Pure Python.">
  <link rel="icon" href="decktile-mark.svg">
  <style>
    :root {{ --ink:#0f172a; --muted:#475569; --teal:#0d9488; --bg:#f8fafc; --card:#fff; --line:#e2e8f0; }}
    @media (prefers-color-scheme: dark) {{
      :root {{ --ink:#f1f5f9; --muted:#94a3b8; --teal:#5eead4; --bg:#0d1117; --card:#161b22; --line:#30363d; }}
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color:var(--ink); background:var(--bg); }}
    a {{ color: var(--teal); }}
    header, main, footer {{ max-width: 1120px; margin: 0 auto; padding: 0 24px; }}
    header {{ padding-top: 56px; padding-bottom: 24px; }}
    header img {{ height: 72px; }}
    .lead {{ font-size: 1.3rem; color: var(--muted); max-width: 46rem; }}
    pre {{ background: var(--card); border:1px solid var(--line); border-radius: 10px; padding: 14px 18px; overflow-x:auto; }}
    nav a {{ margin-right: 18px; font-weight: 600; }}
    ul.why {{ padding-left: 1.2rem; color: var(--muted); line-height: 1.7; }}
    ul.why b {{ color: var(--ink); }}
    h2 {{ margin-top: 48px; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; }}
    .deck {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; overflow:hidden; }}
    .deck h3, .deck p {{ margin: 10px 16px; }}
    .deck p {{ color: var(--muted); }}
    .deck .links {{ font-size: .9rem; margin-bottom: 16px; }}
    .thumb {{ display:block; position:relative; aspect-ratio: 16/9; overflow:hidden; border-bottom:1px solid var(--line); }}
    .thumb iframe {{ position:absolute; top:0; left:0; width:1280px; height:720px; border:0; transform: scale(.25); transform-origin: 0 0; pointer-events:none; }}
    footer {{ padding: 48px 24px; color: var(--muted); font-size: .9rem; }}
  </style>
</head>
<body>
  <header>
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="decktile-logo-dark.svg">
      <img src="decktile-logo.svg" alt="decktile">
    </picture>
    <p class="lead">Write slides in Markdown. Get designed decks as HTML, PDF and editable ODP.</p>
    <nav>
      <a href="#examples">Examples</a>
      <a href="{api}">Docs &amp; API</a>
      <a href="{repo}">GitHub</a>
      <a href="{pypi}">PyPI</a>
    </nav>
  </header>
  <main>
    <pre><code>pip install decktile
decktile --pdf --odp slides.md</code></pre>
    <ul class="why">
      <li><b>Pure Python.</b> No Node.js, no browser, no system tools for diagrams.</li>
      <li><b>Looks designed by default.</b> Cards, grids, metrics, timelines and conference themes, no CSS to write.</li>
      <li><b>Editable ODP.</b> Opens in PowerPoint, Keynote, Google Slides and LibreOffice, with real text, lists and tables.</li>
      <li><b>Diagrams built in.</b> predictygraph, mermaid and seaborn blocks take your theme's fonts and colours. predictygraph diagrams can animate: flowing edges and pulsing outlines in the HTML deck, a clean still frame in PDF.</li>
    </ul>
    <h2 id="examples">Example decks</h2>
    <p class="lead" style="font-size:1rem">Each deck is built from the Markdown next to it by this site's CI with the latest decktile. Click to present; press <b>P</b> for presenter view.</p>
    <div class="grid">{cards}
    </div>
  </main>
  <footer>
    decktile is GPL-3.0-or-later. <a href="{api}">Documentation and API reference</a> ·
    <a href="{repo}">Source</a> · <a href="{repo}/releases">Releases</a>
  </footer>
</body>
</html>
"""


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--src", type=Path, default=Path("decktile/examples"),
                   help="examples/ of a decktile checkout")
    p.add_argument("--out", type=Path, default=Path("_site"))
    p.add_argument("--decktile", default="decktile", help="command to run decktile")
    args = p.parse_args()
    SiteBuilder(args.src, args.out, args.decktile.split()).build()


if __name__ == "__main__":
    main()
