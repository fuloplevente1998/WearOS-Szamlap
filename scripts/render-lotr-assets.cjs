// Rasterize independent LOTR artwork; does not touch the HALO resources.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
(async () => {
  const root = path.resolve(__dirname, '..');
  const source = path.join(root, 'design', 'lotr', 'svg');
  const target = path.join(root, 'lotrwatchface', 'src', 'main', 'res', 'drawable-nodpi');
  fs.mkdirSync(target, { recursive: true });
  const opts = { headless: true };
  if (process.env.CHROMIUM_PATH) opts.executablePath = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(opts);
  try {
    const page = await browser.newPage({ viewport: { width: 900, height: 900 }, deviceScaleFactor: 1 });
    for (const [input, output] of [['map.svg','lotr_middle_earth_map.png'], ['bezel.svg','lotr_one_ring_bezel.png']]) {
      const svg = fs.readFileSync(path.join(source,input), 'utf8');
      const base64 = await page.evaluate(async xml => {
        const image = new Image();
        image.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(xml)));
        await image.decode();
        const canvas = document.createElement('canvas');
        canvas.width = 900; canvas.height = 900;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(image, 0, 0, 900, 900);
        return canvas.toDataURL('image/png').split(',')[1];
      }, svg);
      fs.writeFileSync(path.join(target,output), Buffer.from(base64,'base64'));
      process.stdout.write('Generated '+output+'\n');
    }
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
