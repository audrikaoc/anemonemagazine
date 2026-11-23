#!/usr/bin/env python3
"""Render the magazine into the docs directory for GitHub Pages."""

import json
import re
from html import escape
from pathlib import Path
from xml.etree import ElementTree
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site'
OUTPUT = ROOT / 'docs'
DOMAIN = 'https://www.anemonemagazine.com/'
PLACEHOLDER = re.compile(r'{{(\w+)}}')

PAGES = {
    '': ('Anemone Magazine | A place for your voice', 'An independent literary magazine publishing fiction, nonfiction, poetry, and art by young creators.'),
    'issues': ('Issue archive', 'Read past general and themed editions of Anemone Magazine.'),
    'submissions': ('Submission guidelines', 'Submit fiction, nonfiction, poetry, art, or photography to Anemone Magazine.'),
    'upcoming-issues': ('Calls for work', 'Find Anemone’s upcoming issues, submission deadlines, and staff applications.'),
    'writingworkshops': ('Writing workshops', 'Join Anemone’s free writing workshops or apply to volunteer as a mentor.'),
    'reach': ('Our reach', 'Explore a country-level map of Anemone Magazine’s contributors and readers.'),
    'masthead': ('Masthead', 'Meet the editors and creative team behind Anemone Magazine.'),
    'faqs': ('Frequently asked questions', 'Find answers to common questions about submitting to Anemone Magazine.'),
    'privacy-policy': ('Privacy policy', 'Learn how Anemone Magazine handles contributor information.'),
}
NAVIGATION = {'issues': 'Issues', 'writingworkshops': 'Workshops', 'masthead': 'Masthead', 'reach': 'Reach'}


def substitute(template, values):
    return PLACEHOLDER.sub(lambda match: values[match[1]], template)


def metadata(issue):
    label = f'Themed Issue {issue["theme"]}' if 'theme' in issue else 'General issue'
    return f'{label} · {issue["date"]}'


def artwork(filename, root, css_class, *, lazy=False):
    path = f'assets/images/{filename}'
    if not (OUTPUT / path).is_file():
        raise FileNotFoundError(OUTPUT / path)
    loading = ' loading="lazy"' if lazy else ''
    return (f'<img class="{css_class}" src="{root}{escape(path)}" alt="" '
            f'width="960" height="640" decoding="async"{loading}>')


def cover(issue, root, detail=False):
    title = escape(issue['title'])
    if filename := issue.get('cover'):
        cover_path = OUTPUT / 'assets' / 'covers' / filename
        if not cover_path.is_file():
            raise FileNotFoundError(cover_path)
        alt = f'Cover of {title}' if detail else ''
        loading = '' if detail else ' loading="lazy" decoding="async"'
        return f'<div class="cover-stage"><img src="{root}assets/covers/{escape(filename)}" alt="{alt}"{loading}></div>'
    return f'<div class="cover-stage fallback" aria-hidden="true"><span>{title}</span></div>'


def issue_cards(issues, root):
    return '\n    '.join(
        f'<a class="issue-card" href="{root}{issue["slug"]}/">'
        f'{cover(issue, root)}<span class="issue-meta">{escape(metadata(issue))}</span>'
        f'<span class="issue-title">{escape(issue["title"])}</span></a>'
        for issue in issues
    )


