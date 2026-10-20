// Design previews, NOT Wear OS screenshots. Source-of-truth: WFF XML and packed artwork.
// Chromium measures the actual drawn sample strings at Galaxy Watch7-scale sizes.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

(async () => {
  const root = path.resolve(__dirname, '..');
  const drawable = path.join(root,'lotrwatchface/src/main/res/drawable-nodpi');
  const out = path.join(root,'dist/lotr-preview');
  fs.mkdirSync(out,{recursive:true});
  const xml = fs.readFileSync(path.join(root,'lotrwatchface/src/main/res/raw/watchface.xml'),'utf8');
  const names = ['lotr_middle_earth_map','lotr_one_ring_bezel','lotr_hour_hand','lotr_minute_hand','lotr_second_hand'];
  const assets = {};
  for (const name of names) {
    const file = path.join(drawable,name+'.png');
    if (!fs.existsSync(file)) throw new Error('Missing rasterized LOTR artwork: '+file);
    assets[name] = 'data:image/png;base64,'+fs.readFileSync(file).toString('base64');
  }
  const options = {headless:true};
  if (process.env.CHROMIUM_PATH) options.executablePath=process.env.CHROMIUM_PATH;
  const browser=await chromium.launch(options);
  try {
    const page=await browser.newPage({viewport:{width:480,height:480}});
    const results=await page.evaluate(async ({xml,assets}) => {
      const parsed=new DOMParser().parseFromString(xml,'application/xml');
      if(parsed.querySelector('parsererror'))throw new Error('Invalid WFF XML');
      const slots=[...parsed.querySelectorAll('ComplicationSlot')];
      if(slots.length!==5) throw new Error('Expected 5 native complication slots');
      const ordered=['lotr_battery_slot','lotr_heart_rate_slot','lotr_steps_slot','lotr_date_slot','lotr_workout_slot'];
      const samples=['100%','199 BPM','100 000','OCT 20','NYITÁS'];
      const images={};
      for(const [k,v] of Object.entries(assets)){
        const img=new Image();img.src=v;await img.decode();images[k]=img;
      }
      const output=[];
      const checks=[];
      const testCanvas=document.createElement('canvas');
      const measure=testCanvas.getContext('2d');
      function number(el,attr){return Number(el.getAttribute(attr));}
      for(const size of [432,480]){
        const scale=size/450;
        for(let i=0;i<slots.length;i++){
          const slot=slots[i];
          if(slot.getAttribute('displayName')!==ordered[i])throw new Error('Slot order changed');
          const comp=slot.querySelector('Complication[type="SHORT_TEXT"]')||slot.querySelector('Complication[type="LONG_TEXT"]');
          if(!comp)throw new Error('Missing short/long text renderer for slot '+i);
          const txt=[...comp.querySelectorAll('PartText')];
          if(txt.length!==2)throw new Error('Expected two text rows in '+ordered[i]);
          const top=txt[0],bottom=txt[1];
          const topEnd=number(top,'y')+number(top,'height');
          const bottomStart=number(bottom,'y');
          if(topEnd>bottomStart)throw new Error('Overlapping caption/value in '+ordered[i]);
          const title=top.querySelector('Font').textContent.trim();
          const x=number(slot,'x'),y=number(slot,'y'),w=number(slot,'width'),h=number(slot,'height');
          const corners=[[x,y],[x+w,y],[x,y+h],[x+w,y+h]];
          for(const [cx,cy] of corners)if(Math.hypot(cx-225,cy-225)>=190)
            throw new Error(ordered[i]+' encroaches on gold bezel');
          for(const [part,value] of [[top,title],[bottom,samples[i]]]){
            const font=part.querySelector('Font');
            const fontSize=number(font,'size');
            measure.font='700 '+(fontSize*scale)+'px sans-serif';
            const measured=measure.measureText(value).width;
            const available=(number(part,'width')-4)*scale;
            if(measured>available+0.01)throw new Error(ordered[i]+' text overflow ('+value+') at '+size+': '+measured.toFixed(1)+'px > '+available.toFixed(1)+'px');
            if(fontSize>number(part,'height')-2)throw new Error(ordered[i]+' vertical text clipping');
            checks.push({size,slot:ordered[i],row:part===top?'caption':'value',value,measuredWidthPx:+measured.toFixed(2),availableWidthPx:+available.toFixed(2),pass:true});
          }
        }
        for(const ambient of [false,true]){
          const canvas=document.createElement('canvas');canvas.width=size;canvas.height=size;
          const ctx=canvas.getContext('2d');
          ctx.fillStyle='#26190e';ctx.fillRect(0,0,size,size);
          ctx.save();ctx.scale(scale,scale);
          ctx.beginPath();ctx.arc(225,225,225,0,Math.PI*2);ctx.clip();
          if(!ambient)ctx.drawImage(images.lotr_middle_earth_map,0,0,450,450);
          ctx.save();ctx.globalAlpha=ambient?.35:1;
          ctx.drawImage(images.lotr_one_ring_bezel,0,0,450,450);
          ctx.restore();
          if(!ambient){
            slots.forEach((slot,i)=>{
              const x=number(slot,'x'),y=number(slot,'y'),w=number(slot,'width'),h=number(slot,'height');
              const p=(slot.querySelector('Complication[type="SHORT_TEXT"]')||slot.querySelector('Complication[type="LONG_TEXT"]'));
              const txt=[...p.querySelectorAll('PartText')];
              ctx.fillStyle='#CCB28A';ctx.fillRect(x,y,w,h);
              ctx.strokeStyle='#6E4927';ctx.lineWidth=1.1;ctx.strokeRect(x+.5,y+.5,w-1,h-1);
              ctx.strokeStyle='#E6C796';ctx.lineWidth=.55;ctx.strokeRect(x+3,y+3,w-6,h-6);
              txt.forEach((part,n)=>{
                const font=part.querySelector('Font');
                const text=n===0?font.textContent.trim():samples[i];
                const size=number(font,'size'), px=x+number(part,'x'),py=y+number(part,'y');
                ctx.font='700 '+size+'px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
                ctx.fillStyle='#342317';ctx.fillText(text,px+number(part,'width')/2,py+number(part,'height')/2);
              });
            });
          }
          function hand(name,degrees,w,h,px,py) {
            ctx.save();ctx.translate(225,225);ctx.rotate(degrees*Math.PI/180);
            ctx.drawImage(images[name],-w*px,-h*py,w,h);
            ctx.restore();
          }
          // 10:08:30 reference position. Native rotation is handled by WFF, not this preview.
          hand('lotr_hour_hand',304.25,24,125,.5,.896);
          hand('lotr_minute_hand',51,18,190,.5,.905263);
          if(!ambient)hand('lotr_second_hand',180,6,196,.5,.867347);
          ctx.fillStyle='#4D321B';ctx.beginPath();ctx.arc(225,225,6,0,Math.PI*2);ctx.fill();
          ctx.fillStyle='#D8BC74';ctx.beginPath();ctx.arc(225,225,3,0,Math.PI*2);ctx.fill();
          ctx.restore();
          output.push({filename:'one-ring-'+size+(ambient?'-ambient':'-active')+'.png',base64:canvas.toDataURL('image/png').split(',')[1]});
        }
      }
      return {output,checks,note:'Raster previews with illustrative sample values; not Wear OS runtime capture.'};
    },{xml,assets});
    for(const item of results.output)fs.writeFileSync(path.join(out,item.filename),Buffer.from(item.base64,'base64'));
    fs.writeFileSync(path.join(out,'layout-report.json'),JSON.stringify({checks:results.checks,note:results.note},null,2)+'\n');
    console.log('PASS: 432/480 px sample text bounds and non-overlapping rows; '+results.output.length+' active/ambient previews generated');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
