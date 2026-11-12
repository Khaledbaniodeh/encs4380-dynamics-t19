#!/usr/bin/env python3
"""Safely add Module 4 to an EXISTING local Dynamics Lab repo.

No GitHub API, no upload, no network writes. Run on a local copy of:
  Khaledbaniodeh/encs4380-dynamics-t19

Usage:
  python tools/integrate_module4.py --repo "C:/path/to/encs4380-dynamics-t19"
  python tools/integrate_module4.py --repo "C:/path/to/encs4380-dynamics-t19" --apply

Without --apply it is a DRY RUN. On apply, existing files are backed up.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys


def add_index_card(html: str) -> str:
    """Enable existing Module 4 roadmap card and add its working link."""
    if 'href="module-4.html"' not in html:
        old = ('<article><p class="card-kicker">04 / Planned</p>'
               '<h3>Guess the sensor</h3><p>Read an unfamiliar response curve and estimate the hidden sensor’s characteristics.</p></article>')
        new = ('<article><p class="card-kicker">04 / Available</p>'
               '<h3>Guess the sensor</h3><p>Read a noisy step or sine response and estimate the hidden sensor parameters. '
               'Reveal the true curve and score your guess.</p>'
               '<p><a class="btn primary" href="module-4.html">Open Module 4 <span aria-hidden="true">→</span></a></p></article>')
        if old not in html:
            raise ValueError('Index page changed; cannot safely find the planned Module 4 card.')
        html = html.replace(old, new, 1)
    html = html.replace('Modules 1–3 available', 'Modules 1–4 available')
    html = html.replace('Continue with Modules 2 and 3 · Module 4 coming next', 'Continue with Modules 2, 3 and 4')
    return html


def add_header_link(html: str, module: int) -> str:
    """Add a Module 4 link to the existing module switcher in Modules 2 and 3."""
    if 'href="module-4.html"' in html:
        return html
    nav_start = html.find('<nav class="module-nav"')
    if nav_start == -1:
        raise ValueError(f'Module {module} nav not found; cannot patch safely.')
    nav_end = html.find('</nav>', nav_start)
    if nav_end == -1:
        raise ValueError(f'Module {module} nav is incomplete.')
    return html[:nav_end] + '      <a href="module-4.html">Module 4</a>\n    ' + html[nav_end:]


def add_module1_switcher(html: str) -> str:
    """Module 1 has no header module-nav; add a compact switcher near breadcrumb."""
    if 'href="module-4.html"' in html:
        return html
    breadcrumb_end = html.find('</nav>', html.find('<nav class="breadcrumb"'))
    if breadcrumb_end == -1:
        raise ValueError('Module 1 breadcrumb not found; cannot add module switcher.')
    breadcrumb_end += len('</nav>')
    switcher = '''
 <nav class="module4-switcher" aria-label="Switch between modules">
  <a href="./">Home</a><a href="module-1.html" aria-current="page">Module 1</a>
  <a href="module-2.html">Module 2</a><a href="module-3.html">Module 3</a>
  <a href="module-4.html">Module 4</a>
 </nav>'''
    css = '''
/* Small, responsive module switcher added for integration with Module 4. */
.module4-switcher{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0 16px}
.module4-switcher a{display:inline-flex;align-items:center;min-height:40px;padding:8px 12px;
  border:1px solid #c7d5d6;border-radius:9px;color:#087f72;font-size:12px;font-weight:650}
.module4-switcher a[aria-current="page"]{background:#e7f5f1;border-color:#087f72}
@media(max-width:440px){.module4-switcher{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}
.module4-switcher a{justify-content:center;padding:8px 4px}}
'''
    if '</style>' not in html:
        raise ValueError('Module 1 style closing tag not found.')
    html = html.replace('</style>', css + '</style>', 1)
    # The CSS insertion is before the breadcrumb; insert switcher into the updated markup.
    breadcrumb_end = html.find('</nav>', html.find('<nav class="breadcrumb"')) + len('</nav>')
    html = html[:breadcrumb_end] + switcher + html[breadcrumb_end:]
    return html


def add_readme_note(html: str) -> str:
    title = '## Module 4 — Guess the Sensor'
    if title in html:
        return html
    return html.rstrip() + '''

## Module 4 — Guess the Sensor

- **Owner:** [add the responsible team member]
- **Page:** [Module 4](module-4.html)
- **Features:** random first-order step/sine and second-order step challenges;
  noisy measurements; estimation hints; hidden true parameters until submit;
  plotted true and predicted responses; 10% full-credit threshold;
  partial-credit scoring; and a session total with average and round count.
- **Technology:** Python closed-form calculations running in-browser via Pyodide,
  plus JavaScript and Plotly. No server or login is required for visitors.
- **Testing:** `python -m unittest discover -s tests -v` and desktop/mobile
  browser checks; take screenshots from the running page for the submission.
- **AI assistance:** ChatGPT was used to help draft and review Module 4 code,
  tests, documentation and integration instructions. The team should review,
  understand and be prepared to explain every submitted line.

See the Module 4 section of `README.md` for formulas, scoring and browser setup.
'''


def build_changes(repo: Path, package: Path) -> dict[Path, str | Path]:
    required = ['index.html', 'module-1.html', 'module-2.html', 'module-3.html', 'README.md']
    for name in required:
        if not (repo / name).is_file():
            raise FileNotFoundError(f'Cannot find {name} in local repository {repo}.')
    updates: dict[Path, str | Path] = {}
    updates[repo/'index.html'] = add_index_card((repo/'index.html').read_text(encoding='utf-8'))
    updates[repo/'module-1.html'] = add_module1_switcher((repo/'module-1.html').read_text(encoding='utf-8'))
    for num in (2, 3):
        src = repo/f'module-{num}.html'
        updates[src] = add_header_link(src.read_text(encoding='utf-8'), num)
    updates[repo/'README.md'] = add_readme_note((repo/'README.md').read_text(encoding='utf-8'))
    for relative_path in (
        'module-4.html', 'python/guess_sensor.py', 'tests/test_guess_sensor.py',
        'docs/module4_demo.md',
    ):
        src = package/relative_path
        if not src.is_file():
            raise FileNotFoundError(f'Missing package file: {src}')
        updates[repo/relative_path] = src
    return updates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True, help='Path to local team repository')
    parser.add_argument('--apply', action='store_true', help='Write local files (default: preview only)')
    args = parser.parse_args()
    package = Path(__file__).resolve().parents[1]
    repo = args.repo.expanduser().resolve()
    if not repo.is_dir():
        parser.error('Local repository directory not found.')
    try:
        updates = build_changes(repo, package)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    changed: dict[Path, str | Path] = {}
    for dest, data in updates.items():
        new_bytes = data.encode('utf-8') if isinstance(data, str) else data.read_bytes()
        if not dest.exists() or dest.read_bytes() != new_bytes:
            changed[dest] = data
    if not changed:
        print('Already integrated; no changes needed.')
        return

    print(f'{"APPLY" if args.apply else "PREVIEW ONLY"} — {len(changed)} files:')
    for dest in changed:
        print('  ', dest.relative_to(repo))
    if not args.apply:
        print('No files modified. Re-run with --apply to change a LOCAL copy.')
        return

    backup = repo/'.module4-backups'/datetime.now().strftime('%Y%m%d-%H%M%S')
    for dest in changed:
        if dest.exists():
            target = backup/dest.relative_to(repo)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, target)
    for dest, data in changed.items():
        dest.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, str):
            dest.write_text(data, encoding='utf-8')
        else:
            shutil.copy2(data, dest)
    print('Finished LOCAL integration. GitHub was NOT modified.')
    print('Backup of overwritten files:', backup)
    print('Test: python -m http.server 8000 (from your local repo directory)')


if __name__ == '__main__':
    main()
