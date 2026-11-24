// Install in the Apps Script project bound to Anemone's newsletter signup form.
const SITE_URLS = ['https://www.anemonemagazine.com/', 'https://audrikaoc.github.io/anemonemagazine/'];
const REPOSITORY_FEED = 'https://raw.githubusercontent.com/audrikaoc/anemonemagazine/main/docs/newsletter.json';

function readNewsletter_() {
  for (const base of [...SITE_URLS, null]) {
    try {
      const response = UrlFetchApp.fetch(base ? base + 'newsletter.json' : REPOSITORY_FEED, {muteHttpExceptions: true});
      if (response.getResponseCode() !== 200) continue;
      const data = JSON.parse(response.getContentText());
      if (!Array.isArray(data.issues) || !data.signup_form) continue;
      return {base, data};
    } catch (error) {
      console.warn('Newsletter feed unavailable at ' + (base || REPOSITORY_FEED));
    }
  }
  throw new Error('Could not read the Anemone newsletter feed. The next run will retry.');
}

function setupNewsletter() {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const store = PropertiesService.getScriptProperties();
    const form = FormApp.getActiveForm();
    const {data} = readNewsletter_();
    const questions = form ? form.getItems(FormApp.ItemType.TEXT) : [];
    if (questions.length !== 1) throw new Error('Open Apps Script from the signup form with its one email question.');
    const emailQuestion = questions[0].asTextItem();
    const prefill = form.createResponse().withItemResponse(emailQuestion.createResponse('sample@example.com')).toPrefilledUrl();
    if (form.getPublishedUrl().split('?')[0] !== data.signup_form && !prefill.includes(data.email_field + '=')) {
      throw new Error('This is a different form. Open Apps Script from the Anemone newsletter signup form.');
    }
    if (!store.getProperty('config')) {
      store.setProperty('config', JSON.stringify({
        signupId: form.getId(), emailItem: emailQuestion.getId(), secret: Utilities.getUuid(),
        started: Date.now(), archive: data.issues.map(issue => issue.slug)
      }));
    }
    if (!ScriptApp.getProjectTriggers().some(trigger => trigger.getHandlerFunction() === 'runNewsletter')) {
      ScriptApp.newTrigger('runNewsletter').timeBased().everyMinutes(15).create();
    }
  } finally {
    lock.releaseLock();
  }
}

// Replay the boundary minute after each run. Repeated signups and opt-outs are idempotent.
function readResponses_(store, formId, itemId, visit) {
  const key = 'checked.' + formId;
  const previous = Number(store.getProperty(key));
  const started = Date.now();
  const form = FormApp.openById(formId);
  const item = form.getItemById(itemId);
  if (!item) throw new Error('A newsletter form question has been replaced. Check its configuration.');
  const responses = previous ? form.getResponses(new Date(previous - 60000)) : form.getResponses();
  for (const response of responses) {
    const answer = response.getResponseForItem(item);
    if (answer) visit(String(answer.getResponse()).trim(), response.getTimestamp().getTime());
  }
  store.setProperty(key, String(started));
}

