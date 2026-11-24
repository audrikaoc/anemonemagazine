"""Render the submission schedule and export dated calls as all-day events."""

from datetime import date, timedelta
from html import escape

CALENDAR_FILE = 'assets/downloads/anemone-submission-deadlines.ics'


def time_label(iso_date):
    day = date.fromisoformat(iso_date)
    return f'<time datetime="{iso_date}">{day:%B} {day.day}, {day.year}</time>'


def deadline_preview(calls, root):
    dated = sorted((call for call in calls if call.get('closes')), key=lambda call: call['closes'])
    return ''.join(
        f'\n    <p data-deadline="{escape(call["closes"])}" hidden>'
        f'<a href="{root}upcoming-issues/#{escape(call["id"])}">{escape(call["title"])}</a> closes '
        f'{time_label(call["closes"])}.</p>'
        for call in dated
    )


def calendar_calls(calls, instagram):
    sections = []
    for call in calls:
        opens = call.get('opens', '')
        closes = call.get('closes', '')
        if opens and closes and date.fromisoformat(opens) > date.fromisoformat(closes):
            raise ValueError(f'{call["id"]} closes before it opens')
        dates = []
        for field, label in [('opens', 'Opens'), ('closes', 'Deadline'), ('release', 'Tentative release')]:
            if value := call.get(field):
                dates.append(f'<div><dt>{label}</dt><dd>{time_label(value)}</dd></div>')
        schedule = f'\n      <dl class="call-dates">{"".join(dates)}</dl>' if dates else ''
        if form := call.get('form'):
            action = (
                f'<a class="button" href="{escape(form)}" target="_blank" rel="noopener" '
                f'data-submission-form="{escape(call["id"])}">'
                'Open the submission form</a>'
            )
            if note := call.get('form_note'):
                action += f'<p class="small">{escape(note)}</p>'
        else:
            action = f'<p>Follow <a href="{escape(instagram)}">Anemone on Instagram</a> for the submission announcement.</p>'
        status = '<p class="call-status" data-call-status hidden></p>'
        if not opens and not closes:
            status = '<p class="call-status">Dates to be announced</p>'
        sections.append(f'''<section class="listing submission-call" data-submission-call data-opens="{escape(opens)}" data-closes="{escape(closes)}" aria-labelledby="{escape(call['id'])}">
    <div>
      <p class="eyebrow">{escape(call['label'])}</p>
      <h2 id="{escape(call['id'])}">{escape(call['title'])}</h2>
      {status}
    </div>
    <div>
      <p>{escape(call['description'])}</p>{schedule}
      {action}
    </div>
  </section>''')
    return '\n  '.join(sections) or '<p>There are no announced calls right now.</p>'


def calendar_text(value):
    return value.replace('\\', '\\\\').replace('\n', '\\n').replace(',', '\\,').replace(';', '\\;')


def fold_line(line):
    parts = []
    chunk = ''
    size = 0
    for char in line:
        length = len(char.encode('utf-8'))
        if size + length > 75:
            parts.append(chunk)
            chunk = ' '
            size = 1
        chunk += char
        size += length
    return '\r\n'.join([*parts, chunk])


def write_calendar(schedule, output, site_url):
    destination = output / CALENDAR_FILE
    stamp = date.fromisoformat(schedule['updated']).strftime('%Y%m%d') + 'T000000Z'
    events = []
    for call in schedule['calls']:
        if not call.get('closes'):
            continue
        deadline = date.fromisoformat(call['closes'])
        next_day = deadline + timedelta(days=1)
        events.extend([
            'BEGIN:VEVENT', f'UID:{call["id"]}-deadline@anemonemagazine.com', f'DTSTAMP:{stamp}',
            f'DTSTART;VALUE=DATE:{deadline:%Y%m%d}', f'DTEND;VALUE=DATE:{next_day:%Y%m%d}',
            f'SUMMARY:{calendar_text("Anemone " + call["title"] + " submission deadline")}',
            f'URL:{site_url}upcoming-issues/#{call["id"]}', 'TRANSP:TRANSPARENT', 'END:VEVENT',
        ])
    if not events:
        destination.unlink(missing_ok=True)
        return False
    content = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Anemone Magazine//Submission Deadlines//EN',
               'CALSCALE:GREGORIAN', *events, 'END:VCALENDAR']
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(('\r\n'.join(fold_line(line) for line in content) + '\r\n').encode('utf-8'))
    return True
