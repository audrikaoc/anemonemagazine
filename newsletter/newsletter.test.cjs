const assert = require('node:assert/strict');
const {createHmac} = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const {test} = require('node:test');
const vm = require('node:vm');

function fixture() {
  const feed = JSON.parse(fs.readFileSync(path.join(__dirname, '../docs/newsletter.json'), 'utf8'));
  const state = {now: 100000, live: false, quota: 100, mail: [], triggers: [], errors: [], records: {}};
  function form(id, publicUrl, entry) {
    const item = {getId: () => 123, asTextItem: () => item, createResponse: value => value,
      setTitle: () => item, setRequired: () => item};
    const responses = [];
    const api = {
      getItems: () => [item], getItemById: () => item, addTextItem: () => item,
      getId: () => id, getPublishedUrl: () => publicUrl, setDescription: () => api,
      setCollectEmail: () => api, setPublishingSummary: () => api, setLimitOneResponsePerUser: () => api,
      setConfirmationMessage: () => api, createResponse: () => ({withItemResponse: value => ({
        toPrefilledUrl: () => publicUrl + '?' + entry + '=' + encodeURIComponent(value)
      })}),
      getResponses: since => responses.filter(r => !since || r.getTimestamp() >= since),
      respond: (value, when = state.now) => responses.push({
        getResponseForItem: field => field === item ? {getResponse: () => value} : null,
        getTimestamp: () => new Date(when)
      })
    };
    return api;
  }
  const signup = form('signup', feed.signup_form, feed.email_field);
  const optOut = form('optOut', 'https://forms.example/unsubscribe', 'entry.456');
  const store = {getProperty: key => state.records[key] ?? null,
    setProperty: (key, value) => {state.records[key] = value;}, getProperties: () => ({...state.records})};
  const context = vm.createContext({
    Date: class extends Date { static now() { return state.now; } },
    console: {warn() {}, error: message => state.errors.push(message)},
    PropertiesService: {getScriptProperties: () => store},
    FormApp: {ItemType: {TEXT: 'TEXT'}, getActiveForm: () => signup, create: () => optOut,
      openById: id => ({signup, optOut})[id]},
    Utilities: {getUuid: () => 'test-secret', base64EncodeWebSafe: bytes => bytes.toString('base64url'),
      computeHmacSha256Signature: (email, secret) => createHmac('sha256', secret).update(email).digest()},
    LockService: {getScriptLock: () => ({waitLock() {}, tryLock: () => !state.locked, releaseLock() {}})},
    ScriptApp: {getProjectTriggers: () => state.triggers, newTrigger: handler => ({timeBased() {return this;},
      everyMinutes() {return this;}, create() {state.triggers.push({getHandlerFunction: () => handler});}})},
    UrlFetchApp: {fetch: url => ({
      getResponseCode: () => state.live || url.includes('raw.githubusercontent') ? 200 : 404,
      getContentText: () => JSON.stringify(feed)
    })},
    MailApp: {getRemainingDailyQuota: () => state.quota, sendEmail: message => {
      if (state.failure) throw new Error(state.failure);
      state.mail.push(message);
    }}
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname, 'Code.gs'), 'utf8'), context);
  return {state, feed, signup, optOut, setup: context.setupNewsletter, run: context.runNewsletter};
}

test('one welcome, published editions only, retries, and unsubscribe', () => {
  const {state, feed, signup, optOut, setup, run} = fixture();
  signup.respond('archive-reader@example.org', state.now - 1000);
  setup();
  setup();
  assert.equal(state.triggers.length, 1);
  state.now += 1000;
  signup.respond(' Reader@example.org ');
  signup.respond('reader@example.org');
  signup.respond('wrong@example.org,other@example.org');
  run();
  run();
  assert.equal(state.mail.length, 1);
  const welcome = state.mail[0];
  assert.equal(welcome.to, 'reader@example.org');
  assert.ok(welcome.body.includes(feed.pick.title) && welcome.body.includes(feed.pick.author));
  assert.ok(welcome.body.includes(feed.pick.reader));
  const token = new URL(welcome.body.split('Unsubscribe: ')[1]).searchParams.get('entry.456');
  assert.match(token, /^[\w-]{43}$/);
  feed.issues.unshift({slug: 'new-edition', title: 'New Edition', date: 'Winter 2027', readable: false});
  state.live = true;
  run();
  assert.equal(state.mail.length, 1);
  state.live = false;
  feed.issues[0].readable = true;
  run();
  assert.equal(state.mail.length, 1);
  state.live = true;
  state.quota = 0;
  run();
  assert.equal(state.mail.length, 1);
  state.quota = 1;
  run();
  assert.equal(state.mail.length, 2);
  run();
  assert.deepEqual(state.mail.slice(1).map(m => m.to).sort(), ['archive-reader@example.org', 'reader@example.org']);
  assert.ok(state.mail[1].body.includes('https://www.anemonemagazine.com/new-edition/'));
  feed.issues.reverse();
  feed.issues.find(i => i.slug === 'new-edition').title = 'Corrected title';
  run();
  assert.equal(state.mail.length, 3);
  state.now += 1000;
  optOut.respond(token);
  signup.respond('reader@example.org');
  signup.respond('late@example.org');
  state.quota = 5;
  run();
  const liveWelcome = state.mail.at(-1);
  assert.equal(liveWelcome.to, 'late@example.org');
  assert.ok(liveWelcome.body.includes('/editors-picks/' + feed.pick.slug + '/'));
  run();
  assert.equal(state.mail.length, 4);
  feed.issues.push({slug: 'themed-new', title: 'Themed Edition', date: 'Spring 2027', readable: true});
  run();
  assert.deepEqual(state.mail.slice(4).map(m => m.to).sort(), ['archive-reader@example.org', 'late@example.org']);
});

test('quota rejections resume, uncertain handoffs stay held, and concurrent checks skip sending', () => {
  const {state, signup, setup, run} = fixture();
  setup();
  signup.respond('reader@example.org', ++state.now);
  state.locked = true;
  run();
  state.locked = false;
  state.failure = 'Service invoked too many times for one day: email';
  run();
  assert.equal(state.mail.length, 0);
  state.failure = null;
  run();
  assert.equal(state.mail.length, 1);
  signup.respond('other@example.org', ++state.now);
  state.failure = 'Connection interrupted';
  run();
  assert.equal(state.errors.length, 1);
  state.failure = null;
  signup.respond('third@example.org', ++state.now);
  run();
  run();
  assert.deepEqual(state.mail.map(m => m.to), ['reader@example.org', 'third@example.org']);
});
