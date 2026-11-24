#!/usr/bin/env python3
"""Render the magazine into the docs directory for GitHub Pages."""

import json
import re
from hashlib import sha256
from html import escape
from pathlib import Path
from xml.etree import ElementTree
from xml.sax.saxutils import escape as xml_escape

from submission_calendar import CALENDAR_FILE, calendar_calls, deadline_preview, write_calendar

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site'
OUTPUT = ROOT / 'docs'
DOMAIN = 'https://www.anemonemagazine.com/'
PLACEHOLDER = re.compile(r'{{(\w+)}}')

PAGES = {
    '': ('Anemone Magazine | A place for your voice', 'An independent literary magazine publishing fiction, nonfiction, poetry, and art by young creators.'),
    'issues': ('Issue archive', 'Read past general and themed editions of Anemone Magazine.'),
    'editors-picks': ('Editor’s Picks', 'Discover selected fiction, poetry, and essays from the Anemone Magazine archive.'),
    'submissions': ('Submission guidelines', 'Submit fiction, nonfiction, poetry, art, or photography to Anemone Magazine.'),
    'upcoming-issues': ('Submission calendar', 'Find Anemone’s submission deadlines, upcoming themes, and staff applications.'),
    'writingworkshops': ('Writing workshops', 'Join Anemone’s free writing workshops or apply to volunteer as a mentor.'),
    'writing-resources': ('Writing resources', 'Find poetry prompts for teens, fiction revision exercises, and a guide to submitting your first short story.'),
    'reach': ('Our reach', 'Explore a country-level map of Anemone Magazine’s contributors and readers.'),
    'masthead': ('Masthead', 'Meet the editors and creative team behind Anemone Magazine.'),
    'faqs': ('Frequently asked questions', 'Find answers to common questions about submitting to Anemone Magazine.'),
    'feedback': ('Feedback', 'Tell the Anemone Magazine editors what’s working well and what we could improve.'),
    'privacy-policy': ('Privacy policy', 'Learn how Anemone Magazine handles contributor information.'),
}
NAVIGATION = {'issues': 'Issues', 'writingworkshops': 'Workshops', 'writing-resources': 'Resources',
              'masthead': 'Masthead', 'reach': 'Reach'}


def substitute(template, values):
    return PLACEHOLDER.sub(lambda match: values[match[1]], template)


def relative_root(slug):
    return '../' * (slug.count('/') + 1) if slug else './'


def asset_version(filename):
    return sha256((OUTPUT / 'assets' / filename).read_bytes()).hexdigest()[:12]


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


def publication_year(issue):
    match = re.search(r'\b([0-9]{4})\s*$', issue['date'])
    return match.group(1) if match else ''


def issue_cards(issues, root, *, filterable=False):
    cards = []
    for issue in issues:
        year = f' data-year="{publication_year(issue)}"' if filterable else ''
        cards.append(
            f'<a class="issue-card" href="{root}{issue["slug"]}/"{year}>'
            f'{cover(issue, root)}<span class="issue-meta">{escape(metadata(issue))}</span>'
            f'<span class="issue-title">{escape(issue["title"])}</span></a>'
        )
    return '\n    '.join(cards)


def google_form_action(form):
    url = form['url']
    if not re.fullmatch(r'https://docs\.google\.com/forms/d/e/[A-Za-z0-9_-]+/viewform', url):
        raise ValueError('Use the full public responder URL for the Google Form')
    return url.removesuffix('/viewform') + '/formResponse'


def newsletter_signup(data):
    form = data['newsletter_google_form']
    email_field = form['email_field']
    if not re.fullmatch(r'entry\.[0-9]+|emailAddress', email_field):
        raise ValueError('Use the Google Forms email field name for newsletter_google_form.email_field')
    action = google_form_action(form)
    # Extend the browser's email check with SMTP length limits and dot placement.
    email_pattern = (
        r'(?=.{1,254}$)(?=[^@]{1,64}@)'
        r'[^.\s@]+(?:\.[^.\s@]+)*@[^.\s@]+(?:\.[^.\s@]+)+'
    )
    return f'''<form class="google-form newsletter-form" data-google-form="newsletter signup" action="{action}" method="post" target="_blank" rel="noopener" aria-labelledby="newsletter">
      <label for="newsletter-email">Email address</label>
      <div class="newsletter-fields">
        <input id="newsletter-email" name="{email_field}" type="email" autocomplete="email" pattern="{email_pattern}" aria-describedby="newsletter-status" data-required-message="Enter your email address." data-invalid-message="Enter a valid email address, such as reader@example.com." required>
        <button class="button" type="submit">Subscribe</button>
      </div>
      <p class="small form-status" id="newsletter-status" role="status"></p>
    </form>'''


