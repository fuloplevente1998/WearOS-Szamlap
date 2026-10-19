const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

(async () => {
  const root = path.resolve(__dirname, '..');
  const svgDir = path.join(root, 'design/svg');
  const drawableDir = path.join(root, 'watchface/src/main/res/drawable-nodpi');

  // SVG Definitions for LOTR watch face
  const svgs = {
    // 1. One Ring Tengwar Glow Ring
    lotr_ring_tengwar: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 450" width="450" height="450">
      <defs>
        <radialGradient id="ringGlow" cx="50%" cy="50%" r="50%">
          <stop offset="70%" stop-color="#000" stop-opacity="0"/>
          <stop offset="85%" stop-color="#ff8c00" stop-opacity="0.3"/>
          <stop offset="92%" stop-color="#ffaa00" stop-opacity="0.6"/>
          <stop offset="98%" stop-color="#ff8c00" stop-opacity="0.1"/>
          <stop offset="100%" stop-color="#000" stop-opacity="0"/>
        </radialGradient>
        <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="2.5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <path id="textPathOuter" d="M 225,225 m -185,0 a 185,185 0 1,1 370,0 a 185,185 0 1,1 -370,0" />
        <path id="textPathInner" d="M 225,225 m -160,0 a 160,160 0 1,0 320,0 a 160,160 0 1,0 -320,0" />
      </defs>

      <circle cx="225" cy="225" r="225" fill="url(#ringGlow)" />
      <circle cx="225" cy="225" r="185" stroke="#ffaa00" stroke-width="1.5" fill="none" opacity="0.4" />
      <circle cx="225" cy="225" r="162" stroke="#ff8c00" stroke-width="1.5" fill="none" opacity="0.4" />

      <g filter="url(#glowFilter)">
        <text fill="#ffd700" font-family="serif" font-weight="bold" font-size="16" letter-spacing="3">
          <textPath href="#textPathOuter" startOffset="0%">
            Ash nazg durbatulûk, ash nazg gimbatul, ash nazg thrakatulûk agh burzum-ishi krimpatul.
          </textPath>
        </text>
        <text fill="#ffe4b5" font-family="serif" font-weight="bold" font-size="14" letter-spacing="2" opacity="0.85">
          <textPath href="#textPathInner" startOffset="0%">
            One Ring to rule them all, One Ring to find them, One Ring to bring them all and in the darkness bind them.
          </textPath>
        </text>
      </g>
    </svg>`,

    // 2. Middle-earth Map Background
    lotr_map_background: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 450" width="450" height="450">
      <defs>
        <radialGradient id="bgGrad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#241005"/>
          <stop offset="60%" stop-color="#120804"/>
          <stop offset="100%" stop-color="#080301"/>
        </radialGradient>
      </defs>
      <rect width="450" height="450" fill="url(#bgGrad)" />

      <g stroke="#a86528" opacity="0.25" stroke-width="1" fill="none">
        <circle cx="225" cy="225" r="140" stroke-dasharray="2 4" />
        <circle cx="225" cy="225" r="110" stroke-dasharray="1 3" />
        <path d="M 225,75 L 225,375 M 75,225 L 375,225" stroke-dasharray="3 3" />
        <path d="M 119,119 L 331,331 M 331,119 L 119,331" stroke-dasharray="2 4" />

        <path d="M 170,120 Q 180,160 175,210 T 190,280" stroke-width="1.5" />
        <path d="M 160,220 Q 210,225 270,230" stroke-width="1.5" />
        <path d="M 240,250 L 310,250 L 310,310 L 240,310 Z" stroke-dasharray="4 2" />

        <text x="225" y="105" text-anchor="middle" fill="#a86528" font-size="11" font-family="serif" letter-spacing="4" opacity="0.6">RHdescriptionON</text>
        <text x="285" y="280" text-anchor="middle" fill="#a86528" font-size="12" font-family="serif" letter-spacing="3" opacity="0.7">MORDOR</text>
        <text x="150" y="260" text-anchor="middle" fill="#a86528" font-size="10" font-family="serif" letter-spacing="2" opacity="0.5">GONDO</text>
        <text x="140" y="170" text-anchor="middle" fill="#a86528" font-size="10" font-family="serif" letter-spacing="2" opacity="0.5">ERIADOR</text>
      </g>
    </svg>`,

    // 3. Hour Hand (Andúril Narsil Sword)
    lotr_hand_hour: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 450" width="450" height="450">
      <g transform="translate(225,225)">
        <path d="M -4,0 L -2,-105 L 0,-125 L 2,-105 L 4,0 L 8,5 L -8,5 Z" fill="#fff5cc" stroke="#ff8c00" stroke-width="1" />
        <line x1="0" y1="-5" x2="0" y2="-110" stroke="#ff8c00" stroke-width="1.5" />
        <path d="M -10,-5 C -5,-8 5,-8 10,-5" stroke="#fff5cc" stroke-width="3" fill="none" />
        <circle cx="0" cy="0" r="6" fill="#ff8c00" />
      </g>
    </svg>`,

    // 4. Minute Hand (Elven Blade)
    lotr_hand_minute: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 450" width="450" height="450">
      <g transform="translate(225,225)">
        <path d="M -3,0 Q -7,-85 0,-155 Q 7,-85 3,0 Z" fill="#fff5cc" stroke="#ff8c00" stroke-width="1" />
        <line x1="0" y1="-5" x2="0" y2="-145" stroke="#ff8c00" stroke-width="1.5" />
        <circle cx="0" cy="0" r="5" fill="#ffaa00" />
      </g>
    </svg>`,

    // 5. Second Hand (Flame Needle)
    lotr_hand_second: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 450" width="450" height="450">
      <g transform="translate(225,225)">
        <line x1="0" y1="25" x2="0" y2="-170" stroke="#ff4500" stroke-width="1.5" />
        <circle cx="0" cy="-155" r="4" fill="#ffd700" />
        <circle cx="0" cy="0" r="3" fill="#ff4500" />
      </g>
    </svg>`,

    // 6. Ring Center Cap
    lotr_center_cap: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 450" width="450" height="450">
      <circle cx="225" cy="225" r="9" fill="#241005" stroke="#ffd700" stroke-width="2" />
      <circle cx="225" cy="225" r="4" fill="#ff8c00" />
    </svg>`
  };

  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();

    for (const [name, svgContent] of Object.entries(svgs)) {
      // Save SVG in design/svg
      fs.writeFileSync(path.join(svgDir, `${name}.svg`), svgContent);

      // Convert SVG to PNG in drawable-nodpi
      const pngBase64 = await page.evaluate(async svg => {
        const img = new Image();
        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
        await img.decode();
        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        canvas.getContext('2d').drawImage(img, 0, 0);
        return canvas.toDataURL('image/png').split(',')[1];
      }, svgContent);

      fs.writeFileSync(path.join(drawableDir, `${name}.png`), Buffer.from(pngBase64, 'base64'));
      console.log(`Exported asset: ${name}.png`);
    }
  } finally {
    await browser.close();
  }
})();
