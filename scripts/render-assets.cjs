// Only needed when editing the artwork. APK builds use the committed PNGs.
// npm install --no-save playwright@1.62.1; npx playwright install chromium
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
(async () => {
  const root = path.resolve(__dirname, '..');
  const checkOnly = process.env.CHECK_ONLY === '1';
  const version = fs.readFileSync(path.join(root,'watchface/build.gradle.kts'),'utf8')
    .match(/versionName\s*=\s*"([^"]+)"/)[1].replace(/-test$/, '');
  const dir = path.join(root, 'watchface/src/main/res/drawable-nodpi');
  const results = path.join(root, 'dist');
  fs.mkdirSync(results, {recursive:true});
  const options = {headless:true};
  if (process.env.CHROMIUM_PATH) options.executablePath = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(options);
  try {
    const page = await browser.newPage();
    for (const file of fs.readdirSync(path.join(root, 'design/svg')).filter(f=>f.endsWith('.svg'))) {
      const svg = fs.readFileSync(path.join(root, 'design/svg', file), 'utf8');
      const png = await page.evaluate(async svg => {
        const img = new Image();
        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
        await img.decode();
        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth; canvas.height = img.naturalHeight;
        canvas.getContext('2d').drawImage(img, 0, 0);
        return canvas.toDataURL('image/png').split(',')[1];
      }, svg);
      if (!checkOnly) fs.writeFileSync(path.join(dir, file.replace('.svg','.png')), Buffer.from(png,'base64'));
    }
    // Static illustrations use the native layout, resources and font sizes.
    // Sample provider data is confined to these previews, never the watch face.
    // These images are not Android runtime screenshots.
    const assets = {};
    for (const f of fs.readdirSync(dir).filter(f=>f.endsWith('.png') && f!=='preview.png'))
      assets[f.replace('.png','')] = 'data:image/png;base64,' + fs.readFileSync(path.join(dir,f)).toString('base64');
    const layout = JSON.parse(fs.readFileSync(path.join(root, 'design/layout.json')));
    const font = 'data:font/ttf;base64,' + fs.readFileSync(path.join(root,'watchface/src/main/res/font/hud_bold.ttf')).toString('base64');
    const scene = JSON.parse(fs.readFileSync(path.join(root, 'design/scene.json')));
    const {previews,checks} = await page.evaluate(async ({assets,layout,scene,font}) => {
      const face=new FontFace('HUD', `url(${font})`, {weight:'700'});await face.load();document.fonts.add(face);await document.fonts.ready;
      const images = {};
      for (const [name,url] of Object.entries(assets)) {
        const img = new Image(); img.src=url; await img.decode(); images[name]=img;
      }
      function render(theme, size=900, disabled=[], ambient=false, worst=false, bezel='metal') {
        const canvas=document.createElement('canvas'); canvas.width=size;canvas.height=size;
        const ctx=canvas.getContext('2d');ctx.scale(size/450,size/450);
        ctx.fillStyle='#000';ctx.fillRect(0,0,450,450);
        ctx.save();ctx.beginPath();ctx.arc(225,225,225,0,Math.PI*2);ctx.clip();
        function image(name,r,tint) {
          const [x,y,w,h]=r,img=images[name];
          if(!tint) {ctx.drawImage(img,x,y,w,h);return;}
          const layer=document.createElement('canvas');layer.width=w*2;layer.height=h*2;
          const c=layer.getContext('2d');c.drawImage(img,0,0,layer.width,layer.height);
          c.globalCompositeOperation='source-in';c.fillStyle=tint;c.fillRect(0,0,layer.width,layer.height);
          ctx.drawImage(layer,x,y,w,h);
        }
        const [primary,ice,greenEdge,blueEdge,hudIcon]=scene.palettes[theme].colors;
        function label(value,r,fontSize,color=ice) {
          const [x,y,w,h]=r;
          ctx.font=`700 ${fontSize}px HUD`;
          ctx.textAlign='center';ctx.fillStyle=color;
          const m=ctx.measureText(value);
          const baseline=y+(h+m.actualBoundingBoxAscent-m.actualBoundingBoxDescent)/2;
          ctx.fillText(value,x+w/2,baseline);
        }
        function global(p,r) {return [p.rect[0]+r[0],p.rect[1]+r[1],r[2],r[3]];}
        function digits(value,config) {
          const [bx,by,bw,bh]=config.rect, size=config.fontSize;
          const total=([...value].reduce((s,c)=>s+(c===':'?16:70)+8,0)-8)*size/100;
          let x=bx+(bw-total)/2, y=by+(bh-size)/2;
          for(const char of value) {
            const w=(char===':'?16:70)*size/100;
            image('digit_'+(char===':'?'colon':char),[x,y,w,size],primary);
            x+=w+8*size/100;
          }
        }
        if(ambient) {
          ctx.font='300 70px sans-serif';ctx.textAlign='center';ctx.fillStyle='#c4dde5';
          ctx.fillText('10:34',225,250);
        } else {
          image('armor_background',[0,0,450,450]);
          const shade=scene.backgroundShade;
          ctx.fillStyle='#'+shade.slice(3)+shade.slice(1,3);ctx.fillRect(0,0,450,450);
          if(bezel==='metal')image('bezel_metal',[0,0,450,450]);
          if(bezel!=='off')image('hud_track',[0,0,450,450],greenEdge);
          image('clock_frame',scene.clockFrame.rect,greenEdge);
          digits('10:34',scene.time);digits('27',scene.seconds);
          label('OCT 15 · THU',scene.date.rect,scene.date.fontSize,ice);
          const sample={armor:['ARMOR',worst?'100%':'81%'],health:['HEALTH',worst?'199 BPM':'97'],radar:['WORLD',worst?'23:59':'16:27'],steps:['ACTIVITY',worst?'100 000':'4 987'],battery:['POWER',worst?'100%':'82%'],training:['APP','Samsung Health']};
          for(const p of layout) {
            if(disabled.includes(p.id))continue;
            const [x,y,w,h]=p.rect,[bx,by,bw,bh]=p.bounds;
            ctx.save();ctx.beginPath();ctx.rect(x+bx,y+by,bw,bh);ctx.clip();
            image('glass_'+p.id,p.rect);
            image('edge_'+p.id,p.rect,['armor','radar'].includes(p.id)?greenEdge:blueEdge);
            const tint=['armor','health','radar'].includes(p.id)||p.id.startsWith('quick_')?hudIcon:ice;
            image('icon_'+p.icon,global(p,p.content.icon),tint);
            if(!p.id.startsWith('quick_')) {
              label(sample[p.id][0],global(p,p.content.caption),scene.fontSizes.caption);
              const value=sample[p.id][1];
              const size=p.id==='training'?scene.fontSizes.appValue:value.length>6?21:p.id==='health'?scene.fontSizes.healthValue:scene.fontSizes.value;
              label(value,global(p,p.content.value),size,p.id==='armor'?hudIcon:ice);
            }
            ctx.restore();
          }
        }
        ctx.restore();return canvas.toDataURL('image/png').split(',')[1];
      }
      // Check actual rasterized panel alpha and the arc cutouts at watch sizes.
      const checks={nativeWearOSRuntime:false, previewIcons:'Manual HUD illustration; live provider icons depend on the selected app/source', glass:[], sizes:[], curvedPanels:[]};
      for(const p of layout) {
        const img=images['glass_'+p.id], c=document.createElement('canvas');
        c.width=img.naturalWidth;c.height=img.naturalHeight;
        const ctx=c.getContext('2d');ctx.drawImage(img,0,0);
        const data=ctx.getImageData(0,0,c.width,c.height).data;
        let max=0;
        for(let i=3;i<data.length;i+=4)max=Math.max(max,data[i]);
        if(max>80)throw new Error(`${p.id}: glass too opaque (${max}/255)`);
        checks.glass.push({id:p.id,maxAlpha:max/255});
        if(p.outerArc) {
          if(!p.outline.d.includes(' A 204 204 '))throw new Error('Missing circular arc: '+p.id);
          let outside=0;
          for(let py=0;py<c.height;py++)for(let px=0;px<c.width;px++) {
            const gx=p.rect[0]+(px+.5)*p.rect[2]/c.width;
            const gy=p.rect[1]+(py+.5)*p.rect[3]/c.height;
            if(Math.hypot(gx-225,gy-225)>205 && data[(py*c.width+px)*4+3]>2)outside++;
          }
          if(outside)throw new Error(`${p.id}: panel fill escapes the common circular contour`);
          checks.curvedPanels.push(p.id);
        }
      }
      // Measure representative real provider values using the exact bundled font.
      // No fillText(maxWidth) compression: a failed fit must fail this check.
      const measure=document.createElement('canvas').getContext('2d');
      checks.text=[];
      for(const p of layout.filter(p=>p.content.value)) {
        const examples=p.id==='training'?['Samsung Health','TrainPilot']:p.id==='health'?['199 BPM','97','--']:p.id==='steps'?['4 987','99\u202f999','100 000','0','--']:p.id==='radar'?['23:59','16:27','--']:['100%','82%','0%','--'];
        for(const value of examples) {
          const size=p.id==='training'?scene.fontSizes.appValue:value.length>6?21:p.id==='health'?scene.fontSizes.healthValue:scene.fontSizes.value;
          measure.font=`700 ${size}px HUD`;const m=measure.measureText(value);
          const r=p.content.value, line=m.fontBoundingBoxAscent+m.fontBoundingBoxDescent;
          if(m.width+2>r[2])throw new Error(`${p.id}: ${value} width ${m.width} > ${r[2]}`);
          if(line+4>r[3])throw new Error(`${p.id}: ${value} line ${line} + padding > ${r[3]}`);
          checks.text.push({id:p.id,value,fontSize:size,width:m.width,lineHeight:line,box:r.slice(2)});
        }
      }
      for(const size of [432,480]) {
        for(const p of layout) {
          if(p.bounds[0]!==0 || p.bounds[1]!==0 || p.bounds[2]!==p.rect[2] || p.bounds[3]!==p.rect[3])
            throw new Error(`${p.id}: the native render crop must include the whole panel`);
        }
        checks.sizes.push(size);
      }
      const metal=images.bezel_metal, test=document.createElement('canvas');test.width=900;test.height=900;
      const metalCtx=test.getContext('2d');metalCtx.drawImage(metal,0,0);
      const pixels=metalCtx.getImageData(0,0,900,900).data;let intrusions=0;
      for(let y=0;y<900;y++)for(let x=0;x<900;x++)
        if(Math.hypot((x+.5)/2-225,(y+.5)/2-225)<217 && pixels[(y*900+x)*4+3]>2)intrusions++;
      if(intrusions)throw new Error('Metal bezel must not paint over the face interior');
      checks.bezel={transparentInteriorRadius:217,intrusions:0};
      checks.defaultPalette=scene.defaultPalette;
      const ref=scene.defaultPalette;
      const previews={picker:render(ref,450),reference:render(ref),cyan:render('unsc'),green:render('green'),ambient:render(ref,900,[],true),disabled:render(ref,900,['armor','steps','training','quick_left']),worst:render(ref,900,[],false,true),watch432:render(ref,432),watch480:render(ref,480),hudOnly:render(ref,900,[],false,false,'hud'),noBezel:render(ref,900,[],false,false,'off')};
      return {previews,checks};
    },{assets,layout,scene,font});
    if (!checkOnly) fs.writeFileSync(path.join(dir,'preview.png'),Buffer.from(previews.picker,'base64'));
    for(const name of ['reference','cyan','green','ambient','disabled','worst','watch432','watch480','hudOnly','noBezel'])
      fs.writeFileSync(path.join(results,`spartan-night-${version}-${name}.png`),Buffer.from(previews[name],'base64'));
    fs.writeFileSync(path.join(results,`geometry-checks-${version}.json`),JSON.stringify(checks,null,2)+'\n');
    console.log(`PASS: ${checks.curvedPanels.length} panels use circle arcs; all glass alpha <= 80/255; ${checks.text.length} text fits and native render crops checked at 432 and 480 px.`);
  } finally { await browser.close(); }
})();
