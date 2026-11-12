const { chromium } = require('playwright');
// Browser checks for every action and state. Needs Playwright.
//   python3 -m http.server 8137 --directory dist   (in another terminal)
//   node tests/behaviour.js
const D = process.env.BASE_URL || 'http://127.0.0.1:8137';
let pass = 0, fail = 0;
const ok = (name, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + name + (extra && !cond ? ' -> ' + extra : '')); };
(async () => {
  const b = await chromium.launch(); const c = await b.newContext({ viewport: { width: 390, height: 844 } }); const p = await c.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  const vis = sel => p.$$eval(sel, els => els.filter(e => e.offsetParent !== null).map(e => e.innerText.trim()));

  // Game page: Azul
  await p.goto(D + '/games/azul');
  ok('count control visible with script', await p.isVisible('fieldset.count'));
  ok('All is selected first', await p.isChecked('input[name=players][value=""]'));
  ok('all three factory variants listed initially', (await vis('#setup .variant')).length === 3);
  ok('help text explains initial state', (await p.innerText('.count-help')).startsWith('Showing every player count'));
  await p.check('input[name=players][value="3"]', { force: true });
  let v = await vis('#setup .variant');
  ok('only the 3-player variant shows', v.length === 1 && /7 Factory displays/.test(v[0]), JSON.stringify(v));
  let k = await vis('#numbers .per');
  ok('key number shows 7 only', k.length === 1 && /7/.test(k[0]) && !/players/.test(k[0]), JSON.stringify(k));
  ok('help text says 3 players', (await p.innerText('.count-help')) === 'Showing 3 players.');
  ok('URL carries the count', p.url().includes('players=3'));
  // ticks
  await p.check('#step-0'); await p.check('#step-2');
  ok('Clear ticks appears', await p.isVisible('.clear-ticks'));
  await p.reload();
  ok('count restored after reload', await p.isChecked('input[name=players][value="3"]'));
  ok('ticks restored after reload', await p.isChecked('#step-0') && await p.isChecked('#step-2') && !(await p.isChecked('#step-1')));
  await p.click('.clear-ticks');
  ok('ticks cleared and button hidden', !(await p.isChecked('#step-0')) && !(await p.isVisible('.clear-ticks')));
  ok('focus moved to Setup heading', await p.evaluate(() => document.activeElement && document.activeElement.textContent === 'Setup'));

  // Remembered count carries to another game (no URL param)
  await p.goto(D + '/games/cascadia');
  ok('remembered 3 applied on Cascadia', await p.isChecked('input[name=players][value="3"]'));
  let sc = await vis('#scoring li');
  ok('2-player-only scoring line hidden at 3', !sc.some(t => /2 points; if tied/.test(t)) && sc.some(t => /3 points, and 1 point/.test(t)), JSON.stringify(sc));
  ok('only-label hidden once a count is chosen', (await vis('#scoring .only-label')).length === 0);
  ok('solo option is disabled with a reason', await p.isDisabled('input[name=players][value="1"]') && /Solo play isn't covered yet/.test(await p.innerText('.count-note')));

  // Remembered count outside a game's range
  await p.goto(D + '/games/uno'); await p.check('input[name=players][value="8"]', { force: true });
  await p.goto(D + '/games/azul');
  ok('out-of-range count falls back to All', await p.isChecked('input[name=players][value=""]'));
  ok('fallback is explained', /You last chose 8 players\. This game takes 2–4 players, so every count is shown\./.test(await p.innerText('.count-help')), await p.innerText('.count-help'));
  // back to All by choice
  await p.check('input[name=players][value="2"]', { force: true }); await p.check('input[name=players][value=""]', { force: true });
  ok('choosing All shows every variant again', (await vis('#setup .variant')).length === 3 && !p.url().includes('players='));
  // keyboard: arrow keys move the radio selection
  await p.focus('input[name=players][value=""]'); await p.keyboard.press('ArrowRight');
  ok('arrow key selects next count', await p.isChecked('input[name=players][value="2"]'));
  // 2-player-only UNO rule
  await p.goto(D + '/games/uno?players=2');
  ok('URL count wins and UNO 2-player rules show', (await vis('#missed li')).some(t => /Reverse acts like a Skip/.test(t)));
  await p.goto(D + '/games/uno?players=4');
  ok('2-player rules hidden at 4', !(await vis('#missed li')).some(t => /Reverse acts like a Skip/.test(t)));
  // partial notice
  await p.goto(D + '/games/ark-nova');
  ok('partial notice shown on Ark Nova', /Partial entry/.test(await p.innerText('.notice')));
  ok('rulebook link present', (await p.getAttribute('#about a', 'href')).startsWith('https://www.feuerland-spiele.de/'));

  // Home
  await p.goto(D + '');
  ok('finder visible', await p.isVisible('#find'));
  await p.fill('#find', 'kutna');
  ok('search ignores accents', JSON.stringify(await vis('.game-row a')) === JSON.stringify(['Kutná Hora: The City of Silver']));
  await p.fill('#find', 'zzz');
  ok('no-match state names the term', await p.isVisible('.no-match') && /No game matches “zzz”\. \d+ games/.test(await p.innerText('.no-match')));
  await p.click('.clear-search');
  ok('clear search restores list and focuses field', (await vis('.game-row a')).length >= 9 && await p.evaluate(() => document.activeElement.id === 'find'));
  await p.click('.game-row a >> text=Wingspan');
  ok('row link opens the game page', /games\/wingspan\//.test(p.url()) && (await p.innerText('h1')) === 'Wingspan');
  await p.click('.site-name');
  ok('site name returns home', new URL(p.url()).pathname === '/', p.url());
  ok('no script errors', errs.length === 0, errs.join('; '));

  // No-script state
  const c2 = await b.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } }); const q = await c2.newPage();
  await q.goto(D + '/games/azul');
  ok('without script: control hidden, all variants readable', !(await q.isVisible('fieldset.count')) && (await q.$$eval('#setup .variant', e => e.length)) === 3);
  await b.close(); console.log(`\n${pass} passed, ${fail} failed`); process.exit(fail ? 1 : 0);
})();