function syncReaders_(store, config) {
  readResponses_(store, config.signupId, config.emailItem, (address, joined) => {
    const email = address.toLowerCase();
    // MailApp also accepts comma-separated recipients. Each signup must be one mailbox.
    if (!/^[^\s@,;<>:"]+@[^\s@,;<>:"]+\.[^\s@,;<>:"]+$/.test(email)) return;
    const signature = Utilities.computeHmacSha256Signature(email, config.secret);
    const token = Utilities.base64EncodeWebSafe(signature).replace(/=+$/, '');
    const key = 'reader.' + token;
    if (!store.getProperty(key)) {
      store.setProperty(key, JSON.stringify({email, joined, welcomed: joined < config.started, lastIssue: 0}));
    }
  });
  // Honor links from emails sent before the switch to unsubscribe by reply.
  if (!config.optOutId) return;
  readResponses_(store, config.optOutId, config.codeItem, token => {
    if (!/^[A-Za-z0-9_-]{43}$/.test(token)) return;
    const key = 'reader.' + token;
    if (store.getProperty(key)) store.setProperty(key, JSON.stringify({stopped: true}));
  });
}

function publishedIssues_(store, config, feed, records) {
  const releases = Object.keys(records).filter(key => key.startsWith('issue.'))
    .map(key => ({...JSON.parse(records[key]), slug: key.slice('issue.'.length)}))
    .sort((a, b) => a.number - b.number);
  for (const issue of feed.data.issues.slice().reverse()) {
    const key = 'issue.' + issue.slug;
    if (!issue.readable || records[key] || config.archive.includes(issue.slug)) continue;
    const release = {number: releases.length + 1, at: Date.now(), title: issue.title, date: issue.date, slug: issue.slug};
    store.setProperty(key, JSON.stringify(release));
    records[key] = JSON.stringify(release);
    releases.push(release);
  }
  return releases;
}

function nextLetter_(reader, feed, releases) {
  if (!reader.welcomed) {
    const pick = feed.data.pick;
    if (!pick) return null;
    const url = feed.base + 'editors-picks/' + encodeURIComponent(pick.slug) + '/';
    return {id: 'welcome', subject: 'Welcome to Anemone Magazine',
      text: 'Thank you for joining Anemone, a literary magazine for young writers and artists. ' +
        'We picked a piece for your first visit: “' + pick.title + '” by ' + pick.author + '.\n\n' +
        pick.summary + '\n\nRead “' + pick.title + '” on Anemone: ' + url +
        '\n\nWe’ll write again when a new issue comes out.'};
  }
  const issue = releases.find(item => item.number > reader.lastIssue && item.at >= reader.joined);
  if (!issue) return null;
  const url = feed.base + encodeURIComponent(issue.slug) + '/';
  return {id: 'issue-' + issue.number, number: issue.number, subject: issue.title + ' is out · Anemone Magazine',
    text: 'Our ' + issue.date + ' edition, ' + issue.title + ', is ready to read. ' +
      'Spend a little time with the young writers and artists in its pages.\n\nOpen the issue: ' + url};
}

function runNewsletter() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(1000)) return;
  try {
    const deadline = Date.now() + 240000;
    const store = PropertiesService.getScriptProperties();
    const config = JSON.parse(store.getProperty('config'));
    if (!config) throw new Error('Run setupNewsletter first.');
    syncReaders_(store, config);
    const feed = readNewsletter_();
    if (!feed.base) {
      console.info('Newsletter delivery is waiting for the public Anemone site.');
      return;
    }
    const records = store.getProperties();
    const releases = publishedIssues_(store, config, feed, records);
    let remaining = MailApp.getRemainingDailyQuota();
    for (const [key, value] of Object.entries(records)) {
      if (remaining <= 0 || Date.now() >= deadline) break;
      if (!key.startsWith('reader.')) continue;
      const reader = JSON.parse(value);
      if (reader.stopped || reader.pending) continue;
      const letter = nextLetter_(reader, feed, releases);
      if (!letter) continue;
      const body = letter.text + '\n\nThe editors at Anemone Magazine' +
        '\n\nReply with UNSUBSCRIBE to stop receiving these emails.';
      // MailApp has no idempotency key. Persist the claim before handing it a message.
      reader.pending = letter.id;
      store.setProperty(key, JSON.stringify(reader));
      try {
        MailApp.sendEmail({to: reader.email, subject: letter.subject, body, name: 'Anemone Magazine'});
      } catch (error) {
        if (/quota|limit exceeded|too many times/i.test(String(error))) {
          delete reader.pending;
          store.setProperty(key, JSON.stringify(reader));
          break;
        }
        // Leave uncertain deliveries on hold for the editor. Other subscribers can still receive mail.
        console.error('Newsletter delivery needs review for ' + letter.id + ' (reader …' + key.slice(-6) + ').');
        continue;
      }
      remaining--;
      if (letter.id === 'welcome') reader.welcomed = true;
      else reader.lastIssue = letter.number;
      delete reader.pending;
      store.setProperty(key, JSON.stringify(reader));
    }
  } finally {
    lock.releaseLock();
  }
}
