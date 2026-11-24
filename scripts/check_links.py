#!/usr/bin/env python3
"""Check the built site’s local destinations, asset paths, and fragments."""

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree

DOCS = Path(__file__).resolve().parents[1] / 'docs'
HOST = 'www.anemonemagazine.com'
CSS_LINK = re.compile(r'url\([\'\"]?([^\'\"\s)]+)')


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.targets = set()
        self.links = set()
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get('id'):
            self.targets.add(attributes['id'])
        self.links.update(attributes[key] for key in ('href', 'src') if attributes.get(key))
        if tag == 'meta' and attributes.get('http-equiv', '').lower() == 'refresh':
            self.links.add(attributes['content'].partition('url=')[2])


def check():
    pages = {path: Page(path) for path in DOCS.rglob('*.html')}
    sources = {path: page.links for path, page in pages.items()}
    targets = {path: page.targets for path, page in pages.items()}
    for path in DOCS.rglob('*.svg'):
        targets[path] = {element.get('id') for element in ElementTree.parse(path).iter() if 'id' in element.attrib}
    for path in DOCS.rglob('*.css'):
        sources[path] = set(CSS_LINK.findall(path.read_text(encoding='utf-8')))

    errors = []
    checked = 0
    for source, links in sources.items():
        base = f'https://{HOST}/{source.relative_to(DOCS).as_posix()}'
        for value in sorted(links):
            url = urlsplit(urljoin(base, value))
            if url.hostname != HOST:
                continue
            checked += 1
            target = DOCS / unquote(url.path.lstrip('/'))
            if target.is_dir():
                target /= 'index.html'
            if not target.is_file() or not target.resolve().is_relative_to(DOCS):
                errors.append(f'{source.relative_to(DOCS)}: missing target {value}')
            elif url.fragment and target in targets and unquote(url.fragment) not in targets[target]:
                errors.append(f'{source.relative_to(DOCS)}: missing fragment {value}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Checked {checked} internal links and assets across {len(pages)} pages.')


if __name__ == '__main__':
    check()