def reach_audiences(root):
    data = json.loads((SOURCE / 'reach.json').read_text(encoding='utf-8'))
    asset = 'assets/world-countries.svg'
    map_svg = ElementTree.parse(OUTPUT / asset).getroot()
    by_id = {element.get('id'): element for element in map_svg.iter() if 'id' in element.attrib}
    names = {
        key.removeprefix('country-'): element.findtext('{*}title')
        for key, element in by_id.items() if key.startswith('country-')
    }
    panels = []
    for audience, title in [('contributors', 'Contributor countries'), ('readers', 'Reader countries')]:
        detail = data[audience]
        codes = set(detail['countries'])
        if missing := codes - names.keys():
            raise ValueError(f'Unknown {audience} country codes: {", ".join(sorted(missing))}')
        ordered = sorted(codes, key=names.get)
        highlights = ''.join(f'<use href="{root}{asset}#country-{code}"/>' for code in ordered)
        markers = ''.join(f'<use href="{root}{asset}#marker-{code}"/>' for code in ordered if f'marker-{code}' in by_id)
        countries = ''
        if ordered:
            items = ''.join(f'<li>{escape(names[code])}</li>' for code in ordered)
            countries = f'\n      <ul class="reach-countries" aria-label="Countries shown">{items}</ul>'
        panels.append(f'''<section class="reach-panel reach-{audience}" aria-labelledby="{audience}-title">
      <svg class="reach-map" viewBox="{map_svg.attrib['viewBox']}" aria-hidden="true" fill-rule="evenodd">
        <use class="map-grid" href="{root}{asset}#world-graticule"/>
        <use class="map-land" href="{root}{asset}#world-land"/>
        <g class="map-highlight">{highlights}{markers}</g>
      </svg>
      <div class="reach-details">
        <h2 id="{audience}-title">{title}</h2>
        <p>{escape(detail['note'])}</p>{countries}
      </div>
    </section>''')
    return '\n    '.join(panels)


def team_cards(people, root):
    cards = []
    for person in people:
        if filename := person.get('portrait'):
            portrait = f'<img src="{root}assets/team/{escape(filename)}" alt="" loading="lazy" decoding="async" width="320" height="320">'
        else:
            initials = ''.join(part[0] for part in person['name'].split())
            portrait = f'<span aria-hidden="true">{escape(initials)}</span>'
        cards.append(
            f'<article class="person"><div class="person-photo">{portrait}</div><p class="role">{escape(person["role"])}</p>'
            f'<h3>{escape(person["name"])}</h3><p>{escape(person["bio"])}</p></article>'
        )
    return '\n    '.join(cards)


def issue_body(issue, default_artwork):
    title = escape(issue['title'])
    if reader := issue.get('reader'):
        description = '<p class="lede">Read the full edition in the magazine’s Canva reader.</p>'
        action = f'<a class="button" href="{escape(reader)}">Read the issue on Canva</a>'
    else:
        description = '<p class="lede">A digital reader is currently unavailable for this issue.</p>'
        action = '<a class="text-link" href="mailto:anemone.magazin@gmail.com">Ask the editors about this issue</a>'
    contents = ''
    if groups := issue.get('contents'):
        sections = []
        for group, pieces in groups.items():
            entries = ''.join(f'<li>{escape(piece)} <span>{escape(author)}</span></li>' for piece, author in pieces)
            sections.append(f'<section><h3>{escape(group)}</h3><ul>{entries}</ul></section>')
        contents = '\n    <div id="contents" class="prose issue-contents"><h2>In this issue</h2>' + ''.join(sections) + '</div>'
    return f'''<article class="wrap issue-detail">
  <div class="issue-detail-copy">
    <a class="back text-link" href="../issues/">All issues</a>
    <p class="eyebrow">{escape(metadata(issue))}</p>
    <h1>{title}</h1>
    {description}
    <div class="actions">{action}</div>{contents}
  </div>
  <figure class="issue-cover">{cover(issue, '../', detail=True)}</figure>
  {artwork(issue.get('artwork', default_artwork), '../', 'issue-art', lazy=True)}
</article>'''


def migration_redirect(destination, message):
    return f'''<header class="page-heading wrap">
  <h1>{message}</h1>
  <p><a class="text-link" href="../{destination}">Continue</a></p>
</header>'''


def write_page(path, html):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding='utf-8')