def pick_cards(picks, root, heading_level):
    return '\n    '.join(
        f'<a class="pick-card" href="{root}editors-picks/{escape(pick["slug"])}/">'
        f'{artwork(pick["artwork"], root, "pick-image", lazy=True)}'
        f'<div class="pick-copy"><p class="eyebrow">{escape(pick["genre"])}</p>'
        f'<h{heading_level}>{escape(pick["title"])}</h{heading_level}>'
        f'<p class="pick-byline">By {escape(pick["author"])}</p>'
        f'<p>{escape(pick["summary"])}</p></div></a>'
        for pick in picks
    )


def pick_spotlight(pick, root):
    feature = f'{root}editors-picks/{escape(pick["slug"])}/'
    return f'''<section class="wrap section" aria-labelledby="spotlight-title">
  <div class="spotlight-panel">
    <div class="spotlight-copy">
      <p class="eyebrow">Editor’s Pick · {escape(pick['genre'])}</p>
      <h2 id="spotlight-title">{escape(pick['title'])}</h2>
      <p class="pick-byline">By {escape(pick['author'])}</p>
      <blockquote class="spotlight-excerpt" cite="{escape(pick['reader'])}"><p>{escape(pick['excerpt'])}</p></blockquote>
      <div class="actions">
        <a class="button" href="{feature}">Read the feature</a>
        <a class="text-link" href="{feature}#share-pick">Share this pick</a>
      </div>
    </div>
    {artwork(pick['artwork'], root, 'spotlight-image', lazy=True)}
  </div>
</section>'''


def pick_body(pick, issue, root, graphic):
    title = escape(pick['title'])
    reader = escape(pick['reader'])
    reading_link = reader
    reading_label = 'Read the full piece'
    if page_id := pick.get('canva_page_id'):
        issue_reader = issue.get('reader', '').split('#', 1)[0]
        if not issue_reader.startswith('https://www.canva.com/design/') or not re.fullmatch(r'[A-Za-z0-9_-]+', page_id):
            raise ValueError(f'Check the Canva reader URL and page ID for {pick["slug"]}')
        reading_link = escape(f'{issue_reader}#page-{page_id}')
        reading_label = 'Read in the original issue'
    return f'''<article class="wrap pick-article">
  <header class="page-heading page-heading-art">
    <div class="page-intro">
      <a class="pick-back text-link" href="{root}editors-picks/">All Editor’s Picks</a>
      <p class="eyebrow">{escape(pick['genre'])}</p>
      <h1>{title}</h1>
      <p class="pick-byline">By {escape(pick['author'])}</p>
      <p class="lede">{escape(pick['summary'])}</p>
      <div class="actions">
        <a class="button" href="{reading_link}">{reading_label}</a>
        <a class="text-link" href="{root}{escape(issue['slug'])}/">View {escape(issue['title'])}</a>
        <a class="text-link" href="#share-pick">Share</a>
      </div>
      <p class="pick-issue-page small">Page {pick['page']} in the issue.</p>
    </div>
    {artwork(pick['artwork'], root, 'page-art')}
  </header>
  <div class="content-layout">
    <div class="prose">
      <h2>Excerpt</h2>
      <blockquote class="pick-excerpt" cite="{reader}"><p>{escape(pick['excerpt'])}</p></blockquote>
      <h2>Why we picked it</h2>
      <p>{escape(pick['note'])}</p>
    </div>
    <aside class="aside-panel pick-share" aria-labelledby="share-pick">
      <h2 id="share-pick">Share this piece</h2>
      <img src="{root}{escape(graphic)}" width="1200" height="630" loading="lazy" decoding="async" alt="Anemone Magazine share graphic for {title} by {escape(pick['author'])}">
      <div class="actions">
        <button class="button" type="button" data-copy-link="pick-copy-status" hidden>Copy link</button>
        <a class="text-link" href="{root}{escape(graphic)}" download="anemone-{escape(pick['slug'])}-share.png">Download graphic</a>
      </div>
      <p id="pick-copy-status" class="copy-link-status small" role="status"></p>
    </aside>
  </div>
</article>
<script src="{root}assets/share-link.js" defer></script>'''


def resource_cards(resources, root):
    return '\n    '.join(
        f'<a class="pick-card resource-card" href="{root}writing-resources/{escape(resource["slug"])}/">'
        f'{artwork(resource["artwork"], root, "pick-image", lazy=True)}'
        f'<div class="pick-copy"><p class="eyebrow">{escape(resource["topic"])}</p>'
        f'<h2>{escape(resource["title"])}</h2><p>{escape(resource["summary"])}</p></div></a>'
        for resource in resources
    )


