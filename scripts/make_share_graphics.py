#!/usr/bin/env python3
"""Render branded share graphics for an issue or the Editor’s Picks with Chrome."""

import argparse
import base64
import json
import subprocess
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'docs' / 'assets'
WIDTH, HEIGHT = 1200, 630


def embedded(path, media_type):
    content = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'data:{media_type};base64,{content}'


def design(title, label, subtitle, image_path, url, serif, sans, *, photo=None):
    artwork = embedded(image_path, 'image/jpeg')
    mark = embedded(ASSETS / 'flower.svg', 'image/svg+xml')
    credit = ''
    if photo:
        attribution = escape(f'Photo by {photo["photographer"]} · {photo["license"]}')
        credit = f'<p class="photo-credit">{attribution}<br>anemonemagazine.com/photo-credits/</p>'
    title_length = len(title)
    title_size = 86 if title_length <= 24 else 68 if title_length <= 48 else 54
    page_class = '' if photo else ' class="edition"'
    return f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><title>{escape(title)} · Anemone Magazine</title>
<style>
@font-face {{ font-family: Instrument; src: url({serif}); }}
@font-face {{ font-family: DM; src: url({sans}); font-weight: 400 700; }}
*, *::before, *::after {{ box-sizing: border-box; }}
body {{ width: {WIDTH}px; height: {HEIGHT}px; margin: 0; display: grid; grid-template-columns: 54% 46%; background: #faf7ee; color: #25271c; font-family: DM, sans-serif; }}
.copy {{ display: flex; flex-direction: column; justify-content: space-between; gap: 22px; padding: 46px 54px; }}
.brand {{ display: flex; align-items: center; gap: 12px; font: 44px/1 Instrument, Georgia, serif; }}
.brand img {{ width: 34px; height: 34px; }}
.genre {{ margin: 0 0 15px; font-size: 19px; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; }}
h1 {{ margin: 0; font: {title_size}px/.97 Instrument, Georgia, serif; letter-spacing: -.012em; overflow-wrap: anywhere; }}
.author {{ margin: 20px 0 0; font-size: 29px; font-weight: 650; }}
.footer {{ padding-top: 18px; border-top: 1px solid #cbc9b9; color: #424b3c; font-size: 19px; font-weight: 650; }}
.photo-credit {{ margin: 6px 0 0; font-size: 16px; font-weight: 400; line-height: 1.35; }}
.art {{ min-width: 0; height: {HEIGHT}px; padding: 32px 32px 32px 0; }}
.art img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
.edition .art {{ padding: 32px; background: #eee5f1; }}
.edition .art img {{ object-fit: contain; filter: drop-shadow(0 5px 10px #25271c30); }}
</style>
<body{page_class}>
  <main class="copy">
    <div class="brand"><img src="{mark}" alt="">Anemone Magazine</div>
    <div>
      <p class="genre">{escape(label)}</p>
      <h1>{escape(title)}</h1>
      <p class="author">{escape(subtitle)}</p>
    </div>
    <div class="footer">{escape(url)}{credit}</div>
  </main>
  <div class="art"><img src="{artwork}" alt=""></div>
</body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', required=True, help='Path to a Chrome or Chromium executable')
    parser.add_argument('--issue', help='Render the share graphic for an issue by its slug')
    args = parser.parse_args()
    serif = embedded(ASSETS / 'fonts' / 'instrument-serif.woff2', 'font/woff2')
    sans = embedded(ASSETS / 'fonts' / 'dm-sans.woff2', 'font/woff2')
    destination = ASSETS / 'share'
    destination.mkdir(parents=True, exist_ok=True)

    if args.issue:
        data = json.loads((ROOT / 'site' / 'magazine.json').read_text(encoding='utf-8'))
        issue = next((item for item in data['issues'] if item['slug'] == args.issue), None)
        if not issue or not issue.get('reading_guide') or not issue.get('cover'):
            parser.error('Select an issue with a cover and reading guide')
        label = f'Themed Issue {issue["theme"]}' if 'theme' in issue else 'General issue'
        artworks = [(args.issue, design(issue['title'], f'{label} · {issue["date"]}',
                                       issue['reading_guide']['subtitle'], ASSETS / 'covers' / issue['cover'],
                                       f'anemonemagazine.com/{args.issue}/', serif, sans))]
    else:
        picks = json.loads((ROOT / 'site' / 'editors-picks.json').read_text(encoding='utf-8'))
        photos = json.loads((ROOT / 'site' / 'photo-credits.json').read_text(encoding='utf-8'))
        artworks = [
            (pick['slug'], design(pick['title'], f'Editor’s Picks · {pick["genre"]}', f'By {pick["author"]}',
                                 ASSETS / 'images' / pick['artwork'], 'anemonemagazine.com', serif, sans,
                                 photo=photos[pick['artwork']]))
            for pick in picks
        ]

    with TemporaryDirectory(prefix='anemone-share-') as directory:
        scratch = Path(directory)
        for slug, html in artworks:
            source = scratch / f'{slug}.html'
            graphic = scratch / f'{slug}.png'
            source.write_text(html, encoding='utf-8')
            subprocess.run([
                args.browser, '--headless', '--no-first-run', '--disable-gpu', '--hide-scrollbars',
                f'--user-data-dir={scratch / "chrome"}', f'--window-size={WIDTH},{HEIGHT}',
                '--force-device-scale-factor=1', '--virtual-time-budget=2000',
                f'--screenshot={graphic}', source.as_uri(),
            ], check=True, capture_output=True)
            (destination / graphic.name).write_bytes(graphic.read_bytes())
            print((destination / graphic.name).relative_to(ROOT))


if __name__ == '__main__':
    main()
