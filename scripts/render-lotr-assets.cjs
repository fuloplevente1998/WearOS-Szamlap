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
      if (input === 'bezel.svg') {
        await page.evaluate(xml => {
          const root = document.importNode(new DOMParser().parseFromString(xml, 'image/svg+xml').documentElement, true);
          document.body.appendChild(root);
          try {
            const markers = [...root.querySelectorAll('#hour-numerals > g')];
            if (markers.length !== 12) throw new Error('Expected 12 bezel hour numerals');
            const base = root.getCTM().inverse();
            for (let i = 0; i < markers.length; i++) {
              const marker = markers[i], text = marker.querySelector('text'), plate = marker.querySelector('rect');
              if (text.textContent !== String(i + 1) || marker.getAttribute('data-hour') !== String(i + 1))
                throw new Error('Wrong hour sequence');
              const t = text.getBBox(), p = plate.getBBox();
              if (t.x < p.x + 1 || t.y < p.y + 1 || t.x + t.width > p.x + p.width - 1 || t.y + t.height > p.y + p.height - 1)
                throw new Error('Hour numeral overflows plaque: ' + text.textContent);
              const m = base.multiply(marker.getCTM());
              for (const [x,y] of [[p.x,p.y],[p.x+p.width,p.y],[p.x,p.y+p.height],[p.x+p.width,p.y+p.height]]) {
                const point = new DOMPoint(x,y).matrixTransform(m), radius = Math.hypot(point.x-225,point.y-225);
                if (radius < 190 || radius > 224) throw new Error('Hour plaque outside bezel');
              }
            }
          } finally { root.remove(); }
        }, svg);
        process.stdout.write('PASS: 12 hour numerals fit their plaques and bezel band\n');
      }
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