def resource_body(resource, resources, root):
    content = (SOURCE / 'resources' / f'{resource["slug"]}.html').read_text(encoding='utf-8')
    related = '\n        '.join(
        f'<li><a href="{root}writing-resources/{escape(guide["slug"])}/">{escape(guide["title"])}</a></li>'
        for guide in resources if guide['slug'] != resource['slug']
    )
    return f'''<article class="wrap resource-article">
  <p class="resource-print-brand">Anemone Magazine · anemonemagazine.com</p>
  <header class="page-heading page-heading-art">
    <div class="page-intro">
      <a class="pick-back text-link" href="{root}writing-resources/">All writing resources</a>
      <p class="eyebrow">{escape(resource['topic'])}</p>
      <h1>{escape(resource['title'])}</h1>
      <p class="lede">{escape(resource['summary'])}</p>
      <div class="actions resource-actions" hidden>
        <button class="button" type="button" data-copy-link="resource-copy-status" hidden>Copy link</button>
        <button class="button resource-print" type="button">Print guide</button>
      </div>
      <p id="resource-copy-status" class="copy-link-status small" role="status"></p>
    </div>
    {artwork(resource['artwork'], root, 'page-art')}
  </header>
  <div class="content-layout">
    <div class="prose resource-content">
{substitute(content.rstrip(), {'root': root})}
    </div>
    <aside class="aside-panel resource-related">
      <h2>More writing resources</h2>
      <ul>
        {related}
      </ul>
    </aside>
  </div>
</article>
<script src="{root}assets/share-link.js" defer></script>
<script src="{root}assets/writing-resources.js?v={asset_version('writing-resources.js')}" defer></script>'''


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


