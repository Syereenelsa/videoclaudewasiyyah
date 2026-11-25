// Usage:
//   node render.js stills out_dir t1 t2 ...       -> PNG per timestamp
//   node render.js video out.mp4 [fps] [workers]  -> MP4 (1080x1920)
//   node render.js cues out.json                  -> SFX cue sheet + duration
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// PAGE=short60.html node render.js ...   renders another page in this folder
const URL = 'file://' + path.join(__dirname, process.env.PAGE || 'index.html') + '?render';

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto(URL);
  await page.evaluate(() => document.fonts.ready);
  return page;
}

async function stills(outDir, times) {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await openPage(browser);
  for (const t of times) {
    await page.evaluate(t => window.seek(t), +t);
    await page.screenshot({ path: path.join(outDir, `t${String(t).padStart(6, '0')}.png`) });
  }
  await browser.close();
}

async function segment(browser, from, to, fps, file) {
  const page = await openPage(browser);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '18', '-r', String(fps), file]);
  for (let f = from; f < to; f++) {
    await page.evaluate(t => window.seek(t), f / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await page.close();
}

async function video(out, fps = 30, workers = 4) {
  const browser = await chromium.launch();
  const probe = await openPage(browser);
  const dur = await probe.evaluate(() => window.DURATION);
  await probe.close();
  const total = Math.ceil(dur * fps);
  const per = Math.ceil(total / workers);
  const tmp = path.join(path.dirname(path.resolve(out)), '.seg');
  fs.mkdirSync(tmp, { recursive: true });
  const files = [];
  await Promise.all([...Array(workers)].map((_, i) => {
    const f = path.join(tmp, `seg${i}.mp4`); files.push(f);
    return segment(browser, i * per, Math.min(total, (i + 1) * per), fps, f);
  }));
  await browser.close();
  const list = path.join(tmp, 'list.txt');
  fs.writeFileSync(list, files.map(f => `file '${f}'`).join('\n'));
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', '-movflags', '+faststart', out]);
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log(`done: ${out} (${dur.toFixed(1)}s, ${total} frames)`);
}

async function cues(out) {
  const browser = await chromium.launch();
  const page = await openPage(browser);
  const data = await page.evaluate(() => ({ duration: window.DURATION, cues: window.SFX, vo: window.VO, vo_src: window.VO_SRC, vo_tempo: window.VO_TEMPO || 1 }));
  fs.writeFileSync(out, JSON.stringify(data, null, 1));
  await browser.close();
  console.log(`${data.cues.length} cues, ${data.duration}s -> ${out}`);
}

const [mode, out, ...rest] = process.argv.slice(2);
(mode === 'stills' ? stills(out, rest) : mode === 'cues' ? cues(out) : video(out, +(rest[0] || 30), +(rest[1] || 4)))
  .catch(e => { console.error(e); process.exit(1); });