def build():
    data = json.loads((SOURCE / 'magazine.json').read_text(encoding='utf-8'))
    layout = (SOURCE / 'layout.html').read_text(encoding='utf-8')
    issues = {issue['slug']: issue for issue in data['issues']}
    page_artwork = data['page_artwork']
    external_links = {key: escape(value) for key, value in data.items() if isinstance(value, str)}
    urls = []

    def render(slug, title, desc, body, *, redirect=None, page_missing=False):
        root = './' if not slug else '../'
        url = f'{DOMAIN}{slug}/' if slug else DOMAIN
        head = f'<link rel="canonical" href="{url}">\n  <meta property="og:url" content="{url}">'
        if redirect is not None:
            head = f'<meta http-equiv="refresh" content="0; url={root}{redirect}">\n  <meta name="robots" content="noindex">'
        elif page_missing:
            root = '/'
            head = '<meta name="robots" content="noindex">'
            head += '''
  <script>
    if (location.hostname === 'audrikaoc.github.io') {
      document.addEventListener('DOMContentLoaded', () => {
        for (const element of document.querySelectorAll('[href^="/"], [src^="/"]')) {
          const attribute = element.hasAttribute('href') ? 'href' : 'src';
          element.setAttribute(attribute, '/anemonemagazine' + element.getAttribute(attribute));
        }
      });
    }
  </script>'''
        else:
            urls.append(url)
        navigation = ''
        for target, label in NAVIGATION.items():
            current = ' aria-current="page"' if target == slug else ''
            navigation += f'<li><a href="{root}{target}/"{current}>{label}</a></li>'
        issue = issues.get(slug, {})
        image_file = page_artwork.get(slug, issue.get('artwork', 'anemones-daylight.jpg'))
        image = f'assets/images/{image_file}'
        if cover_file := issue.get('cover'):
            image = f'assets/covers/{cover_file}'
        context = {
            **external_links,
            'root': root,
            'title': escape(f'{title} | Anemone Magazine' if slug else title),
            'description': escape(desc),
            'head': head,
            'social_image': DOMAIN + image,
            'navigation': navigation,
            'submission_current': ' aria-current="page"' if slug == 'submissions' else '',
            'body': body,
        }
        html = substitute(substitute(layout, context), context)
        path = OUTPUT / ('404.html' if page_missing else (f'{slug}/index.html' if slug else 'index.html'))
        write_page(path, html)

    for slug, (title, desc) in PAGES.items():
        root = '../' if slug else './'
        template = (SOURCE / 'pages' / f'{slug or "home"}.html').read_text(encoding='utf-8')
        keys = {
            **external_links,
            'root': root,
            'featured_issues': issue_cards((issues[key] for key in data['featured']), root) if not slug else '',
            'general_issues': issue_cards((issue for issue in issues.values() if 'theme' not in issue), root) if slug == 'issues' else '',
            'themed_issues': issue_cards((issue for issue in issues.values() if 'theme' in issue), root) if slug == 'issues' else '',
            'team': team_cards(data['team'], root) if slug == 'masthead' else '',
            'reach_audiences': reach_audiences(root) if slug == 'reach' else '',
            'page_artwork': artwork(page_artwork[slug], root, 'page-art') if slug in page_artwork else '',
            'mission_artwork': artwork('anemone-engraving.jpg', root, 'mission-art', lazy=True) if not slug else '',
        }
        render(slug, title, desc, substitute(template, keys))

    for issue in issues.values():
        render(issue['slug'], issue['title'], f'{metadata(issue)} from Anemone Magazine.',
               issue_body(issue, page_artwork['issues']))

    for slug, (destination, message) in {
        'home': ('', 'Anemone Magazine'),
        'questions': ('faqs/', 'Questions for the editors'),
        'new-page': ('issue-1/#contents', 'Art from Issue 1'),
        'new-page-1': ('issue-1/#contents', 'Light Dancer'),
        'new-page-2': ('issue-1/#contents', 'Decorated Cows'),
        'new-page-3': ('issue-1/#contents', 'CRACK'),
        'new-page-4': ('issues/', 'The issue archive'),
        'store': ('issues/', 'The issue archive'),
    }.items():
        render(slug, message, 'This page has moved.', migration_redirect(destination, message), redirect=destination)

    missing = substitute((SOURCE / 'pages' / '404.html').read_text(encoding='utf-8'), {
        'root': '/',
        'page_artwork': artwork(page_artwork['404'], '/', 'page-art'),
    })
    render('404', 'Page missing', 'Find your way back to Anemone Magazine.', missing, page_missing=True)
    write_page(OUTPUT / '.nojekyll', '')
    locations = '\n'.join(f'  <url><loc>{xml_escape(url)}</loc></url>' for url in sorted(urls))
    write_page(OUTPUT / 'sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
               f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{locations}\n</urlset>\n')
    write_page(OUTPUT / 'robots.txt', f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}sitemap.xml\n')


if __name__ == '__main__':
    build()