def issue_navigation(series, issues, index):
    neighbors = []
    if index > 0:
        neighbors.append(('Newer issue', issues[index - 1]))
    if index + 1 < len(issues):
        neighbors.append(('Older issue', issues[index + 1]))
    if not neighbors:
        return ''
    links = '\n    '.join(
        f'<a href="../{escape(issue["slug"])}/">'
        f'<span class="small">{label} · {escape(issue["date"])}</span>'
        f'<span class="issue-neighbor-title">{escape(issue["title"])}</span></a>'
        for label, issue in neighbors
    )
    return f'''
<nav class="wrap section" aria-label="More {series} issues">
  <div class="issue-neighbors">
    {links}
  </div>
</nav>'''


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
    return f'''<article class="wrap issue-detail" data-issue-slug="{escape(issue['slug'])}">
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
    analytics_id = data.get('analytics_measurement_id') or ''
    if analytics_id and not re.fullmatch(r'G-[A-Z0-9]+', analytics_id):
        raise ValueError('Set analytics_measurement_id to a Google Analytics 4 Measurement ID beginning with G-')
    analytics_version = asset_version('analytics.js') if analytics_id else ''
    feedback_form = data['feedback_google_form']
    feedback_action = google_form_action(feedback_form)
    feedback_field = feedback_form['response_field']
    if not re.fullmatch(r'entry\.[0-9]+', feedback_field):
        raise ValueError('Use the Google Forms question name for feedback_google_form.response_field')
    google_form_version = asset_version('google-form.js')
    picks = json.loads((SOURCE / 'editors-picks.json').read_text(encoding='utf-8'))
    spotlight = next(iter(picks), None)
    if spotlight_slug := data.get('spotlight_pick'):
        spotlight = {pick['slug']: pick for pick in picks}[spotlight_slug]
    more_picks = [pick for pick in picks if pick != spotlight][:3]
    issues = {issue['slug']: issue for issue in data['issues']}
    newsletter = {
        'signup_form': data['newsletter_google_form']['url'],
        'email_field': data['newsletter_google_form']['email_field'],
        'pick': {key: spotlight[key] for key in ('slug', 'title', 'author', 'summary')} if spotlight else None,
        'issues': [
            {'slug': issue['slug'], 'title': issue['title'], 'date': issue['date'],
             'readable': bool(issue.get('reader') or issue.get('contents'))}
            for issue in issues.values()
        ],
    }
    write_page(OUTPUT / 'newsletter.json', json.dumps(newsletter, ensure_ascii=False, indent=2) + '\n')
    resources = json.loads((SOURCE / 'writing-resources.json').read_text(encoding='utf-8'))
    schedule = json.loads((SOURCE / 'submission-calendar.json').read_text(encoding='utf-8'))
    calls = calendar_calls(schedule['calls'], data['instagram'])
    has_calendar = write_calendar(schedule, OUTPUT, DOMAIN)
    layout = (SOURCE / 'layout.html').read_text(encoding='utf-8')
    issue_series = {
        'general': [issue for issue in issues.values() if 'theme' not in issue],
        'themed': [issue for issue in issues.values() if 'theme' in issue],
    }
    years = sorted({publication_year(issue) for issue in issues.values()} - {''}, reverse=True)
    page_artwork = dict(data['page_artwork'])
    page_artwork.update({f'editors-picks/{pick["slug"]}': pick['artwork'] for pick in picks})
    page_artwork.update({f'writing-resources/{resource["slug"]}': resource['artwork'] for resource in resources})
    external_links = {key: escape(value) for key, value in data.items() if isinstance(value, str)}
    stylesheet_version = asset_version('site.css')
    urls = []

    def render(slug, title, desc, body, *, redirect=None, page_missing=False, share_image=None):
        root = relative_root(slug)
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
        if share_image:
            head += '\n  <meta name="twitter:card" content="summary_large_image">'
        navigation = ''
        for target, label in NAVIGATION.items():
            current = ' aria-current="page"' if target == slug else ''
            navigation += f'<li><a href="{root}{target}/"{current}>{label}</a></li>'
        issue = issues.get(slug, {})
        image_file = page_artwork.get(slug, issue.get('artwork', 'anemones-daylight.jpg'))
        image = f'assets/images/{image_file}'
        if cover_file := issue.get('cover'):
            image = f'assets/covers/{cover_file}'
        analytics_script = ''
        if analytics_id and redirect is None and not page_missing:
            analytics_script = (f'  <script src="{root}assets/analytics.js?v={analytics_version}" '
                                f'data-measurement-id="{analytics_id}" defer></script>\n')
        context = {
            **external_links,
            'root': root,
            'title': escape(f'{title} | Anemone Magazine' if slug else title),
            'description': escape(desc),
            'head': head,
            'social_image': DOMAIN + (share_image or image),
            'stylesheet_version': stylesheet_version,
            'navigation': navigation,
            'submission_current': ' aria-current="page"' if slug == 'submissions' else '',
            'analytics_script': analytics_script,
            'body': body,
        }
        html = substitute(substitute(layout, context), context)
        path = OUTPUT / ('404.html' if page_missing else (f'{slug}/index.html' if slug else 'index.html'))
        write_page(path, html)

    for slug, (title, desc) in PAGES.items():
        root = relative_root(slug)
        template = (SOURCE / 'pages' / f'{slug or "home"}.html').read_text(encoding='utf-8')
        download = ''
        if slug == 'upcoming-issues' and has_calendar:
            download = f'\n      <a class="button" href="{root}{CALENDAR_FILE}" download>Download deadlines (.ics)</a>'
        selections = ''
        if not slug:
            selections = pick_cards(more_picks, root, 3)
        elif slug == 'editors-picks':
            selections = pick_cards(picks, root, 2)
        keys = {
            **external_links,
            'root': root,
            'featured_issues': issue_cards((issues[key] for key in data['featured']), root) if not slug else '',
            'general_issues': issue_cards(issue_series['general'], root, filterable=True) if slug == 'issues' else '',
            'themed_issues': issue_cards(issue_series['themed'], root, filterable=True) if slug == 'issues' else '',
            'archive_years': '\n        '.join(f'<option>{escape(year)}</option>' for year in years),
            'team': team_cards(data['team'], root) if slug == 'masthead' else '',
            'reach_audiences': reach_audiences(root) if slug == 'reach' else '',
            'page_artwork': artwork(page_artwork[slug], root, 'page-art') if slug in page_artwork else '',
            'mission_artwork': artwork('anemone-engraving.jpg', root, 'mission-art', lazy=True) if not slug else '',
            'deadline_preview': deadline_preview(schedule['calls'], root) if not slug else '',
            'newsletter_signup_form': newsletter_signup(data) if not slug else '',
            'google_form_version': google_form_version,
            'feedback_action': feedback_action,
            'feedback_field': feedback_field,
            'calendar_calls': calls,
            'calendar_download': download,
            'pick_spotlight': pick_spotlight(spotlight, root) if not slug and spotlight else '',
            'more_picks_visibility': '' if more_picks else ' hidden',
            'editors_picks': selections,
            'writing_resources': resource_cards(resources, root) if slug == 'writing-resources' else '',
        }
        render(slug, title, desc, substitute(template, keys))

    for series, editions in issue_series.items():
        for index, issue in enumerate(editions):
            body = issue_body(issue, page_artwork['issues']) + issue_navigation(series, editions, index)
            render(issue['slug'], issue['title'], f'{metadata(issue)} from Anemone Magazine.', body)

    for pick in picks:
        slug = f'editors-picks/{pick["slug"]}'
        graphic = f'assets/share/{pick["slug"]}.png'
        if not (OUTPUT / graphic).is_file():
            raise FileNotFoundError(OUTPUT / graphic)
        render(slug, f'{pick["title"]} by {pick["author"]}', pick['summary'],
               pick_body(pick, issues[pick['issue']], relative_root(slug), graphic), share_image=graphic)

    for resource in resources:
        slug = f'writing-resources/{resource["slug"]}'
        render(slug, resource['title'], resource['summary'], resource_body(resource, resources, relative_root(slug)))

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
