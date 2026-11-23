#!/usr/bin/env python3
"""Render the branded Editor’s Picks share graphics with Chrome."""

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


def design(pick, serif, sans):
    flower = embedded(ASSETS / 'images' / pick['artwork'], 'image/jpeg')
    mark = embedded(ASSETS / 'flower.svg', 'image/svg+xml')
    title = escape(pick['title'])
    byline = escape(pick['author'])
    genre = escape(pick['genre'])
    title_length = len(pick['title'])
    title_size = 86 if title_length <= 24 else 68 if title_length <= 48 else 54
    return f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><title>{title} by {byline}</title>
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
.art {{ min-width: 0; height: {HEIGHT}px; padding: 32px 32px 32px 0; }}
.art img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
</style>
<body>
  <main class="copy">
    <div class="brand"><img src="{mark}" alt="">Anemone Magazine</div>
    <div>
      <p class="genre">Editor’s Picks · {genre}</p>
      <h1>{title}</h1>
      <p class="author">By {byline}</p>
    </div>
    <div class="footer">anemonemagazine.com</div>
  </main>
  <div class="art"><img src="{flower}" alt=""></div>
</body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', required=True, help='Path to a Chrome or Chromium executable')
    args = parser.parse_args()
    picks = json.loads((ROOT / 'site' / 'editors-picks.json').read_text(encoding='utf-8'))
    serif = embedded(ASSETS / 'fonts' / 'instrument-serif.woff2', 'font/woff2')
    sans = embedded(ASSETS / 'fonts' / 'dm-sans.woff2', 'font/woff2')
    destination = ASSETS / 'share'
    destination.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(prefix='anemone-share-') as directory:
        scratch = Path(directory)
        for pick in picks:
            source = scratch / f'{pick["slug"]}.html'
            graphic = scratch / f'{pick["slug"]}.png'
            source.write_text(design(pick, serif, sans), encoding='utf-8')
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
