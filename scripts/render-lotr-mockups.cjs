const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

(async () => {
  const root = path.resolve(__dirname, '..');
  const dist = path.join(root, 'dist');
  const drawableDir = path.join(root, 'lotr/src/main/res/drawable-nodpi');
  fs.mkdirSync(dist, { recursive: true });
  fs.mkdirSync(drawableDir, { recursive: true });

  const launchOpts = process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : { headless: true };
  const browser = await chromium.launch(launchOpts);
  try {
    const page = await browser.newPage();

    function createRingSVG(glowColor, textColor) {
      return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 450" width="450" height="450">
        <defs>
          <radialGradient id="ringGlow" cx="50%" cy="50%" r="50%">
            <stop offset="70%" stop-color="#000" stop-opacity="0"/>
            <stop offset="85%" stop-color="${glowColor}" stop-opacity="0.3"/>
            <stop offset="92%" stop-color="${glowColor}" stop-opacity="0.6"/>
            <stop offset="98%" stop-color="${glowColor}" stop-opacity="0.1"/>
            <stop offset="100%" stop-color="#000" stop-opacity="0"/>
          </radialGradient>
          <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <path id="textPathOuter" d="M 225,225 m -185,0 a 185,185 0 1,1 370,0 a 185,185 0 1,1 -370,0" />
          <path id="textPathInner" d="M 225,225 m -160,0 a 160,160 0 1,0 320,0 a 160,160 0 1,0 -320,0" />
        </defs>

        <circle cx="225" cy="225" r="225" fill="url(#ringGlow)" />
        <circle cx="225" cy="225" r="185" stroke="${glowColor}" stroke-width="1.5" fill="none" opacity="0.4" />
        <circle cx="225" cy="225" r="162" stroke="${glowColor}" stroke-width="1.5" fill="none" opacity="0.4" />

        <g filter="url(#glowFilter)">
          <text fill="${textColor}" font-family="serif" font-weight="bold" font-size="16" letter-spacing="3">
            <textPath href="#textPathOuter" startOffset="0%">
              Ash nazg durbatulûk, ash nazg gimbatul, ash nazg thrakatulûk agh burzum-ishi krimpatul.
            </textPath>
          </text>
          <text fill="${textColor}" font-family="serif" font-weight="bold" font-size="14" letter-spacing="2" opacity="0.85">
            <textPath href="#textPathInner" startOffset="0%">
              One Ring to rule them all, One Ring to find them, One Ring to bring them all and in the darkness bind them.
            </textPath>
          </text>
        </g>
      </svg>`;
    }

    function createMapSVG(theme) {
      let bgGrad, strokeColor;
      if (theme === 'fire') {
        bgGrad = ['#120804', '#241005', '#080301'];
        strokeColor = '#a86528';
      } else if (theme === 'silver') {
        bgGrad = ['#061018', '#0d1e2e', '#03080e'];
        strokeColor = '#4a82a6';
      } else {
        bgGrad = ['#111315', '#22262a', '#0a0b0c'];
        strokeColor = '#8a99a6';
      }

      return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 450" width="450" height="450">
        <defs>
          <radialGradient id="bgGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="${bgGrad[1]}"/>
            <stop offset="60%" stop-color="${bgGrad[0]}"/>
            <stop offset="100%" stop-color="${bgGrad[2]}"/>
          </radialGradient>
        </defs>
        <rect width="450" height="450" fill="url(#bgGrad)" />

        <g stroke="${strokeColor}" opacity="0.22" stroke-width="1" fill="none">
          <circle cx="225" cy="225" r="140" stroke-dasharray="2 4" />
          <circle cx="225" cy="225" r="110" stroke-dasharray="1 3" />
          <path d="M 225,75 L 225,375 M 75,225 L 375,225" stroke-dasharray="3 3" />
          <path d="M 119,119 L 331,331 M 331,119 L 119,331" stroke-dasharray="2 4" />

          <path d="M 170,120 Q 180,160 175,210 T 190,280" stroke-width="1.5" />
          <path d="M 160,220 Q 210,225 270,230" stroke-width="1.5" />
          <path d="M 240,250 L 310,250 L 310,310 L 240,310 Z" stroke-dasharray="4 2" />

          <text x="225" y="105" text-anchor="middle" fill="${strokeColor}" font-size="11" font-family="serif" letter-spacing="4" opacity="0.6">RHdescriptionON</text>
          <text x="285" y="280" text-anchor="middle" fill="${strokeColor}" font-size="12" font-family="serif" letter-spacing="3" opacity="0.7">MORDOR</text>
          <text x="150" y="260" text-anchor="middle" fill="${strokeColor}" font-size="10" font-family="serif" letter-spacing="2" opacity="0.5">GONDO</text>
          <text x="140" y="170" text-anchor="middle" fill="${strokeColor}" font-size="10" font-family="serif" letter-spacing="2" opacity="0.5">ERIADOR</text>
        </g>
      </svg>`;
    }

    function createHandsSVG(hourAngle, minAngle, secAngle, color, glowColor) {
      return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 450" width="450" height="450">
        <defs>
          <filter id="handGlow">
            <feGaussianBlur stdDeviation="2" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        <circle cx="225" cy="225" r="8" fill="${color}" stroke="${glowColor}" stroke-width="2" />

        <g transform="rotate(${hourAngle} 225 225)" filter="url(#handGlow)">
          <path d="M 221,225 L 223,120 L 225,100 L 227,120 L 229,225 L 233,230 L 217,230 Z" fill="${color}" stroke="${glowColor}" stroke-width="1" />
          <line x1="225" y1="220" x2="225" y2="115" stroke="${glowColor}" stroke-width="1.5" />
          <path d="M 215,220 C 220,218 230,218 235,220" stroke="${color}" stroke-width="3" fill="none" />
        </g>

        <g transform="rotate(${minAngle} 225 225)" filter="url(#handGlow)">
          <path d="M 222,225 Q 218,140 225,70 Q 232,140 228,225 Z" fill="${color}" stroke="${glowColor}" stroke-width="1" />
          <line x1="225" y1="220" x2="225" y2="80" stroke="${glowColor}" stroke-width="1.5" />
        </g>

        <g transform="rotate(${secAngle} 225 225)">
          <line x1="225" y1="250" x2="225" y2="55" stroke="${glowColor}" stroke-width="1.5" />
          <circle cx="225" cy="70" r="4" fill="${glowColor}" />
          <circle cx="225" cy="225" r="3" fill="${glowColor}" />
        </g>
      </svg>`;
    }

    async function renderMockup(themeName, themeConfig, isAOD = false) {
      const { glowColor, textColor, mainColor, mapTheme } = themeConfig;

      const ringSvg = createRingSVG(glowColor, textColor);
      const mapSvg = createMapSVG(mapTheme);
      const handsSvg = createHandsSVG(100, 210, 45, mainColor, glowColor);

      const html = `<!DOCTYPE html>
      <html>
      <head>
        <style>
          body { margin: 0; background: #000; width: 450px; height: 450px; overflow: hidden; font-family: serif; }
          .container { position: relative; width: 450px; height: 450px; border-radius: 50%; overflow: hidden; }
          .layer { position: absolute; top: 0; left: 0; width: 450px; height: 450px; }
          .hud-text { position: absolute; text-align: center; color: ${textColor}; text-shadow: 0 0 6px ${glowColor}; }
          .aod-dim { opacity: ${isAOD ? 0.45 : 1.0}; }
        </style>
      </head>
      <body>
        <div class="container ${isAOD ? 'aod-dim' : ''}">
          <div class="layer">${mapSvg}</div>
          <div class="layer">${ringSvg}</div>
          <div class="hud-text" style="top: 105px; left: 125px; width: 200px; font-size: 15px; font-weight: bold;">
            OCT 15 · THU
          </div>
          <div class="hud-text" style="top: 150px; left: 145px; width: 160px; font-size: 12px;">
            BATTERY 82%
          </div>
          <div class="hud-text" style="top: 275px; left: 145px; width: 160px; font-size: 12px;">
            STEPS 4 987
          </div>
          ${isAOD ? '' : `<div class="layer">${handsSvg}</div>`}
        </div>
      </body>
      </html>`;

      await page.setContent(html);
      const screenshot = await page.screenshot({ type: 'png' });
      fs.writeFileSync(path.join(dist, `lotr-mockup-${themeName}.png`), screenshot);
      if (themeName === 'fire-gold') {
        fs.writeFileSync(path.join(drawableDir, 'preview.png'), screenshot);
      }
      console.log(`Rendered mockup: lotr-mockup-${themeName}.png`);
    }

    await renderMockup('fire-gold', {
      glowColor: '#ff8c00',
      textColor: '#ffd700',
      mainColor: '#fff5cc',
      mapTheme: 'fire'
    });

    await renderMockup('elven-silver', {
      glowColor: '#38b6ff',
      textColor: '#e0f7ff',
      mainColor: '#ffffff',
      mapTheme: 'silver'
    });

    await renderMockup('gondor-white', {
      glowColor: '#c0c0c0',
      textColor: '#f0f0f0',
      mainColor: '#ffffff',
      mapTheme: 'gondor'
    });

    await renderMockup('aod', {
      glowColor: '#ff8c00',
      textColor: '#ffd700',
      mainColor: '#fff5cc',
      mapTheme: 'fire'
    }, true);

  } finally {
    await browser.close();
  }
})();
